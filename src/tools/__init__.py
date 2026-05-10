import os
import subprocess
from langchain_core.tools import tool
from src.workspace import workspace_manager

@tool
def set_workspace(path: str) -> str:
    """Set the current working project/directory to work on."""
    result = workspace_manager.set(path)
    return result

@tool
def get_workspace() -> str:
    """Get the current working project directory and its structure."""
    if not workspace_manager.is_set():
        return "No workspace set. Use set_workspace first."
    tree = workspace_manager.get_tree()
    return f"Workspace: {workspace_manager.get()}\n\n{tree}"

@tool
def run_terminal_command(command: str) -> str:
    """Run a terminal/shell command in the current workspace."""
    cwd = workspace_manager.get() if workspace_manager.is_set() else os.getcwd()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        output = result.stdout or result.stderr
        return output if output else "Command executed with no output."
    except Exception as e:
        return f"Error running command: {e}"


@tool
def read_file(file_path: str) -> str:
    """Read file with line numbers. Use relative paths if workspace is set."""
    full_path = workspace_manager.resolve(file_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        numbered = ""
        for i, line in enumerate(lines, start=1):
            numbered += f"{i:4d} | {line}"
        return numbered
    except FileNotFoundError:
        return f"File not found: {full_path}"
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file. Use relative paths if workspace is set."""
    full_path = workspace_manager.resolve(file_path)
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True) if os.path.dirname(full_path) else None
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {full_path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def list_files(directory: str = ".") -> str:
    """List files. Uses workspace if set, otherwise current directory."""
    if directory == "." and workspace_manager.is_set():
        directory = workspace_manager.get()
    else:
        directory = workspace_manager.resolve(directory)
    try:
        result = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in {
                ".git", "__pycache__", "venv", "node_modules", ".venv"
            }]
            level = root.replace(directory, "").count(os.sep)
            indent = "  " * level
            result.append(f"{indent}{os.path.basename(root)}/")
            for file in files:
                result.append(f"{indent}  {file}")
        return "\n".join(result)
    except Exception as e:
         return f"Error listing files: {e}"

@tool
def delete_file(file_path: str) -> str:
    """Delete a file at the given path. Use relative paths if workspace is set."""
    full_path = workspace_manager.resolve(file_path)
    try:
        os.remove(full_path)
        return f"Successfully deleted {full_path}"
    except FileNotFoundError:
        return f"File not found: {full_path}"
    except Exception as e:
        return f"Error deleting file: {e}"

@tool
def apply_diff(file_path: str, start_line: int, end_line: int, new_content: str) -> str:
    """Replace lines in file. Use relative paths if workspace is set."""
    full_path = workspace_manager.resolve(file_path)
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        total_lines = len(lines)
        if start_line < 1 or start_line > total_lines:
            return f"Error: start_line {start_line} out of range (file has {total_lines} lines)"
        if end_line < start_line or end_line > total_lines:
            return f"Error: end_line {end_line} out of range (file has {total_lines} lines)"
        old_content = "".join(lines[start_line - 1:end_line]).rstrip()
        new_lines = new_content.rstrip() + "\n"
        updated = lines[:start_line - 1] + [new_lines] + lines[end_line:]
        with open(full_path, "w", encoding="utf-8") as f:
            f.writelines(updated)
        diff = f"✅ Applied to {full_path} (lines {start_line}-{end_line})\n\n"
        diff += "--- REMOVED ---\n"
        diff += old_content + "\n\n"
        diff += "+++ ADDED +++\n"
        diff += new_content.rstrip()
        return diff
    except FileNotFoundError:
        return f"File not found: {full_path}"
    except Exception as e:
        return f"Error applying diff: {e}"

tools = [
    read_file,
    write_file,
    list_files,
    delete_file,
    run_terminal_command,
    apply_diff,
    set_workspace,
    get_workspace,
]