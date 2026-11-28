import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from agent_runtime.core import Store
from agent_runtime import worker_preflight as probe


class NativePreflight(unittest.TestCase):
    @unittest.skipUnless(shutil.which('codex') and Path('/proc/self/ns/mnt').exists(),
                         'Linux Codex integration')
    def test_actual_backend_and_recheck(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tree = root / 'tree'
            subprocess.run(['git', 'init', '-q', str(tree)], check=True)
            store = Store(root / 'state.sqlite')
            output = tree / 'out'
            with self.assertRaisesRegex(ValueError, 'unsupported capability'):
                probe.check(store, 'codex', tree, output, {'file_read'})
            try:
                probe.check(store, 'codex', tree, output, probe.CAPABILITIES)
            except RuntimeError as error:
                if 'Failed to make / slave: Permission denied' not in str(error):
                    raise
                with self.assertRaisesRegex(RuntimeError, 'circuit open'):
                    probe.check(store, 'codex', tree, output, probe.CAPABILITIES)
                with self.assertRaisesRegex(RuntimeError, 'preflight failed'):
                    probe.check(store, 'codex', tree, output, probe.CAPABILITIES, refresh=True)
                (tree / '.codex').mkdir()
                (tree / '.codex/config.toml').write_text('# changed scope')
                with self.assertRaisesRegex(RuntimeError, 'preflight failed'):
                    probe.check(store, 'codex', tree, output, probe.CAPABILITIES)
            self.assertFalse(list(tree.glob('.worker-probe.*')))
            with store.transaction() as db:
                records = db.execute('SELECT binding FROM worker_capabilities').fetchall()
            self.assertTrue(all(json.loads(r['binding'])['tree'] == str(tree) for r in records))
