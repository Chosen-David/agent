from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from agent_runtime.training_workspace import TrainingWorkspace


class WorkspaceTest(unittest.TestCase):
    def test_two_worktrees_one_physical_layout(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            trees=[root/'treeA',root/'treeB']
            docs=root/'docs'
            assets=root/'assets'
            for path in [*trees,docs,assets]:
                path.mkdir()
            db=TrainingWorkspace(root/'db')
            for tree in trees:
                db.bind(tree,'project',assets,docs)
            self.assertEqual(db.layout(trees[0],'test')['managed_output'],db.layout(trees[1],'test')['managed_output'])
            with self.assertRaises(ValueError):
                db.layout(trees[1],'../outside')
            self.assertFalse((trees[0]/'outputs').exists())
            db.db.close()
