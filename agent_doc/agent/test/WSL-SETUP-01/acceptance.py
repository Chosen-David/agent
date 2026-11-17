import os
from pathlib import Path
import sys
import shutil
import unittest

root = Path(os.environ['AGENT_TEST_PROJECT_ROOT'])
if os.name != 'nt' or not shutil.which('powershell'):
    raise SystemExit('Required Windows PowerShell 5.1 runtime unavailable; WSL acceptance blocked')
suite = unittest.TestLoader().discover(str(root / 'tests'), pattern='test_setup_wsl.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() and result.testsRun > 0 and not result.skipped else 1)
