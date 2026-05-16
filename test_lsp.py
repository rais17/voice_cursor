# test_lsp.py
from src.workspace import workspace_manager
from src.lsp.manager import lsp_manager

# Setup — hamesha chahiye
workspace_manager.set('D:/PyVoiceCursor')
lsp_manager.on_workspace_set('D:/PyVoiceCursor')

import time
time.sleep(2)  # LSP startup

# ========================
# Test karna ho woh yahan
# ========================

from src.tools import find_references

# NOT WORKING — get_definition_location is currently disabled in system prompt

# get_definition_location test
# result = get_definition_location.func('src/tools/__init__.py', '_find_symbol_position')
# print("[get_definition_location]", result)

# find_references test
result = find_references.func('src/tools/__init__.py', 'find_references')
print("[find_references]", result)