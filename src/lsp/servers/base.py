from dataclasses import dataclass, field


@dataclass
class BaseServerConfig:
    """
    Har language server ki config ka blueprint.
    
    name: server ka naam (logging ke liye)
    command: server start karne ka shell command
    extensions: kaunsi files is server se handle hongi
    install_check: verify karne ka command ki server installed hai ya nahi
    """
    name: str = ""
    command: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    install_check: str = ""

    def is_installed(self) -> bool:
        """Server installed hai ya nahi check karo."""
        import shutil
        return shutil.which(self.install_check) is not None