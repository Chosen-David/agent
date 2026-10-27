"""Temporal navigation counts preserve scope unions, ties and read-only CLI use."""
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.project_memory import MemoryError, MemoryLedger


def expected_rows(entries):
    rows = []
    for entry in entries:
        newer = {other['id'] for other in entries
                 if other['id'] != entry['id'] and
                 set(entry['scope']) & set(other['scope']) and
                 other['created_at'] > entry['created_at']}
        if newer:
            rows.append({'id': entry['id'], 'scope': entry['scope'],
                         'newer_sibling_count': len(newer), 'signal': 'newer_sibling_in_scope'})
    return rows


class MemorySiblingCountTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.ledger = MemoryLedger(self.root, create=True)

    def seed(self, rows):
        for name, scopes, timestamp in rows:
            self.ledger.add(name, 'observation', '更正 evidence', 'fixture',
                            scope=scopes, evidence='verified')
        with self.ledger._connect(write=True) as db:
            db.executemany('UPDATE entries SET created_at=? WHERE id=?',
                           [(timestamp, name) for name, _, timestamp in rows])

    def test_literal_overlaps_ties_and_output_order(self):
        self.seed([('old', ['b', 'a'], '01'), ('twin', ['a', 'b'], '01'),
                   ('middle', ['a'], '02'), ('latest', ['a', 'b'], '03'),
                   ('other', ['c'], '04'), ('empty', [], '00')])
        result = self.ledger.reconcile()
        self.assertEqual(result['potentially_obsolete'], [
            {'id': 'old', 'scope': ['b', 'a'], 'newer_sibling_count': 2,
             'signal': 'newer_sibling_in_scope'},
            {'id': 'twin', 'scope': ['a', 'b'], 'newer_sibling_count': 2,
             'signal': 'newer_sibling_in_scope'},
            {'id': 'middle', 'scope': ['a'], 'newer_sibling_count': 1,
             'signal': 'newer_sibling_in_scope'}])

    def test_deterministic_layouts_match_pairwise_oracle(self):
        rng = random.Random(609)
        # Custom list is a supported extension: reorder and vary scope signatures.
        for size in (0, 1, 2, 7, 31):
            for layout in range(6):
                entries = [{'id': f'e{i}', 'kind': 'observation', 'content': 'x',
                            'scope': rng.sample(['a', 'b', 'c', 'd'], rng.randrange(5)),
                            'created_at': str(rng.randrange(4)), 'evidence': 'verified'}
                           for i in range(size)]
                rng.shuffle(entries)
                self.ledger.list = lambda status, scope: entries
                with self.subTest(size=size, layout=layout):
                    self.assertEqual(self.ledger.reconcile()['potentially_obsolete'],
                                     expected_rows(entries))

    def test_custom_duplicate_ids_exclude_self_and_union_once(self):
        entries = [{'id': name, 'kind': 'claim', 'content': 'x', 'scope': scopes,
                    'created_at': timestamp, 'evidence': 'verified'}
                   for name, scopes, timestamp in [
                       ('same', ['a', 'b'], '00'), ('same', ['b', 'a'], '04'),
                       ('peer', ['a'], '01'), ('peer', ['b'], '03'),
                       ('last', ['b', 'a'], '04'), ('single', ['z'], '00')]]
        self.ledger.list = lambda status, scope: entries
        result = self.ledger.reconcile()
        self.assertEqual(result['potentially_obsolete'], expected_rows(entries))
        self.assertIn('custom list snapshot consistency unchecked', result['scope'])

    def test_corrections_status_filter_and_budget_preserve_bytes(self):
        self.seed([('old', ['a'], '01'), ('later', ['a'], '02'), ('raw', ['b'], '00')])
        self.ledger.add('derived', 'claim', 'old interpretation', 'fixture',
                        deps=['old'], scope=['a'], evidence='verified')
        self.ledger.correct('old', 'replacement', 'correct interpretation', 'fixture', 'correction')
        before = self.ledger.path.read_bytes()
        entries = self.ledger.list()
        result = self.ledger.reconcile(detect_contradictions=True)
        self.assertEqual(result['potentially_obsolete'], expected_rows(entries))
        self.assertNotIn('old', [r['id'] for r in result['potentially_obsolete']])
        self.assertNotIn('derived', [r['id'] for r in result['potentially_obsolete']])
        self.assertEqual(self.ledger.reconcile('b')['potentially_obsolete'], [])
        with self.assertRaises(MemoryError):
            self.ledger.reconcile(max_chars=1)
        self.assertEqual(self.ledger.path.read_bytes(), before)

    def test_native_cli_full_body_and_refusal_are_read_only(self):
        self.seed([(f'e{i:02}', ['b', 'a'] if i % 2 else ['a', 'b'], f'{i // 3:03}')
                   for i in range(48)])
        expected = self.ledger.reconcile(detect_contradictions=True)
        before = hashlib.sha256(self.ledger.path.read_bytes()).hexdigest()
        script = Path(__file__).resolve().parents[1] / 'agent_runtime/project_memory.py'
        for encoding in ('cp936', 'ascii'):
            env = dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING=encoding)
            argv = [sys.executable, '-m', 'agent_runtime.project_memory', '--root', str(self.root),
                    'reconcile', '--detect-contradictions', '--max-chars']
            ok = subprocess.run(argv + ['200000'], cwd=script.parents[1], env=env,
                                capture_output=True, timeout=15)
            self.assertEqual(ok.returncode, 0, ok.stderr.decode('utf-8'))
            self.assertEqual(json.loads(ok.stdout.decode('utf-8')), expected)
            refused = subprocess.run(argv + ['256'], cwd=script.parents[1], env=env,
                                     capture_output=True, timeout=15)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(refused.stdout, b'')
            self.assertIn('error', json.loads(refused.stderr.decode('utf-8')))
        self.assertEqual(hashlib.sha256(self.ledger.path.read_bytes()).hexdigest(), before)
