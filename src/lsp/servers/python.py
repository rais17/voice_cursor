import sys
from src.lsp.servers.base import BaseServerConfig


class PythonServerConfig(BaseServerConfig):
    def __init__(self):
        super().__init__(
            name="python",
            command=[sys.executable, "-m", "pylsp"],
            extensions=[".py"],
            install_check="pylsp",
        )

    def is_installed(self) -> bool:
        try:
            import pylsp
            return True
        except ImportError:
            return False