"""Real Git checks for the trusted host's bounded index reconciliation."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts.run_knowledge_windows import git_sync


class HostGitTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        base=Path(self.temp.name); self.remote=base/'remote.git'; self.repo=base/'repo'; self.run=base/'run'
        self.run.mkdir(); self.env=dict(os.environ,GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never')
        self.git(base,'init','--bare','--initial-branch=main',str(self.remote))
        self.git(base,'init','--initial-branch=main',str(self.repo))
        self.identity(self.repo); (self.repo/'knowledge').mkdir()
        (self.repo/'knowledge/card.txt').write_text('initial',encoding='utf-8')
        self.git(self.repo,'add','.'); self.git(self.repo,'commit','-m','fixture baseline')
        self.git(self.repo,'remote','add','origin',str(self.remote))
        self.git(self.repo,'push','-u','origin','main')
        self.head=self.git(self.repo,'rev-parse','HEAD')

    def git(self,root,*args):
        result=subprocess.run(['git',*args],cwd=root,env=self.env,capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)
        return result.stdout.strip()

    def identity(self,repo):
        self.git(repo,'config','user.name','Knowledge fixture')
        self.git(repo,'config','user.email','fixture@example.invalid')

    def publish(self):
        publisher=self.repo.parent/'publisher'
        self.git(self.repo.parent,'clone',str(self.remote),str(publisher)); self.identity(publisher)
        (publisher/'knowledge/card.txt').write_text('published',encoding='utf-8')
        self.git(publisher,'add','.'); self.git(publisher,'commit','-m','fixture publication')
        self.git(publisher,'push','origin','main')
        return self.git(publisher,'rev-parse','HEAD')

    def test_preflight_refuses_dirty_repository(self):
        (self.repo/'knowledge/card.txt').write_text('user change',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'dirty'):
            git_sync(self.repo,self.run,self.env,before=True)
        self.assertEqual(self.git(self.repo,'rev-parse','HEAD'),self.head)

    def test_matching_published_tree_updates_only_metadata(self):
        published=self.publish()
        card=self.repo/'knowledge/card.txt'; card.write_text('published',encoding='utf-8')
        result=git_sync(self.repo,self.run,self.env,before=False)
        self.assertEqual(result['head'],published)
        self.assertEqual(card.read_text(),'published')
        self.assertEqual(self.git(self.repo,'status','--porcelain'),'')
        self.assertFalse((self.run/'reconcile.index').exists())

    def test_mismatch_keeps_working_file_and_original_branch(self):
        self.publish(); card=self.repo/'knowledge/card.txt'; card.write_text('unpublished user work',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'differs'):
            git_sync(self.repo,self.run,self.env,before=False)
        self.assertEqual(card.read_text(),'unpublished user work')
        self.assertEqual(self.git(self.repo,'rev-parse','HEAD'),self.head)

    def test_staged_out_of_scope_work_is_preserved(self):
        path=self.repo/'unexpected.py'; path.write_text('user work',encoding='utf-8')
        self.git(self.repo,'add',path.name)
        with self.assertRaisesRegex(RuntimeError,'outside'):
            git_sync(self.repo,self.run,self.env,before=False)
        self.assertEqual(path.read_text(),'user work')
        self.assertEqual(self.git(self.repo,'rev-parse','HEAD'),self.head)


if __name__=='__main__': unittest.main()
