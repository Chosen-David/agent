"""Static instruction/config regression checks, not LLM behavior evaluations."""
from pathlib import Path
import re
import unittest

try:
    import tomllib
except ImportError:
    tomllib = None

ROOT = Path(__file__).resolve().parents[1]
ENTRY_POINTS = (
    'prompts/orchestrator.md',
    'prompts/research_orchestrator.md',
    'plugins/research-assistant/skills/research-assistant/references/orchestrator.md',
)


def review_block(text):
    start = text.index('【执行前反思与决策门禁】')
    ends = [p for token in ('\n【', '\n```') if (p := text.find(token, start + 1)) >= 0]
    return text[start:min(ends)].strip()


class MainAIContractChecks(unittest.TestCase):
    def test_standalone_entry_points_share_gate_before_routing(self):
        canonical = review_block((ROOT / 'prompts/decision_review.md').read_text())
        for name in ENTRY_POINTS:
            with self.subTest(entry=name):
                text = (ROOT / name).read_text()
                self.assertEqual(review_block(text), canonical)
                routing = '【任务路由】' if name == ENTRY_POINTS[0] else '【1. 动态能力选择必须先行】'
                self.assertLess(text.index(canonical), text.index(routing))

    def test_gate_preserves_decision_and_evidence_boundaries(self):
        text = (ROOT / 'prompts/decision_review.md').read_text()
        # Critical clauses are contracts for prompt authors, not a behavioral oracle.
        for required in (
            'EXECUTE', 'PROPOSE_AND_WAIT', 'VERIFY_OR_ASK',
            'tmp/decision-proposals/<task-id>.md', 'status=awaiting_alignment',
            'status=aligned', '沉默不是同意', '不先实现替代方案',
            '生产者→消费者', '类型/单位/版本', '原始文献/官方文档',
            '观察、来源事实、推导、假设、估计和未知',
            '不输出私密思维链', '无需强制联网', '不改用户全局设置或安全权限',
            '目的→合理性→接口/资源→方案比较→证据→决策',
            '用代表性输入核对生产者实际输出能否被消费者接受',
            '同一目标、硬约束、验收和资源预算', '结论与证据逐项对应',
            '提案路径/版本和待决定项', '仅同意讨论或验证 B 不等于同意实施 B',
            '续跑时先读取', '专业流程的自主优化只能在该授权内执行',
            '不以角色切换绕过对齐',
        ):
            with self.subTest(clause=required):
                self.assertIn(required, text)

    @unittest.skipIf(tomllib is None, 'TOML parsing requires Python 3.11+')
    def test_project_reasoning_default_does_not_expand_permissions(self):
        config = tomllib.loads((ROOT / '.codex/config.toml').read_text())
        self.assertEqual(config['model_reasoning_effort'], 'high')
        self.assertEqual(set(config), {'model_reasoning_effort', 'plugins'})
        for plugin in ('research-assistant', 'travel-assistant'):
            self.assertEqual(config['plugins'][plugin + '@chosen-david-agents'], {'enabled': True})

    def test_new_document_links_resolve(self):
        for name in ('README.md', 'prompts/decision_review.md', 'docs/main_ai_validation.md',
                     'docs/decisions/travel_workflow_sync.md', 'templates/decision_proposal.md'):
            source = ROOT / name
            for target in re.findall(r'\]\(([^)]+)\)', source.read_text()):
                if '://' in target or target.startswith('#'):
                    continue
                with self.subTest(source=name, target=target):
                    self.assertTrue((source.parent / target.split('#')[0]).exists())

    def test_native_and_plugin_entry_points_are_wired(self):
        self.assertIn('prompts/decision_review.md', (ROOT / 'AGENTS.md').read_text())
        skill = ROOT / 'plugins/research-assistant/skills/research-assistant/SKILL.md'
        self.assertIn('references/orchestrator.md', skill.read_text())
        self.assertTrue((skill.parent / 'references/orchestrator.md').exists())


if __name__ == '__main__':
    unittest.main()
