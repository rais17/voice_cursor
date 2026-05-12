import os


class WorkspaceManager:
    def __init__(self):
        self._workspace = None

    def set(self, path: str) -> str:
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return f"Path does not exist: {path}"
        if not os.path.isdir(path):
            return f"Path is not a directory: {path}"
        self._workspace = path
        
        # Start LSP server for detected language
        from src.lsp import lsp_manager
        lsp_status = lsp_manager.on_workspace_set(path)
        
        return f"Workspace set to: {path}\n{lsp_status}"

    def get(self) -> str | None:
        return self._workspace

    def is_set(self) -> bool:
        return self._workspace is not None

    def resolve(self, file_path: str) -> str:
        """
        Relative path ko workspace ke saath resolve karo.
        Agar absolute path hai toh as-is return karo.
        """
        if self._workspace and not os.path.isabs(file_path):
            return os.path.join(self._workspace, file_path)
        return file_path

    def get_tree(self, max_depth: int = 3) -> str:
        """Project structure tree generate karo."""
        if not self._workspace:
            return "No workspace set."

        lines = []
        skip_dirs = {".git", "__pycache__", "venv", "node_modules", ".venv", "dist", "build"}

        for root, dirs, files in os.walk(self._workspace):
            # Depth check
            depth = root.replace(self._workspace, "").count(os.sep)
            if depth >= max_depth:
                dirs.clear()
                continue

            # Skip unwanted dirs
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            indent = "  " * depth
            folder = os.path.basename(root)
            lines.append(f"{indent}{folder}/")

            for file in sorted(files):
                lines.append(f"{indent}  {file}")

        return "\n".join(lines)