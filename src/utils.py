import ast
def _find_symbol_position(content: str, symbol: str) -> tuple[int, int] | None:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        # Fallback: regex with word boundary
        import re
        for i, line in enumerate(content.splitlines()):
            match = re.search(rf'\b{re.escape(symbol)}\b', line)
            if match:
                return i + 1, match.start()
        return None

    for node in ast.walk(tree):
        # Function/class definition
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == symbol:
                return node.lineno, node.col_offset
        # Variable assignment
        elif isinstance(node, ast.Name):
            if node.id == symbol:
                return node.lineno, node.col_offset

    return None