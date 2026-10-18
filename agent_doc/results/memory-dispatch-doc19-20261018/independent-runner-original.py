"""Isolated-process baseline swap; never rewrites production sources."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from agent_runtime import task_manifest
if '--baseline' in sys.argv:
    source = subprocess.check_output(['git', 'show', 'b58836816ff178abce4028348b7d3de3f21a31c7:agent_runtime/task_manifest.py'], cwd=ROOT)
    exec(compile(source, '<baseline task_manifest b588368>', 'exec'), task_manifest.__dict__)
paths = [ROOT / 'tests/test_dispatch_freshness.py', Path(__file__).with_name('independent-cases.py')]
suite = unittest.TestSuite()
for n, path in enumerate(paths):
    spec = importlib.util.spec_from_file_location('independent_loaded_' + str(n), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
