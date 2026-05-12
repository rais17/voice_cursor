from src.lsp.servers.python import PythonServerConfig
from src.lsp.servers.typescript import TypeScriptServerConfig

# Language → Config mapping
# Naya language add karna ho toh sirf yahan entry add karo
SERVER_REGISTRY = {
    "python": PythonServerConfig,
    "typescript": TypeScriptServerConfig,
}

def get_server_config(language: str):
    """Language ke liye server config return karo."""
    config_class = SERVER_REGISTRY.get(language)
    if not config_class:
        return None
    return config_class()