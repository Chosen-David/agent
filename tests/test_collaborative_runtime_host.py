"""Include task-bound runtime acceptance in normal regression discovery."""
import importlib.util
from tests.central_acceptance import acceptance_path

path = acceptance_path('collaborative-flow/test_runtime_host.py')
spec = importlib.util.spec_from_file_location('collaborative_runtime_acceptance', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
RuntimeHostTests = module.RuntimeHostTests
