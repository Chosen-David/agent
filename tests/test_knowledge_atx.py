"""Raw ATX boundaries, not a full Markdown/inline renderer conformance suite."""
import unittest

from agent_runtime.knowledge_index import sections


# None means not a heading; titles retain raw inline syntax deliberately.
CASES = [
    ('# C#', 'C#', 1),
    ('## foo###', 'foo###', 2),
    ('# foo #', 'foo', 1),
    ('# foo\t### \t', 'foo', 1),
    ('# foo \\#', 'foo \\#', 1),
    ('## foo #\\##', 'foo #\\##', 2),
    ('# foo ### bar', 'foo ### bar', 1),
    ('# foo\u00a0#', 'foo\u00a0#', 1),
    ('# foo #\u00a0', 'foo #\u00a0', 1),
    ('#\u00a0foo', None, 0),
    ('#\u2003foo', None, 0),
    ('# \u00a0foo\u00a0', '\u00a0foo\u00a0', 1),
    ('#', '', 1),
    ('## \t', '', 2),
    ('### ###', '', 3),
    ('######', '', 6),
    ('####### foo', None, 0),
    ('#foo', None, 0),
    ('    # foo', None, 0),
    ('   ### foo ###', 'foo', 3),
    ('\t# foo', None, 0),
    ('#\tfoo', 'foo', 1),
    ('\\# foo', None, 0),
    ('# *raw* \\*inline\\*', '*raw* \\*inline\\*', 1),
]


def expected_single(content, title, level):
    return [{'node': 'intro' if title is None else 's1',
             'title': 'Document' if title is None else title,
             'level': level, 'start_line': 1, 'parent': None,
             'end_line': 1, 'text': content}]


class AtxBoundaryTests(unittest.TestCase):
    def test_raw_heading_boundary_matrix(self):
        for source, title, level in CASES:
            for ending in ('', '\n', '\r\n'):
                with self.subTest(source=source, ending=ending):
                    content = source + ending
                    self.assertEqual(sections({'title': 'Document', 'content': content}),
                                     expected_single(content, title, level))

    def test_empty_heading_hierarchy_and_fenced_literal(self):
        content = '# C#\nroot\n##\nchild\n```\n### hidden#\n```\n# End #\n'
        expected = [
            {'node': 's1', 'title': 'C#', 'level': 1, 'start_line': 1,
             'parent': None, 'end_line': 2, 'text': '# C#\nroot\n'},
            {'node': 's2', 'title': '', 'level': 2, 'start_line': 3,
             'parent': 's1', 'end_line': 7,
             'text': '##\nchild\n```\n### hidden#\n```\n'},
            {'node': 's3', 'title': 'End', 'level': 1, 'start_line': 8,
             'parent': None, 'end_line': 8, 'text': '# End #\n'},
        ]
        actual = sections({'title': 'Document', 'content': content})
        self.assertEqual(actual, expected)
        self.assertEqual(''.join(n['text'] for n in actual), content)

    def test_long_whitespace_and_hash_runs(self):
        for raw, title in [('#' + ' ' * 10000 + 'tail', 'tail'),
                           ('# foo ' + '#' * 10000 + 'x', 'foo ' + '#' * 10000 + 'x'),
                           ('# foo ' + '#' * 10000 + '\t' * 10000, 'foo')]:
            with self.subTest(length=len(raw)):
                self.assertEqual(sections({'title': 'Document', 'content': raw}),
                                 expected_single(raw, title, 1))


if __name__ == '__main__':
    unittest.main()
