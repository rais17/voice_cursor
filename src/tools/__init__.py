import os
import subprocess
from langchain_core.tools import tool

@tool
def run_terminal_command(command: str) -> str:
    """Run a terminal/shell command and return the output. Use for git operations, running scripts, etc."""

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        output = result.stdout or result.stderr
        return output if output else "Command executed with no output."
    except Exception as e:
        return f"Error running command: {e}"


@tool
def read_file(file_path: str) -> str:
    """Read the contents of a file with line numbers."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        numbered = ""
        for i, line in enumerate(lines, start=1):
            numbered += f"{i:4d} | {line}"
        
        return numbered
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"

@tool
def write_file(file_path: str, content: str) -> str:
    """Write content to a file at the given path. Creates file if it doesn't exist."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {e}"

@tool
def edit_file(file_path: str, old_content: str, new_content: str) -> str:
    """Replace a specific string in a file with new content. Use for targeted edits."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        if old_content not in content:
            return f"Could not find the specified content in {file_path}"
        updated = content.replace(old_content, new_content, 1)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated)
        return f"Successfully edited {file_path}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error editing file: {e}"

@tool
def list_files(directory: str = ".") -> str:
    """List all files and folders in a directory recursively."""
    try:
        result = []
        for root, dirs, files in os.walk(directory):
            # skip hidden and venv folders
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "venv" and d != "node_modules" and d != "__pycache__"]
            level = root.replace(directory, "").count(os.sep)
            indent = "  " * level
            result.append(f"{indent}{os.path.basename(root)}/")
            for file in files:
                result.append(f"{indent}  {file}")
        return "\n".join(result)
    except Exception as e:
        return f"Error listing files: {e}"

# @tool
# def create_file(file_path: str, content: str = "") -> str:
#     """Create a new file with optional initial content."""
#     try:
#         if os.path.exists(file_path):
#             return f"File already exists: {file_path}. Use write_file or edit_file instead."
#         os.makedirs(os.path.dirname(file_path), exist_ok=True) if os.path.dirname(file_path) else None
#         with open(file_path, "w", encoding="utf-8") as f:
#             f.write(content)
#         return f"Successfully created {file_path}"
#     except Exception as e:
#         return f"Error creating file: {e}"

@tool
def delete_file(file_path: str) -> str:
    """Delete a file at the given path."""
    try:
        os.remove(file_path)
        return f"Successfully deleted {file_path}"
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error deleting file: {e}"

@tool
def apply_diff(file_path: str, start_line: int, end_line: int, new_content: str) -> str:
    """
    Replace lines start_line to end_line (inclusive) in a file with new_content.
    Use read_file first to see line numbers, then call this tool.
    
    Args:
        file_path: Path to the file
        start_line: First line to replace (1-indexed)
        end_line: Last line to replace (1-indexed, inclusive)
        new_content: New content to insert (no need to add newlines at start/end)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        
        # Validation
        if start_line < 1 or start_line > total_lines:
            return f"Error: start_line {start_line} out of range (file has {total_lines} lines)"
        if end_line < start_line or end_line > total_lines:
            return f"Error: end_line {end_line} out of range (file has {total_lines} lines)"
        
        # Old content for diff display
        old_lines = lines[start_line - 1:end_line]
        old_content = "".join(old_lines).rstrip()
        
        # New content prepare
        new_lines = new_content.rstrip() + "\n"
        
        # Apply
        updated = lines[:start_line - 1] + [new_lines] + lines[end_line:]
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(updated)
        
        # Show diff
        diff = f"✅ Applied to {file_path} (lines {start_line}-{end_line})\n\n"
        diff += "--- REMOVED ---\n"
        diff += old_content + "\n\n"
        diff += "+++ ADDED +++\n"
        diff += new_content.rstrip()
        
        return diff
    
    except FileNotFoundError:
        return f"File not found: {file_path}"
    except Exception as e:
        return f"Error applying diff: {e}"
    
tools = [
    read_file,
    write_file,
    edit_file,
    list_files,
    # create_file,
    delete_file,
    # get_weather,
    run_terminal_command,
    apply_diff
]