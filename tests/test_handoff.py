import hashlib
import importlib.util
import tempfile
import unittest
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
        self.assertEqual(M.validate(self.record, self.root, True), [])

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
        self.assertTrue(M.validate(self.record,self.root,True))

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
        self.record['tasks']=[{'task_id':str(i),'status':'todo','depends_on':[str(i-1)] if i else []} for i in range(1100)]
        self.assertEqual(M.validate(self.record,self.root), [])

    def test_malformed_input_is_diagnostic(self):
        for value in (None, [], {'schema_version':1}, {'status':[], 'artifacts':[{}], 'checks':[{'status':[]}], 'tasks':[{'task_id':'a','status':{}}]}):
            self.assertTrue(M.validate(value,self.root))


if __name__=='__main__':
    unittest.main()
