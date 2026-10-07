"""Consumer-owned knowledge bindings over real files and SQLite deliveries."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from agent_runtime.communication import Mailbox
from agent_runtime.knowledge import KnowledgeStore, check_handoff_knowledge

ROOT = Path(__file__).resolve().parents[1]


class KnowledgeHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / 'knowledge', self.root / 'corpus')
        self.refs = KnowledgeStore(self.root / 'corpus').get('math.topk-margin')['knowledge_refs']
        self.request = dict(schema_version=1, input_version='v1', tasks=[{'task_id': 'T1'}],
                            knowledge_root='corpus', knowledge_refs=self.refs)
        self.record = dict(schema_version=1, run_id='kb', role='code', input_version='v1',
                           status='completed', limitations=[], knowledge_refs=self.refs,
                           artifacts=[self.save('result.json', {'synthetic': True}, 'result')],
                           checks=[dict(criterion='file', status='pass', artifact_ids=['result'])],
                           tasks=[dict(task_id='T1', status='done', evidence=['result'])])
        plan = dict(schema_version=1, run_id='kb', input_version='v1', routes=[
            dict(sender='code', recipient='review', task_id='T1', kind='artifact')])
        self.box = Mailbox(self.root / 'mail.sqlite', plan, self.root)

    def save(self, name, obj, aid):
        data = json.dumps(obj).encode()
        (self.root / name).write_bytes(data)
        return dict(id=aid, path=name, sha256=hashlib.sha256(data).hexdigest())

    def send(self):
        ref = self.save('handoff.json', self.record, 'handoff')
        return self.box.publish(dict(event_id='E1', run_id='kb', input_version='v1', sender='code',
                                    task_id='T1', kind='artifact', summary='result', action='verify',
                                    refs=[ref]))['seq']

    def test_valid_delivery_then_corpus_change_is_rejected_without_ack(self):
        seq = self.send()
        self.assertEqual(self.box.consume_handoff('review', seq, self.request)['knowledge_refs'], self.refs)
        path = self.root / 'corpus/entries/math.topk-margin.md'
        path.write_text(path.read_text() + '\nUpdated content\n')
        with self.assertRaisesRegex(ValueError, 'stale knowledge ref'):
            self.box.consume_handoff('review', seq, self.request)
        self.assertIsNone(self.box.status()[0]['receipt'])

    def test_producer_cannot_omit_required_refs(self):
        self.record.pop('knowledge_refs')
        seq = self.send()
        with self.assertRaisesRegex(ValueError, 'omits required'):
            self.box.consume_handoff('review', seq, self.request)

    def test_producer_cannot_replace_corpus(self):
        self.record['knowledge_root'] = 'corpus'
        request = dict(self.request, knowledge_root='missing')
        with self.assertRaises(ValueError):
            check_handoff_knowledge(self.root, self.record, request)

    def test_consumer_root_must_be_explicit_and_confined(self):
        for relative in (None, '', '../', str(self.root / 'corpus')):
            with self.subTest(root=relative), self.assertRaises(ValueError):
                check_handoff_knowledge(self.root, self.record, dict(self.request, knowledge_root=relative))
        (self.root / 'escape').symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'outside project'):
            check_handoff_knowledge(self.root, self.record, dict(self.request, knowledge_root='escape'))

    def test_undeclared_extra_dependency_still_gets_validated(self):
        bad = deepcopy(self.refs)
        bad[0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'stale'):
            check_handoff_knowledge(self.root, dict(self.record, knowledge_refs=bad),
                                    dict(self.request, knowledge_refs=[]))

    def test_missing_required_subset_and_prerequisite(self):
        unrelated = KnowledgeStore(self.root / 'corpus').get('physics.dimensionless')['knowledge_refs']
        with self.assertRaisesRegex(ValueError, 'omits consumer-required'):
            check_handoff_knowledge(self.root, dict(self.record, knowledge_refs=unrelated), self.request)
        store = KnowledgeStore(self.root / 'corpus')
        dependent = next(k for k, v in store.records.items() if v['requires'])
        with self.assertRaisesRegex(ValueError, 'omit prerequisites'):
            check_handoff_knowledge(self.root, dict(self.record, knowledge_refs=[store.ref(dependent)]),
                                    dict(self.request, knowledge_refs=[]))

    def test_legacy_no_knowledge_and_malformed_lists(self):
        self.assertEqual(check_handoff_knowledge(self.root, {}, {}), [])
        for bad in (None, {}, 'text'):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'must be lists'):
                check_handoff_knowledge(self.root, {'knowledge_refs': bad}, {})


if __name__ == '__main__':
    unittest.main()
