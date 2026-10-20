import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLES = ('research-assistant', 'research-implement-optimize', 'code-organization')


class ConciseEngineeringTests(unittest.TestCase):
    def test_claude_uses_canonical_authority(self):
        text = (ROOT / 'CLAUDE.md').read_text()
        self.assertIn('\n@AGENTS.md\n', text)
        self.assertNotRegex(text, r'(?<!agent_)doc/')
        for path in ('AGENTS.md', 'prompts/orchestrator.md', 'SETUP.md'):
            self.assertIn(path, text)
            self.assertTrue((ROOT / path).is_file())
        self.assertLess(len(text.encode()), 2515)

    def test_existing_skills_reach_local_contract(self):
        for role in ROLES:
            root = ROOT / 'plugins/research-assistant/skills' / role
            text = (root / 'SKILL.md').read_text()
            self.assertIn('references/concise_engineering.md', text)
            ref = root / 'references/concise_engineering.md'
            self.assertTrue(ref.is_file())
            for link in re.findall(r'\]\(([^)#]+)', ref.read_text()):
                if not re.match(r'https?://', link):
                    self.assertTrue((ref.parent / link).exists(), link)

    def test_preservation_and_context_contract(self):
        text = (ROOT / 'workflows/concise_engineering.md').read_text()
        for requirement in ('SPDX', 'noqa', 'docstring', 'AGENTS.md',
                            'CLAUDE.md', 'agent_doc/guide/', '否定',
                            '证据', '冲突', '字符', '按需'):
            self.assertIn(requirement, text)
        self.assertIn('concise_engineering.md', (ROOT / 'AGENTS.md').read_text())


if __name__ == '__main__':
    unittest.main()
