"""Figure prompt/package contracts and small synthetic preservation checks.

The route taskset is an offline, normative review rubric. These tests do not run
an LLM or a production router, render figures, judge aesthetics, or demonstrate
that installed tools follow the instructions. The executable fixture checks
only establish that the specified numeric/semantic invariants detect mutations.
"""
import copy
from fractions import Fraction
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / 'plugins/research-assistant/skills'
FIXTURE_PATH = ROOT / 'tests/fixtures/figure_tasks.json'
COMMON = ('figure_shared.md', 'figure_tools.md', 'figure_inputs.md')
SPECIALISTS = {
    'research-data-visualization': 'data_visualization_workflow.md',
    'research-diagrams': 'diagram_workflow.md',
}
CANONICAL = ('figure_workflow.md', *COMMON, *SPECIALISTS.values())
PACKAGES = {
    'research-figures': {
        'workflow.md': 'figure_workflow.md',
        **{name: name for name in (*COMMON, *SPECIALISTS.values())},
    },
    'research-assistant': {name: name for name in CANONICAL},
    **{
        skill: {'workflow.md': workflow, **{name: name for name in COMMON}}
        for skill, workflow in SPECIALISTS.items()
    },
}
ROUTE_OWNERS = {
    'data_visualization': ['research-data-visualization'],
    'diagram': ['research-diagrams'],
    'mixed': ['research-data-visualization', 'research-diagrams'],
    'asset_only': [],
    'clarify': [],
}
QA_DIMENSIONS = {
    'final_size', 'palette', 'typography', 'whitespace', 'accessibility',
    'evidence_preservation',
}


def read(path):
    return path.read_text(encoding='utf-8')


def local_links(text):
    """Only documented Markdown links and explicit local reference paths.

    Example code paths are intentionally not treated as package dependencies.
    Anchor existence is a Markdown-renderer concern; files must still resolve.
    """
    links = re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', text)
    links += re.findall(r'`(references/[A-Za-z0-9_./-]+\.md)`', text)
    for target in links:
        target = target.strip().strip('<>')
        # Optional Markdown title is not part of a file path.
        target = re.split(r'\s+[\"\']', target, maxsplit=1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield unquote(parsed.path)


def scientific_projection(artifact):
    """Fixture-only conservative rule: polish can alter the style subtree.

    Protected encodings (including prescribed object-color identity), evidence,
    labels and source provenance remain outside style. This is not a validator
    for arbitrary plotting programs or exported images.
    """
    return {key: value for key, value in artifact.items() if key != 'style'}


def apply_changes(artifact, changes):
    result = copy.deepcopy(artifact)
    for change in changes:
        path = change['path']
        node = result
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = copy.deepcopy(change['value'])
    return result


class FigurePackageContractChecks(unittest.TestCase):
    def require_token(self, token, text):
        self.assertTrue(token in text, f'Missing contract token: {token}')

    def require_pattern(self, pattern, text):
        self.assertIsNotNone(re.search(pattern, text), f'Missing contract concept: {pattern}')

    def test_canonical_files_and_standalone_snapshots_are_exact(self):
        for skill, snapshots in PACKAGES.items():
            for local_name, canonical_name in snapshots.items():
                with self.subTest(skill=skill, reference=local_name):
                    canonical = ROOT / 'workflows' / canonical_name
                    snapshot = SKILLS / skill / 'references' / local_name
                    self.assertTrue(canonical.is_file(), str(canonical))
                    self.assertTrue(snapshot.is_file(), str(snapshot))
                    self.assertTrue(snapshot.read_bytes() == canonical.read_bytes(),
                                    f'Snapshot drift: {snapshot.relative_to(ROOT)} != '
                                    f'{canonical.relative_to(ROOT)}; refresh the complete copy.')

    def test_local_document_links_resolve_without_repository_escape(self):
        for name in CANONICAL:
            source = ROOT / 'workflows' / name
            for target in local_links(read(source)):
                with self.subTest(source=str(source.relative_to(ROOT)), target=target):
                    resolved = (source.parent / target).resolve()
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.is_file(), str(resolved))
        for skill, snapshots in PACKAGES.items():
            package = SKILLS / skill
            sources = [package / 'SKILL.md']
            sources += [package / 'references' / name for name in snapshots]
            for source in sources:
                for target in local_links(read(source)):
                    with self.subTest(source=str(source.relative_to(ROOT)), target=target):
                        resolved = (source.parent / target).resolve()
                        self.assertTrue(resolved.is_relative_to(package),
                                        'Standalone skills cannot depend on sibling/repo files.')
                        self.assertTrue(resolved.is_file(), str(resolved))

    def test_skill_entries_and_agent_metadata_are_wired(self):
        installed = {path.parent.name for path in SKILLS.glob('*/SKILL.md')}
        self.assertEqual(len(installed), 12, 'Update advertised skill counts when the package changes.')
        readme = read(ROOT / 'README.md')
        self.require_pattern(r'包含\s+12\s+个技能', readme)
        for skill in installed:
            self.require_token('`' + skill + '`', readme)
        plugin = json.loads(read(SKILLS.parent / 'plugin.json'))
        interface = plugin['extensions']['com.openai']['interface']
        self.require_token('十二个技能', interface['shortDescription'])
        self.require_token('十一个专业技能', interface['longDescription'])
        for skill in ('research-figures', *SPECIALISTS):
            package = SKILLS / skill
            text = read(package / 'SKILL.md')
            with self.subTest(skill=skill):
                self.require_pattern(r'(?m)^name: ' + re.escape(skill) + r'$', text)
                self.require_pattern(r'(?m)^description:\s*\S', text)
                self.require_token('references/workflow.md', text)
                self.require_token('references/figure_shared.md', text)
                metadata = read(package / 'agents/openai.yaml')
                for field in ('display_name:', 'short_description:', 'default_prompt:'):
                    self.require_token(field, metadata)
                self.require_token('$' + skill, metadata)
                self.require_pattern(r'allow_implicit_invocation:\s*true\b', metadata)

    def test_main_routes_expose_both_specialists_and_compatibility_entry(self):
        for path in (
            'README.md', 'prompts/orchestrator.md', 'prompts/research_orchestrator.md',
            'plugins/research-assistant/skills/research-assistant/SKILL.md',
            'plugins/research-assistant/skills/research-assistant/references/orchestrator.md',
        ):
            text = read(ROOT / path)
            with self.subTest(entry=path):
                for role in ('research-figures', *SPECIALISTS):
                    self.require_token(role, text)
        # Existing concept-explanation packages retain their snapshot prefaces;
        # compare the actual routing row rather than unrelated historical text.
        concept_paths = (
            'workflows/concept_explanation_workflow.md',
            'plugins/research-assistant/skills/explain-research-concepts/references/workflow.md',
            'plugins/research-assistant/skills/research-assistant/references/concept_explanation_workflow.md',
            'plugins/research-assistant/skills/paper-reading-companion/references/concept_explanation_workflow.md',
        )
        canonical_row = None
        for path in concept_paths:
            with self.subTest(concept_entry=path):
                rows = [line for line in read(ROOT / path).splitlines()
                        if line.startswith('| 直观图解 |')]
                self.assertEqual(len(rows), 1, 'Keep one unambiguous concept-figure route.')
                for role in ('research-figures', *SPECIALISTS):
                    self.require_token(role, rows[0])
                if canonical_row is None:
                    canonical_row = rows[0]
                self.assertEqual(rows[0], canonical_row)

    def test_router_has_explicit_evidence_based_boundaries(self):
        text = read(ROOT / 'workflows/figure_workflow.md')
        route_rows = {}
        for route in ROUTE_OWNERS:
            with self.subTest(route=route):
                match = re.search(r'(?m)^\|\s*`?' + route + r'`?\s*\|([^\n]+)$', text)
                self.assertIsNotNone(match, f'Missing explicit routing-table row: {route}')
                route_rows[route] = match.group(1)
        for route in ('data_visualization', 'diagram'):
            self.require_token(ROUTE_OWNERS[route][0], route_rows[route])
        self.require_pattern(r'唯一|单一', route_rows['mixed'])
        self.require_pattern(r'owner|负责人', route_rows['mixed'])
        self.require_pattern(r'问|澄清', route_rows['clarify'])
        for pattern in (
            r'理论|函数', r'热图|heatmap', r'截图', r'polish|精修',
            r'图像|影像|素材|插画|image', r'混合|mixed', r'唯一|单一|一个.*主源|owner',
        ):
            self.require_pattern(pattern, text)
        for role in SPECIALISTS:
            self.require_token(role, text)

    def test_shared_qa_has_visual_and_evidence_gates(self):
        text = read(ROOT / 'workflows/figure_shared.md')
        for dimension in QA_DIMENSIONS:
            with self.subTest(dimension=dimension):
                self.require_token(dimension, text)
        for required in (
            'draft', 'ready-for-review', 'submission-spec-verified',
            'figure_tools.md', 'figure_inputs.md',
        ):
            self.require_token(required, text)
        # Concepts rather than a frozen copy of every sentence. Exact snapshots
        # above protect packaging; these guards protect the critical contract.
        for pattern in (
            r'最终.*尺寸|实际.*尺寸', r'主源', r'来源|source', r'证据|evidence',
            r'渲染', r'查看|读图', r'重渲|再次渲染', r'色盲|色觉',
            r'灰度|黑白', r'不能.*脚本|不以.*脚本|脚本.*不.*视觉|不能.*生成成功|程序无错不能证明美观',
            r'未完成|未验证', r'合成|synthetic',
        ):
            self.require_pattern(pattern, text)

    def test_specialists_preserve_scientific_boundaries(self):
        data = read(ROOT / 'workflows/data_visualization_workflow.md')
        diagram = read(ROOT / 'workflows/diagram_workflow.md')
        for pattern in (
            r'理论|函数', r'定义域|domain', r'独立.*单位|独立.*重复',
            r'误差|置信|uncertainty', r'变换|聚合', r'轴限|坐标范围',
            r'截图', r'原始数据|原始数值', r'精修|polish', r'快照',
        ):
            with self.subTest(data_contract=pattern):
                self.require_pattern(pattern, data)
        for pattern in (
            r'SVG|TikZ', r'节点', r'箭头|连线', r'因果', r'数据流',
            r'proposed', r'schematic', r'语义', r'精修|polish',
        ):
            with self.subTest(diagram_contract=pattern):
                self.require_pattern(pattern, diagram)
        for text in (data, diagram):
            self.require_token('figure_shared.md', text)
            self.require_pattern(r'可编辑', text)
            self.require_pattern(r'未.*数据|不.*编造|不.*虚构|不.*制造', text)


class FigureTasksetChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(read(FIXTURE_PATH))

    def test_taskset_is_explicitly_normative_not_a_model_evaluation(self):
        self.assertEqual(self.fixture['schema_version'], 1)
        scope = self.fixture['validation_scope']
        self.assertEqual(scope['kind'], 'normative_offline_taskset')
        for claim in ('runs_model', 'runs_production_router', 'renders_figures',
                      'proves_aesthetic_quality', 'proves_tool_integration'):
            self.assertIs(scope[claim], False)
        self.assertTrue(scope['fixture_preservation_only'])

    def test_taskset_routes_and_review_fields_are_complete(self):
        ids = set()
        coverage = set()
        routes = set()
        for case in self.fixture['cases']:
            with self.subTest(case=case['id']):
                self.assertNotIn(case['id'], ids)
                ids.add(case['id'])
                self.assertTrue(case['request'])
                self.assertTrue(case['evidence'])
                self.assertTrue(case['expected']['must_preserve'])
                self.assertTrue(case['expected']['must_not'])
                self.assertTrue(case['expected']['next_action'])
                route = case['expected']['route']
                routes.add(route)
                self.assertIn(route, ROUTE_OWNERS)
                self.assertEqual(case['expected']['specialists'], ROUTE_OWNERS[route])
                self.assertEqual(case['expected']['assembly_owner'],
                                 'research-figures' if route == 'mixed' else None)
                if route == 'clarify':
                    self.assertTrue(case['expected']['clarification'])
                self.assertTrue(set(case['qa_dimensions']).issubset(QA_DIMENSIONS))
                coverage.update(case['tags'])
        self.assertEqual(routes, set(ROUTE_OWNERS))
        self.assertTrue({
            'mixed', 'theoretical_curve', 'conceptual_curve', 'numeric_heatmap',
            'schematic_heatmap', 'ambiguous_heatmap', 'real_image_asset',
            'generated_illustration', 'polish_data', 'polish_diagram',
            'screenshot_no_data', 'refuse_fabrication', 'semantic_edge_preservation',
            'source_preservation', 'actual_size', 'accessibility',
        }.issubset(coverage))

    def test_qa_rubric_requires_review_evidence_not_only_process_success(self):
        rubric = self.fixture['qa_rubric']
        self.assertEqual(set(rubric), QA_DIMENSIONS)
        for dimension, contract in rubric.items():
            with self.subTest(dimension=dimension):
                self.assertTrue(contract['pass_criteria'])
                self.assertTrue(contract['required_evidence'])
                self.assertTrue(contract['failure_examples'])
        self.assertIs(self.fixture['acceptance']['requires_actual_render_inspection'], True)
        self.assertIs(self.fixture['acceptance']['script_success_is_sufficient'], False)
        self.assertIs(self.fixture['acceptance']['unknown_or_unchecked_can_pass'], False)
        self.assertEqual(self.fixture['acceptance']['unresolved_status'], 'draft')

    def test_cosmetic_fixture_edits_preserve_numeric_and_graph_contracts(self):
        kinds = set()
        for example in self.fixture['preservation_examples']:
            with self.subTest(example=example['id']):
                kinds.add(example['kind'])
                before = example['before']
                after = apply_changes(before, example['allowed_changes'])
                self.assertNotEqual(before, after)
                self.assertEqual(scientific_projection(before), scientific_projection(after))
                for mutation in example['forbidden_changes']:
                    with self.subTest(mutation=mutation['reason']):
                        changed = apply_changes(before, [mutation])
                        self.assertNotEqual(scientific_projection(before),
                                            scientific_projection(changed))
        self.assertEqual(kinds, {'numeric', 'semantic_graph'})

    def test_semantic_graph_fixture_has_resolvable_nodes_and_edges(self):
        example = next(x for x in self.fixture['preservation_examples']
                       if x['kind'] == 'semantic_graph')
        graph = example['before']
        ids = [node['id'] for node in graph['nodes']]
        self.assertEqual(len(ids), len(set(ids)))
        for edge in graph['edges']:
            self.assertIn(edge['source'], ids)
            self.assertIn(edge['target'], ids)
            self.assertEqual(edge['relation'], 'data_flow')
            self.assertTrue(edge['label'])
        for members in graph['encoding']['groups'].values():
            self.assertTrue(set(members).issubset(ids))
        self.assertEqual(set(graph['style']['positions']), set(ids))

    def test_numeric_fixture_summary_uses_independent_runs_and_explicit_units(self):
        example = next(x for x in self.fixture['preservation_examples']
                       if x['kind'] == 'numeric')
        data = example['before']['data']
        self.assertEqual(data['unit'], 'ms')
        self.assertEqual(example['before']['analysis']['independent_unit'], 'run_id')
        observed = {}
        seen = set()
        for row in data['rows']:
            key = (row['method'], row['run_id'])
            self.assertNotIn(key, seen)
            seen.add(key)
            observed.setdefault(row['method'], []).append(Fraction(str(row['latency_ms'])))
        means = {key: str(sum(values) / len(values)) for key, values in observed.items()}
        self.assertEqual(means, example['expected_means_ms'])

    def test_theory_curve_fixture_is_a_function_example_not_experimental_data(self):
        example = self.fixture['theory_curve_example']
        self.assertEqual(example['evidence_kind'], 'theoretical_function')
        self.assertEqual(example['function'], 'y = x^2')
        self.assertEqual(example['parameters'], {})
        lower, upper = map(Fraction, example['domain'])
        self.assertLess(lower, upper)
        for x, y in example['numeric_snapshot']:
            x, y = Fraction(x), Fraction(y)
            self.assertLessEqual(lower, x)
            self.assertLessEqual(x, upper)
            self.assertEqual(y, x * x)
        self.assertFalse(example['empirical_claim'])


if __name__ == '__main__':
    unittest.main()
