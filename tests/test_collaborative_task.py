import importlib.util
from tests.central_acceptance import acceptance_path

_path = acceptance_path('collaborative-task/test_contract.py')
_spec = importlib.util.spec_from_file_location('collaborative_task_acceptance', _path)
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
TaskContractTests = _module.TaskContractTests

_review_spec = importlib.util.spec_from_file_location(
    'collaborative_review_evidence', _path.with_name('test_review_evidence.py'))
_review_module = importlib.util.module_from_spec(_review_spec)
_review_spec.loader.exec_module(_review_module)
ReviewEvidenceTests = _review_module.ReviewEvidenceTests

_dual_spec = importlib.util.spec_from_file_location(
    'collaborative_dual_model', _path.with_name('test_dual_model.py'))
_dual_module = importlib.util.module_from_spec(_dual_spec)
_dual_spec.loader.exec_module(_dual_module)
DualModelTests = _dual_module.DualModelTests
