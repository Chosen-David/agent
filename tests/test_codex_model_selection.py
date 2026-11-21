import importlib.util
from tests.central_acceptance import acceptance_path

_path = acceptance_path('collaborative-flow/test_model_selection.py')
_spec = importlib.util.spec_from_file_location('codex_model_selection_acceptance', _path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
ModelSelectionTests = _module.ModelSelectionTests
