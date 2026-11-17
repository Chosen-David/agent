import importlib.util
from pathlib import Path

_path = (Path(__file__).resolve().parents[1] /
         'agent_doc/agent/test/collaborative-task/test_contract.py')
_spec = importlib.util.spec_from_file_location('collaborative_task_acceptance', _path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
TaskContractTests = _module.TaskContractTests
