"""Project-document entrypoint and installer contracts; no model/runtime claims."""
import importlib.util
import json
import re
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

setup = load_module('document_setup', ROOT / 'setup.py')
codex_setup = load_module('document_codex_setup', ROOT / 'scripts/setup_codex.py')
sync = load_module('document_reference_sync', ROOT / 'scripts/sync_plugin_references.py')


class DocumentWorkflowTests(unittest.TestCase):
    def test_all_registered_roles_discover_package_local_document_contract(self):
        roles = json.loads((ROOT / 'config/role_registry.json').read_text())['roles']
        destinations = sync.MAPPINGS['workflows/project_document_workflow.md']
        expected = []
        for role in roles:
            source = ROOT / role['skill']
            text = source.read_text()
            with self.subTest(role=role['id']):
                for required in ('references/project_document_workflow.md',
                                 'agent_doc/task/TASK.md', 'agent_doc/task/task_details/*.md',
                                 'agent_doc/guide/GUIDE.md', 'agent_doc/advice/', 'adopt/adapt/reject/defer'):
                    self.assertIn(required, text)
                expected.append((Path(role['skill']).parent / 'references/project_document_workflow.md').as_posix())
        self.assertEqual(destinations, expected)
        self.assertEqual(len(destinations), len(set(destinations)))

    def test_documented_index_and_detail_execute_against_runtime(self):
        from agent_runtime.project_docs import snapshot_project_docs, write_task_progress
        examples = re.findall(r'```markdown\n(.*?)\n```',
                              (ROOT / 'workflows/project_document_workflow.md').read_text(), re.S)
        self.assertEqual(len(examples), 2)
        with tempfile.TemporaryDirectory(prefix='document-example-') as temporary:
            root = Path(temporary)
            details = root / 'agent_doc/task/task_details'
            details.mkdir(parents=True)
            (root / 'agent_doc/task/TASK.md').write_text(examples[0] + '\n')
            (details / 'DOC-01.md').write_text(examples[1] + '\n')
            original = snapshot_project_docs(root)
            self.assertEqual(original['layout'], 'canonical')
            self.assertEqual(set(original['task_details']), {'DOC-01'})
            refreshed = write_task_progress(root, 'DOC-01', 'Independent synthetic progress example.\n',
                                            expected_plan_sha256=original['task_details']['DOC-01']['sha256'])
            self.assertEqual(refreshed['task_details'], original['task_details'])
            self.assertFalse((root / 'agent_doc/guide').exists())

    def test_reflection_searches_prior_results_before_planning_in_all_sources(self):
        def gate(text):
            start = text.index('【执行前反思与决策门禁】')
            ends = [pos for marker in ('\n【', '\n```')
                    if (pos := text.find(marker, start + 1)) >= 0]
            return text[start:min(ends)].strip()
        canonical = gate((ROOT / 'prompts/decision_review.md').read_text())
        self.assertLess(canonical.index('agent_doc/results/'), canonical.index('目的→合理性→接口/资源→方案比较'))
        for required in ('保存实际查询', '代码、输入、配置、环境', '指标/单位',
                         '当前独立验证', 'verify_experiment_result/required_result_refs',
                         '最小针对性复验', '明确复现', '新主张', '旧冻结文件可哈希索引引用'):
            self.assertIn(required, canonical)
        for source in ('prompts/orchestrator.md', 'prompts/research_orchestrator.md'):
            self.assertEqual(gate((ROOT / source).read_text()), canonical)
        roles = json.loads((ROOT / 'config/role_registry.json').read_text())['roles']
        self.assertEqual(len(sync.MAPPINGS['workflows/result_reuse_workflow.md']), len(roles))
        for role in roles:
            text = (ROOT / role['skill']).read_text()
            self.assertIn('references/result_reuse_workflow.md', text)
            self.assertIn('agent_doc/results/', text)
        for text in (setup.block(), (ROOT / 'templates/codex_global_instructions.md').read_text()):
            self.assertIn('result_reuse_workflow.md', text)
            self.assertIn('agent_doc/results/', text)

    def test_standalone_contract_preserves_target_project_example_links(self):
        source = 'workflows/project_document_workflow.md'
        for destination in sync.MAPPINGS[source]:
            self.assertEqual(sync.render(source, destination), (ROOT / source).read_text())
            self.assertIn('([详情](task_details/DOC-01.md))', sync.render(source, destination))

    def test_result_validation_is_discovered_by_all_roles_and_main_entries(self):
        roles = json.loads((ROOT / 'config/role_registry.json').read_text())['roles']
        self.assertEqual(len(sync.MAPPINGS['workflows/result_validation_workflow.md']), len(roles))
        for role in roles:
            text = (ROOT / role['skill']).read_text()
            self.assertIn('references/result_validation_workflow.md', text)
            self.assertIn('verify_experiment_result', text)
            self.assertIn('usable-with-scope', text)
        for relative in ('prompts/orchestrator.md', 'prompts/research_orchestrator.md'):
            text = (ROOT / relative).read_text()
            for required in ('producer.experiment_result', 'gate.result_validation',
                             'consumer.required_result_refs', 'pending', 'invalid',
                             'usable-with-scope', '修复→重测→独立复验', '不能保证绝对没有bug'):
                self.assertIn(required, text)

    def test_standalone_main_prompts_include_authority_and_writes(self):
        for relative in ('prompts/orchestrator.md', 'prompts/research_orchestrator.md'):
            text = (ROOT / relative).read_text()
            with self.subTest(source=relative):
                for required in ('【项目文档治理与执行依据】', 'agent_doc/task/TASK.md',
                                 'agent_doc/task/task_details/*.md', 'agent_doc/guide/GUIDE.md',
                                 '最高项目规划优先级', '不能盲从', '## Plan', '## Progress',
                                 '不能授予新权限', 'agent_doc/advice/'):
                    self.assertIn(required, text)
                self.assertNotIn('TASK.md 固定在当前项目根目录', text)

    def test_version_and_advice_semantics_are_explicit(self):
        text = (ROOT / 'workflows/project_document_workflow.md').read_text()
        for required in ('guide_reviews', 'owner_authored', 'owner_approved',
                         'authorization_reference', 'advice_assessments',
                         'guide_alignment: compatible', 'bind_advice', 'document_refs',
                         '## Plan', '## Progress', '不是 OS ACL', '不会静默改变当前执行',
                         'agent_doc/task/legacy/', '取消', '阻塞'):
            with self.subTest(required=required):
                self.assertIn(required, text)

    def test_templates_do_not_create_competing_active_tasks_or_guides(self):
        task_template = (ROOT / 'templates/TASK.md').read_text()
        detail_template = (ROOT / 'templates/task_detail.md').read_text()
        self.assertIn('agent_doc/task/TASK.md', task_template)
        self.assertIn('task_details/T1.md', task_template)
        for required in ('Task-ID:', 'Date:', '## Plan', '## Progress'):
            self.assertIn(required, detail_template)
        # Existing owner-approved source guides are not installer scaffolding.
        # Exercise the actual initializer: it may mkdir but must not copy/create
        # any guide file, even when this workflow repository has a human guide.
        guide = ROOT / 'agent_doc/guide'
        before = {p.relative_to(guide).as_posix(): p.read_bytes()
                  for p in guide.rglob('*') if p.is_file()} if guide.exists() else {}
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            setup.install(target)
            self.assertTrue((target / 'agent_doc/guide').is_dir())
            self.assertEqual(list((target / 'agent_doc/guide').rglob('*')), [])
        after = {p.relative_to(guide).as_posix(): p.read_bytes()
                 for p in guide.rglob('*') if p.is_file()} if guide.exists() else {}
        self.assertEqual(after, before, 'Installer must preserve source human guides')

    def test_claude_and_codex_entry_instructions_use_current_project(self):
        for text in (setup.block(), (ROOT / 'templates/codex_global_instructions.md').read_text()):
            for required in ('agent_doc/task/TASK.md', 'agent_doc/task/task_details/*.md',
                             'agent_doc/guide/GUIDE.md', 'agent_doc/advice/', 'adopt/adapt/reject/defer'):
                self.assertIn(required, text)
        for role, _, description in setup.catalog():
            text = setup.agent_text(role, description)
            self.assertIn('references/project_document_workflow.md', text)
            self.assertIn('document_refs', text)
            self.assertIn('agent_doc/guide/', text)


class DocumentSetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='document-setup-')
        self.addCleanup(self.temporary.cleanup)
        self.target = Path(self.temporary.name)

    def test_empty_project_bootstrap_creates_only_empty_guide_directory(self):
        setup.install(self.target)
        self.assertTrue((self.target / 'agent_doc/task/TASK.md').is_file())
        self.assertTrue((self.target / 'agent_doc/task/task_details').is_dir())
        self.assertTrue((self.target / 'agent_doc/advice').is_dir())
        self.assertTrue((self.target / 'agent_doc/results').is_dir())
        self.assertEqual(list((self.target / 'agent_doc/guide').iterdir()), [])
        self.assertFalse((self.target / 'TASK.md').exists())
        self.assertEqual(setup.check(self.target)['status'], 'configured')
        setup.uninstall(self.target)
        self.assertTrue((self.target / 'agent_doc/task/TASK.md').is_file())
        self.assertEqual(list((self.target / 'agent_doc/guide').iterdir()), [])

    def test_unmigrated_legacy_file_is_preserved_before_any_install_writes(self):
        legacy = self.target / 'TASK.md'
        legacy.write_bytes(b'# Existing user tasks\n- [ ] [REAL] Preserve\n')
        before = legacy.read_bytes()
        with self.assertRaisesRegex(ValueError, 'explicit migration first'):
            setup.install(self.target)
        self.assertEqual(legacy.read_bytes(), before)
        self.assertEqual({p.name for p in self.target.iterdir()}, {'TASK.md'})

    def test_two_active_task_lists_are_rejected_before_writes(self):
        canonical = self.target / 'agent_doc/task/TASK.md'
        canonical.parent.mkdir(parents=True)
        canonical.write_text('- [ ] [NEW] Current\n')
        (self.target / 'TASK.md').write_text('- [x] [OLD] Historical but still active\n')
        with self.assertRaisesRegex(ValueError, 'Two active task lists'):
            setup.install(self.target)
        self.assertFalse((self.target / '.claude').exists())
        self.assertIn('Current', canonical.read_text())

    def test_root_navigation_is_allowed_and_never_replaced(self):
        canonical = self.target / 'agent_doc/task/TASK.md'
        canonical.parent.mkdir(parents=True)
        canonical.write_text('# Project tasks\n')
        pointer = self.target / 'TASK.md'
        pointer.write_text('Moved to [tasks](agent_doc/task/TASK.md).\n')
        setup.install(self.target)
        self.assertEqual(pointer.read_text(), 'Moved to [tasks](agent_doc/task/TASK.md).\n')
        self.assertEqual(canonical.read_text(), '# Project tasks\n')

    def test_document_directory_conflict_is_preflighted(self):
        (self.target / 'agent_doc').mkdir()
        (self.target / 'agent_doc/advice').write_text('user file')
        with self.assertRaisesRegex(ValueError, 'directory conflict'):
            setup.install(self.target)
        self.assertFalse((self.target / '.claude').exists())
        self.assertFalse((self.target / 'CLAUDE.md').exists())
        self.assertEqual((self.target / 'agent_doc/advice').read_text(), 'user file')

    def test_existing_results_file_is_preserved_without_partial_install(self):
        (self.target / 'agent_doc').mkdir()
        result_file = self.target / 'agent_doc/results'
        result_file.write_bytes(b'Existing result archive, not a directory')
        with self.assertRaisesRegex(ValueError, 'directory conflict'):
            setup.install(self.target)
        self.assertEqual(result_file.read_bytes(), b'Existing result archive, not a directory')
        self.assertFalse((self.target / '.claude').exists())
        self.assertFalse((self.target / 'CLAUDE.md').exists())

    def test_task_alias_into_human_guide_is_rejected(self):
        guide = self.target / 'agent_doc/guide'
        guide.mkdir(parents=True)
        (self.target / 'agent_doc/task').symlink_to(guide, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symbolic link|redirects'):
            setup.install(self.target)
        self.assertEqual(list(guide.iterdir()), [])
        self.assertFalse((self.target / '.claude').exists())

    def test_skill_parent_alias_into_guide_is_rejected_before_writes(self):
        guide = self.target / 'agent_doc/guide'
        guide.mkdir(parents=True)
        (self.target / '.claude').mkdir()
        (self.target / '.claude/skills').symlink_to(guide, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symbolic link'):
            setup.install(self.target)
        self.assertEqual(list(guide.iterdir()), [])
        self.assertFalse((self.target / '.claude/agents').exists())
        self.assertFalse((self.target / 'CLAUDE.md').exists())

    def test_uninstall_preflights_guide_alias_before_any_removal(self):
        setup.install(self.target)
        skills = self.target / '.claude/skills'
        skills.rename(self.target / '.claude/skills-original')
        guide = self.target / 'agent_doc/guide'
        skills.symlink_to(guide, target_is_directory=True)
        manifest = self.target / '.claude/agent-workflows/installation.json'
        before = manifest.read_bytes()
        with self.assertRaisesRegex(ValueError, 'symbolic link'):
            setup.uninstall(self.target)
        self.assertEqual(list(guide.iterdir()), [])
        self.assertEqual(manifest.read_bytes(), before)
        self.assertTrue((self.target / '.claude/agents/agent-research-assistant.md').is_file())
        self.assertEqual(setup.check(self.target)['status'], 'needs_setup')

    def test_claude_install_target_cannot_be_inside_a_guide_tree(self):
        guide = self.target / 'agent_doc/guide'
        guide.mkdir(parents=True)
        alias = self.target / 'installer-alias'
        alias.symlink_to(guide, target_is_directory=True)
        for target in (guide, guide / 'nested', alias):
            with self.subTest(target=target):
                with self.assertRaisesRegex(ValueError, 'Human-only agent_doc/guide'):
                    setup.install(target)
                self.assertEqual(list(guide.iterdir()), [])

    def test_codex_writable_roots_cannot_target_guide_directly_or_via_alias(self):
        guide = self.target / 'agent_doc/guide'
        guide.mkdir(parents=True)
        alias = self.target / 'installer-alias'
        alias.symlink_to(guide, target_is_directory=True)
        for position in range(3):
            for rejected in (guide, alias):
                roots = [self.target / 'skills', self.target / 'state', self.target / 'codex']
                roots[position] = rejected
                with self.subTest(position=position, rejected=rejected):
                    with self.assertRaisesRegex(ValueError, 'Human-only agent_doc/guide'):
                        codex_setup.synchronize(ROOT, *roots)
                    self.assertEqual(list(guide.iterdir()), [])
                    self.assertFalse((self.target / 'state').exists())

    def test_codex_state_child_alias_into_guide_is_preflighted(self):
        guide = self.target / 'agent_doc/guide'
        guide.mkdir(parents=True)
        state = self.target / 'state'
        state.mkdir()
        for relative in ('backups', 'installation.json', 'pending.json', 'sync.lock'):
            alias = state / relative
            alias.symlink_to(guide, target_is_directory=True)
            try:
                with self.subTest(relative=relative):
                    with self.assertRaisesRegex(ValueError, 'Human-only agent_doc/guide'):
                        codex_setup.synchronize(ROOT, self.target / 'skills', state, self.target / 'codex')
                    self.assertEqual(list(guide.iterdir()), [])
                    self.assertFalse((self.target / 'skills').exists())
                    self.assertFalse((self.target / 'codex').exists())
            finally:
                alias.unlink()

    def test_human_guide_directory_is_never_owned_by_installer(self):
        setup.install(self.target)
        manifest = json.loads((self.target / '.claude/agent-workflows/installation.json').read_text())
        self.assertFalse(any(path.startswith('agent_doc/') for path in manifest['files']))
        self.assertFalse(any(path.startswith('agent_doc/') for path in manifest['links']))


if __name__ == '__main__':
    unittest.main()
