"""Same-main host callbacks and real artifacts; no AI or model backend calls."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch

from agent_runtime.core import Store
from agent_runtime.plan_review import PlanReviewError, ReviewSession, check_plan_review
from agent_runtime.task_manifest import prepare, review
from tests import test_plan_review as legacy_fixtures

SINGLE = 'single-main-plan-review/v1'
INDEPENDENT = 'main-plan-review/v1'
ROOT = Path(__file__).resolve().parents[1]


class SingleMainPlanTests(unittest.TestCase):
    def fixture(self, schema=SINGLE):
        case = legacy_fixtures.PlanReviewTests()
        case.setUp()
        self.addCleanup(case.doCleanups)
        case.plan['plan_review']['schema_version'] = schema
        case.self_review = schema == SINGLE
        original = case.reviewer
        def self_check(request, plan, previous):
            result = original(request, plan, previous)
            if schema == SINGLE:
                case.records[result['proof']].update(fresh_context=False, single_main=True)
            return result
        case.session = ReviewSession(case.root, 'logical-T1', planner_identity=case.planner,
            reviewer=self_check, authenticate=case.authenticate, max_cycles=3, max_seconds=90,
            clock=lambda: case.now[0], **({'single_main': True} if schema == SINGLE else {}))
        return case

    def approve_main(self, case):
        try:
            case.approve()
        except PlanReviewError as exc:
            self.fail('single-main host self-check was rejected: ' + str(exc))

    def test_fresh_prepare_defaults_to_single_main(self):
        case = self.fixture(INDEPENDENT)
        draft = prepare(case.root, 'fresh', 'manual', 'current user single-main instruction')
        self.assertEqual(draft['plan_review']['schema_version'], SINGLE)

    @unittest.skipIf(os.name == 'nt', 'managed tmux CLI requires POSIX/WSL')
    def test_actual_prepare_cli_uses_single_main_without_launching(self):
        case = self.fixture(INDEPENDENT)
        output = case.root / 'draft.json'
        run = subprocess.run([sys.executable, '-B', '-m', 'agent_runtime.task_supervisor', 'prepare',
                              '--project-root', str(case.root), '--run-id', 'cli',
                              '--authorization-reference', 'user single main', '--out', str(output)],
                             cwd=ROOT, capture_output=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stderr.decode())
        self.assertEqual(json.loads(output.read_text(encoding='utf-8'))['plan_review']['schema_version'], SINGLE)
        self.assertEqual(case.calls, [])

    @unittest.skipIf(os.name == 'nt', 'managed tmux CLI requires POSIX/WSL')
    def test_actual_review_cli_preserves_same_main_execution_and_label(self):
        case = self.fixture()
        source, output = case.root / 'source.json', case.root / 'checked.json'
        source.write_text(json.dumps(case.plan), encoding='utf-8')
        adapter = ROOT / 'tests/fixtures/single_main_host.py'
        run = subprocess.run([sys.executable, '-B', '-m', 'agent_runtime.task_supervisor', 'review',
                              '--plan', str(source), '--project-root', str(case.root),
                              '--state-dir', str(case.root / 'state'), '--adapter', str(adapter),
                              '--out', str(output)], cwd=ROOT, capture_output=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stderr.decode())
        status = json.loads(run.stdout)
        self.assertEqual(status['status'], 'self-checked')
        self.assertIs(status['independent'], False)
        self.assertEqual((case.root / 'host-calls.txt').read_text().splitlines(), ['planner', 'self-check'])
        case.plan = json.loads(output.read_text(encoding='utf-8'))
        spec = importlib.util.spec_from_file_location('same_main_cpu_host', adapter)
        host = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(host)
        case.session = host.build(case.root, None, 'r1')['plan_review_session']
        store, engine = case.engine()
        self.assertEqual(engine.tick('r1', 'after-cli-review')['status'], 'done')
        self.assertTrue(review(store.snapshot('r1'), case.root,
                               plan_review_verifier=case.session.verify)['all_reportable'])
        self.assertEqual((case.root / 'host-calls.txt').read_text().splitlines(), ['planner', 'self-check'])

    def test_same_context_complete_engine_and_report_are_self_checked(self):
        case = self.fixture()
        self.approve_main(case)
        store, engine = case.engine()
        self.assertEqual(engine.tick('r1', 'main-step')['status'], 'done')
        report = review(store.snapshot('r1'), case.root, plan_review_verifier=case.session.verify)
        self.assertTrue(report['all_reportable'])
        self.assertEqual(report['plan_review']['status'], 'self-checked')
        self.assertIs(report['plan_review']['independent'], False)
        self.assertEqual(len(case.calls), 1)
        request = case.calls[0][0]
        observed = case.records[request['request_id']]
        self.assertEqual(observed['planner'], observed['reviewer'])

    def test_other_context_is_rejected_in_single_main_mode(self):
        case = self.fixture()
        case.self_review = False
        with self.assertRaises(PlanReviewError):
            case.approve()

    def test_undeclared_backend_is_rejected_before_any_callback(self):
        case = self.fixture()
        calls = []
        case.session.single_main = False
        case.session.planner_identity = lambda *_: calls.append('planner')
        case.session.reviewer = lambda *_: calls.append('reviewer')
        with self.assertRaisesRegex(PlanReviewError, 'host review mode unavailable'):
            case.approve()
        self.assertEqual(calls, [])

    def test_self_check_does_not_replace_independent_publication(self):
        case = self.fixture()
        case.session.purpose = 'publication'
        case.session.publication_task_refs = ['T1']
        with self.assertRaisesRegex(PlanReviewError, 'publication'):
            case.approve()
        self.assertEqual(case.calls, [])

    def test_old_independent_protocol_still_rejects_self_approval(self):
        case = self.fixture(INDEPENDENT)
        case.self_review = True
        with self.assertRaisesRegex(PlanReviewError, 'self-approval'):
            case.approve()

    def test_protocol_cannot_change_before_first_review(self):
        case = self.fixture(INDEPENDENT)
        store = Store(case.root / 'reserved.sqlite')
        store.create(case.plan, project_root=case.root)
        altered = copy.deepcopy(case.plan)
        altered['run_id'] = 'different-run'
        altered['plan_review']['schema_version'] = SINGLE
        with self.assertRaises(PlanReviewError):
            store.create(altered, project_root=case.root)

    def test_protocol_cannot_change_after_independent_receipt(self):
        case = self.fixture(INDEPENDENT)
        case.approve()
        altered = copy.deepcopy(case.plan)
        altered.pop('plan_review_receipt')
        altered['run_id'] = 'different-run'
        altered['plan_review']['schema_version'] = SINGLE
        with self.assertRaises(PlanReviewError):
            case.session.submit(altered)

    def test_legacy_sqlite_reservations_default_to_independent(self):
        case = self.fixture(INDEPENDENT)
        path = case.root / '.agent-runs/plan-review.sqlite'
        path.parent.mkdir(exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE review_protected (requirement TEXT PRIMARY KEY, lineage TEXT)')
            db.execute('INSERT INTO review_protected VALUES (?,?)', ('T1', 'logical-T1'))
        Store(case.root / 'reserved.sqlite').create(case.plan, project_root=case.root)
        with sqlite3.connect(path) as db:
            columns = {row[1] for row in db.execute('PRAGMA table_info(review_protected)')}
            self.assertIn('policy_schema', columns)
            self.assertEqual(db.execute('SELECT policy_schema FROM review_protected').fetchone()[0], INDEPENDENT)

    def test_revocation_and_receipt_relabeling_do_not_dispatch(self):
        case = self.fixture()
        self.approve_main(case)
        altered = copy.deepcopy(case.plan)
        altered['plan_review_receipt']['schema_version'] = INDEPENDENT
        with self.assertRaises(PlanReviewError):
            check_plan_review(altered, case.root, case.session.verify)
        case.revoked = True
        store, engine = case.engine()
        state = engine.tick('r1', 'revoked')
        self.assertEqual(state['status'], 'blocked')
        self.assertEqual(state['tasks']['T1']['attempts'], 0)

    def test_self_check_budget_survives_new_run_ids(self):
        case = self.fixture()
        for index in range(3):
            case.plan.pop('plan_review_receipt', None)
            case.plan['run_id'] = 'main-' + str(index)
            self.approve_main(case)
        case.plan.pop('plan_review_receipt')
        case.plan['run_id'] = 'main-budget-exhausted'
        with self.assertRaisesRegex(PlanReviewError, 'budget exhausted'):
            case.approve()
        self.assertEqual(len(case.calls), 3)

    def test_normal_review_scopes_close_acquired_connections(self):
        from agent_runtime import plan_review as protocol
        case = self.fixture()
        acquired = []
        original = protocol._db
        def observe(root):
            connection = original(root)
            acquired.append(connection)
            return connection
        try:
            with patch.object(protocol, '_db', side_effect=observe):
                self.approve_main(case)
            self.assertTrue(acquired)
            for connection in acquired:
                with self.assertRaises(sqlite3.ProgrammingError):
                    connection.execute('SELECT 1')
        finally:
            for connection in acquired:
                connection.close()


if __name__ == '__main__':
    unittest.main()
