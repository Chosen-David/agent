import os
import importlib.util
import io
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

root = Path(os.environ["AGENT_TEST_PROJECT_ROOT"])
sys.path.insert(0, str(root))
spec = importlib.util.spec_from_file_location('flow_mutation_tests', Path(__file__).with_name('test_flow.py'))
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
source = (root / 'agent_runtime/collaborative_flow.py').read_text()
cases = [
    ('delegate-human-decision', "if not human and q['kind'] != 'implementation':", 'if False:',
     'test_nonimplementation_decisions_cannot_be_delegated'),
    ('ignore-changed-tests', "if runner.suite_state(directory) != self.state['test_binding']:", 'if False:',
     'test_test_tampering_blocks_implementation'),
    ('premature-switch', "if self.state['phase'] != 'waiting' or self.clock() < self.state['deadline']:",
     "if self.state['phase'] != 'waiting':", 'test_default_waiting_and_eventual_timeout'),
]
for name, before, after, test in cases:
    baseline = unittest.TextTestRunner(stream=io.StringIO()).run(tests.FlowTests(test))
    if not baseline.wasSuccessful():
        raise SystemExit('baseline failed: ' + name)
    if source.count(before) != 1:
        raise SystemExit('mutation target changed: ' + name)
    module = types.ModuleType('agent_runtime.collaborative_flow')
    module.__package__ = 'agent_runtime'
    exec(compile(source.replace(before, after), str(root/'agent_runtime/collaborative_flow.py'), 'exec'), module.__dict__)
    with patch.dict(sys.modules, {'agent_runtime.collaborative_flow': module}):
        result = unittest.TextTestRunner(stream=io.StringIO()).run(tests.FlowTests(test))
    if not result.failures or result.errors:
        raise SystemExit('mutation survived or errored: ' + name)
    print(name + ': baseline passed; mutated behavior rejected by assertion')
