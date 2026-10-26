"""Native communication JSON survives legacy terminal encodings."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

from agent_runtime.communication import canonical
import test_communication as fixture


class CommunicationOutputTests(unittest.TestCase):
    def make_fixture(self):
        value = fixture.CommunicationTests()
        value.setUp()
        self.addCleanup(value.doCleanups)
        target = '证据🚦.json'
        (value.root/'result.json').rename(value.root/target)
        value.ref['path'] = target
        value.record['checks'][0]['criterion'] = '核验完整🚦'
        value.manifest = value.save('handoff.json', value.record, 'handoff')
        value.event.update(event_id='结果🚦', summary='保留更正🚦',
                           action='先核验范围再执行🚦', refs=[value.manifest])
        seq = value.box.publish(value.event)['seq']
        value.box.acknowledge('reviewer', seq, {'status': 'consumed', 'reason': '已审阅🚦'})
        for name, data in (('plan', value.plan), ('request', value.request)):
            (value.root/(name+'.json')).write_bytes(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        return value, seq

    def run_cli(self, value, args, encoding, compact):
        command = [sys.executable, '-B', '-m', 'agent_runtime.communication',
                   '--root', str(value.root), '--db', str(value.db),
                   '--plan', str(value.root/'plan.json')]
        if compact:
            command.append('--compact')
        return subprocess.run(command+args, cwd=Path(__file__).resolve().parents[1],
                              capture_output=True, timeout=15,
                              env=dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING=encoding))

    def decode(self, run, code=0):
        self.assertEqual(run.returncode, code, run.stderr)
        self.assertEqual(run.stderr, b'')
        return json.loads(run.stdout.decode('utf-8'))

    def files(self, value):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in value.root.iterdir() if p.is_file() and p.suffix == '.json'}

    def database(self, value):
        with value.box.connect() as db:
            return tuple(db.iterdump())

    def test_readonly_full_outputs_and_ascii_index_control(self):
        for encoding in ('cp936', 'ascii'):
            for compact in (False, True):
                value, seq = self.make_fixture()
                body_sha = hashlib.sha256(canonical(value.event).encode('utf-8')).hexdigest()
                cases = [(['inbox', 'writer'], [{'seq': seq, 'event': value.event}]),
                         (['read-pending', 'writer', str(seq), '--body-sha256', body_sha],
                          {'seq': seq, 'event': value.event}),
                         (['status'], value.box.status()),
                         (['inbox-index', 'writer'], value.box.inbox_index('writer'))]
                for args, expected in cases:
                    with self.subTest(encoding=encoding, compact=compact, command=args[0]):
                        before_files, before_db = self.files(value), self.database(value)
                        run = self.run_cli(value, args, encoding, compact)
                        self.assertEqual(self.files(value), before_files)
                        self.assertEqual(self.database(value), before_db)
                        self.assertEqual(self.decode(run), expected)

    def test_consumption_outputs_preserve_basis_without_ack(self):
        for encoding in ('cp936', 'ascii'):
            for compact in (False, True):
                for action in ('consume', 'context'):
                    with self.subTest(encoding=encoding, compact=compact, command=action):
                        value, seq = self.make_fixture()
                        before_files, receipts = self.files(value), value.box.status()
                        args = [action, 'writer', str(seq), '--request', str(value.root/'request.json')]
                        run = self.run_cli(value, args, encoding, compact)
                        # Check committed local state even if rendering failed afterwards.
                        with value.box.connect() as db:
                            row = db.execute('SELECT record,request FROM communication_basis WHERE seq=? AND recipient=?',
                                             (seq, 'writer')).fetchone()
                        self.assertIsNotNone(row)
                        self.assertEqual(json.loads(row['record']), value.record)
                        self.assertEqual(json.loads(row['request']), value.request)
                        self.assertEqual(value.box.status(), receipts)
                        self.assertEqual(self.files(value), before_files)
                        output = self.decode(run)
                        if action == 'consume':
                            self.assertEqual(output, value.record)
                        else:
                            payload = json.loads(output['payload'])
                            self.assertEqual(payload, {'input_version': 'data:v1', 'knowledge_refs': [],
                                'memory_refs': [], 'evidence_claims': [], 'artifacts': [value.ref],
                                'knowledge_entries': [], 'memory_entries': []})
                            self.assertIsNone(output['usage']['tokens'])
                            self.assertIsNone(output['selection'])

    def test_unicode_data_error_keeps_original_json_exit_protocol(self):
        for encoding in ('cp936', 'ascii'):
            for compact in (False, True):
                with self.subTest(encoding=encoding, compact=compact):
                    value, _ = self.make_fixture()
                    (value.root/'plan.json').write_bytes('{"重复🚦":1,"重复🚦":2}'.encode('utf-8'))
                    before_files, before_db = self.files(value), self.database(value)
                    run = self.run_cli(value, ['status'], encoding, compact)
                    self.assertEqual(self.files(value), before_files)
                    self.assertEqual(self.database(value), before_db)
                    self.assertEqual(self.decode(run, 1), {'error': 'duplicate JSON key: 重复🚦'})
