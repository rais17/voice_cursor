import ast
import os

def _find_symbol_position(content: str, symbol: str) -> tuple[int, int] | None:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        import re
        for i, line in enumerate(content.splitlines()):
            match = re.search(rf'\b{re.escape(symbol)}\b', line)
            if match:
                return i + 1, match.start()
        return None

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == symbol:
                line = content.splitlines()[node.lineno - 1]
                return node.lineno, line.find(node.name)

    return None


def _find_definition_file(symbol: str, workspace: str) -> tuple[str, int, int] | None:
    """Poori workspace mein symbol ki definition dhundo."""
    for root, dirs, files in os.walk(workspace):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', 'venv', '.git', 'node_modules']]
        for file in files:
            if file.endswith('.py'):
                full = os.path.join(root, file)
                try:
                    with open(full, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    continue

                position = _find_symbol_position(content, symbol)
                if position:
                    return os.path.relpath(full, workspace), position[0], position[1]

    return None