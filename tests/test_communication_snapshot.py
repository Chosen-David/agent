"""Exact raw manifest binding across deterministic, real-file replacements."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from agent_runtime import communication, external_json
from scripts.validate_handoff import _load_json
import test_communication as fixtures


class ManifestSnapshotTests(unittest.TestCase):
    setUp = fixtures.CommunicationTests.setUp
    save = fixtures.CommunicationTests.save

    def assert_unconsumed(self):
        with self.box.connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM communication_basis').fetchone()[0], 0)
        self.assertTrue(all(row['receipt'] is None for row in self.box.status()))

    def test_replace_between_envelope_validation_and_manifest_read(self):
        for restore in (False, True):
            with self.subTest(restore=restore):
                original = (self.root / 'handoff.json').read_bytes()
                replacement = dict(self.record, limitations=['unbound replacement'])
                seq = self.box.publish(dict(self.event, event_id=f'replace:{restore}'))['seq']
                validate = communication.validate
                swapped = False
                def interpose(record, *args, **kwargs):
                    nonlocal swapped
                    errors = validate(record, *args, **kwargs)
                    if record.get('limitations') == ['pending consumption'] and not errors:
                        (self.root / 'handoff.json').write_text(json.dumps(replacement))
                        swapped = True
                    elif restore and swapped:
                        (self.root / 'handoff.json').write_bytes(original)
                    return errors
                try:
                    with patch.object(communication, 'validate', interpose):
                        with self.assertRaisesRegex(ValueError, 'sha256 mismatch'):
                            self.box.consume_handoff('writer', seq, self.request)
                    self.assertTrue(swapped)
                    self.assert_unconsumed()
                finally:
                    (self.root / 'handoff.json').write_bytes(original)

    def test_replacement_after_single_read_returns_only_bound_snapshot(self):
        seq = self.box.publish(self.event)['seq']
        path = self.root / 'handoff.json'
        original_read = external_json.regular_bytes
        swapped = False
        def interpose(target, **kwargs):
            nonlocal swapped
            data = original_read(target, **kwargs)
            if Path(target) == path and not swapped:
                swapped = True
                path.write_text(json.dumps(dict(self.record, limitations=['later replacement'])))
            return data
        with patch.object(external_json, 'regular_bytes', interpose):
            result = self.box.consume_handoff('writer', seq, self.request)
        self.assertTrue(swapped)
        self.assertEqual(result, self.record)
        with self.box.connect() as db:
            stored = json.loads(db.execute('SELECT record FROM communication_basis').fetchone()[0])
        self.assertEqual(stored, self.record)
        self.assertEqual(self.box.impact()[0]['recipient'], 'writer')
        self.assertTrue(all(row['receipt'] is None for row in self.box.status()))

    def test_utf8_crlf_preserves_raw_digest_contract(self):
        record = dict(self.record, limitations=['中文设计原因'])
        data = json.dumps(record, ensure_ascii=False, indent=2).replace('\n', '\r\n').encode('utf-8')
        (self.root / 'handoff.json').write_bytes(data)
        ref = dict(self.manifest, sha256=hashlib.sha256(data).hexdigest())
        seq = self.box.publish(dict(self.event, refs=[ref]))['seq']
        self.assertEqual(self.box.consume_handoff('writer', seq, self.request), record)

    def test_strict_parser_rejects_invalid_bound_bytes(self):
        for data in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'\xff'):
            with self.subTest(data=data):
                path = self.root / 'invalid.json'
                path.write_bytes(data)
                with self.assertRaises(ValueError):
                    _load_json(path, expected_sha256=hashlib.sha256(data).hexdigest())


if __name__ == '__main__':
    unittest.main()
