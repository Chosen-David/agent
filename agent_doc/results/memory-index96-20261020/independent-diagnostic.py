"""Independent baseline/current CLI diagnostic; no implementation mutations."""
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
mode = sys.argv[1]
if mode == 'baseline':
    source = subprocess.check_output(['git', 'show', '50c1ca1e74df1026ba05b4cfd53903605315b234:agent_runtime/project_memory.py'], cwd=ROOT)
    module = types.ModuleType('agent_runtime.project_memory')
    module.__package__ = 'agent_runtime'
    module.__file__ = str(ROOT / 'agent_runtime/project_memory.py')
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, 'exec'), module.__dict__)

class Result(unittest.TextTestResult):
    def _capture(self, err):
        tb = err[2]
        while tb:
            local = tb.tb_frame.f_locals
            captured = local.get('err')
            if isinstance(captured, io.StringIO):
                self.stream.writeln('CAPTURED_STDERR=' + repr(captured.getvalue()))
            tb = tb.tb_next
    def addError(self, test, err):
        self._capture(err)
        super().addError(test, err)
    def addSubTest(self, test, subtest, err):
        if err:
            self._capture(err)
        super().addSubTest(test, subtest, err)

names = ['tests.test_memory_retrieval', 'tests.test_memory_check',
         'tests.test_memory_context_closure', 'tests.test_memory_cli_input']
suite = unittest.defaultTestLoader.loadTestsFromNames(names)
print(json.dumps({'mode': mode, 'python': sys.version, 'tests': names}), flush=True)
result = unittest.TextTestRunner(verbosity=1, resultclass=Result, warnings='default').run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
