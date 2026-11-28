import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from agent_runtime.training_claim import execute
from agent_runtime.training_supervisor import TrainingSupervisor


class RetryTest(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.database = self.root / 'db'
        self.supervisor = TrainingSupervisor(self.database)
        self.addCleanup(self.supervisor.db.close)
        self.review = dict(task='review', experiment='optimizer', cycle='test', producer='training',
                           pool='independent', evidence='{attempt_evidence}', contract='verify contents',
                           on_pass='report', on_reject='repair', authorization='controlled test',
                           takeover=True, dependencies=[])

    def train(self,label,rc,variant, retry_of=None):
        output = self.root / label
        output.mkdir()
        plan = dict(physical_output=str(output), run_id=label, policy='profile', steps=2,
                    interval=None, checkpoint_bytes=0, extra_bytes=0, reserve_bytes=0)
        budget = self.root / (label + '.json')
        budget.write_text(json.dumps(plan))
        req = dict(family='test-family', trajectory=label, purpose='performance', goal='2 updates',
                   mode='NEW_TRAIN', evidence_gap='test attempt', artifact_plan=str(budget),
                   scientific_context={'scope':'optimizer','execution':{'variant':variant}})
        if retry_of is not None:
            req["retry_of"] = retry_of
        command = [sys.executable, '-c', 'import pathlib,sys; pathlib.Path(sys.argv[1]).write_text(sys.argv[2]); sys.exit(int(sys.argv[3]))',
                   str(output/'result'),label,str(rc)]
        self.assertEqual(execute(self.database,req,command),rc)
        row = self.supervisor.db.execute('SELECT claim,owner FROM training_claims WHERE json_extract(request,\'$.trajectory\')=?', (label,)).fetchone()
        return req, tuple(row)

    def first(self, pair, request):
        return self.supervisor.bind('review', *pair, request=request, review=self.review,
                                    evidence_relative='result', max_attempts=2)

    def next(self, pair, predecessor):
        return self.supervisor.bind('review', *pair, after_owner=predecessor[1], reason='repair launch')

    def test_consumer_survives_failure_and_restart(self):
        _, old = self.train('old', 7, 'wrong')
        expected, new = self.train('clean', 0, 'correct')
        self.first(old,expected)
        watch = subprocess.Popen([sys.executable,'-u','-m','agent_runtime.training_supervisor',
                                  str(self.database),'watch','review','--interval','1','--timeout','8'],
                                 stdout=subprocess.PIPE,text=True)
        self.addCleanup(watch.stdout.close)
        self.addCleanup(watch.kill)
        self.assertEqual(json.loads(watch.stdout.readline())['state'],'retry-needed')
        self.assertEqual(self.next(new,old),2)
        self.assertEqual(self.next(new,old),2)
        self.assertEqual(watch.wait(timeout=10),0)
        self.assertEqual(json.loads(watch.stdout.readline())['state'],'review-enqueued')
        restarted = TrainingSupervisor(self.database)
        self.addCleanup(restarted.db.close)
        self.assertEqual(restarted.tick('review')['state'],'review-enqueued')
        spec = json.loads(restarted.db.execute('SELECT spec FROM research_reviews').fetchone()[0])
        self.assertEqual(Path(spec['evidence']).read_text(),'clean')
        self.assertEqual(restarted.db.execute('SELECT count(*) FROM research_events').fetchone()[0],1)
        class Reader:
            def human(self, spec, decision):
                observed = Path(spec['evidence']).read_text()
                if observed != 'clean':
                    raise ValueError('wrong attempt selected')
                return {'decision':'passed','reason':observed}

            def valid(self, spec, receipt):
                return receipt['reason'] == Path(spec['evidence']).read_text()

            def resume(self, spec, receipt):
                return self.valid(spec, receipt)

        self.assertEqual(restarted.reviews.advance('review', Reader(), human='controlled receipt'), 'passed')
        self.assertEqual(restarted.reviews.advance('review', Reader()), 'completed')
        with self.assertRaisesRegex(ValueError,'predecessor'):
            self.supervisor.bind('review',*new,after_owner='stale',reason='repair launch')

    def test_follow_registered_retry_after_real_failure(self):
        expected, old = self.train('broken', 7, 'stable')
        self.first(old, expected)
        calls = []
        def launch(predecessor, event):
            calls.append(event)
            self.train('fixed', 0, 'stable', retry_of=predecessor)
        self.assertEqual(self.supervisor.follow_retry('review',remediate=launch)['state'], 'review-enqueued')
        restarted = TrainingSupervisor(self.database)
        self.addCleanup(restarted.db.close)
        self.assertEqual(restarted.follow_retry('review',remediate=launch)['attempt'], 2)
        self.assertEqual(len(calls), 1)
        spec = json.loads(restarted.db.execute('SELECT spec FROM research_reviews').fetchone()[0])
        self.assertEqual(Path(spec['evidence']).read_text(),'fixed')

    def test_refuse_ambiguous_registered_successors(self):
        expected, old = self.train('broken', 7, 'stable')
        self.first(old, expected)
        lineage = dict(task='review', claim=old[0], owner=old[1])
        for label in ('first', 'second'):
            self.train(label,0,'stable',retry_of=lineage)
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            self.supervisor.follow_retry('review')
        self.assertFalse(self.supervisor.db.execute('SELECT 1 FROM research_reviews').fetchone())

    def test_failure_budget_and_changed_successor(self):
        expected, old = self.train('old', 2, 'stable')
        _, wrong = self.train('wrong', 0, 'changed')
        _, failed = self.train('retry', 3, 'stable')
        self.first(old, expected)
        with self.assertRaisesRegex(ValueError,'scientific contract'):
            self.next(wrong,old)
        self.next(failed, old)
        self.assertEqual(self.supervisor.tick('review')['state'],'attempts-exhausted')
        with self.assertRaisesRegex(ValueError,'budget exhausted'):
            self.next(wrong,failed)
        self.assertFalse(self.supervisor.db.execute('SELECT 1 FROM research_reviews').fetchone())

    def test_no_rebinding_success_or_missing_evidence(self):
        expected, initial = self.train('original',0,'stable')
        _, other = self.train('other',0,'stable')
        self.first(initial,expected)
        (self.root/'original'/'result').unlink()
        self.assertEqual(self.supervisor.tick('review')['state'],'blocked-evidence')
        with self.assertRaisesRegex(ValueError,'no terminal failure receipt'):
            self.next(other,initial)
