"""Read-only Markdown context command; prefer `python -m agent_runtime.markdown_context`."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.markdown_context import main  # noqa: E402
if __name__ == '__main__':
    raise SystemExit(main())
