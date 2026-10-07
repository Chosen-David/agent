#!/usr/bin/env python3
"""Bounded local demonstration: actual file effects, SQLite and scheduler readback.

Explicit legacy-unprotected example. No LLM, cloud scheduler, paid compute, external message, or installed daemon.
The handler is explicitly registered trusted code; task JSON is not executable.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import threading
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.core import ArtifactHandler, Engine, Outcome, Store
from agent_runtime.scheduler import LocalScheduler, arm


class WriteDemo(ArtifactHandler):
    required_capabilities = frozenset({'write_demo_artifacts'})

    def run(self, task, context):
        if not context.current():
            return Outcome('blocked', 'cancelled or stale')
        target = self.root / task['done_when']['artifacts'][0]['path']
        content = task['inputs']['text']
        # Deterministic content + stable key; repeating this synthetic action is safe.
        temp = self.root / (context.idempotency_key + '.tmp')
        temp.write_text(content)
        temp.replace(target)
        return super().run(task, context)


def main():
    with tempfile.TemporaryDirectory(prefix='task-supervisor-demo-') as directory:
        root = Path(directory)
        plan = {'schema_version': 'task-dag/v1', 'run_id': 'demo',
                'user_goal': 'Produce two verified local demonstration artifacts',
                'authorization_reference': 'bounded demo invocation, temporary files only',
                'supervision': {'min_seconds': 1, 'max_seconds': 2,
                                'rationale': 'tiny local writes, low risk, 1–2 second demo budget'},
                'tasks': []}
        for index in range(2):
            text = f'Verified demonstration artifact {index}\n'
            plan['tasks'].append({'task_id': str(index), 'owner': 'demo-host', 'action': 'write_demo',
                                  'depends_on': [str(index - 1)] if index else [],
                                  'inputs': {'text': text}, 'estimated_seconds': 1, 'risk': 'low',
                                  'max_attempts': 2, 'done_when': {'artifacts': [
                                      {'path': f'{index}.txt', 'sha256': hashlib.sha256(text.encode()).hexdigest()}]}})
        store = Store(root / 'state.sqlite')
        store.create(plan)
        handler = WriteDemo(root)
        engine = Engine(store, {'write_demo': handler}, authorize=lambda p, t, h: h is handler, allow_legacy=True)
        scheduler = LocalScheduler(store)
        stopped = threading.Event()
        worker = threading.Thread(target=scheduler.serve, args=(engine, stopped.is_set, 10))
        worker.start()
        try:
            deadline = time.monotonic() + 8
            while not scheduler.capabilities()['ready'] and time.monotonic() < deadline:
                time.sleep(0.05)
            receipt = arm(scheduler, plan['run_id'])
            while time.monotonic() < deadline:
                state = store.snapshot('demo')['state']
                if state['status'] == 'done':
                    break
                time.sleep(0.1)
            report = {'scope': 'real local IO and scheduler; synthetic deterministic task, no LLM',
                      'arm': receipt, 'state': store.snapshot('demo')['state'],
                      'monitor_readback': scheduler.read('local:demo'),
                      'artifacts': {p.name: p.read_text() for p in root.glob('*.txt')}}
            if report['state']['status'] != 'done' or report['monitor_readback']['status'] != 'stopped':
                raise RuntimeError('demo did not converge and stop')
            print(json.dumps(report, indent=2))
        finally:
            stopped.set()
            worker.join()


if __name__ == '__main__':
    main()
