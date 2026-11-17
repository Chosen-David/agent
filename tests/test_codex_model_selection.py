import importlib.util
from pathlib import Path

_path = Path(__file__).resolve().parents[1] / 'agent_doc/agent/test/collaborative-flow/test_model_selection.py'
_spec = importlib.util.spec_from_file_location('codex_model_selection_acceptance', _path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
ModelSelectionTests = _module.ModelSelectionTests
