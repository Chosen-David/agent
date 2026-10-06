"""TASK.md coverage and evidence reports for the managed supervisor.

TASK.md describes requirements, never executable commands or permissions.
The main AI supplies actions, dependencies and independent acceptance handlers.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from .core import Outcome, validate


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=path.name + '.')
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def requirements(path):
    """Read explicit stable IDs; ignore examples inside fenced code blocks."""
    items, fence = [], None
    for line in Path(path).read_text(encoding='utf-8').splitlines():
        stripped = line.lstrip()
        marker = re.match(r'(`{3,}|~{3,})', stripped)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        match = re.match(r'^\s*[-*+] \[([ xX])\] \[([A-Za-z0-9][A-Za-z0-9_.-]*)\] (.+)$', line)
        if match:
            items.append({'id': match[2], 'title': match[3], 'checked': match[1] != ' '})
        elif re.match(r'^\s*[-*+] \[[ xX]\]', line):
            raise ValueError('every TASK.md checkbox needs a stable [ID] and title')
    if not items or len({t['id'] for t in items}) != len(items):
        raise ValueError('TASK.md requires nonempty, unique task IDs')
    return items


def prepare(task_file, run_id, mode, authorization_reference):
    task_file = Path(task_file).resolve()
    items = requirements(task_file)
    return {
        'schema_version': 'task-dag/v1', 'run_id': run_id,
        'user_goal': 'Complete all TASK.md requirements with reportable evidence',
        'authorization_reference': authorization_reference,
        'task_source': {'path': str(task_file), 'sha256': digest(task_file), 'mode': mode},
        'supervision': {'min_seconds': 30, 'max_seconds': 300,
                        'rationale': 'Main AI must refine ETA, risk and cadence before starting'},
        'tasks': [{'task_id': item['id'], 'task_refs': [item['id']], 'owner': 'main-ai',
                   'action': 'configure_host_action', 'depends_on': [], 'risk': 'low',
                   'estimated_seconds': 120, 'max_attempts': 3, 'inputs': {'goal': item['title']},
                   'outputs': [], 'done_when': {'configure_acceptance': True},
                   'report_path': f'.agent-runs/{hashlib.sha256(run_id.encode()).hexdigest()[:16]}/results/{item["id"]}.json'}
                  for item in items],
    }


def validate_contract(plan, root):
    validate(plan)
    root = Path(root).resolve()
    source = plan['task_source']
    if source['mode'] not in ('auto', 'manual'):
        raise ValueError('task source mode must be auto or manual')
    path = Path(source['path']).resolve()
    if path != root / 'TASK.md':
        raise ValueError('the single task source must be project-root TASK.md')
    if not path.is_relative_to(root) or digest(path) != source['sha256']:
        raise ValueError('TASK.md missing, changed or outside project; reconcile and version the plan')
    items = requirements(path)
    ids, covered = {item['id'] for item in items}, set()
    report_paths = set()
    for task in plan['tasks']:
        refs = task.get('task_refs')
        if not isinstance(refs, list) or not refs or not all(isinstance(r, str) and r in ids for r in refs):
            raise ValueError('each runtime task must map to known TASK.md IDs')
        covered.update(refs)
        report = (root / task['report_path']).resolve()
        if not report.is_relative_to(root) or report in report_paths or report == path:
            raise ValueError('unique result report paths inside project required')
        report_paths.add(report)
    if covered != ids:
        raise ValueError('plan omits TASK.md requirements: ' + ', '.join(sorted(ids - covered)))
    return items


def result_report(root, task):
    path = (Path(root).resolve() / task['report_path']).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise ValueError('result report outside project')
    # Reuse bounded, regular-file validation before parsing the exact bytes.
    # A report digest is a consistency binding, not independent scientific proof.
    flags = os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_NOFOLLOW', 0)
    import stat
    fd = os.open(path, flags)
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('result report must be a regular file')
        data = stream.read(1024 * 1024 + 1)
    if len(data) > 1024 * 1024:
        raise ValueError('result report exceeds 1 MiB')
    value = json.loads(data)
    if (value.get('task_id') != task['task_id'] or not isinstance(value.get('summary'), str)
            or not value['summary'].strip() or not isinstance(value.get('data'), list)
            or not value['data']):
        raise ValueError('report requires task_id, summary and nonempty data')
    for item in value['data']:
        if (not isinstance(item, dict) or item.get('kind') not in
                ('measured', 'derived', 'synthetic', 'not_applicable')
                or not isinstance(item.get('description'), str) or not item['description'].strip()):
            raise ValueError('each datum needs kind and description; distinguish measured/synthetic/N/A')
    return value, {'path': task['report_path'], 'sha256': hashlib.sha256(data).hexdigest()}


class ReportingHandler:
    """Completion requires both independent acceptance and a bound result report."""
    def __init__(self, handler, root):
        self.handler, self.root = handler, root
        self.idempotent = handler.idempotent
        self.required_capabilities = handler.required_capabilities

    def run(self, task, context):
        outcome = self.handler.run(task, context)
        if outcome.status == 'complete':
            try:
                _, proof = result_report(self.root, task)
            except (OSError, ValueError) as exc:
                return Outcome('blocked', f'result report required: {exc}')
            return Outcome('complete', outcome.reason, (outcome.evidence or []) + [{'task_report': proof}])
        return outcome

    def verify(self, task, evidence):
        if not evidence or not isinstance(evidence[-1], dict) or 'task_report' not in evidence[-1]:
            return False
        _, proof = result_report(self.root, task)
        return (proof == evidence[-1]['task_report']
                and self.handler.verify(task, evidence[:-1]))


def review(snapshot, root):
    """Derived view only; checkbox marks never turn SQLite nodes into done."""
    plan, state = snapshot['plan'], snapshot['state']
    error = None
    try:
        items = validate_contract(plan, root)
    except (OSError, ValueError, KeyError) as exc:
        error = str(exc)
        try:
            items = requirements(plan['task_source']['path'])
        except (OSError, ValueError, KeyError):
            items = []
    rows = []
    for item in items:
        nodes = []
        for task in plan['tasks']:
            if item['id'] not in task.get('task_refs', []):
                continue
            node = state['tasks'][task['task_id']]
            entry = {'task_id': task['task_id'], 'status': node['status'],
                     'owner': task['owner'], 'action': task['action'],
                     'depends_on': task.get('depends_on', []),
                     'reason': node.get('reason'), 'evidence': node['evidence'], 'result': None,
                     'next_step': {'todo': 'dispatch when dependencies and retry deadline allow',
                                   'doing': 'poll owned job and check lease',
                                   'blocked': 'main AI resolves the recorded blocker',
                                   'failed': 'main AI diagnoses and versions authorized recovery',
                                   'cancelled': 'respect cancellation', 'done': 'verified result available'}[node['status']]}
            if node['status'] == 'done':
                try:
                    value, proof = result_report(root, task)
                    if not node['evidence'] or node['evidence'][-1].get('task_report') != proof:
                        raise ValueError('result report changed after acceptance')
                    entry['result'] = value
                except (OSError, ValueError, AttributeError) as exc:
                    entry.update(status='needs_review', reason=str(exc),
                                 next_step='main AI revalidates changed or missing result evidence')
            nodes.append(entry)
        rows.append({**item, 'done': bool(nodes) and all(n['status'] == 'done' for n in nodes), 'nodes': nodes})
    remaining = [r['id'] for r in rows if not r['done']]
    return {'run_id': plan['run_id'], 'source': plan['task_source'], 'source_error': error,
            'runtime_status': state['status'], 'requirements': rows, 'remaining': remaining,
            'all_reportable': bool(rows) and not error and not remaining and state['status'] == 'done'}
