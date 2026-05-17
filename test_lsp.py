# test_lsp.py
from src.workspace import workspace_manager
from src.lsp.manager import lsp_manager

# Setup — hamesha chahiye
workspace_manager.set('D:/PyVoiceCursor')
lsp_manager.on_workspace_set('D:/PyVoiceCursor')

# ========================
# Test karna ho woh yahan
# ========================

from src.tools import find_references

# NOT WORKING — get_definition_location is currently disabled in system prompt

# get_definition_location test
# result = get_definition_location.func('src/tools/__init__.py', '_find_symbol_position')
# print("[get_definition_location]", result)

# find_references test
result = find_references('open_file')
print("[find_references]", result)

# test_lsp.py mein add karo
# import jedi

# with open('D:/PyVoiceCursor/src/lsp/client.py', 'r') as f:
#     content = f.read()

# script = jedi.Script(content, path='D:/PyVoiceCursor/src/lsp/client.py', 
#                      project=jedi.Project('D:/PyVoiceCursor'))

# # Line 216 pe open_file defined hai
# refs = script.get_references(216, 8)
# for r in refs:
#     print(f"name={r.name} file={r.module_path} line={r.line} col={r.column}")
