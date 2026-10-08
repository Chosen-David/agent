"""Program tests with real temporary Git repositories and a local bare remote.

No external backend, credentials or model-quality claims. The fixture acceptance
callback independently executes the staged program and checks its output.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from agent_runtime.project_memory import MemoryLedger
from agent_runtime.publication import PublicationError, PublicationLedger, local_remote_reader


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.root = self.directory / 'repository'
        self.root.mkdir()
        self.remote = self.directory / 'remote.git'
        self.git('init', '-b', 'main')
        self.git('config', 'user.email', 'fixture@example.invalid')
        self.git('config', 'user.name', 'Publication fixture')
        subprocess.run(['git', 'init', '--bare', str(self.remote)], check=True, capture_output=True)
        (self.root / '.gitignore').write_text('.agent-runs/\n.agent-memory/\n')
        (self.root / 'TASK.md').write_text('- [ ] [T1] Program output\n- [ ] [T2] Document output\n')
        (self.root / 'app.py').write_text("print('baseline')\n")
        self.git('add', '.')
        self.git('commit', '-m', 'baseline')
        self.git('remote', 'add', 'origin', str(self.remote))
        self.git('push', 'origin', 'main')
        (self.root / 'app.py').write_text("print('candidate')\n")
        self.git('add', 'app.py')
        self.state = self.root / '.agent-runs' / 'publication.json'
        self.evidence_path = self.directory / 'acceptance.json'
        self.evidence_path.write_text(json.dumps({'expected_stdout': 'candidate\n'}))
        self.allowed = True
        self.accept_calls = 0
        self.ledger = self.open()

    def git(self, *args):
        result = subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def authorize(self, scope, action):
        return (self.allowed and scope == {
            'repository': str(self.root), 'remote': 'origin', 'remote_url': str(self.remote),
            'branch': 'main', 'authorization_reference': 'fixture explicit user approval'})

    def accept(self, candidate, evidence):
        self.accept_calls += 1
        expected = json.loads(self.evidence_path.read_text())['expected_stdout']
        actual = subprocess.run([sys.executable, str(self.root / 'app.py')], capture_output=True, text=True)
        # Actual executed behavior is checked, not a report's self-asserted pass.
        return (actual.returncode == 0 and actual.stdout == expected == 'candidate\n'
                and candidate['files']['app.py']['sha256'] ==
                hashlib.sha256((self.root / 'app.py').read_bytes()).hexdigest())

    def open(self, **kwargs):
        options = dict(authorize=self.authorize, accept=self.accept, remote_reader=local_remote_reader)
        options.update(kwargs)
        return PublicationLedger(self.root, self.state, **options, allow_legacy=True)

    def freeze(self, mapping=None):
        return self.ledger.freeze(mapping if mapping is not None else {'app.py': ['T1']},
                                  remote='origin', branch='main',
                                  authorization_reference='fixture explicit user approval')

    def evidence(self, value):
        return [{'path': str(self.evidence_path), 'sha256': hashlib.sha256(self.evidence_path.read_bytes()).hexdigest(),
                 'task_refs': ['T1'], 'candidate_sha256': value['candidate']['sha256']}]

    def _tested(self):
        value = self.freeze()
        return self.ledger.mark_tested(self.evidence(value))

    def committed(self):
        self._tested()
        self.git('commit', '-m', 'candidate')
        return self.ledger.observe_commit()

    def test_recoverable_lifecycle_real_local_readback(self):
        tested = self._tested()
        self.assertTrue(tested['tested'])
        self.assertFalse(tested['committed'])
        self.ledger = self.open()
        self.git('commit', '-m', 'candidate')
        committed = self.ledger.observe_commit()
        self.assertEqual(committed['commit'], self.git('rev-parse', 'HEAD'))
        with self.assertRaisesRegex(PublicationError, 'readback'):
            self.ledger.observe_pushed()
        self.assertEqual(self.ledger.status()['phase'], 'committed')
        self.git('push', 'origin', 'main')
        self.assertEqual(self.ledger.observe_pushed()['phase'], 'pushed')
        self.ledger = self.open()
        done = self.ledger.verify_remote()
        self.assertTrue(all(done[k] for k in ('tested', 'committed', 'pushed', 'remote_verified')))
        self.assertEqual(done['remote_readback']['commit'], committed['commit'])
        self.assertEqual([e['action'] for e in done['events']],
                         ['tested', 'committed', 'pushed', 'remote_verified'])
        self.assertGreaterEqual(self.accept_calls, 6)

    def test_observation_does_not_stage_commit_push_or_rewrite_index(self):
        index = (self.root / '.git' / 'index').read_bytes()
        head = self.git('rev-parse', 'HEAD')
        before = local_remote_reader({'remote_url': str(self.remote), 'branch': 'main'})
        self._tested()
        self.assertEqual((self.root / '.git' / 'index').read_bytes(), index)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(local_remote_reader({'remote_url': str(self.remote), 'branch': 'main'}), before)

    def test_missing_unknown_and_extra_file_task_mapping(self):
        for mapping in ({}, {'app.py': []}, {'app.py': ['UNKNOWN']},
                        {'app.py': ['T1'], 'TASK.md': ['T1']}, {'app.py': ['T1', 'T1']}):
            with self.subTest(mapping=mapping), self.assertRaises(PublicationError):
                self.freeze(mapping)
        self.assertFalse(self.state.exists())

    def test_add_and_delete_changes_need_ownership(self):
        (self.root / 'app.py').unlink()
        (self.root / 'new.py').write_text('new bytes\n')
        self.git('add', '-A')
        with self.assertRaisesRegex(PublicationError, 'ownership'):
            self.freeze({'new.py': ['T2']})
        value = self.freeze({'new.py': ['T2'], 'app.py': ['T1']})
        self.assertNotIn('app.py', value['candidate']['files'])
        self.assertIn('new.py', value['candidate']['files'])

    def test_mode_is_bound_even_when_bytes_are_unchanged(self):
        self.git('restore', '--staged', '--worktree', 'app.py')
        (self.root / 'app.py').chmod(0o755)
        self.git('add', 'app.py')
        value = self.freeze()
        self.assertEqual(value['candidate']['files']['app.py']['mode'], '100755')
        (self.root / 'app.py').chmod(0o644)
        with self.assertRaisesRegex(PublicationError, 'unstaged content or mode'):
            self.ledger.mark_tested(self.evidence(value))

    def test_unstaged_and_untracked_content_rejected(self):
        (self.root / 'app.py').write_text("print('different')\n")
        with self.assertRaisesRegex(PublicationError, 'unstaged'):
            self.freeze()
        self.git('add', 'app.py')
        (self.root / 'extra.txt').write_text('unmapped')
        with self.assertRaisesRegex(PublicationError, 'untracked'):
            self.freeze()

    def test_default_deny_and_authorization_revocation(self):
        self.ledger = self.open(authorize=None)
        with self.assertRaisesRegex(PublicationError, 'authorization'):
            self.freeze()
        self.ledger = self.open()
        value = self.freeze()
        self.allowed = False
        with self.assertRaisesRegex(PublicationError, 'authorization'):
            self.ledger.mark_tested(self.evidence(value))

    def test_wrong_branch_and_remote_rejected(self):
        value = self.freeze()
        self.git('branch', '-m', 'other')
        with self.assertRaisesRegex(PublicationError, 'remote or branch'):
            self.ledger.mark_tested(self.evidence(value))
        self.git('branch', '-m', 'main')
        self.git('remote', 'set-url', 'origin', str(self.directory / 'other.git'))
        with self.assertRaisesRegex(PublicationError, 'remote or branch'):
            self.ledger.mark_tested(self.evidence(value))

    def test_reports_and_hashes_cannot_replace_independent_acceptance(self):
        value = self.freeze()
        self.ledger = self.open(accept=None)
        with self.assertRaisesRegex(PublicationError, 'independent acceptance'):
            self.ledger.mark_tested(self.evidence(value))
        self.ledger = self.open()
        self.evidence_path.write_text(json.dumps({'expected_stdout': 'wrong\n', 'pass': True}))
        with self.assertRaisesRegex(PublicationError, 'independent acceptance'):
            self.ledger.mark_tested(self.evidence(value))
        self.assertEqual(self.ledger.status()['phase'], 'pending')

    def test_evidence_requires_exact_candidate_and_task_coverage(self):
        value = self.freeze()
        evidence = self.evidence(value)
        evidence[0]['candidate_sha256'] = 'older candidate'
        with self.assertRaisesRegex(PublicationError, 'stale'):
            self.ledger.mark_tested(evidence)
        for refs in ([], ['T2']):
            evidence = self.evidence(value)
            evidence[0]['task_refs'] = refs
            with self.assertRaisesRegex(PublicationError, 'TASK IDs'):
                self.ledger.mark_tested(evidence)

    def test_changed_evidence_after_test_prevents_commit_observation(self):
        self._tested()
        self.git('commit', '-m', 'candidate')
        self.evidence_path.write_text('{}')
        with self.assertRaisesRegex(PublicationError, 'changed acceptance'):
            self.ledger.observe_commit()
        self.assertFalse(self.ledger.status()['committed'])

    def test_independent_acceptance_cannot_change_evidence_during_callback(self):
        value = self.freeze()
        evidence = self.evidence(value)
        def changing(candidate, evidence):
            self.evidence_path.write_text('changed by acceptance callback')
            return True
        self.ledger = self.open(accept=changing)
        with self.assertRaisesRegex(PublicationError, 'changed acceptance evidence'):
            self.ledger.mark_tested(evidence)
        self.assertFalse(self.ledger.status()['tested'])

    def test_acceptance_must_cover_every_changed_requirement(self):
        (self.root / 'notes.txt').write_text('documented candidate output')
        self.git('add', 'notes.txt')
        value = self.freeze({'app.py': ['T1'], 'notes.txt': ['T2']})
        with self.assertRaisesRegex(PublicationError, 'omits changed TASK'):
            self.ledger.mark_tested(self.evidence(value))

    def test_changed_content_after_acceptance_requires_new_candidate(self):
        self._tested()
        (self.root / 'app.py').write_text("print('changed after test')\n")
        self.git('add', 'app.py')
        self.git('commit', '-m', 'different candidate')
        with self.assertRaisesRegex(PublicationError, 'candidate changed'):
            self.ledger.observe_commit()

    def test_changed_task_source_invalidates_test(self):
        value = self.freeze()
        (self.root / 'TASK.md').write_text('- [ ] [T1] Changed goal\n')
        self.git('add', 'TASK.md')
        with self.assertRaisesRegex(PublicationError, 'candidate changed'):
            self.ledger.mark_tested(self.evidence(value))

    def test_uncommitted_and_wrong_parent_cannot_be_reported_committed(self):
        self._tested()
        with self.assertRaisesRegex(PublicationError, 'exact tested tree'):
            self.ledger.observe_commit()
        self.git('commit', '-m', 'candidate')
        self.git('commit', '--allow-empty', '-m', 'extra untested parent')
        with self.assertRaisesRegex(PublicationError, 'single parent'):
            self.ledger.observe_commit()

    def test_local_replace_ref_cannot_substitute_the_commit_sent_to_remote(self):
        value = self._tested()
        base = value['candidate']['base_commit']
        good = self.git('commit-tree', self.git('write-tree'), '-p', base, '-m', 'tested tree')
        bad = self.git('commit-tree', self.git('rev-parse', base + '^{tree}'),
                       '-p', base, '-m', 'untested baseline tree')
        self.git('update-ref', 'refs/heads/main', bad)
        self.git('replace', bad, good)
        # Ordinary local inspection is now misleading; only replacement-disabled
        # inspection sees the actual object that would be sent by a Git push.
        self.assertEqual(self.git('show', 'HEAD:app.py'), "print('candidate')")
        with self.assertRaisesRegex(PublicationError, 'exact tested tree'):
            self.ledger.observe_commit()
        self.assertFalse(self.ledger.status()['committed'])

    def test_legacy_graft_cannot_substitute_original_commit_parent(self):
        value = self._tested()
        base = value['candidate']['base_commit']
        tree = self.git('write-tree')
        unrelated = self.git('commit-tree', tree, '-m', 'unrelated root')
        self.git('update-ref', 'refs/heads/main', unrelated)
        (self.root / '.git' / 'info' / 'grafts').write_text(unrelated + ' ' + base + '\n')
        self.assertEqual(self.git('show', '-s', '--format=%P', 'HEAD'), base)
        with self.assertRaisesRegex(PublicationError, 'original single parent'):
            self.ledger.observe_commit()

    def test_failed_push_is_pending_and_recovers_without_retesting(self):
        self.committed()
        # Actual failed local Git push (destination directory is not a repository).
        result = subprocess.run(['git', '-C', str(self.root), 'push', str(self.directory), 'main'],
                                capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        value = self.ledger.record_push_failure('local test remote unavailable')
        self.assertEqual(value['phase'], 'committed')
        self.assertFalse(value['pushed'])
        self.ledger = self.open()
        self.assertEqual(self.ledger.status()['last_error'], 'local test remote unavailable')
        self.git('push', 'origin', 'main')
        self.ledger.observe_pushed()
        self.assertEqual(self.ledger.verify_remote()['phase'], 'remote_verified')

    def test_no_remote_readback_and_wrong_scope_cannot_claim_push(self):
        self.committed()
        self.git('push', 'origin', 'main')
        self.ledger = self.open(remote_reader=None)
        with self.assertRaisesRegex(PublicationError, 'readback unavailable'):
            self.ledger.observe_pushed()
        for key in ('remote_url', 'branch', 'commit'):
            def wrong(scope, key=key):
                result = local_remote_reader(scope)
                result[key] = 'wrong'
                return result
            self.ledger = self.open(remote_reader=wrong)
            with self.assertRaisesRegex(PublicationError, 'readback does not match'):
                self.ledger.observe_pushed()
        self.assertFalse(self.ledger.status()['pushed'])

    def test_second_remote_read_is_required_and_detects_remote_change(self):
        self.committed()
        self.git('push', 'origin', 'main')
        self.ledger.observe_pushed()
        base = self.ledger.status()['candidate']['base_commit']
        subprocess.run(['git', '-C', str(self.remote), 'update-ref', 'refs/heads/main', base], check=True)
        with self.assertRaisesRegex(PublicationError, 'readback'):
            self.ledger.verify_remote()
        self.assertFalse(self.ledger.status()['remote_verified'])

    def test_stale_project_memory_blocks_acceptance(self):
        memory = MemoryLedger(self.root, create=True)
        memory.add('intent-v1', 'intention', 'Output candidate', 'fixture user', evidence='user_confirmed')
        value = self.freeze()
        evidence = self.evidence(value)
        evidence[0]['memory_refs'] = ['intent-v1']
        self.ledger.mark_tested(evidence)
        memory.correct('intent-v1', 'intent-v2', 'Different output', 'fixture correction', 'corrected goal')
        self.git('commit', '-m', 'candidate')
        with self.assertRaisesRegex(ValueError, 'superseded'):
            self.ledger.observe_commit()

    def test_state_and_evidence_symlinks_and_special_files_rejected(self):
        value = self.freeze()
        evidence = self.evidence(value)
        self.evidence_path.unlink()
        self.evidence_path.symlink_to(self.root / 'app.py')
        with self.assertRaisesRegex(PublicationError, 'symlink'):
            self.ledger.mark_tested(evidence)
        self.evidence_path.unlink()
        if hasattr(os, 'mkfifo'):
            os.mkfifo(self.evidence_path)
            with self.assertRaisesRegex(PublicationError, 'regular files'):
                self.ledger.mark_tested(evidence)
        self.state.unlink()
        self.state.symlink_to(self.root / 'TASK.md')
        with self.assertRaisesRegex(PublicationError, 'symlink'):
            self.ledger.status()

    def test_state_cannot_pollute_candidate_and_no_network_default(self):
        with self.assertRaisesRegex(PublicationError, 'ignored'):
            PublicationLedger(self.root, self.root / 'publication.json', allow_legacy=True)
        with self.assertRaisesRegex(PublicationError, 'absolute local'):
            local_remote_reader({'remote_url': 'https://example.invalid/repo', 'branch': 'main'})
        with self.assertRaisesRegex(PublicationError, 'ignored'):
            PublicationLedger(self.root, self.root / '.agent-runs' / '..' / 'TASK.md', allow_legacy=True)

    def test_tracked_state_cannot_be_its_own_candidate(self):
        self.state.parent.mkdir()
        self.state.write_text('{}')
        self.git('add', '-f', str(self.state))
        with self.assertRaisesRegex(PublicationError, 'must not be tracked'):
            self.open()

    def test_freeze_is_immutable_and_callback_cannot_mutate_state(self):
        value = self.freeze()
        with self.assertRaisesRegex(PublicationError, 'already exists'):
            self.freeze()
        value['candidate']['sha256'] = 'caller mutated copy'
        self.assertNotEqual(self.ledger.status()['candidate']['sha256'], value['candidate']['sha256'])
        evidence = self.evidence(self.ledger.status())
        def modifying(candidate, evidence):
            candidate['sha256'] = 'attempted mutation'
            (self.root / 'app.py').write_text("print('changed by verifier')\n")
            return True
        self.ledger = self.open(accept=modifying)
        with self.assertRaisesRegex(PublicationError, 'unstaged'):
            self.ledger.mark_tested(evidence)
        self.assertEqual(self.ledger.status()['phase'], 'pending')


    def test_canonical_project_index_and_details_are_frozen(self):
        from agent_runtime.project_docs import migrate
        migrate(self.root, '2026-10-07')
        self.git('add', '-A')
        mapping = {name: ['T1'] for name in self.git('diff', '--cached', '--name-only').splitlines()}
        value = self.freeze(mapping)
        self.assertEqual(value['candidate']['task_path'], 'agent_doc/task/TASK.md')
        self.assertEqual(set(value['candidate']['project_documents']['task_details']), {'T1', 'T2'})
        self.ledger.mark_tested(self.evidence(value))

    def test_ai_publication_cannot_include_any_guide_changes(self):
        guide = self.root / 'agent_doc/guide/guide.md'; guide.parent.mkdir(parents=True)
        guide.write_text('Human fixture input, not AI output')
        self.git('add', 'agent_doc/guide/guide.md')
        with self.assertRaisesRegex(PublicationError, 'human guide'):
            self.freeze({'app.py': ['T1'], 'agent_doc/guide/guide.md': ['T1']})
        self.assertFalse(self.state.exists())

    def test_ignored_human_guide_change_stales_candidate_without_git_tree_change(self):
        guide = self.root / 'agent_doc/guide/guide.md'; guide.parent.mkdir(parents=True)
        guide.write_text('Human fixture input')
        exclude = self.root / '.git/info/exclude'
        exclude.write_text(exclude.read_text() + '\nagent_doc/guide/\n')
        value = self.freeze()
        guide.write_text('Changed human requirement')
        with self.assertRaisesRegex(PublicationError, 'project documents changed'):
            self.ledger.mark_tested(self.evidence(value))


if __name__ == '__main__':
    unittest.main()
