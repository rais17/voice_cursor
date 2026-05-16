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
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == symbol:
                line = content.splitlines()[node.lineno - 1]
                char_pos = line.find(node.name)
                return node.lineno, char_pos
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == symbol:
                    return target.lineno, target.col_offset

    return None