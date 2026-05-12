import os
from collections import Counter


EXTENSION_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "typescript",   # typescript-language-server JS bhi handle karta hai
    ".jsx": "typescript",
}

IGNORE_DIRS = {
    ".git", "__pycache__", "venv", "node_modules",
    ".venv", "dist", "build", ".next"
}


def detect_language(workspace_path: str) -> str | None:
    """
    Workspace mein files scan karo aur primary language return karo.
    
    Returns: "python", "typescript", ya None agar kuch detect na ho
    """
    counts = Counter()

    for root, dirs, files in os.walk(workspace_path):
        # Unwanted directories skip karo
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            language = EXTENSION_MAP.get(ext)
            if language:
                counts[language] += 1

    if not counts:
        return None

    # Sabse zyada files wali language return karo
    return counts.most_common(1)[0][0]