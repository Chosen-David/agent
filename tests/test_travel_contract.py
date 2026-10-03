"""Static travel-doc checks and executable TEST-ONLY synthetic spec examples.

The small oracles below illustrate selected planning rules on deliberately reduced
fixtures. They are NOT a production runtime/schema validator, JourneyPilot
adapter, live travel verification, or tests of an LLM's behavior/compliance.
"""
from copy import deepcopy
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/travel-assistant'
SKILL = PLUGIN / 'skills/travel-planner/SKILL.md'
WORKFLOW = SKILL.parent / 'references/workflow.md'
CONTRACT = SKILL.parent / 'references/planning_contract.md'
LEGACY = SKILL.parent / 'references/travel_planning_workflow.md'
TOP_LEVEL = ROOT / 'workflows/travel_planning_workflow.md'
FIXTURES = Path(__file__).parent / 'fixtures/travel_contract_scenarios.json'


def markdown_links(text):
    """Local documentation subset: inline and reference-style Markdown links."""
    # Fenced examples are data, not navigation; avoid interpreting their contents.
    text = re.sub(r'^(```|~~~).*?^\1[^\n]*$', '', text, flags=re.M | re.S)
    definitions = dict(re.findall(r'^\s*\[([^\]]+)\]:\s*<?([^\s>]+)>?', text, re.M))
    links = re.findall(r'\]\(\s*<?([^\s)>]+)>?(?:\s+["\'][^\n]*?["\'])?\s*\)', text)
    for label, reference in re.findall(r'\[([^\]]+)\]\[([^\]]*)\]', text):
        reference = reference or label
        if reference not in definitions:
            raise AssertionError('Unresolved Markdown reference: ' + reference)
        links.append(definitions[reference])
    return links


def markdown_anchors(text):
    """GitHub-like heading anchors (including Unicode) plus explicit HTML IDs."""
    anchors = set(re.findall(r'\b(?:id|name)=["\']([^"\']+)["\']', text))
    counts = {}
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        heading = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', heading)
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        anchors.add(slug if count == 0 else f'{slug}-{count}')
    return anchors


def local_target(source, href):
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        return None
    return (source.parent / unquote(parsed.path)).resolve() if parsed.path else source.resolve()


def iso(value):
    instant = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if instant.tzinfo is None:
        raise ValueError('Synthetic examples must specify a timezone')
    return instant


def synthetic_must_do_coverage(case):
    required = {i['intent_id'] for i in case['intents'] if i['must_do']}
    covered = {intent for stop in case['itinerary'] for intent in stop.get('intent_ids', [])}
    return required <= covered


def synthetic_exact_selection(case):
    candidates = {item['candidate_id']: item for item in case['candidates']}
    allowed = {candidate_id for selection in case['selection_plan']
               for candidate_id in [selection['primary'], *selection['alternatives'],
                                    *selection['fallbacks']]}
    for stop in case['itinerary']:
        candidate = candidates.get(stop['candidate_id'])
        if (stop['candidate_id'] not in allowed or not candidate
                or candidate['admission'] != 'admitted'
                or not candidate['navigable_address'].strip()):
            return False
        # The reduced fixture includes the rendered address projection, so a
        # correct candidate ID with a different printed branch cannot pass.
        if stop.get('navigable_address') != candidate['navigable_address']:
            return False
    return True


def synthetic_service_window(case):
    start, end = iso(case['start']), iso(case['end'])
    if end <= start:
        return False
    for window in case['service_windows']:
        if not iso(window['open']) <= start < end <= iso(window['close']):
            continue
        if window.get('last_admission') and start > iso(window['last_admission']):
            continue
        if window.get('last_order'):
            if not case.get('order_at'):
                continue  # Unknown ordering time cannot pass this check.
            if not start <= iso(case['order_at']) <= min(iso(window['last_order']), end):
                continue
        return True
    return False


def synthetic_independent_rest(case):
    waiver = case.get('waiver', {})
    if not case['covers_midday'] or (waiver.get('explicit') is True
                                    and waiver.get('by') == 'user'
                                    and bool(waiver.get('reason'))):
        return True
    for block in case['blocks']:
        if block['kind'] != 'rest':
            continue
        start, end = iso(block['start']), iso(block['end'])
        minutes = (end - start).total_seconds() / 60
        adjustment = case.get('rest_adjustment', {})
        user_adjusted = (adjustment.get('by') == 'user'
                         and adjustment.get('explicit') is True
                         and adjustment.get('minutes') == minutes)
        if not (60 <= minutes <= 90 or user_adjusted):
            continue
        if all(other is block or not (start < iso(other['end']) and iso(other['start']) < end)
               for other in case['blocks']):
            return True
    return False


def synthetic_budget(case):
    """Single-currency examples; unknown amounts remain unknown, never zero."""
    total = Decimal('0')
    for line in case['lines']:
        if line['amount'] is None:
            return None
        if line['unit'] not in ('per_person', 'per_car'):
            raise ValueError('Unit is outside these reduced test-only examples')
        total += Decimal(line['amount']) * line['quantity']
    return str(total)


# This dependency graph is an executable specification example only. It does not
# manage real artifacts or implement the repository's planning runtime.
SYNTHETIC_DEPENDENTS = {
    'request_contract': {'candidates'},
    'candidates': {'selection_plan'},
    'selection_plan': {'commutes', 'itinerary', 'budget'},
    'itinerary': {'intent_coverage', 'deliverables'},
    'intent_coverage': {'deliverables'},
    'commutes': {'itinerary', 'budget', 'intent_coverage', 'deliverables'},
    'budget': {'intent_coverage', 'deliverables'},
}


def synthetic_amendment(case):
    result = deepcopy(case['before'])
    invalidated = set()
    pending = list(case['changed'])
    while pending:
        for dependent in SYNTHETIC_DEPENDENTS.get(pending.pop(), set()):
            if dependent not in invalidated:
                invalidated.add(dependent)
                pending.append(dependent)
    result['revision'] += 1
    for name in invalidated:
        result['artifacts'][name]['validity'] = 'stale'
    return result, sorted(invalidated)


def synthetic_current_artifact(case):
    artifact = case['artifact']
    return (artifact['bundle_revision'] == case['current_revision']
            and artifact['validity'] == 'current'
            and artifact['qa'] == 'passed'
            and all(d['validity'] == 'current' and d['recorded_revision'] == d['actual_revision']
                    for d in artifact['dependencies']))


def synthetic_resume(case):
    """Reuse only completed results whose versioned dependency closure is valid."""
    nodes, cache = case['nodes'], {}

    def reusable(name, visiting):
        if name in cache:
            return cache[name]
        if name not in nodes or name in visiting:
            return False
        node = nodes[name]
        valid = (node['status'] == 'COMPLETED'
                 and node['validity'] == 'current'
                 and node['validated_for_revision'] == case['contract_revision']
                 and (not node.get('expires_at') or iso(node['expires_at']) > iso(case['now'])))
        for dependency, recorded_revision in node.get('dependencies', {}).items():
            valid = (valid and dependency in nodes
                     and recorded_revision == nodes[dependency]['revision']
                     and reusable(dependency, visiting | {name}))
        cache[name] = bool(valid)
        return cache[name]

    reuse = sorted(name for name in nodes if reusable(name, set()))
    return {'reuse': reuse, 'refresh': sorted(set(nodes) - set(reuse))}


class TravelDocumentationContractChecks(unittest.TestCase):
    def test_real_entries_explicitly_load_shared_contract(self):
        for entry in (TOP_LEVEL, WORKFLOW, SKILL):
            with self.subTest(entry=entry.relative_to(ROOT)):
                self.assertIn(CONTRACT.resolve(), [local_target(entry, link)
                                                   for link in markdown_links(entry.read_text())])
        self.assertIn(WORKFLOW.resolve(), [local_target(SKILL, link)
                                          for link in markdown_links(SKILL.read_text())])

    def test_plugin_navigation_closes_inside_distributable_subtree(self):
        pending, visited = [SKILL, LEGACY], set()
        while pending:
            source = pending.pop().resolve()
            if source in visited:
                continue
            visited.add(source)
            for href in markdown_links(source.read_text()):
                target = local_target(source, href)
                if target is None:
                    continue
                with self.subTest(source=source.relative_to(ROOT), href=href):
                    self.assertTrue(target.is_relative_to(PLUGIN.resolve()),
                                    'Installed plugin must not require repository-only files')
                    self.assertTrue(target.is_file(), f'Missing local target: {target}')
                    fragment = unquote(urlsplit(href).fragment)
                    if fragment and target.suffix == '.md':
                        self.assertIn(fragment, markdown_anchors(target.read_text()),
                                      f'Missing Markdown anchor: {href}')
                if target.suffix == '.md':
                    pending.append(target)
        self.assertTrue({CONTRACT.resolve(), WORKFLOW.resolve()} <= visited)

    def test_top_level_navigation_resolves(self):
        for href in markdown_links(TOP_LEVEL.read_text()):
            target = local_target(TOP_LEVEL, href)
            if target is not None:
                with self.subTest(href=href):
                    self.assertTrue(target.is_file())
                    fragment = unquote(urlsplit(href).fragment)
                    if fragment and target.suffix == '.md':
                        self.assertIn(fragment, markdown_anchors(target.read_text()))

    def test_legacy_reference_is_local_redirect_not_a_third_full_copy(self):
        legacy = LEGACY.read_text()
        targets = {local_target(LEGACY, link) for link in markdown_links(legacy)}
        self.assertIn(WORKFLOW.resolve(), targets)
        self.assertIn(CONTRACT.resolve(), targets)
        self.assertLess(len(legacy.splitlines()), 40)
        self.assertNotIn('schema_version:', legacy)

    def test_shared_contract_declares_local_schema_and_required_fields(self):
        text = CONTRACT.read_text()
        self.assertIn('local-travel/v1', text)
        for field in ('schema_version', 'trip_id', 'revision', 'request_contract', 'trip_brief',
                      'hard_constraints', 'desired_intents', 'soft_preferences', 'unknowns',
                      'acceptance_criteria', 'facts', 'candidates', 'selection_plan', 'itinerary',
                      'commutes', 'budget', 'intent_coverage', 'sources', 'open_questions',
                      'deliverables', 'run_state'):
            with self.subTest(field=field):
                self.assertRegex(text, rf'\b{field}\b')

    def test_shared_roles_and_runtime_boundary_are_explicit(self):
        text = CONTRACT.read_text()
        clauses = (
            'RequestContract', 'ResearchQueryPlan', 'CandidateSelectionPlan',
            'Intent Fidelity Gate', 'typed candidates/facts',
            '不自由生成最终行程', '只使用获准选择的 candidate_id',
            '同一 DeliveryBundle revision', '不输出私密思维链',
            '不是可执行 schema', '没有生产级旅行校验器',
            '不兼容', 'JourneyPilot Python schema', '不直接把上述 YAML 当 API 入参',
            '真正接入须另有用户授权及版本固定的适配设计',
            'validated_for_revision', 'built_from_revision', 'current/stale',
            'COMPLETED', 'INTERRUPTED', 'stale 产物不能作为当前最终链接',
            'service_windows', 'last_order', 'order_at <= last_order',
            '60–90分钟独立午休', 'per_person', 'per_car',
        )
        for clause in clauses:
            with self.subTest(clause=clause):
                self.assertIn(clause, text)

    def test_legacy_migration_and_intake_examples_preserve_canonical_state(self):
        contract = CONTRACT.read_text()
        for clause in ('run_state.json（run_id/tasks）', '保留 run_id', 'tasks 的键映射 stage_id',
                       'artifact 映射 outputs', '未知 input_revision/depends_on/validity',
                       '不凭 COMPLETED 直接复用', 'date_only', '不虚构发布时间/时区'):
            with self.subTest(clause=clause):
                self.assertIn(clause, contract)
        workflow = WORKFLOW.read_text()
        for clause in ('facts 使用 fact_id/source_ids',
                       '不持久维护可独立修改的 source_url 别名',
                       'HH:MM 仅为说明窗口的当地钟点示例',
                       '展开成带偏移量的完整 ISO 8601 时间', '跨午夜用次日日期'):
            with self.subTest(clause=clause):
                self.assertIn(clause, workflow)

    def test_link_checker_handles_fragments_and_reference_links(self):
        sample = '# 标题 Title\n\n[section](#标题-title) [ref][local]\n\n[local]: workflow.md\n'
        self.assertEqual(markdown_links(sample), ['#标题-title', 'workflow.md'])
        self.assertIn('标题-title', markdown_anchors(sample))
        with self.assertRaises(AssertionError):
            markdown_links('[missing][undefined]')
        self.assertIsNone(local_target(SKILL, 'https://example.invalid/path#anchor'))
        self.assertFalse(local_target(SKILL, '../../../../README.md').is_relative_to(PLUGIN))


class SyntheticTravelSpecificationExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = json.loads(FIXTURES.read_text())

    def check_cases(self, section, oracle):
        cases = self.fixtures[section]
        self.assertTrue(cases, section)
        for case in cases:
            with self.subTest(synthetic_example=case['id']):
                self.assertEqual(oracle(case), case['expected'])

    def test_fixture_scope_is_explicit(self):
        self.assertEqual(self.fixtures['scope'], 'TEST_ONLY_SYNTHETIC_SPEC_EXAMPLES')
        self.assertIn('not a production runtime validator', self.fixtures['limitations'])
        self.assertIn('not LLM behavior tests', self.fixtures['limitations'])
        identifiers = [case['id'] for key, cases in self.fixtures.items()
                       if isinstance(cases, list) for case in cases]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_must_do_coverage(self):
        self.check_cases('must_do', synthetic_must_do_coverage)

    def test_exact_selected_entity(self):
        self.check_cases('exact_entity', synthetic_exact_selection)

    def test_split_service_windows(self):
        self.check_cases('service_windows', synthetic_service_window)

    def test_independent_rest_and_explicit_user_waiver(self):
        self.check_cases('rest', synthetic_independent_rest)

    def test_budget_units(self):
        self.check_cases('budget', synthetic_budget)

    def test_constraint_changes_increment_revision_and_invalidate_transitively(self):
        for case in self.fixtures['amendment']:
            with self.subTest(synthetic_example=case['id']):
                original = deepcopy(case['before'])
                result, invalidated = synthetic_amendment(case)
                self.assertEqual(invalidated, sorted(case['expected_invalidated']))
                self.assertEqual(result['revision'], case['expected_revision'])
                self.assertEqual(case['before'], original, 'History must not be rewritten')
                for name, artifact in result['artifacts'].items():
                    self.assertEqual(artifact['validity'], 'stale' if name in invalidated
                                     else original['artifacts'][name]['validity'])
                    self.assertEqual(artifact['status'], original['artifacts'][name]['status'],
                                     'Completed history is distinct from current validity')

    def test_stale_artifacts_are_not_current_delivery(self):
        self.check_cases('artifact', synthetic_current_artifact)

    def test_resume_reuses_current_results_and_refreshes_expired_dependencies(self):
        self.check_cases('resume', synthetic_resume)


if __name__ == '__main__':
    unittest.main()
