import json
import sys
import subprocess
import threading
from pathlib import Path
from typing import Any
# from pathlib import Path
import platform

from langsmith import traceable



class LSPClient:
    """Generic LSP client — works with any language server."""

    def __init__(self, server_config):
        self._config = server_config
        self._process = None
        self._request_id = 0
        self._pending = {}
        self._responses = {}
        self._diagnostics = {}
        self._diagnostic_events = {}
        self._lock = threading.Lock()
        self._reader_thread = None
        self._running = False

    # ==========================================
    # Server Lifecycle
    # ==========================================

    def start(self, workspace_path: str) -> bool:
        if not self._config.is_installed():
            print(f"[LSP] {self._config.name} server not installed")
            return False

        try:
            # Windows specific — hide console window
            kwargs = {}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

            self._process = subprocess.Popen(
                self._config.command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **kwargs
            )
            self._running = True

            self._reader_thread = threading.Thread(
                target=self._read_loop,
                daemon=True
            )
            self._reader_thread.start()
            
            # Add this
            self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            self._stderr_thread.start()

            self._initialize(workspace_path)
            return True

        except Exception as e:
            print(f"[LSP] Failed to start {self._config.name}: {e}")
            return False
        
    def _read_stderr(self):
        print("[LSP STDERR THREAD] started")  # add this
        for line in self._process.stderr:
            print(f"[LSP STDERR] {line.decode(errors='replace').strip()}")


    def stop(self):
        self._running = False
        if self._process:
            try:
                self._send_notification("shutdown")
                self._send_notification("exit")
                self._process.terminate()
            except:
                pass
            self._process = None

    # ==========================================
    # Message Sending
    # ==========================================

    def _next_id(self) -> int:
        with self._lock:
            self._request_id += 1
            return self._request_id

    def _send(self, message: dict):
        if not self._process or not self._process.stdin:
            return

        body = json.dumps(message).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")

        try:
            self._process.stdin.write(header + body)
            self._process.stdin.flush()
        except BrokenPipeError:
            self._running = False

    def _send_request(self, method: str, params: dict = None) -> Any:
        req_id = self._next_id()
        event = threading.Event()

        with self._lock:
            self._pending[req_id] = event

        self._send({
            "jsonrpc": "2.0",
            "id": req_id,
            "method": method,
            "params": params or {}
        })

        event.wait(timeout=5.0)

        with self._lock:
            return self._responses.pop(req_id, None)

    def _send_notification(self, method: str, params: dict = None):
        self._send({
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        })

    # ==========================================
    # Response Reading
    # ==========================================

    def _read_loop(self):
        while self._running and self._process:
            try:
                message = self._read_message()
                if message:
                    self._handle_message(message)
            except Exception as e:  
                print(f"[LSP READ ERROR] {e}")
                break

    def _read_message(self) -> dict | None:
        if not self._process or not self._process.stdout:
            return None

        headers = {}
        while True:
            line = self._process.stdout.readline().decode("utf-8").strip()
            if not line:
                break
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()

        content_length = int(headers.get("Content-Length", 0))
        if content_length == 0:
            return None

        body = self._process.stdout.read(content_length)
        return json.loads(body.decode("utf-8"))

    @traceable
    def _handle_message(self, message: dict):
        
        print(f"[LSP MSG] {message.get('method', 'response')} id={message.get('id')}")
        print("DEBUG__message", message)
        msg_id = message.get("id")
        method = message.get("method", "")
        
        print(f"[LSP MSG] method={method} id={msg_id}")  # debug

        if msg_id is not None and "result" in message:
            with self._lock:
                self._responses[msg_id] = message.get("result")
                event = self._pending.pop(msg_id, None)
                if event:
                    event.set()

        elif method == "textDocument/publishDiagnostics":
            params = message.get("params", {})
            uri = params.get("uri", "")
            diagnostics = params.get("diagnostics", [])
            print(f"[LSP DIAG] uri={uri} count={len(diagnostics)}")  # debug
            self._diagnostics[uri] = diagnostics
            event = self._diagnostic_events.get(uri)
            if event:
                event.set()

    # ==========================================
    # LSP Handshake
    # ==========================================

    def _initialize(self, workspace_path: str):
        workspace_uri = self._path_to_uri(workspace_path)

        self._send_request("initialize", {
            "processId": None,
            "rootUri": workspace_uri,
            "capabilities": {
                "textDocument": {
                    "publishDiagnostics": {},
                    "hover": {"contentFormat": ["plaintext"]},
                }
            }
        })

        self._send_notification("initialized", {})

    # ==========================================
    # Public API
    # ==========================================

    @traceable
    def open_file(self, file_path: str, content: str):
        uri = self._path_to_uri(file_path)
        
        # Reset event and diagnostics before sending
        event = threading.Event()
        self._diagnostic_events[uri] = event
        self._diagnostics.pop(uri, None)
        
        print(f"[LSP OPEN] {uri}")
        
        self._send_notification("textDocument/didOpen", {
            "textDocument": {
                "uri": uri,
                "languageId": self._config.name,
                "version": 1,
                "text": content
            }
        })
        
        # self._send_notification("textDocument/didChange", {
        #     "textDocument": {"uri": uri, "version": 2},
        #     "contentChanges": [{"text": content}]
        # })

    @traceable
    def get_diagnostics(self, file_path: str, timeout: float = 5.0) -> list[dict]:
        uri = self._path_to_uri(file_path)
        
        event = self._diagnostic_events.get(uri)
        if event:
            event.wait(timeout=timeout)
        
        raw = self._diagnostics.get(uri, [])
        return self._format_diagnostics(raw)

    def get_hover(self, file_path: str, line: int, character: int = 0) -> str:
        uri = self._path_to_uri(file_path)
        result = self._send_request("textDocument/hover", {
            "textDocument": {"uri": uri},
            "position": {"line": line - 1, "character": character}
        })

        if not result:
            return ""

        contents = result.get("contents", {})
        if isinstance(contents, dict):
            return contents.get("value", "")
        return str(contents)

    # ==========================================
    # Helpers
    # ==========================================

    def _path_to_uri(self, path: str) -> str:
        try:
            resolved = Path(path).resolve()

            if platform.system() == "Windows":
                print(f"DEBUG__Resolved path 1: {resolved}")
                return "file:///" + str(resolved).replace("\\", "/")

            print(f"DEBUG__Resolved path 2: {resolved}")
            return resolved.as_uri()
        except Exception:
            # Fallback — direct path use karo
            print(f"WARNING: Failed to resolve path {path}, using fallback URI")
            clean = str(path).replace("\\", "/")
            return f"file:///{clean}"

    def _format_diagnostics(self, raw: list) -> list[dict]:
        severity_map = {1: "error", 2: "warning", 3: "info", 4: "hint"}
        result = []
        for d in raw:
            result.append({
                "line": d.get("range", {}).get("start", {}).get("line", 0) + 1,
                "message": d.get("message", ""),
                "severity": severity_map.get(d.get("severity", 1), "error"),
                "source": d.get("source", "")
            })
        return result