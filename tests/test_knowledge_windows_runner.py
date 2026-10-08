"""Real Git checks for the trusted host's bounded index reconciliation."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts.run_knowledge_windows import git_sync, sync_host_skills, prepare_host


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

    def test_preflight_refuses_unpublished_local_commit(self):
        (self.repo/'knowledge/card.txt').write_text('unpublished',encoding='utf-8')
        self.git(self.repo,'add','.'); self.git(self.repo,'commit','-m','local only')
        local=self.git(self.repo,'rev-parse','HEAD')
        with self.assertRaisesRegex(RuntimeError,'not clean fetched main'):
            prepare_host(self.repo,self.run,self.env,skills=True)
        self.assertEqual(self.git(self.repo,'rev-parse','HEAD'),local)
        self.assertFalse((self.run/'host-skills-before.json').exists())

    def skill_fixture(self):
        directory=self.repo/'scripts'; directory.mkdir()
        script=directory/'setup_codex.py'
        script.write_text("raise RuntimeError('old updater must not run')\n",encoding='utf-8')
        self.git(self.repo,'add','.'); self.git(self.repo,'commit','-m','old updater')
        self.git(self.repo,'push','origin','main')
        self.publish()
        publisher=self.repo.parent/'publisher'
        (publisher/'scripts/setup_codex.py').write_text(
            "import os,sys\nfrom pathlib import Path\n"
            "p=Path(os.environ['FIXTURE_SKILL_LOG'])\n"
            "with p.open('a') as f: f.write(('check' if '--check' in sys.argv else 'sync')+'\\n')\n"
            "if os.environ.get('FIXTURE_SKILL_CONFLICT'): sys.exit('local edit preserved')\n",
            encoding='utf-8')
        self.git(publisher,'add','.'); self.git(publisher,'commit','-m','new updater')
        self.git(publisher,'push','origin','main')
        self.env['FIXTURE_SKILL_LOG']=str(self.run/'skill-steps.txt')
        return self.git(publisher,'rev-parse','HEAD')

    def test_pull_loads_new_updater_then_checks_before_model(self):
        import json
        published=self.skill_fixture()
        result=prepare_host(self.repo,self.run,self.env,skills=True)
        self.assertEqual(result['head'],published)
        self.assertEqual((self.run/'skill-steps.txt').read_text(),'sync\ncheck\n')
        receipt=json.loads((self.run/'host-skills-before.json').read_text())
        self.assertEqual(receipt['phase'],'before')
        self.assertEqual(receipt['check']['exit_code'],0)
        self.assertFalse((self.run/'host-skills.json').exists())
        sync_host_skills(self.repo,self.run,self.env)
        self.assertEqual(json.loads((self.run/'host-skills-before.json').read_text()),receipt)
        self.assertEqual(json.loads((self.run/'host-skills.json').read_text())['phase'],'after')

    def test_pull_conflict_preserves_diagnostics_and_blocks_launch(self):
        import json
        published=self.skill_fixture()
        self.env['FIXTURE_SKILL_CONFLICT']='1'
        with self.assertRaisesRegex(RuntimeError,'No model launched.*local edit preserved'):
            prepare_host(self.repo,self.run,self.env,skills=True)
        self.assertEqual(self.git(self.repo,'rev-parse','HEAD'),published)
        receipt=json.loads((self.run/'host-skills-before.json').read_text())
        self.assertNotEqual(receipt['exit_code'],0)
        self.assertNotIn('check',receipt)
        self.assertEqual((self.run/'skill-steps.txt').read_text(),'sync\n')

    def test_git_only_preflight_does_not_install_skills(self):
        self.skill_fixture()
        prepare_host(self.repo,self.run,self.env)
        self.assertFalse((self.run/'skill-steps.txt').exists())

    def test_post_install_check_failure_blocks_launch(self):
        import json
        directory=self.repo/'scripts'; directory.mkdir()
        (directory/'setup_codex.py').write_text(
            "import sys\nif '--check' in sys.argv: sys.exit('snapshot changed')\n",
            encoding='utf-8')
        self.git(self.repo,'add','.'); self.git(self.repo,'commit','-m','check fixture')
        self.git(self.repo,'push','origin','main')
        with self.assertRaisesRegex(RuntimeError,'No model launched.*snapshot changed'):
            prepare_host(self.repo,self.run,self.env,skills=True)
        receipt=json.loads((self.run/'host-skills-before.json').read_text())
        self.assertEqual(receipt['exit_code'],0)
        self.assertNotEqual(receipt['check']['exit_code'],0)

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

    def test_published_canonical_task_and_results_reconcile(self):
        self.publish(); publisher=self.repo.parent/'publisher'
        for root in (publisher,self.repo):
            for relative in ('agent_doc/task/TASK.md','agent_doc/task/task_details/K-01.md','agent_doc/results/round/check.json'):
                p=root/relative; p.parent.mkdir(parents=True,exist_ok=True)
                p.write_text('published fixture',encoding='utf-8')
        self.git(publisher,'add','.'); self.git(publisher,'commit','-m','canonical outputs')
        self.git(publisher,'push','origin','main')
        (self.repo/'knowledge/card.txt').write_text('published',encoding='utf-8')
        receipt=git_sync(self.repo,self.run,self.env,before=False)
        self.assertEqual(receipt['head'],self.git(publisher,'rev-parse','HEAD'))
        self.assertEqual(self.git(self.repo,'status','--porcelain'),'')

    def test_human_guide_is_outside_host_reconciliation_scope(self):
        p=self.repo/'agent_doc/guide/guide.md'; p.parent.mkdir(parents=True)
        p.write_text('human-only fixture',encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError,'outside'):
            git_sync(self.repo,self.run,self.env,before=False)
        self.assertEqual(p.read_text(),'human-only fixture')

    def test_host_skill_failure_is_reported_without_discarding_published_work(self):
        import json
        directory=self.repo/'scripts'; directory.mkdir()
        (directory/'setup_codex.py').write_text("import sys\nprint('local edit preserved')\nsys.exit(1)\n",encoding='utf-8')
        before=(self.repo/'knowledge/card.txt').read_bytes()
        with self.assertRaisesRegex(RuntimeError,'local skill synchronization blocked'):
            sync_host_skills(self.repo,self.run,self.env)
        receipt=json.loads((self.run/'host-skills.json').read_text())
        self.assertEqual(receipt['exit_code'],1)
        self.assertEqual((self.repo/'knowledge/card.txt').read_bytes(),before)
        self.assertEqual(self.git(self.repo,'rev-parse','HEAD'),self.head)


if __name__=='__main__': unittest.main()
