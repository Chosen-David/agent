"""Interpretation controls for package navigation, not production-code claims."""
from pathlib import Path
import tempfile
import unittest

try:
    from .markdown_links import local_markdown_links, package_markdown_targets
except ImportError:
    from markdown_links import local_markdown_links, package_markdown_targets


class MarkdownLiteralTests(unittest.TestCase):
    def links(self, text):
        return list(local_markdown_links(text))

    def test_backtick_and_tilde_fenced_examples_are_not_navigation(self):
        text = ('[before](before.md)\n\n```markdown\n'
                '- [ ] [DOC-01] Goal ([详情](task_details/DOC-01.md))\n'
                '> [quoted-looking code](not-a-file.md)\n```\n'
                '~~~text\n[also example](absent.md)\n~~~\n[after](after.md)\n')
        self.assertEqual(self.links(text), ['before.md', 'after.md'])

    def test_fence_close_uses_matching_marker_and_minimum_length(self):
        text = ('````md\n[example](one.md)\n```\n[still example](two.md)\n'
                '~~~~\n[still code](three.md)\n`````\n[real](real.md)\n')
        self.assertEqual(self.links(text), ['real.md'])

    def test_inline_literals_and_different_length_delimiters(self):
        text = ('`[example](one.md)` and ``[example with ` tick](two.md)`` '
                'and [real `code label`](real.md)')
        self.assertEqual(self.links(text), ['real.md'])

    def test_escaped_backticks_do_not_hide_live_links(self):
        self.assertEqual(self.links(r'\`[real](real.md)\`'), ['real.md'])
        # Two backslashes do not escape the delimiter; this is a code span.
        self.assertEqual(self.links(r'\\`[example](not-a-file.md)`'), [])

    def test_unmatched_inline_backticks_do_not_hide_live_links(self):
        self.assertEqual(self.links('`literal [real](real.md)'), ['real.md'])
        self.assertEqual(self.links('``literal [real](real.md)`'), ['real.md'])

    def test_inline_literals_cannot_swallow_another_paragraph(self):
        self.assertEqual(self.links('`unmatched\n\n[real](real.md) `'), ['real.md'])

    def test_prose_quotes_and_blockquotes_are_still_navigation(self):
        self.assertEqual(self.links('"[quoted](quoted.md)"\n> [quote](quote.md)\n'),
                         ['quoted.md', 'quote.md'])

    def test_quoted_code_fences_are_literals_but_following_links_live(self):
        text = ('> ```md\n> [example](absent.md)\n> ```\n'
                '> [live](live.md)\n\n> ```md\n> [code](also-absent.md)\n'
                '[outside quote](outside.md)\n')
        self.assertEqual(self.links(text), ['live.md', 'outside.md'])

    def test_titles_fragments_images_and_external_links(self):
        text = ('[file](file.md#section "title") ![image](<my%20image.svg>) '
                '[anchor](#part) [web](https://example.com/missing.md) '
                '[mail](mailto:a@example.com) [network](//example.com/file.md)')
        self.assertEqual(self.links(text), ['file.md', 'my image.svg'])


class PackageClosureControls(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='markdown-closure-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / 'skill'
        self.package.mkdir()
        self.source = self.package / 'SKILL.md'
        (self.package / 'real.md').write_text('Real dependency.\n')
        (self.root / 'outside.md').write_text('Exists, but outside package.\n')

    def targets(self, text):
        self.source.write_text(text, encoding='utf-8')
        return list(package_markdown_targets(self.source, self.package))

    def test_literal_missing_examples_are_ignored_and_real_dependency_checked(self):
        text = ('`[example](missing.md)`\n\n```markdown\n'
                '[example](task_details/DOC-01.md)\n```\n[real](real.md)\n')
        self.assertEqual(self.targets(text), [self.package / 'real.md'])
        (self.package / 'real.md').unlink()
        with self.assertRaisesRegex(ValueError, 'file missing'):
            self.targets(text)

    def test_real_missing_file_still_fails(self):
        with self.assertRaisesRegex(ValueError, 'file missing'):
            self.targets('[real dependency](missing.md)')

    def test_real_existing_outside_file_still_fails(self):
        with self.assertRaisesRegex(ValueError, 'leaves package'):
            self.targets('[real dependency](../outside.md)')

    def test_symlink_outside_package_still_fails(self):
        (self.package / 'alias.md').symlink_to(self.root / 'outside.md')
        with self.assertRaisesRegex(ValueError, 'leaves package'):
            self.targets('[real dependency](alias.md)')

    def test_ordinary_quotes_and_escaped_ticks_cannot_hide_missing_dependency(self):
        for text in ('"[real](missing.md)"', '> [real](missing.md)', r'\`[real](missing.md)\`'):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, 'file missing'):
                self.targets(text)


if __name__ == '__main__':
    unittest.main()
