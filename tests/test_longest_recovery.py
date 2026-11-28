import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from agent_runtime.result_store import ResultStore


class JsonStateAdapter:
    def save_completed(self, root, manifest):
        return (root / manifest['files'][1]['path']).read_text() == 'committed'

    def restore(self, root, manifest):
        self.state = json.loads((root / manifest['files'][0]['path']).read_text())
        return self.state['step'] == manifest['completed_step']

    def verify_training_state(self, root, manifest):
        return all(k in self.state for k in ('optimizer', 'rng', 'data', 'scheduler', 'model'))


class RecoveryTest(unittest.TestCase):
    def test_fallback_without_crossing_trajectories(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = ResultStore(root)
            adapter = JsonStateAdapter()
            family = hashlib.sha256(b'schedule-100').hexdigest()
            for step, trajectory in [(20,'one'), (40,'one'), (60,'two'), (80,'one')]:
                run = 'r'+str(step)
                d = root/run
                d.mkdir()
                state = dict(step=step, model=[1], rng=0, scheduler=step, data=step)
                if step != 40:
                    state['optimizer'] = {'momentum': [1]}
                (d/'rank').write_text(json.dumps(state))
                (d/'meta').write_text('committed')
                refs = []
                for filename, role in [('rank','rank'),('meta','metadata')]:
                    f = d/filename
                    refs.append(dict(path=str(f.relative_to(root)), type=role, rank=0,
                        sha256=hashlib.sha256(f.read_bytes()).hexdigest(), expected_size_bytes=f.stat().st_size))
                manifest = dict(schema_version='recovery-manifest/v1', run_id=run, producer='test',
                    source_run=trajectory, code_revision='1', input_revision='1', retention_reason='test',
                    consumers=[], dependencies=[], save_state='complete', files=refs, world_size=1,
                    asset_level='L3', family_sha256=family, trajectory_id=trajectory, completed_step=step)
                (d/'manifest').write_text(json.dumps(manifest))
                store.register_recovery(run+'/manifest', byte_limit=4096, provider=adapter)
            ids = ['r20','r40','r60','r80']
            result = store.longest_recovery(ids, trajectory_id='one', family_sha256=family,
                target_step=70, byte_limit=4096, provider=adapter)
            self.assertEqual(result['step'],20)
            self.assertEqual(result['failed'][0]['run_id'],'r40')
            result = store.longest_recovery(ids, trajectory_id='one', family_sha256='0'*64,
                target_step=100, byte_limit=4096, provider=adapter)
            self.assertEqual(result['action'],'verify_delta')
