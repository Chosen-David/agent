import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from agent_runtime.research_handoff import ResearchHandoff


class HandoffIntegration(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.time=1000
        self.h=ResearchHandoff(self.root/'catalog',lambda:self.time)
        self.addCleanup(self.h.db.close)
        self.s=dict(task='review',experiment='one',cycle='cycle',producer='writer',pool='reviewer',evidence='evidence.json',
                    contract='digest',on_pass='continue',on_reject='repair',authorization='test scope',takeover=True,dependencies=[])
        self.h.submit(self.s)
        self.receipt=dict(decision='passed',reason='controlled human review of fixture')
        self.launch=self.root/'launched'
    def valid(self,s,r):return r==self.receipt
    def human(self,s,answer):
        if answer!='trusted human input':raise ValueError('untrusted')
        return self.receipt
    def review(self,s):return self.receipt
    def resume(self,s,r):
        if not self.launch.exists():
            subprocess.run([sys.executable,'-c','import sys;open(sys.argv[1],"x").write("started")',str(self.launch)],check=True)
        return True
    def advance(self,**kw):return self.h.advance('review',self,**kw)
    def test_a_f_restart(self):
        self.assertEqual(self.advance(human='trusted human input'),'passed')
        other=ResearchHandoff(self.root/'catalog',lambda:self.time)
        try:
            self.assertEqual(other.advance('review',self),'completed')
            self.assertEqual(other.advance('review',self),'completed')
        finally:other.db.close()
        self.assertEqual(self.launch.read_text(),'started')
    def test_predeadline_and_human_only(self):
        self.h.submit(dict(self.s,task='permission',takeover=False))
        self.assertEqual(self.advance(),'waiting-human')
        self.time+=601
        self.assertEqual(self.h.advance('permission',self),'blocked-human')
    def test_d_e(self):
        self.time+=601
        def independent():
            subprocess.run([sys.executable,'-c','import sys;open(sys.argv[1],"x").close()',str(self.root/'diagnostic')],check=True)
            return 'launched'
        out=self.h.tick(self,['review'],idle=lambda:True,independent=[independent])
        self.assertEqual(out,dict(independent='launched',review='blocked-backend'))
        self.assertFalse(self.launch.exists())
    def test_c(self):
        self.time+=601
        self.h.service('reviewer',True,'controlled')
        self.receipt=dict(decision='rejected',reason='known wrong reference')
        self.assertEqual(self.advance(),'rejected')
        self.assertEqual(self.advance(),'rejected')
        self.assertFalse(self.launch.exists())
    def test_g(self):
        with self.h.lock('review') as owns:
            self.assertTrue(owns)
            code='from agent_runtime.research_handoff import ResearchHandoff;import sys;print(ResearchHandoff(sys.argv[1]).advance("review",None))'
            self.assertEqual(subprocess.check_output([sys.executable,'-c',code,str(self.root/'catalog')],text=True).strip(),'busy')
        self.assertEqual(self.advance(human='trusted human input'),'passed')
        self.h.submit(self.s)
        self.assertEqual(self.advance(),'completed')
        self.assertEqual(self.advance(),'completed')

    def test_timeout_dispatch_is_scoped(self):
        from agent_runtime.collaborative_flow import Flow
        import inspect
        for kind,expected in [('implementation','review-dispatched'),('permission','blocked')]:
            flow=Flow(self.root,kind,clock=lambda:self.time)
            flow.create('test',mode='human')
            flow.ask([dict(id='q',kind=kind,question='Which bounded test?',options=['a','b'])])
            self.time+=601
            calls=[]
            def dispatch(task,state):
                calls.append(task)
                self.h.submit(dict(self.s,task=task))
                return dict(task=task,cycle='cycle',consumer='reviewer',authorization='test experiment')
            self.assertTrue(flow.timeout(dispatch))
            self.assertEqual(flow.state['phase'],expected)
            self.assertEqual(len(calls),int(kind=='implementation'))

    def test_unavailable_real_backend_before_dispatch(self):
        from agent_runtime.codex_host import load_profile
        from agent_runtime.training_claim import execute
        try:load_profile(self.root/'missing-profile.json')
        except (ValueError,OSError) as error:self.h.service('reviewer',False,str(error))
        req=dict(family='f',trajectory='t',goal='g',purpose='test',mode='NEW_TRAIN',
                 scientific_context={'scope':'test'},evidence_gap='test gap',review_handoff=self.s)
        with self.assertRaisesRegex(RuntimeError,'review backend unavailable'):
            execute(self.root/'catalog',req,[sys.executable,'-c','raise AssertionError("must not run")'])
        self.assertFalse(self.launch.exists())

    def test_crashed_reviewer_must_reconcile_before_replay(self):
        self.time+=600
        self.h.service('reviewer',True,'test')
        self.h._set('review','running','persisted dispatch')
        self.assertEqual(self.advance(),'blocked-ambiguous')
        self.assertEqual(self.advance(),'blocked-ambiguous')
        self.assertFalse(self.launch.exists())
