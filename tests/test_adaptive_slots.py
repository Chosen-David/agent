import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent_runtime.core import Store
from agent_runtime.research_workers import Admission


class ManagedSlots(unittest.TestCase):
    def test_limits_recovery_and_settlement(self):
        with tempfile.TemporaryDirectory() as folder, patch(
            'agent_runtime.research_workers.inspect_workers', side_effect=lambda records: records
        ):
            path = Path(folder) / 'runtime.sqlite'
            first, second = Admission(Store(path)), Admission(Store(path))
            def take(host, name, parent=None, **overrides):
                options = dict(project='V5', cycle='one', tokens=20, budget=60, final_reserve=10)
                options.update(overrides)
                return host.reserve({'identity': name}, parent=parent, **options)
            self.assertTrue(take(first, 'primary'))
            self.assertTrue(take(second, 'worker', 'primary'))
            self.assertFalse(take(first, 'worker', 'primary'))
            with self.assertRaisesRegex(ValueError, 'host agent limit'):
                take(first, 'third', project='V4')
            with self.assertRaisesRegex(ValueError, 'active primary'):
                take(first, 'grandchild', 'worker', max_agents=3)
            second.settle('worker', 12)
            first.settle('worker', 12)
            with self.assertRaisesRegex(ValueError, 'dispatch limit'):
                take(second, 'again', 'primary', max_spawns=1)
            with self.assertRaisesRegex(ValueError, 'project budget'):
                take(second, 'expensive', 'primary')
            self.assertTrue(take(second, 'small', 'primary', tokens=5))

    def test_worker_cli_counters_include_cached_and_reasoning(self):
        import json
        from agent_runtime.token_usage import worker_turn_usage, short_probe_usage
        events = [dict(type='thread.started', thread_id='worker'),
                  dict(type='turn.started'),
                  dict(type='item.completed', item=dict(type='command_execution')),
                  dict(type='turn.completed', usage=dict(input_tokens=72, cached_input_tokens=55,
                       output_tokens=29, reasoning_output_tokens=10))]
        lines = list(map(json.dumps, events))
        self.assertEqual(worker_turn_usage(lines)['total_tokens'], 101)
        with self.assertRaises(ValueError):
            short_probe_usage(lines)

    def test_two_processes_contend_for_remaining_slot(self):
        import json
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workers = []
            for identity in ('primary', 'one', 'two'):
                tree = root / identity
                subprocess.run(['git', 'init', '-q', '-b', identity, str(tree)], check=True)
                subprocess.run(['git', '-C', str(tree), '-c', 'user.name=test', '-c',
                                'user.email=test@example.invalid', 'commit', '-qm', 'fixture',
                                '--allow-empty'], check=True)
                workers.append(dict(identity=identity, task=identity, branch=identity,
                                    worktree=str(tree), output=str(tree / 'out')))
            path = root / 'shared.sqlite'
            policy = dict(project='science', cycle='A', tokens=1, budget=10, final_reserve=2)
            Admission(Store(path)).reserve(workers[0], parent=None, **policy)
            code = """import sys,json
from agent_runtime.core import Store
from agent_runtime.research_workers import Admission
host=Admission(Store(sys.argv[1]))
try:
    host.reserve(json.loads(sys.argv[2]),parent='primary',**json.loads(sys.argv[3]))
except ValueError as exc:
    if 'host agent limit' not in str(exc): raise
    sys.exit(3)
"""
            children = [subprocess.Popen([sys.executable, '-c', code, str(path),
                                          json.dumps(w), json.dumps(policy)]) for w in workers[1:]]
            self.assertEqual(sorted(child.wait(timeout=30) for child in children), [0, 3])

    def test_single_mode_and_final_budget(self):
        with tempfile.TemporaryDirectory() as directory, patch(
            'agent_runtime.research_workers.inspect_workers', side_effect=lambda records: records
        ):
            host = Admission(Store(Path(directory) / 'shared.sqlite'))
            config = dict(project='p', cycle='first', budget=100, final_reserve=20)
            host.reserve({'identity': 'main'}, parent=None, tokens=80, **config)
            with self.assertRaisesRegex(ValueError, 'scheduling policy'):
                host.reserve({'identity': 'extra'}, parent='main', mode='single', tokens=0, **config)
            with self.assertRaisesRegex(ValueError, 'soft budget'):
                host.reserve({'identity': 'extra'}, parent='main', tokens=0, **config)
            host.settle('main', 80)
            host.reserve({'identity': 'integration'}, parent=None, final=True, tokens=20, **config)
            host.settle('integration', 18, outcome='accepted')
            with self.assertRaisesRegex(ValueError, 'conflicting settlement'):
                host.settle('integration', 18, outcome='insufficient')
