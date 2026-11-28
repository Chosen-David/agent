import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from agent_runtime.research_workers import run_native_worker


class Settlement(unittest.TestCase):
    def run_child(self, root, binary, **options):
        worker = dict(identity='one', task='fixture', worktree=str(root), output=str(root/'out'))
        with patch('agent_runtime.handoff_basis.basis_context', return_value={'payload':'{}'}), \
             patch('agent_runtime.research_workers.inspect_workers'), \
             patch('agent_runtime.research_workers.shutil.which', side_effect=lambda path: path), \
             patch('agent_runtime.worker_preflight.check', return_value='workspace-write'):
            return run_native_worker(self.host, worker, codex=binary, project='test', cycle='a',
                    primary='primary', budget=50, tokens=10, final_reserve=5, root=root,
                    basis={}, request={}, objective='fixture', validate_output=options.pop("validate_output", lambda p: False), **options)

    def test_process_boundaries(self):
        for binary, reconciled, expected in [('/bin/false', True, 'failed'),
                                              ('/bin/false', False, None),
                                              
                                              ('/bin/true', False, 'insufficient')]:
            with self.subTest(binary=binary, reconciled=reconciled), tempfile.TemporaryDirectory() as tmp:
                self.host = Mock()
                try:
                    self.run_child(Path(tmp), binary, reconcile_failure=lambda *args: reconciled)
                except (FileNotFoundError, ValueError):
                    if expected not in ('not_started', 'insufficient'):
                        raise
                if expected:
                    self.host.settle.assert_called_once_with('one', 0 if expected=='not_started' else None,
                                                            outcome=expected)
                else:
                    self.host.settle.assert_not_called()

    def test_output_collision_before_process_creation(self):
        self.host = Mock()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/'out').mkdir()
            (root/'out/codex-events.jsonl').write_text('old evidence')
            with self.assertRaises(FileExistsError):
                self.run_child(root, '/bin/true')
            self.host.settle.assert_called_once_with('one', 0, outcome='not_started')
            self.assertEqual((root/'out/codex-events.jsonl').read_text(), 'old evidence')

    def test_execve_failure_after_claim(self):
        self.host = Mock()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            binary = root/'unstartable'
            binary.write_text('#!/nonexistent-worker-interpreter\n')
            binary.chmod(0o700)
            with self.assertRaises(FileNotFoundError):
                self.run_child(root, str(binary))
            self.host.settle.assert_called_once_with('one', 0, outcome='not_started')

    def test_nonempty_rejection_record_cannot_accept_artifact(self):
        self.host = Mock()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, 'without an accepted artifact'):
                self.run_child(Path(tmp), '/bin/true',
                               validate_output=lambda path: {'status': 'insufficient'})
            self.host.settle.assert_called_once_with('one', None, outcome='insufficient')
