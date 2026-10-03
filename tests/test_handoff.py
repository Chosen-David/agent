import hashlib
import importlib.util
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('handoff', Path(__file__).resolve().parents[1] / 'scripts/validate_handoff.py')
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'answer.md').write_text('Measured result: 4')
        self.record = dict(schema_version=1, run_id='run-1', role='explain-research-concepts',
                           input_version='fixture-v1', status='completed', limitations=[],
                           artifacts=[dict(id='a1', path='answer.md', sha256=hashlib.sha256((self.root/'answer.md').read_bytes()).hexdigest())],
                           checks=[dict(criterion='arithmetic inspected',status='pass',artifact_ids=['a1'])], tasks=[])

    def test_valid_record(self):
        self.assertEqual(M.validate(self.record, self.root, True, expected_input_version='fixture-v1'), [])

    def test_changed_or_missing_artifact(self):
        (self.root / 'answer.md').write_text('changed')
        self.assertIn('artifact 0: sha256 mismatch', M.validate(self.record, self.root))
        (self.root / 'answer.md').unlink()
        self.assertIn('artifact 0: file missing', M.validate(self.record, self.root))

    def test_paths_cannot_escape_root(self):
        for path in ('../outside.md', '/etc/hosts'):
            with self.subTest(path=path):
                self.record['artifacts'][0]['path'] = path
                self.assertTrue(M.validate(self.record, self.root))

    def test_symlink_cannot_escape_root(self):
        (self.root/'link').symlink_to('/etc/hosts')
        self.record['artifacts'][0]['path']='link'
        self.assertIn('artifact 0: path escapes root', M.validate(self.record,self.root))

    def test_false_completion_rejected(self):
        self.record['checks'][0]['status']='not_run'
        self.assertTrue(M.validate(self.record,self.root))
        self.record['status']='partial'
        self.record['limitations']=['need actual run']
        self.assertEqual(M.validate(self.record,self.root), [])
        self.assertTrue(M.validate(self.record,self.root,True, expected_input_version='fixture-v1'))

    def test_dangling_or_absent_evidence(self):
        for refs in ([], ['missing']):
            self.record['checks'][0]['artifact_ids']=refs
            self.assertTrue(M.validate(self.record,self.root))

    def test_cycle_missing_dependency_and_blocked_predecessor(self):
        cases=[
            [{'task_id':'a','status':'todo','depends_on':['b']},{'task_id':'b','status':'todo','depends_on':['a']}],
            [{'task_id':'a','status':'todo','depends_on':['unknown']}],
            [{'task_id':'a','status':'blocked','reason':'input absent'}, {'task_id':'b','status':'done','depends_on':['a'],'evidence':['x']}]
        ]
        for tasks in cases:
            self.record['tasks']=tasks
            self.assertTrue(M.validate(self.record,self.root))

    def test_long_valid_dag(self):
        self.record['tasks']=[{'task_id':str(i),'status':'done','evidence':['a1'],'depends_on':[str(i-1)] if i else []} for i in range(1100)]
        self.assertEqual(M.validate(self.record,self.root), [])

    def test_completed_cannot_hide_pending_tasks(self):
        for status in ('todo', 'doing', 'blocked'):
            with self.subTest(status=status):
                self.record['tasks'] = [dict(task_id='remaining', status=status, reason='waiting for input')]
                self.record['status'] = 'completed'
                self.assertIn('remaining: unfinished task on completed run', M.validate(self.record,self.root))
                self.record['status'] = 'partial'
                self.record['limitations'] = ['Finish remaining task before acceptance']
                self.assertEqual(M.validate(self.record,self.root), [])
                self.assertTrue(M.validate(self.record,self.root,True, expected_input_version='fixture-v1'))

    def test_task_evidence_must_reference_artifacts(self):
        for evidence in ('a1', {'claim':'done'}, ['missing'], [True], [{}], [' '], []):
            with self.subTest(evidence=evidence):
                self.record['tasks'] = [dict(task_id='work', status='done', evidence=evidence)]
                self.assertTrue(M.validate(self.record,self.root))
        self.record['tasks'][0]['evidence'] = ['a1']
        self.assertEqual(M.validate(self.record,self.root,True, expected_input_version='fixture-v1'), [])

    def test_explicit_skip_is_terminal_but_not_dependency_completion(self):
        self.record['tasks'] = [dict(task_id='old', status='skipped', reason='not in current scope')]
        self.assertEqual(M.validate(self.record,self.root,True, expected_input_version='fixture-v1'), [])
        self.record['tasks'].append(dict(task_id='new',status='done',depends_on=['old'],evidence=['a1']))
        self.assertIn('new: done before dependency old', M.validate(self.record,self.root))

    def test_reason_requires_nonblank_string(self):
        self.record['status'] = 'partial'
        self.record['limitations'] = ['needs input']
        for status in ('skipped', 'blocked'):
            for reason in (' ', True, ['input missing'], {}):
                with self.subTest(status=status, reason=reason):
                    self.record['tasks'] = [dict(task_id='work',status=status,reason=reason)]
                    self.assertIn('work: reason/recovery required', M.validate(self.record,self.root))

    def test_bad_artifact_paths_are_diagnostic(self):
        (self.root/'loop').symlink_to('loop')
        for path in ('loop', 'bad\0path', ' '):
            with self.subTest(path=path):
                self.record['artifacts'][0]['path'] = path
                self.assertTrue(M.validate(self.record,self.root))

    def test_unreadable_artifact_is_diagnostic(self):
        with patch.object(Path, 'read_bytes', side_effect=PermissionError('denied')):
            self.assertIn('artifact 0: cannot read path (PermissionError)', M.validate(self.record,self.root))

    def test_looping_root_is_diagnostic(self):
        (self.root/'loop').symlink_to('loop')
        self.assertTrue(M.validate(self.record,self.root/'loop'))

    def test_malformed_input_is_diagnostic(self):
        for value in (None, [], {'schema_version':1}, {'status':[], 'artifacts':[{}], 'checks':[{'status':[]}], 'tasks':[{'task_id':'a','status':{}}]}):
            self.assertTrue(M.validate(value,self.root))


if __name__=='__main__':
    unittest.main()
