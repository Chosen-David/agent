import os
from pathlib import Path

from agent_runtime.project_docs import document_root, uses_external_documents


def acceptance_path(relative):
    root = Path(__file__).resolve().parents[1]
    os.environ.setdefault("AGENT_TEST_PROJECT_ROOT", str(root))
    suite = document_root(root) / "test" if uses_external_documents(root) else root / "agent_doc/agent/test"
    return suite / relative
