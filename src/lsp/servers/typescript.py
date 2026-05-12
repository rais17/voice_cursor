import sys
from src.lsp.servers.base import BaseServerConfig


class TypeScriptServerConfig(BaseServerConfig):
    def __init__(self):
        # Windows needs .cmd extension for npm global packages
        cmd = "typescript-language-server.cmd" if sys.platform == "win32" else "typescript-language-server"
        super().__init__(
            name="typescript",
            command=[cmd, "--stdio"],
            extensions=[".ts", ".tsx", ".js", ".jsx"],
            install_check=cmd,
        )

    def is_installed(self) -> bool:
        import shutil
        return shutil.which(self.install_check) is not None