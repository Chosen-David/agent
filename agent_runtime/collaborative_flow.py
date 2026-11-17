"""Persistent human-first collaboration; trusted hosts supply model execution."""
from copy import deepcopy
from contextlib import contextmanager
import datetime
from . import file_lock as fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import re
import select
import subprocess
import sys
import time
import uuid

from .intake import build_intake
from .plan_review import DUAL_SCHEMA, _authenticate, _identity, _review, protected_lineage, sha
from .project_docs import assert_ai_writable, atomic_write, initialize_project_docs, regular_bytes


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', value):
        raise ValueError('invalid task/project identifier')
    return value


def probe_environment():
    def command(args):
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=5,
                                    env={**os.environ, 'LC_ALL': 'C'})
            return result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            return None
    gpu = command(['nvidia-smi', '--query-gpu=name,driver_version', '--format=csv,noheader'])
    cpu_details = command(['lscpu'])
    cpu_match = re.search(r'(?m)^Model name:\s*(.+)$', cpu_details or '')
    cpu = cpu_match.group(1).strip() if cpu_match else platform.processor() or command(['uname', '-m'])
    return {'python': platform.python_version(), 'python_executable': sys.executable,
            'platform': platform.platform(), 'cpu': cpu,
            'cpu_details': cpu_details, 'gpus': [line.split(',')[0].strip() for line in gpu.splitlines()] if gpu else [],
            'driver': gpu, 'cuda_toolkit': command(['nvcc', '--version']),
            'gpu_probe': 'observed' if gpu else 'unavailable-or-unknown'}


def load_environment_skills(workflow, environment):
    workflow = Path(workflow).resolve()
    registry = json.loads(regular_bytes(workflow, 'config/role_registry.json'))
    selected = ['research-implement-optimize']
    if environment.get('gpus'):
        selected.append('gpu-experiment-dispatch')
    roles = {r['id']: r for r in registry['roles']}
    loaded = []
    for name in selected:
        source = roles[name]['skill']
        content = regular_bytes(workflow, source)
        loaded.append({'skill': name, 'source': str(workflow / source),
                       'sha256': hashlib.sha256(content).hexdigest(), 'content': content.decode(),
                       'environment': deepcopy(environment)})
    return loaded


class Flow:
    def __init__(self, root, task_id, *, clock=time.time):
        self.root = Path(root).resolve()
        if not self.root.is_dir():
            raise ValueError('project root must already exist')
        self.task_id = identifier(task_id)
        self.clock = clock
        self.relative = '.agent-runs/collaboration/' + task_id + '.json'
        self.path = assert_ai_writable(self.root, self.relative)
        self.raw = regular_bytes(self.root, self.relative) if self.path.exists() else None
        self.state = json.loads(self.raw) if self.raw is not None else None
        if self.state is not None and (self.state.get('root') != str(self.root) or self.state.get('task_id') != task_id):
            raise ValueError('state project/task mismatch')

    @contextmanager
    def lock(self):
        path = assert_ai_writable(self.root, self.relative + '.lock')
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        with os.fdopen(fd, 'a') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            actual = regular_bytes(self.root, self.relative) if self.path.exists() else None
            if actual != self.raw:
                raise ValueError('state changed; reload before continuing')
            yield

    def save(self):
        with self.lock():
            raw = json.dumps(self.state, ensure_ascii=False, indent=2, allow_nan=False).encode()
            atomic_write(self.root, self.relative, raw)
            self.raw = raw

    def active(self):
        if self.state is None or self.state['phase'] in ('cancelled', 'done'):
            raise ValueError('flow is not active')
        if self.state.get('inflight'):
            raise ValueError('prior host action ambiguous; reconcile before replay')
        ref = self.state.get('prompt_ref')
        if ref and hashlib.sha256(regular_bytes(self.root, ref['path'])).hexdigest() != ref['sha256']:
            raise ValueError('task prompt file changed; reconcile the requirement version')

    def event(self, name):
        item = {'event': name, 'time': self.clock(), 'revision': self.state['revision']}
        if name in ('questions-presented', 'human-feedback', 'reviewer-discussion'):
            item.update(questions=deepcopy(self.state['questions']), answers=deepcopy(self.state['answers']))
        if name == 'plan-prepared':
            item['plan'] = deepcopy(self.state['plan'])
            item['test_binding'] = deepcopy(self.state['test_binding'])
        self.state['events'].append(item)
        self.save()

    def create(self, prompt, *, mode="human"):
        if mode not in ("human", "dual-ai"):
            raise ValueError("unknown collaboration mode")
        if self.state is not None or not isinstance(prompt, str) or not prompt.strip():
            raise ValueError('existing task or empty prompt')
        if protected_lineage({'tasks': [{'task_refs': [self.task_id]}]}, self.root) is not None:
            raise ValueError('existing protected task requires its original host/ledger reconciliation')
        self.state = {'version': 1, 'root': str(self.root), 'task_id': self.task_id,
                      'prompt': prompt, 'mode': mode, 'phase': 'discussion', 'revision': 1,
                      'questions': [], 'answers': {}, 'choice_visible': False, 'deadline': None,
                      'events': [], 'reviews': [], 'review_calls': 0, 'completed_steps': []}
        self.event('created')

    def ask(self, questions):
        self.active()
        normalized = build_intake(questions)['questions']
        for source, target in zip(questions, normalized):
            kind = source.get('kind')
            if kind not in ('implementation', 'business', 'permission', 'budget'):
                raise ValueError('question requires explicit decision kind')
            target['kind'] = kind
        by_id = {q['id']: q for q in normalized}
        for old in self.state['questions']:
            if old['kind'] != 'implementation' and old['id'] not in self.state['answers']:
                if old['id'] in by_id and by_id[old['id']] != old:
                    raise ValueError('unresolved human decision cannot be replaced')
                if old['id'] not in by_id:
                    normalized.append(deepcopy(old))
        if len(normalized) > 20:
            raise ValueError('too many unresolved questions')
        for q in normalized:
            self.state['answers'].pop(q['id'], None)
        human = self.state['mode'] == 'human'
        self.state.update(questions=normalized, phase='waiting' if human else 'discussion',
                          choice_visible=human, deadline=self.clock() + 600 if human else None,
                          waiting_since=self.clock())
        self.event('questions-presented')

    def switch_mode(self, mode, reason):
        """Explicitly revise this task; never replace its budget or ledger."""
        self.active()
        if mode not in ('human', 'dual-ai') or not isinstance(reason, str) or not reason.strip():
            raise ValueError('valid mode and explicit reason required')
        if self.state['phase'] not in ('discussion', 'waiting', 'planned', 'repair', 'blocked'):
            raise ValueError('finish or reconcile the current phase before switching')
        if protected_lineage({'tasks': [{'task_refs': [self.task_id]}]}, self.root) is not None:
            raise ValueError('protected task requires original ledger reconciliation')
        if mode == self.state['mode']:
            return
        previous = {'mode': self.state['mode'], 'reason': reason.strip(),
                    'revision': self.state['revision']}
        for key in ('plan', 'test_binding', 'acceptance', 'design_review', 'completed_steps',
                    'execution_context', 'environment', 'last_implementation'):
            if key in self.state:
                previous[key] = self.state.pop(key)
        self.state.setdefault('mode_history', []).append(previous)
        self.state['revision'] += 1
        self.state.update(mode=mode, phase='discussion', choice_visible=False,
                          deadline=None, completed_steps=[])
        self.event('mode-switched')

    def timeout(self):
        if self.state['phase'] != 'waiting' or self.clock() < self.state['deadline']:
            return False
        self.state.update(mode='dual-ai', phase='discussion', choice_visible=False, deadline=None)
        self.event('human-timeout')
        return True

    def validated_answers(self, answers, *, human):
        if not isinstance(answers, dict):
            raise ValueError('answers must map question IDs to text')
        questions = {q['id']: q for q in self.state['questions']}
        if set(answers) - questions.keys():
            raise ValueError('unknown question')
        for key, value in answers.items():
            q = questions[key]
            if not human and q['kind'] != 'implementation':
                raise ValueError('human decision required for ' + key)
            if not isinstance(value, str) or not value.strip() or (not q['allow_free_text'] and value not in q['options']):
                raise ValueError('invalid choice or empty detail')
        return answers

    def answer(self, answers):
        if self.state is None or self.state['phase'] == 'cancelled':
            raise ValueError('flow is not active')
        answers = self.validated_answers(answers, human=True)
        if not answers:
            raise ValueError('empty answers do not resolve a question')
        self.state['answers'].update(answers)
        self.state['revision'] += 1
        for key in ('plan', 'test_binding', 'acceptance', 'design_review'):
            self.state.pop(key, None)
        self.state.update(mode='human', phase='blocked' if self.state.get('inflight') else 'discussion',
                          choice_visible=False, deadline=None, completed_steps=[])
        self.event('human-feedback')

    def resolve_review(self, response):
        self.active()
        answers = self.validated_answers(response.get('answers', {}), human=False)
        self.state['answers'].update(answers)
        unresolved = [q for q in self.state['questions'] if q['id'] not in self.state['answers']]
        self.state['phase'] = 'blocked' if unresolved else 'discussion'
        self.event('reviewer-discussion')
        return not unresolved

    def call(self, host, method, payload):
        self.active()
        previous = self.state.get('last_implementation')
        if method == 'implement' and previous and previous['payload_sha256'] == sha(payload):
            return deepcopy(previous['result'])
        callback = getattr(host, method, None)
        if not callable(callback):
            raise ValueError(method + ' backend unavailable')
        self.state['inflight'] = {'method': method, 'revision': self.state['revision'], 'payload_sha256': sha(payload)}
        self.save()
        try:
            result = callback(deepcopy(payload))
        except Exception as exc:
            from .codex_host import HostPreflightError, ProposalRejected
            if isinstance(exc, HostPreflightError):
                self.state.pop('inflight')
                self.state.update(phase='repair' if isinstance(exc, ProposalRejected) else 'blocked',
                                  feedback={'summary': str(exc)})
                self.event('host-rejected-before-side-effects')
            raise
        if method == 'implement':
            self.state['last_implementation'] = {'payload_sha256': sha(payload), 'result': result}
        self.state.pop('inflight')
        self.save()
        return result

    def review(self, host, payload):
        self.active()
        payload = deepcopy(payload)
        if not all(callable(getattr(host, key, None)) for key in ('review', 'authenticate', 'planner_identity')):
            raise ValueError('authenticated reviewer backend unavailable')
        if self.state['review_calls'] >= self.state.get('review_limit', 6):
            raise ValueError('review budget exhausted; human replan required')
        planner = _identity(host.planner_identity(deepcopy(payload)), model_required=True)
        model = getattr(host, 'reviewer_model_id', None)
        if not isinstance(model, str) or not model.strip() or model.strip() != model or planner['model_id'] == model:
            raise ValueError('distinct canonical reviewer model required')
        request = {'schema_version': DUAL_SCHEMA, 'planner': planner, 'reviewer_model_id': model,
                   'request_id': uuid.uuid4().hex, 'project_root': str(self.root),
                   'deadline': self.clock() + 120,
                   'task_id': self.task_id, 'revision': self.state['revision'],
                   'cycle': self.state['review_calls'] + 1, 'payload': deepcopy(payload)}
        self.state['review_calls'] += 1
        self.save()
        result = self.call(host, 'review', request)
        if self.clock() > request['deadline']:
            raise ValueError('review response exceeded its deadline; no approval accepted')
        _review(result['review'], dual_model=True)
        _authenticate(host.authenticate, request, result['review'], result['proof'])
        self.state['reviews'].append({'request': request, **result})
        self.save()
        return result['review']['verdict']

    def add_review_calls(self, additional, reason):
        self.active()
        if type(additional) is not int or not 1 <= additional <= 6 or not isinstance(reason, str) or not reason.strip():
            raise ValueError('explicit reason and 1..6 additional review calls required')
        if protected_lineage({'tasks': [{'task_refs': [self.task_id]}]}, self.root) is not None:
            raise ValueError('protected budget requires original ledger reconciliation')
        old = self.state.get('review_limit', 6)
        self.state['review_limit'] = old + additional
        self.state.setdefault('budget_history', []).append({'previous_limit': old,
            'new_limit': old + additional, 'used_calls': self.state['review_calls'], 'reason': reason.strip()})
        self.event('review-budget-explicitly-extended')

    def retry_final_review(self, host, reason):
        """Reuse unchanged tested inputs; never rerun implementation for missing review evidence."""
        self.active()
        if (self.state['mode'] != 'dual-ai' or self.state['phase'] not in ('repair', 'discussion', 'review') or
                not isinstance(reason, str) or not reason.strip()):
            raise ValueError('active dual-ai review repair and explicit reason required')
        self.check_tests()
        if any(q['id'] not in self.state['answers'] for q in self.state['questions']):
            raise ValueError('unresolved decisions block final review')
        acceptance = self.state.get('acceptance', {})
        if not acceptance or acceptance.get('input_binding') != self.acceptance_binding():
            raise ValueError('acceptance is not bound to the current plan/revision; fresh design and tests required')
        design = self.state.get('design_review')
        if (not design or design['review']['verdict']['decision'] != 'approve' or
                design['request']['revision'] != self.state['revision'] or
                design['request']['payload']['plan'] != self.state['plan'] or
                design['request']['payload']['test_binding'] != self.state['test_binding']):
            raise ValueError('current approved acceptance design required')
        _authenticate(host.authenticate, design['request'], design['review'], design['proof'])
        path = Path(acceptance.get('report', ''))
        raw = path.read_bytes()
        report = json.loads(raw)
        spec = importlib.util.spec_from_file_location('flow_retry_source', Path(self.state['workflow']) / 'scripts/project_test.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        def stable():
            return (acceptance.get('returncode') == 0 and report.get('status') == 'pass' and
                    report.get('sources') == self.state['test_binding'] and
                    report.get('stable_inputs') and hashlib.sha256(raw).hexdigest() == acceptance.get('sha256') and
                    path.read_bytes() == raw and runner.source_state(self.root,
                        exclude_owned=self.state.get('owned_documents')) == report['after'])
        if not stable():
            raise ValueError('tested inputs changed; rerun task acceptance before final review')
        self.state['phase'] = 'review'
        self.event('final-review-explicitly-retried')
        verdict = self.review(host, {'stage': 'implementation', 'acceptance': acceptance,
                                    **self.state['execution_context']})
        self.check_tests()
        self.state['phase'] = 'done' if verdict['decision'] == 'approve' and stable() else 'repair'
        self.event('final-review')
        self.write_detail()

    def acceptance_binding(self):
        context = self.state.get('execution_context')
        if not context:
            raise ValueError('current execution context required; fresh design and tests required')
        design = self.state.get('design_review')
        return {'revision': self.state['revision'], 'plan_sha256': sha(self.state['plan']),
                'execution_context_sha256': sha(context), 'test_binding_sha256': sha(self.state['test_binding']),
                'prompt_sha256': sha(self.state['prompt']), 'answers_sha256': sha(self.state['answers']),
                'questions_sha256': sha(self.state['questions']), 'mode': self.state['mode'],
                'design_review_sha256': sha(design) if design else None}

    def plan(self, plan, workflow, project):
        self.active()
        if any(q['id'] not in self.state['answers'] for q in self.state['questions']):
            raise ValueError('unresolved questions block planning')
        if not isinstance(plan, dict) or not isinstance(plan.get('summary'), str) or not plan['summary'].strip():
            raise ValueError('plan requires a reviewable decision summary')
        seen = set()
        if not isinstance(plan.get('steps'), list) or not plan['steps']:
            raise ValueError('nonempty task chain required')
        for step in plan['steps']:
            identifier(step['id'])
            if step['id'] in seen or not isinstance(step.get('depends_on'), list) or not set(step['depends_on']) <= seen:
                raise ValueError('task chain must be ordered, unique and acyclic')
            seen.add(step['id'])
        workflow = Path(workflow).resolve()
        directory = f'agent_doc/{identifier(project)}/test/{self.task_id}'
        try:
            suite = regular_bytes(workflow, directory + '/suite.json')
        except OSError as exc:
            raise ValueError('task suite must exist before implementation') from exc
        spec = importlib.util.spec_from_file_location('collaboration_project_test', workflow / 'scripts/project_test.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        runner.prepare_suite(workflow, project, self.root, task=self.task_id)
        binding = runner.suite_state(workflow / directory)
        manifest = json.loads(suite)
        if not manifest.get('checks'):
            raise ValueError('task suite must declare checks')
        if self.state.get('plan') is not None:
            self.state['revision'] += 1
        if self.state.get('acceptance'):
            self.state.setdefault('acceptance_history', []).append(self.state.pop('acceptance'))
        for key in ('design_review', 'execution_context', 'last_implementation'):
            self.state.pop(key, None)
        self.state.update(plan=deepcopy(plan), test_binding=binding, workflow=str(workflow), project=project,
                          phase='planned', completed_steps=[])
        self.write_detail()
        self.event('plan-prepared')

    def discussion_context(self):
        """Current decisions plus history references, without nested transcripts."""
        result = deepcopy({k: v for k, v in self.state.items()
                           if k not in ('events', 'reviews', 'mode_history', 'design_review', 'execution_context')})
        result['history'] = {k: {'records': len(self.state.get(k, [])), 'sha256': sha(self.state.get(k, []))}
                             for k in ('events', 'reviews', 'mode_history')}
        if self.state['reviews']:
            result['last_verdict'] = deepcopy(self.state['reviews'][-1]['review']['verdict'])
        return result

    def write_detail(self):
        for owned, expected in self.state.get('owned_documents', {}).items():
            if hashlib.sha256(regular_bytes(self.root, owned)).hexdigest() != expected:
                raise ValueError('controller document changed externally; reconcile before writing: ' + owned)
        initialize_project_docs(self.root)
        relative = 'agent_doc/task/task_details/' + self.task_id + '.md'
        path = assert_ai_writable(self.root, relative)
        marker = '<!-- collaborative-flow:' + self.task_id + ' -->'
        if path.exists() and marker not in regular_bytes(self.root, relative).decode():
            raise ValueError('existing task detail belongs to another writer')
        date = datetime.date.today().isoformat()
        progress = {k: self.state[k] for k in ('mode', 'phase', 'revision', 'review_calls', 'completed_steps')}
        progress.update(answers=self.state['answers'], state_file=self.relative,
                        events_sha256=sha(self.state['events']), event_count=len(self.state['events']),
                        recent_events=[{k: e[k] for k in ('event', 'time', 'revision')}
                                       for e in self.state['events'][-12:]])
        content = (f'# {self.task_id}\n\nTask-ID: {self.task_id}\nDate: {date}\n{marker}\n\n## Plan\n'
                   + self.state['prompt'] + '\n\nDecision summary (not private chain of thought):\n'
                   + json.dumps(self.state['plan'], ensure_ascii=False, indent=2)
                   + '\n\n## Progress\n' + json.dumps(progress, ensure_ascii=False, indent=2) + '\n')
        atomic_write(self.root, relative, content.encode())
        self.state.setdefault('owned_documents', {})[relative] = hashlib.sha256(content.encode()).hexdigest()
        index = 'agent_doc/task/TASK.md'
        text = regular_bytes(self.root, index).decode()
        if f'[{self.task_id}]' not in text:
            text += f'\n## {date}\n\n- [ ] [{self.task_id}] Collaborative task ([details](task_details/{self.task_id}.md))\n'
            atomic_write(self.root, index, text.encode())
        self.state['owned_documents'][index] = hashlib.sha256(text.encode()).hexdigest()
        self.save()

    def cancel(self):
        if self.state is None or self.state['phase'] == 'done':
            raise ValueError('flow is not active')
        self.state.update(phase='cancelled', choice_visible=False, deadline=None)
        self.event('cancelled')

    def check_tests(self):
        workflow = Path(self.state['workflow'])
        spec = importlib.util.spec_from_file_location('flow_tests', workflow / 'scripts/project_test.py')
        runner = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner)
        directory = workflow / 'agent_doc' / self.state['project'] / 'test' / self.task_id
        if runner.suite_state(directory) != self.state['test_binding']:
            raise ValueError('acceptance changed; replan and review before implementation')

    def execute(self, host, output):
        self.active()
        if self.state['phase'] not in ('planned', 'implementing'):
            raise ValueError('reviewed plan required before implementation')
        self.check_tests()
        output = Path(output).absolute()
        if (output.exists() or output.resolve().is_relative_to(self.root) or
                output.resolve().is_relative_to(Path(self.state['workflow']))):
            raise ValueError('acceptance output must be a fresh external directory')
        resuming = self.state['phase'] == 'implementing'
        environment = probe_environment()
        skills = load_environment_skills(self.state['workflow'], environment)
        context = {'task_id': self.task_id, 'revision': self.state['revision'],
                   'prompt': self.state['prompt'], 'answers': self.state['answers'],
                   'plan': self.state['plan'], 'environment': environment, 'skills': skills,
                   'test_binding': self.state['test_binding'], 'project_root': str(self.root)}
        if resuming:
            previous = self.state['execution_context']
            if ([r['sha256'] for r in skills] != [r['sha256'] for r in previous['skills']] or
                    any(environment[k] != previous['environment'][k] for k in ('python', 'gpus', 'cuda_toolkit', 'driver'))):
                raise ValueError('execution environment or Skills changed; replan required')
            context = previous
        if self.state['mode'] == 'dual-ai' and self.state['phase'] == 'planned':
            verdict = self.review(host, {'stage': 'acceptance-design', **context})
            if verdict['decision'] != 'approve':
                self.state.update(phase='repair', feedback=verdict)
                self.event('design-rejected')
                return
            self.state['design_review'] = self.state['reviews'][-1]
        self.state.update(phase='implementing', environment=environment, execution_context=context,
                          skills=[{k: v for k, v in r.items() if k != 'content'} for r in skills])
        self.event('implementation-started')
        for step in self.state['plan']['steps']:
            if step['id'] in self.state['completed_steps']:
                continue
            self.check_tests()
            if self.state['mode'] == 'dual-ai':
                receipt = self.state['design_review']
                _authenticate(host.authenticate, receipt['request'], receipt['review'], receipt['proof'])
            try:
                self.call(host, 'implement', {**context, 'step': step})
            except Exception as exc:
                from .codex_host import ProposalRejected
                if not isinstance(exc, ProposalRejected):
                    raise
                self.write_detail()
                return
            self.check_tests()
            if self.state['mode'] == 'dual-ai' and len(self.state['plan']['steps']) > 1:
                verdict = self.review(host, {'stage': 'supervision', 'step': step, **context})
                if verdict['decision'] != 'approve':
                    self.state.update(phase='repair', feedback=verdict)
                    self.event('supervision-rejected')
                    self.write_detail()
                    return
            self.state['completed_steps'].append(step['id'])
            self.event('step-completed')
        authorize = getattr(host, 'authorize_execution', None)
        if callable(authorize):
            authorize(deepcopy(context))
        self.state['phase'] = 'acceptance'
        self.event('acceptance-started')
        workflow = Path(self.state['workflow'])
        output = Path(output).absolute()
        command = [sys.executable, '-X', 'utf8', str(workflow / 'scripts/project_test.py'),
                   '--workflow-root', str(workflow), '--project', self.state['project'],
                   '--target', str(self.root), '--task', self.task_id, '--output', str(output),
                   '--controller-documents-json', json.dumps(self.state.get('owned_documents', {}))]
        self.state['inflight'] = {'method': 'acceptance', 'output': str(output)}
        self.save()
        run = subprocess.run(command, cwd=self.root, capture_output=True, text=True, encoding='utf8', timeout=1800)
        report_path = output / 'report.json'
        raw = report_path.read_bytes() if report_path.is_file() else b''
        report = json.loads(raw) if raw else {}
        self.state['acceptance'] = {'returncode': run.returncode, 'report': str(report_path),
                                    'sha256': hashlib.sha256(raw).hexdigest(), 'stderr': run.stderr[-4000:],
                                    'input_binding': self.acceptance_binding()}
        if not report or report.get('status') == 'blocked' or any(
                c.get('status') == 'blocked' for c in report.get('checks', [])):
            self.state['phase'] = 'blocked'
            self.event('acceptance-effects-require-reconciliation')
            self.write_detail()
            return
        self.state.pop('inflight')
        self.check_tests()
        if run.returncode != 0 or report.get('status') != 'pass' or not report.get('stable_inputs'):
            self.state['phase'] = 'repair'
            self.event('acceptance-failed')
        elif self.state['mode'] == 'dual-ai':
            self.state['phase'] = 'review'
            self.save()
            verdict = self.review(host, {'stage': 'implementation', 'acceptance': self.state['acceptance'], **context})
            spec = importlib.util.spec_from_file_location('flow_final_source', workflow / 'scripts/project_test.py')
            runner = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(runner)
            stable = runner.source_state(self.root, exclude_owned=self.state.get('owned_documents')) == report['after'] and report_path.read_bytes() == raw
            self.check_tests()
            self.state['phase'] = 'done' if verdict['decision'] == 'approve' and stable else 'repair'
            self.event('final-review')
        else:
            self.state['phase'] = 'done'
            self.event('acceptance-passed')
        self.write_detail()


def input_line(stream, seconds):
    """Return a line or None on timeout; Windows select() only accepts sockets."""
    import io
    if isinstance(stream, io.StringIO):
        return stream.readline()
    if os.name != 'nt':
        end = time.monotonic() + seconds
        data = bytearray()
        while time.monotonic() < end:
            ready, _, _ = select.select([stream], [], [], max(0, end - time.monotonic()))
            if not ready:
                return None
            byte = os.read(stream.fileno(), 1)
            if not byte:
                return data.decode(stream.encoding or 'utf8') if data else ''
            data.extend(byte)
            if byte == b'\n':
                return data.decode(stream.encoding or 'utf8')
        return None
    import ctypes
    import msvcrt
    end = time.monotonic() + seconds
    data = bytearray()
    if stream.isatty():
        chars = []
        while time.monotonic() < end:
            if msvcrt.kbhit():
                char = msvcrt.getwch()
                if char in ('\r', '\n'):
                    return ''.join(chars) + '\n'
                if char == '\x03':
                    raise KeyboardInterrupt
                if char == '\x1a':
                    return ''
                if char in ('\x00', '\xe0'):
                    msvcrt.getwch()
                elif char == '\b':
                    chars = chars[:-1]
                else:
                    chars.append(char)
            else:
                time.sleep(min(.05, max(0, end - time.monotonic())))
        return None
    handle = msvcrt.get_osfhandle(stream.fileno())
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetFileType.argtypes = [ctypes.c_void_p]
    kernel.PeekNamedPipe.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong,
                                   ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong), ctypes.c_void_p]
    if kernel.GetFileType(handle) == 1:  # redirected ordinary file; never waits for a writer
        return stream.readline()
    while time.monotonic() < end:
        available = ctypes.c_ulong()
        if not kernel.PeekNamedPipe(handle, None, 0, None, ctypes.byref(available), None):
            if ctypes.get_last_error() in (109, 232):  # broken/disconnected pipe
                return data.decode(stream.encoding or 'utf8') if data else ''
            raise OSError(ctypes.get_last_error(), 'cannot poll input pipe')
        if available.value:
            # Consume only this line; do not steal a future prompt's answer.
            byte = os.read(stream.fileno(), 1)
            data.extend(byte)
            if byte == b'\n':
                return data.decode(stream.encoding or 'utf8')
        else:
            time.sleep(min(.05, max(0, end - time.monotonic())))
    return None


def wait_for_human(flow, stream=sys.stdin, display=print):
    if flow.timeout():
        display('<双AI模式> 原选择框已关闭，保留问题记录；正在请求审查 AI')
        return
    display('<人类-AI模式> 思考和讨论：单题输入选项编号或细节；多题输入 JSON；/cancel 取消')
    for q in flow.state['questions']:
        display(q['id'] + ': ' + q['question'])
        for number, option in enumerate(q['options'], 1):
            display(f'  {number}. {option}')
    while flow.state['phase'] == 'waiting':
        remaining = max(0, flow.state['deadline'] - flow.clock())
        line = input_line(stream, remaining)
        if line is not None:
            if not line:
                raise ValueError('input disconnected; persisted question remains pending; resume to continue')
            if line.strip() == '/cancel':
                flow.cancel()
                return
            try:
                if len(flow.state['questions']) == 1 and not line.lstrip().startswith('{'):
                    q = flow.state['questions'][0]
                    text = line.strip()
                    if text.isdigit() and 1 <= int(text) <= len(q['options']):
                        text = q['options'][int(text) - 1]
                    flow.answer({q['id']: text})
                else:
                    flow.answer(json.loads(line))
            except (ValueError, json.JSONDecodeError) as exc:
                display(str(exc))
                continue
            return
        if flow.timeout():
            display('<双AI模式> 原选择框已关闭，保留问题记录；正在请求审查 AI')
            return


def main():
    import argparse
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--workflow-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--project', required=True)
    parser.add_argument('--task-id', required=True)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--prompt')
    source.add_argument('--prompt-file', type=Path, help='existing TASK/specification file inside the target project')
    parser.add_argument('--mode', choices=('human', 'dual-ai'), help='initial mode; existing tasks keep their recorded mode')
    parser.add_argument('--adapter', type=Path, help='explicit trusted host exposing build(root, task_id)')
    parser.add_argument('--backend', choices=('codex',), help='built-in authenticated app-server host')
    parser.add_argument('--runtime-profile', type=Path, default=Path.home() / '.codex/chosen-agent/runtime.json')
    parser.add_argument('--write-path', action='append', default=[], help='allowed project-relative source file; repeatable')
    parser.add_argument('--context-path', action='append', default=[], help='project-relative inline context; repeatable')
    parser.add_argument('--trust-project-code', action='store_true', help='authorize tests/imports as current OS user, without execution isolation')
    parser.add_argument('--switch-mode', choices=('human', 'dual-ai'), help='explicitly revise this same active task')
    parser.add_argument('--reason', help='required explanation for explicit mode change')
    parser.add_argument('--add-review-calls', type=int, help='explicitly extend original review ledger, preserving used calls')
    parser.add_argument('--retry-final-review', action='store_true', help='review unchanged passing evidence without rerunning implementation')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--answer', help='resume with a human JSON answer; invalidates affected plan')
    parser.add_argument('--cancel', action='store_true')
    args = parser.parse_args()
    try:
        flow = Flow(args.project_root, args.task_id)
        if flow.state is None:
            if args.prompt_file is not None:
                relative = str(args.prompt_file.absolute().relative_to(flow.root))
                raw = regular_bytes(flow.root, relative)
                flow.create(raw.decode(), mode=args.mode or "dual-ai")
                flow.state['prompt_ref'] = {'path': relative, 'sha256': hashlib.sha256(raw).hexdigest()}
                flow.save()
            else:
                flow.create(args.prompt, mode=args.mode or "dual-ai")
        elif args.mode is not None and args.mode != flow.state["mode"]:
            raise ValueError("existing task mode differs; reconcile the original task before switching")
        if args.switch_mode:
            flow.switch_mode(args.switch_mode, args.reason)
        if args.add_review_calls is not None:
            flow.add_review_calls(args.add_review_calls, args.reason)
        if args.status:
            print(json.dumps(flow.state, ensure_ascii=False))
            return 0
        if args.cancel:
            flow.cancel()
            return 0
        if args.answer:
            flow.answer(json.loads(args.answer))
        if args.adapter is not None and args.backend is not None:
            raise ValueError('select one trusted host, not both adapter and backend')
        if args.backend == 'codex':
            from .codex_host import CodexHost
            host = CodexHost(flow.root, flow.task_id, args.runtime_profile,
                             workflow=args.workflow_root, project=args.project,
                             write_paths=args.write_path, context_paths=args.context_path,
                             trust_project_code=args.trust_project_code)
            if not args.trust_project_code:
                raise ValueError('builtin execution requires explicit --trust-project-code; tests run as current OS user')
        elif args.adapter is None:
            raise ValueError('explicit trusted host adapter required; no model was started')
        else:
            spec = importlib.util.spec_from_file_location('collaboration_host', args.adapter.resolve())
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            host = module.build(flow.root, flow.task_id)
        if flow.state['phase'] == 'waiting':
            wait_for_human(flow)
        if flow.state['phase'] in ('cancelled', 'done'):
            print(flow.state['phase'])
            return 0
        flow.active()
        if args.retry_final_review:
            flow.retry_final_review(host, args.reason)
            print(json.dumps({'mode': flow.state['mode'], 'phase': flow.state['phase'],
                              'review_calls': flow.state['review_calls']}, ensure_ascii=False))
            return 0 if flow.state['phase'] == 'done' else 1
        if flow.state['phase'] not in ('discussion', 'repair', 'planned', 'implementing'):
            raise ValueError('resume requires explicit reconciliation of current phase: ' + flow.state['phase'])
        if args.output is None:
            raise ValueError('external --output directory required for acceptance')
        while True:
            if flow.state['phase'] == 'repair':
                repairs = flow.state.get('repair_count', 0)
                if repairs >= 2:
                    raise ValueError('repair budget exhausted; human replan required')
                flow.state.update(repair_count=repairs + 1, phase='discussion')
                flow.event('repair-requested')
            if flow.state['phase'] == 'discussion':
                print('<' + ('人类-AI模式' if flow.state['mode'] == 'human' else '双AI模式') + '> 思考和讨论')
                discussion = flow.call(host, 'discuss', flow.discussion_context())
                print(discussion['summary'])
                if discussion.get('questions'):
                    flow.ask(discussion['questions'])
                    if flow.state['phase'] == 'waiting':
                        wait_for_human(flow)
                if flow.state['phase'] == 'cancelled':
                    return 0
                if flow.state['mode'] == 'dual-ai':
                    verdict = flow.review(host, {'stage': 'discussion', 'state': flow.discussion_context()})
                    if verdict['decision'] != 'approve' or not flow.resolve_review(verdict):
                        raise ValueError('discussion unresolved; human decision or replan required')
                proposed = flow.call(host, 'plan', flow.discussion_context())
                flow.plan(proposed, args.workflow_root, args.project)
            print('规划：' + str(flow.root / 'agent_doc/task/task_details' / (flow.task_id + '.md')))
            print('<' + ('人类-AI模式' if flow.state['mode'] == 'human' else '双AI模式') + '> 实现与任务验收')
            output = args.output / ('revision-' + str(flow.state['revision']) + '-attempt-' + str(flow.state.get('repair_count', 0)))
            flow.execute(host, output)
            if flow.state['phase'] != 'repair':
                break
        print(json.dumps({'mode': flow.state['mode'], 'phase': flow.state['phase'], 'acceptance': flow.state.get('acceptance')}, ensure_ascii=False))
        return 0 if flow.state['phase'] == 'done' else 1
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'blocked', 'reason': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
