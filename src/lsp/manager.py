import os
from src.lsp.detector import detect_language
from src.lsp.client import LSPClient
from src.lsp.servers import get_server_config


class LSPManager:
    """Manages LSP server lifecycle for the current workspace."""

    def __init__(self):
        self._client: LSPClient | None = None
        self._current_language: str | None = None
        self._current_workspace: str | None = None

    def on_workspace_set(self, workspace_path: str) -> str:
        """
        Called when user sets a new workspace.
        Detects language, starts appropriate LSP server.
        Returns status message.
        """
        # Stop existing server if running
        self.stop()

        # Detect primary language
        language = detect_language(workspace_path)
        if not language:
            return "No supported language detected in workspace."

        # Get server config for detected language
        config = get_server_config(language)
        if not config:
            return f"No LSP server configured for: {language}"

        # Check if server is installed
        if not config.is_installed():
            return f"LSP server for {language} is not installed. Run: {self._install_hint(language)}"

        # Start LSP client
        self._client = LSPClient(config)
        success = self._client.start(workspace_path)

        if not success:
            self._client = None
            return f"Failed to start {language} LSP server."

        self._current_language = language
        self._current_workspace = workspace_path

        return f"LSP server started for {language}."

    def stop(self):
        """Stop current LSP server if running."""
        if self._client:
            self._client.stop()
            self._client = None
            self._current_language = None
            self._current_workspace = None

    def get_client(self) -> LSPClient | None:
        """Return active LSP client, or None if not running."""
        return self._client

    def is_running(self) -> bool:
        return self._client is not None

    def _install_hint(self, language: str) -> str:
        hints = {
            "python": "pip install python-lsp-server",
            "typescript": "npm install -g typescript-language-server typescript"
        }
        return hints.get(language, "check documentation")


# Singleton — one instance shared across the app
lsp_manager = LSPManager()