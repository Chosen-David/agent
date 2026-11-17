"""Compile runtime Python in memory and enforce the core's dependency boundary."""
import ast
import os
from pathlib import Path
import sys


def check(root):
    runtime = root / "agent_runtime"
    files = sorted(runtime.rglob("*.py"))
    if not files or not (runtime / "core.py").is_file():
        print("blocked: expected agent_runtime/core.py and runtime Python files")
        return 2
    for path in files:
        try:
            source = path.read_bytes()
            compile(source, str(path), "exec")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError) as exc:
            print(f"{path}: compile failure: {exc}")
            return 1
        if path.name == "core.py":
            for node in ast.walk(tree):
                names = ([item.name for item in node.names] if isinstance(node, ast.Import)
                         else [node.module or ""] if isinstance(node, ast.ImportFrom) else [])
                if any(name == "scripts" or name.startswith("scripts.") for name in names):
                    print(f"{path}:{node.lineno}: core must not import CLI scripts; move shared behavior into agent_runtime")
                    return 1
    print(f"compiled {len(files)} Python files; core dependency boundary passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(check(Path(os.environ["AGENT_TEST_PROJECT_ROOT"])))
