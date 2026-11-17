"""Include task-bound runtime acceptance in normal regression discovery."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / 'agent_doc/agent/test/collaborative-flow/test_runtime_host.py'
spec = importlib.util.spec_from_file_location('collaborative_runtime_acceptance', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
RuntimeHostTests = module.RuntimeHostTests
