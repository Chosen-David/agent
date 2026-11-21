import importlib.util
from tests.central_acceptance import acceptance_path

_path = acceptance_path('collaborative-flow/test_flow.py')
_spec = importlib.util.spec_from_file_location('collaborative_flow_acceptance', _path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
FlowTests = _module.FlowTests
