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
