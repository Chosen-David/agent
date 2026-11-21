from tests.document_fixture import DocumentFixtureCase
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from comment_policy import violations


class CommentPolicyTests(DocumentFixtureCase):
    def test_added_comment_mutations_are_rejected(self):
        baseline = b"value = 1\n"
        self.assertEqual(violations(baseline, {1}), [])
        for source in (b"# explain workaround\nvalue = 1\n", b"value = 1 # explain workaround\n"):
            self.assertEqual(violations(source, {1, 2}), [1])

    def test_hash_in_strings_is_not_comment(self):
        self.assertEqual(violations(b'value = "# a value"\n', {1}), [])

    def test_required_directives_are_preserved(self):
        source = b"#!/usr/bin/env python3\n# coding: utf-8\n# SPDX-License-Identifier: MIT\n# Copyright 2026 Example\nvalue = 1 # noqa: F841\nother = 2 # type: ignore[assignment]\n"
        self.assertEqual(violations(source, set(range(1, 7))), [])

    def test_prose_cannot_hide_after_tool_directive(self):
        self.assertEqual(violations(b"value = 1 # noqa: F841 because workaround\n", {1}), [1])

    def test_existing_comments_are_not_mass_deleted(self):
        self.assertEqual(violations(b"# preserved historical rationale\nvalue = 2\n", {2}), [])

    def test_public_docstring_is_preserved(self):
        self.assertEqual(violations(b'def interface():\n    """Public API contract."""\n    return 1\n', {1, 2, 3}), [])

    def test_real_git_staged_unstaged_untracked_and_committed_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.check_output(["git", "-C", tmp, *args], stderr=subprocess.PIPE)
            git("init", "-q")
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            path = root / "sample.py"
            path.write_text("# historical rationale\nvalue = 1\n")
            git("add", ".")
            git("commit", "-qm", "baseline")
            base = git("rev-parse", "HEAD").decode().strip()
            def check(expected):
                result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("comment_policy.py")),
                    "--root", tmp, "--base", base], capture_output=True, text=True)
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
            check(0)
            path.write_text("# historical rationale\nvalue = 2 # newly explained\n")
            check(1)
            git("add", ".")
            check(1)
            git("commit", "-qm", "mutation")
            check(1)
            path.write_text("# historical rationale\nvalue = 2\n")
            check(0)
            (root / "new.py").write_text("# new explanation\n")
            check(1)
