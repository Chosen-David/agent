import os
from pathlib import Path
import sys
import unittest

if __name__ == '__main__':
    root = Path(os.environ['AGENT_TEST_PROJECT_ROOT']).resolve()
    sys.path.insert(0, str(root))
    tests = unittest.TestSuite()
    for name in ('workspace_status', 'storage_budget', 'recovery_registration', 'code_flow_html',
                 'agent_eval_pipeline', 'result_store', 'scheduler_ownership', 'scheduled_review',
                 'task_runtime_review', 'task_runtime', 'serial_recovery', 'codex_setup'):
        tests.addTests(unittest.defaultTestLoader.loadTestsFromName('tests.test_' + name))
    raise SystemExit(0 if unittest.TextTestRunner().run(tests).wasSuccessful() else 1)
