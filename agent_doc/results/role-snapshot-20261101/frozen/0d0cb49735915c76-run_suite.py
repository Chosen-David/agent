"""Serialize actual unittest result and full report before exiting."""
from pathlib import Path
import sys
import unittest
from capture import capture
D = Path(__file__).resolve().parent
mode, output = sys.argv[1:]
def suite():
    if mode == 'newtests':
        return unittest.defaultTestLoader.discover(str(D), pattern='test_role_definition.py')
    if mode == 'regression':
        return unittest.defaultTestLoader.loadTestsFromNames(['test_role_process', 'test_model_routing', 'test_setup_text', 'test_setup_manifest', 'test_install_profiles'])
    raise ValueError('unknown suite')
row = capture(suite, output)
print('completed=' + str(row['completed']))
raise SystemExit(0 if row['completed'] and row['result']['was_successful'] else 1)
