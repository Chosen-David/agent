"""Run semantic controls against single-check mutations outside the target checkout."""
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest


root = Path(os.environ['AGENT_TEST_PROJECT_ROOT']).resolve()
sys.path.insert(0, str(root))


def load(name):
    spec = importlib.util.spec_from_file_location(name, root / 'tests' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(case, expected_fault):
    result = unittest.TestResult()
    case.run(result)
    if result.errors or len(result.failures) != int(expected_fault):
        raise AssertionError((result.failures, result.errors))
    if expected_fault and 'AssertionError:' not in result.failures[0][1]:
        raise AssertionError(result.failures)
    print(case.id(), 'semantic rejection' if expected_fault else 'control passed')


workspace = load('test_workspace_status')
recovery = load('test_recovery_registration')
with tempfile.TemporaryDirectory() as temporary:
    directory = Path(temporary)
    for label, before, after, test in (
        ('owner', 'if grant is not True:', 'if False:', 'test_live_owner_conflict_never_creates_slot'),
        ('consumer', "facts.get(key) != []", "(key != 'consumers' and facts.get(key) != [])",
         'test_reclaim_candidate_rechecks_live_consumers_and_local_changes')):
        source = (root / 'scripts/workspace_status.py').read_text(encoding='utf-8')
        assert source.count(before) == 1
        workspace.SCRIPT = root / 'scripts/workspace_status.py'
        check(workspace.WorkspaceTests(test), False)
        workspace.SCRIPT = directory / (label + '.py')
        workspace.SCRIPT.write_text(source.replace(before, after).replace(
            'str(Path(__file__).resolve().parents[1])', repr(str(root))), encoding='utf-8')
        check(workspace.WorkspaceTests(test), True)
    test = 'test_stale_content_or_in_restore_change_refused'
    check(recovery.RegistrationTests(test), False)
    module = root / 'agent_runtime/result_store.py'
    source = module.read_text(encoding='utf-8')
    before = "_need(digest.hexdigest() == ref['sha256'],"
    assert source.count(before) == 1
    mutated = directory / 'mutated_store.py'
    mutated.write_text(source.replace(before, '_need(True,'), encoding='utf-8')
    wrapper = directory / 'integrity.py'
    wrapper.write_text(f'import sys,runpy\nsys.path.insert(0,{str(root)!r})\n'
                       f'import agent_runtime.result_store as m\nexec(compile(open({str(mutated)!r},encoding="utf-8").read(),'
                       f'{str(mutated)!r},"exec"),m.__dict__)\nrunpy.run_path({str(recovery.SCRIPT)!r},run_name="__main__")')
    recovery.SCRIPT = wrapper
    check(recovery.RegistrationTests(test), True)

import inspect
import textwrap
from unittest.mock import patch
from agent_runtime import core, scheduled_review
from tests import test_scheduled_review, test_task_runtime


def replace_check(function, old, new):
    source = textwrap.dedent(inspect.getsource(function))
    if source.count(old) != 1:
        raise AssertionError('mutation target changed: ' + old)
    scope = {}
    exec(compile(source.replace(old, new), '<acceptance mutation>', 'exec'), function.__globals__, scope)
    return scope[function.__name__]


for obj, attribute, function, before, after, case_type, case_name in (
    (core.Engine, 'tick', core.Engine.tick, 'if not owned:', 'if False:',
     test_task_runtime.RuntimeContracts, 'test_expired_idempotent_restarts_with_stable_key_and_fences_old_result'),
    (test_scheduled_review, 'codex_timer_reviewer', scheduled_review.codex_timer_reviewer,
     "'queued_unconfirmed' if", "'consumed' if", test_scheduled_review.OwnerHandoff,
     'test_review_persisted_before_owner_queue'),
    (core.Engine, '_recheck_done', core.Engine._recheck_done, 'self._check_done(plan, state)', 'pass',
     test_task_runtime.RuntimeContracts, 'test_changed_upstream_proof_prevents_downstream_dispatch'),
    (core.Engine, '_tick_owned', core.Engine._tick_owned, 'if handler and handler.idempotent:', 'if handler:',
     test_task_runtime.RuntimeContracts, 'test_expired_nonidempotent_blocks_for_reconciliation')):
    check(case_type(case_name), False)
    with patch.object(obj, attribute, replace_check(function, before, after)):
        check(case_type(case_name), True)
