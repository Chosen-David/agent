from pathlib import Path
import tempfile
import unittest

from agent_runtime.checkpoint_retention import CheckpointRetention


class RetentionTest(unittest.TestCase):
    def test_alias_and_durable_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            db=root/'db'
            source=root/'old'
            source.mkdir()
            alias=root/'worktree'
            alias.symlink_to(source)
            later=root/'later'
            later.mkdir()
            args=dict(run='run',trajectory='trajectory',family='family',step=20,level='L3')
            ledger=CheckpointRetention(db)
            ledger.register('first',source,**args)
            self.assertEqual(ledger.register('first',alias,**args),'first')
            ledger.register('last',later,**dict(args,step=40))
            ledger.reference('first','analysis','momentum milestone')
            ledger.db.close()
            ledger=CheckpointRetention(db)
            result=ledger.review('first','last',store=None,provider=None,byte_limit=1000)
            self.assertEqual(result['status'],'protected')
            self.assertTrue(source.exists())
            self.assertEqual(result['references'],[('analysis','momentum milestone')])
            ledger.db.close()

    def test_preapproved_quarantine_preserves_payload_and_history(self):
        from contextlib import nullcontext
        class Host:
            def generation_matches(self, artifact, path):
                return artifact==path.name
            def release_lease(self, artifact, replacement):
                return nullcontext()
            def purge_facts(self, artifact, replacement, target):
                return dict(restore_verified=True, lightweight_history_retained=True,
                    replacement_reachable=True, all_references_checked=True, grace_elapsed=True,
                    no_unique_scientific_value=True,active_writes=[],consumers=[],
                    recovery_dependencies=[],retention_holds=[],leases=[])
            def review_recovery(self, artifact, replacement, **kwargs):
                return dict(action='candidate-for-review',reasons=[])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            ledger=CheckpointRetention(root/'db')
            files=[root/name for name in ('legacy','first','last')]
            for i,f in enumerate(files):
                f.write_bytes(bytes([i]))
                ledger.register(f.name,f,run='r',family='f',trajectory='t',step=i,level='L3',
                                origin='historical' if i==0 else 'managed',auto=i!=0,purge_after_quarantine=i==1)
            kwargs=dict(store=Host(),provider=Host(),byte_limit=10)
            self.assertEqual(ledger.quarantine('legacy','last',**kwargs)['status'],'protected')
            result=ledger.quarantine('first','last',**kwargs)
            self.assertEqual(Path(result['target']).read_bytes(),bytes([1]))
            self.assertEqual(files[2].read_bytes(),bytes([2]))
            self.assertEqual(files[0].read_bytes(),bytes([0]))
            with self.assertRaises(ValueError):
                ledger.reference('first','late','reader')
            self.assertEqual(ledger.purge_quarantined('legacy','last',provider=Host())['status'],'protected')
            self.assertEqual(ledger.purge_quarantined('first','last',provider=Host())['status'],'purged')
            self.assertFalse(Path(result['target']).exists())
            self.assertTrue(files[0].exists() and files[2].exists())
            ledger.db.close()
