import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root))
import setup

check = unittest.TestCase()

def snap(p):
    return {str(x.relative_to(p)): x.read_bytes() for x in p.rglob('*') if x.is_file()}

with tempfile.TemporaryDirectory(prefix='restart-independent-') as name, patch.dict(os.environ, {}, clear=True):
    p = Path(name)
    setup.install(p, model_inventory=setup.EMPTY_INVENTORY)
    before = snap(p)
    check.assertIs(setup.update_model_inventory(p, setup.EMPTY_INVENTORY), False)
    check.assertEqual(snap(p), before)
    route = p / '.claude/agent-workflows/model-routing.json'
    route.unlink()
    check.assertIs(setup.update_model_inventory(p, setup.EMPTY_INVENTORY), True)
    check.assertEqual(snap(p), before)
    value = setup.doctor(p)['doctor']
    check.assertIs(value['needs_restart'], False)
    check.assertIn('this doctor call', value['restart_scope'])
    check.assertIn('not checked', value['restart_hint'])
    policy = setup.load_json(setup.REPO / 'config/role_model_policy.json')
    inv = {'schema_version': 1, 'models': [{**policy['models']['opus'], 'available': True,
           'transport': 'native', 'capabilities': ['tools', 'vision']}]}
    with patch.object(setup, '_auto_discover_inventory', return_value=inv):
        changed = setup.doctor(p)
    check.assertIs(changed['doctor']['needs_restart'], True)
    check.assertEqual(changed['errors'], [])
    with patch.object(setup, '_auto_discover_inventory') as discover:
        check.assertIs(setup.doctor(p)['doctor']['needs_restart'], False)
    discover.assert_not_called()
    # CLI follows the same scoped report on an actual installed target.
    proc = subprocess.run([sys.executable, str(root / 'setup.py'), '--target', str(p), '--doctor'],
                          capture_output=True, text=True, check=False, timeout=30)
    check.assertEqual(proc.returncode, 0, proc.stderr)
    check.assertIs(json.loads(proc.stdout)['doctor']['needs_restart'], False)
    # A later model conflict cannot turn the additive result into permission to write earlier files.
    manifest = setup.load_json(p / '.claude/agent-workflows/installation.json')
    agent = next(k for k in reversed(list(manifest['files'])) if k.startswith('.claude/agents/'))
    (p / agent).write_text('locally edited\n', encoding='utf-8')
    before = snap(p)
    with check.assertRaisesRegex(ValueError, 'locally edited model file'):
        setup.update_model_inventory(p, setup.EMPTY_INVENTORY)
    check.assertEqual(snap(p), before)
print('PASS: identical contents, missing-file restoration, no-change report scope, real routing change, repeat call, actual CLI, and conflict-before-write')
