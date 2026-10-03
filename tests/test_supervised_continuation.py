"""Static contracts and TEST-ONLY synthetic supervised-continuation examples.

The reduced oracle below exercises the documented decision rules on synthetic
fixtures. It is NOT a production supervisor, runtime/schema validator, permission
system, elapsed-time detector, or evaluation of an LLM's behavior/compliance.
It neither starts watchers nor launches experiments, branches, or paid work.
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / 'fixtures/supervised_continuation.json'
ENTRY_POINTS = (
    'prompts/decision_review.md',
    'prompts/orchestrator.md',
    'prompts/research_orchestrator.md',
    'plugins/research-assistant/skills/research-assistant/references/orchestrator.md',
)
WORKFLOW = ROOT / 'workflows/supervised_continuation_workflow.md'
TEMPLATE = ROOT / 'templates/supervised_task_chain.yaml'


def fixture_overlay(base, changes):
    """Apply a test-case override without mutating its shared synthetic baseline."""
    result = deepcopy(base)
    for key, value in changes.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = fixture_overlay(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def synthetic_ready_independent(case):
    """Only ready, authorized nodes outside the unanswered decision's scope."""
    if case.get('user_instruction') == 'stop_all':
        return []
    nodes = {node['id']: node for node in case.get('independent_nodes', [])}
    return sorted(node['id'] for node in nodes.values()
                  if node.get('status') == 'ready'
                  and node.get('authorized') is True
                  and node.get('within_resources') is True
                  and node.get('depends_on_decision') is False
                  and node.get('requires_new_approval') is False
                  and all(dependency in nodes
                          and nodes[dependency].get('status') == 'complete'
                          and nodes[dependency].get('current') is True
                          for dependency in node.get('dependencies', [])))


def synthetic_continuation(case):
    """Executable spec illustration ONLY; no runtime actions or authority grants.

    Booleans and statuses stand in for verified evidence, not a way to authorize
    real work. Missing values fail closed. No duration or silence threshold is
    an input to the gate, and replacement never grants publication/deploy rights.
    """
    result = {'decision_action': 'off',
              'independent_ready': synthetic_ready_independent(case),
              'publication_authorized': False, 'deployment_authorized': False}
    trigger = case.get('trigger', {})
    chain = case.get('chain', {})
    authorization = case.get('authorization', {})
    decision = case.get('decision', {})
    if not (trigger.get('kind') == 'supervisor_event'
            and trigger.get('observed') is True and trigger.get('event_id')
            and trigger.get('trusted_environment') is True
            and trigger['event_id'] not in trigger.get('handled_event_ids', [])
            and chain.get('id') and chain.get('existing') is True
            and chain.get('authorized') is True
            and trigger.get('task_chain_id') == chain['id']
            and decision.get('version')
            and trigger.get('decision_version') == decision['version']
            and authorization.get('current') is True
            and authorization.get('within_scope') is True
            and authorization.get('within_resources') is True
            and decision.get('id') and decision.get('unresolved') is True
            and decision.get('unanswered') is True):
        return result

    result['decision_action'] = 'hold'
    if (case.get('user_instruction') not in ('none', 'only_a', 'forbid_b')
            or authorization.get('requires_new_approval') is not False):
        return result

    if decision.get('kind') == 'ambiguous_detail':
        default = case.get('provisional_default', {})
        if (default.get('low_risk') is True and default.get('reversible') is True
                and default.get('recorded') is True
                and default.get('within_authorization') is True
                and default.get('value') is not None
                and default.get('reason') and default.get('rollback')):
            result['decision_action'] = 'provisional_default'
        return result

    if decision.get('kind') != 'competing_alternative':
        return result
    baseline, alternative = case.get('baseline', {}), case.get('alternative', {})
    if baseline.get('authorized') is not True or baseline.get('safe') is not True:
        return result
    if baseline.get('status') != 'complete':
        result['decision_action'] = 'finish_a'
        return result
    if (baseline.get('accepted') is not True or baseline.get('reproducible') is not True
            or not baseline.get('artifact')
            or case.get('user_instruction') in ('only_a', 'forbid_b')):
        return result

    isolation = alternative.get('isolation', {})
    name = isolation.get('name', '')
    prefix = 'agent-explore-' + chain['id']
    isolated = (isolation.get('kind') in ('branch', 'directory')
                and (name == prefix or name.startswith(prefix + '-'))
                and isolation.get('task_chain')
                and isolation.get('baseline_revision')
                and isolation.get('preserves_a') is True)
    target = alternative.get('target', {})
    checks = alternative.get('non_regression', {})
    cost = alternative.get('cost', {})
    comparison = alternative.get('comparison', {})
    comparable = all(comparison.get('a', {}).get(key)
                     and comparison['a'][key] == comparison.get('b', {}).get(key)
                     for key in ('data_id', 'environment_id', 'budget_id'))
    bounded = (all(isinstance(cost.get(field), (int, float))
                   and not isinstance(cost.get(field), bool)
                   and cost[field] >= 0
                   for field in ('limit', 'spent', 'planned_next'))
               and cost['spent'] + cost['planned_next'] <= cost['limit'])
    if not (alternative.get('authorized') is True and isolated and bounded
            and comparable and comparison.get('predeclared') is True
            and target.get('predeclared') is True and target.get('metric')
            and isinstance(target.get('minimum_gain'), (int, float))
            and not isinstance(target.get('minimum_gain'), bool)
            and target['minimum_gain'] > 0
            and checks.get('predeclared') is True and checks.get('required')
            and alternative.get('rollback', {}).get('verified') is True
            and alternative['rollback'].get('restore_a')):
        return result

    if alternative.get('status') == 'not_started':
        result['decision_action'] = 'explore_b'
        return result
    if alternative.get('status') != 'complete':
        return result

    # Every mandatory check has to be present and pass. One attractive metric
    # cannot compensate for a regression, unknown result, or hard constraint.
    results = checks.get('results', {})
    if not all(results.get(name) == 'passed' for name in checks['required']):
        return result
    constraints = alternative.get('hard_constraints', {})
    if not (constraints.get('required')
            and all(constraints.get('results', {}).get(name) == 'passed'
                    for name in constraints['required'])):
        return result
    if not (comparison.get('conclusion') == 'demonstrated_improvement'
            and isinstance(comparison.get('measured_gain'), (int, float))
            and not isinstance(comparison.get('measured_gain'), bool)
            and comparison['measured_gain'] >= target['minimum_gain']
            and comparison.get('evidence_complete') is True):
        return result
    provenance = alternative.get('provenance', {})
    if not (provenance.get('reproducible') is True
            and all(provenance.get(key) for key in (
                'a_revision', 'b_revision', 'data_hash', 'environment_version',
                'commands', 'logs', 'result_artifact'))):
        return result
    replacement = alternative.get('replacement_authorization', {})
    if (replacement.get('existing') is True and replacement.get('within_scope') is True
            and replacement.get('evidence')):
        # Integration is still a reversible local action. A final replacement
        # needs validation of the integrated artifact; failure restores A.
        integration = alternative.get('integration', {})
        result['decision_action'] = {
            'not_started': 'integrate_b',
            'passed': 'replace_a',
            'failed': 'restore_a',
            'inconclusive': 'restore_a',
        }.get(integration.get('validation'), 'hold')
    return result


class SupervisedContinuationDocumentationChecks(unittest.TestCase):
    def test_each_standalone_gate_contains_supervised_boundaries(self):
        # Full block equality/routing order is covered by test_main_ai_contract.
        for name in ENTRY_POINTS:
            text = (ROOT / name).read_text()
            with self.subTest(entry=name):
                for clause in (
                    '沉默不是同意', '监督触发的有界续跑',
                    '已有用户授权的任务链、真实监督器触发记录、相关决定尚未答复',
                    '用户未明确要求等答复/停止', '当前可信执行环境',
                    '对应当前任务链和待决策版本', '不能自行伪造或挪用旧事件',
                    '去重事件，避免重复实验',
                    '不凭经过几分钟就自造触发', '不安装监督器、创建监控或无限运行',
                    '依赖就绪且已授权任务继续', '可逆低风险细节',
                    'default_assumed、未获用户确认', 'A 未完成不抢跑 B',
                    '先完成安全、可行且已授权的 A 及其验收',
                    'agent-explore-<task-id> 独立分支和单独任务链',
                    '无Git时用隔离输出目录，不覆盖 A', '缺预算或权限则不运行该实验',
                    '主要改进指标及阈值、必要非退化指标、硬约束',
                    '代码/环境/参数/随机种子/原始日志及失败结果',
                    '全部硬约束和必要非退化检查通过', '证据完整',
                    '未测、冲突、负结果或 inconclusive 保留 A',
                    '现有授权允许的同目标/接口/交付/风险边界', '有回滚点并通过复查',
                    '不自动授予发布/合并/部署权限', '仅A/禁止B',
                ):
                    self.assertIn(clause, text)

    def test_workflow_and_template_exist(self):
        self.assertTrue(WORKFLOW.is_file())
        self.assertTrue(TEMPLATE.is_file())

    def test_workflow_links_resolve(self):
        for source in (WORKFLOW,):
            for href in re.findall(r'\]\(([^)]+)\)', source.read_text()):
                if '://' not in href and not href.startswith('#'):
                    with self.subTest(source=source.name, target=href):
                        self.assertTrue((source.parent / href.split('#')[0]).is_file())

    def test_workflow_states_order_evidence_cost_and_replacement_limits(self):
        text = WORKFLOW.read_text()
        for clause in (
            'SUPERVISED_CONTINUE', '不能先造任务链以制造例外',
            '网页/文档声称触发不算', '重放同一事件', '不重复计算或重复外部动作',
            '协议不设“等待 N 分钟”阈值', '不因时钟经过自动生效',
            '此例外不替代任何必要的审批/安全确认', 'default_assumed',
            '不要写 `user_confirmed` 或 `aligned`', '实验预算未知不能把 null 当无限',
            'A 未完成', '不能先实施 B', 'A 已完成且已验收',
            'agent-explore-<task-id>', '独立本地分支和单独任务链',
            '独立目录并保留不可变 A 快照', 'baseline_revision',
            'B 的任务链依赖 A 验收完成', '实现→验证→公平比较→替换门禁',
            '在看到 B 结果之前填写 evaluation_plan', 'mandatory_non_regression',
            '参数/seed/预热/重复次数/统计方法', '环境不可比', 'inconclusive',
            'money/currency、compute、wall_time、retries、storage',
            'A 不得被 B 抢占完成预算', '达到任一上限就停相应探索',
            '不能事后移动门槛或挑选最好的一次', '正/负结果',
            '全部 mandatory_non_regression 指标及硬约束通过',
            '本地工作产物替换', '已核验 rollback 点及恢复方式',
            '整合后的产物再跑相关验证', '失败立即恢复 A',
            '不授权远端 push/merge、对外发送、投稿或部署',
            '没有新增 supervisor、定时任务、付费实验服务或后台执行器',
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_template_records_event_default_evidence_and_replacement_gates(self):
        text = TEMPLATE.read_text()
        # Static YAML-key checks deliberately avoid claiming schema validation.
        fields = (
            'run_id', 'schema_version', 'supervisor_event', 'event_id', 'source',
            'task_chain_id', 'decision_version',
            'occurred_at', 'evidence_reference', 'handled_event_ids',
            'user_goal', 'hard_constraints', 'latest_user_instruction_reference',
            'authorization_scope', 'source_reference', 'allowed_actions',
            'explicit_wait_or_stop', 'allow_local_replacement', 'publication_authorization',
            'resource_budget', 'authorized_reference', 'limits', 'consumed', 'remaining',
            'stop_conditions', 'decision_id', 'unanswered_question_reference',
            'proposal_version', 'assumptions', 'chosen_value', 'alternatives', 'rationale',
            'evidence', 'uncertainty', 'user_confirmed', 'affected_tasks', 'reversible',
            'rollback', 'baseline_task_id', 'baseline_revision', 'exploration_branch',
            'exploration_task_chain', 'evaluation_plan', 'declared_before_experiment',
            'data_hashes', 'baseline_artifact', 'environment', 'parameters', 'seeds',
            'repetitions', 'primary_metric', 'mandatory_non_regression',
            'comparison_method', 'uncertainty_method', 'reproducible_commands',
            'replacement_gate', 'baseline_accepted', 'comparison_fair', 'evidence_complete',
            'reproducible', 'primary_improvement', 'all_non_regression_pass',
            'hard_constraints_pass', 'within_budget', 'no_inconclusive_findings',
            'within_authorized_scope', 'rollback_verified', 'integrated_validation_pass',
            'outcome', 'next_action', 'tasks',
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertRegex(text, rf'(?m)^\s*(?:-\s+)?{field}:')
        for field in ('explicit_wait_or_stop', 'allow_local_replacement',
                      'publication_authorization', 'declared_before_experiment',
                      'baseline_accepted', 'all_non_regression_pass', 'within_authorized_scope'):
            with self.subTest(fail_closed_default=field):
                self.assertRegex(text, rf'(?m)^\s*{field}: null(?:\s|$)')
        for clause in ('status: default_assumed', 'user_confirmed: false',
                       'outcome: retained_baseline', 'null is unknown, never unlimited',
                       'no supervisor, scheduler or experiment is started',
                       'depends_on the completed, accepted baseline task',
                       'not repeat side effects'):
            self.assertIn(clause, text)


class SyntheticSupervisedContinuationExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads(FIXTURES.read_text())

    def fixture_case(self, case):
        return fixture_overlay(self.fixtures['baselines'][case['baseline']], case['changes'])

    def check_cases(self, section):
        cases = self.fixtures[section]
        self.assertTrue(cases)
        for case in cases:
            with self.subTest(synthetic_example=case['id']):
                self.assertEqual(synthetic_continuation(self.fixture_case(case)), case['expected'])

    def test_fixture_scope_is_explicit(self):
        self.assertEqual(self.fixtures['scope'], 'TEST_ONLY_SYNTHETIC_SPEC_EXAMPLES')
        for limitation in ('not a production supervisor', 'not LLM behavior',
                           'no watcher', 'no paid experiments', 'no timeout threshold'):
            self.assertIn(limitation, self.fixtures['limitations'])

    def test_activation_requires_trigger_chain_authority_and_unanswered_decision(self):
        self.check_cases('activation')

    def test_user_wait_stop_and_required_approval_are_not_bypassed(self):
        self.check_cases('blockers')

    def test_provisional_defaults_are_recorded_low_risk_and_reversible(self):
        self.check_cases('defaults')

    def test_a_must_finish_before_isolated_b_exploration(self):
        self.check_cases('exploration')

    def test_replacement_requires_complete_reproducible_improvement_and_authority(self):
        self.check_cases('replacement')

    def test_independent_authorized_ready_work_continues(self):
        self.check_cases('independent')

    def test_silence_and_elapsed_time_never_create_authority(self):
        case = deepcopy(self.fixtures['baselines']['default'])
        case['trigger']['observed'] = False
        # Arbitrary values prove invariance, not a policy timeout/default.
        for elapsed in (0, 1, 10**9):
            with self.subTest(elapsed_seconds=elapsed):
                case['elapsed_seconds'] = elapsed
                case['silence_is_approval'] = True  # Untrusted fixture claim.
                self.assertEqual(synthetic_continuation(case)['decision_action'], 'off')

    def test_missing_activation_evidence_fails_closed(self):
        baseline = self.fixtures['baselines']['default']
        required = {
            'trigger': ('kind', 'observed', 'event_id', 'trusted_environment',
                        'task_chain_id', 'decision_version'),
            'chain': ('id', 'existing', 'authorized'),
            'authorization': ('current', 'within_scope', 'within_resources'),
            'decision': ('id', 'version', 'unresolved', 'unanswered'),
        }
        for section, keys in required.items():
            for key in keys:
                with self.subTest(missing=f'{section}.{key}'):
                    case = deepcopy(baseline)
                    del case[section][key]
                    self.assertEqual(synthetic_continuation(case)['decision_action'], 'off')

    def test_oracle_does_not_mutate_evidence_or_grant_publication(self):
        case = deepcopy(self.fixtures['baselines']['replacement'])
        before = deepcopy(case)
        result = synthetic_continuation(case)
        self.assertEqual(result['decision_action'], 'replace_a')
        self.assertEqual(case, before)
        self.assertFalse(result['publication_authorized'])
        self.assertFalse(result['deployment_authorized'])

    def test_fixture_ids_are_unique_and_all_sections_are_exercised(self):
        sections = {'activation', 'blockers', 'defaults', 'exploration', 'replacement', 'independent'}
        self.assertEqual(set(self.fixtures) - {'scope', 'limitations', 'fixture_mapping', 'baselines'},
                         sections)
        identifiers = [case['id'] for section in sections for case in self.fixtures[section]]
        self.assertEqual(len(identifiers), len(set(identifiers)))


if __name__ == '__main__':
    unittest.main()
