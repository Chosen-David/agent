"""Offline installation and source-integrity checks, not paper-quality metrics."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'plugins/research-assistant/skills/research-write'
SCRIPT = SKILL / 'scripts/paper_skill_bundle.py'
spec = importlib.util.spec_from_file_location('paper_bundle', SCRIPT)
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


class PaperSkillBundleTests(unittest.TestCase):
    def test_pinned_packages_and_both_aris_host_variants(self):
        for package, license_name in [('aris', 'MIT License'), ('nature-writing', 'Apache License')]:
            record, files = bundle.load(package)
            self.assertEqual(len(record['commit']), 40)
            self.assertIn(license_name.encode(), files['LICENSE'])
            if package == 'aris':
                for prefix in ('skills/', 'skills/skills-codex/'):
                    for phase in ('paper-writing', 'paper-plan', 'paper-figure', 'paper-write',
                                  'paper-compile', 'auto-paper-improvement-loop'):
                        self.assertIn(prefix + phase + '/SKILL.md', files)
                    self.assertIn(prefix + 'shared-references/reviewer-backends.md', files)
                self.assertIn('tools/reviewer_route.py', files)

    def test_nature_manifest_reference_closure(self):
        _, files = bundle.load('nature-writing')
        manifest = files['skills/nature-writing/manifest.yaml'].decode()
        paths = re.findall(r'(?:\.\./nature-shared/|static/|references/)[\w./-]+\.(?:md|yaml)', manifest)
        self.assertGreater(len(paths), 30)
        import posixpath
        for path in paths:
            self.assertIn(posixpath.normpath('skills/nature-writing/' + path), files)

    def test_extract_is_exact_and_never_overwrites_existing_target(self):
        _, files = bundle.load('nature-writing')
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / 'nature'
            bundle.extract(files, dest)
            for name, expected in files.items():
                self.assertEqual((dest / name).read_bytes(), expected)
            with self.assertRaises(FileExistsError):
                bundle.extract(files, dest)
            self.assertEqual((dest / 'LICENSE').read_bytes(), files['LICENSE'])
            empty = Path(temp) / 'empty'; empty.mkdir()
            with self.assertRaises(FileExistsError):
                bundle.extract(files, empty)

    def test_guide_targets_and_aliases_are_rejected_before_creation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); guide = root / 'agent_doc/guide'; guide.mkdir(parents=True)
            (root / 'alias').symlink_to(guide, target_is_directory=True)
            for dest in (guide / 'source', root / 'alias/source'):
                with self.assertRaisesRegex(ValueError, 'human-only'):
                    bundle.extract({'LICENSE': b'data'}, dest)
                self.assertFalse(dest.exists())

    def test_tampered_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            assets = Path(temp)
            (assets / 'sources.lock.json').write_bytes((bundle.ASSETS / 'sources.lock.json').read_bytes())
            (assets / 'nature-writing.tar.xz').write_bytes(b'not the original')
            with self.assertRaisesRegex(ValueError, 'archive hash'):
                bundle.load('nature-writing', assets)

    def test_unsafe_members_and_wrong_member_digest_are_rejected(self):
        for name, kind, digest in [('../escape', tarfile.REGTYPE, None),
                                   ('/absolute', tarfile.REGTYPE, None),
                                   ('link', tarfile.SYMTYPE, None),
                                   ('good', tarfile.REGTYPE, '0' * 64)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                assets = Path(temp); raw = io.BytesIO()
                with tarfile.open(fileobj=raw, mode='w:gz') as archive:
                    member = tarfile.TarInfo(name); member.type = kind
                    member.size = 1 if kind == tarfile.REGTYPE else 0
                    archive.addfile(member, io.BytesIO(b'x'))
                payload = raw.getvalue(); (assets / 'bad.tar.gz').write_bytes(payload)
                record = {'archive': 'bad.tar.gz', 'sha256': hashlib.sha256(payload).hexdigest(),
                          'members': {name: digest or hashlib.sha256(b'x').hexdigest()}}
                (assets / 'sources.lock.json').write_text(json.dumps({'packages': {'test': record}}))
                with self.assertRaisesRegex(ValueError, 'unsafe|member hash'):
                    bundle.load('test', assets)

    def test_real_setup_link_and_copy_keep_offline_bundle_callable(self):
        import setup
        for copied in (False, True):
            with self.subTest(copied=copied), tempfile.TemporaryDirectory() as temp:
                project = Path(temp) / 'project'; project.mkdir()
                original = 'user text\n'; (project / 'CLAUDE.md').write_text(original)
                setup.install(project, copy_skills=copied)
                installed = project / '.claude/skills/research-write'
                command = [sys.executable, str(installed / 'scripts/paper_skill_bundle.py')]
                response = subprocess.run(command + ['read', 'nature-writing', 'skills/nature-writing/SKILL.md'],
                                          cwd=project, capture_output=True, text=True, check=True)
                self.assertIn('name: nature-writing', response.stdout)
                subprocess.run(command + ['extract', 'aris', '--dest', str(project / 'aris')],
                               cwd=project, capture_output=True, check=True)
                self.assertTrue((project / 'aris/skills/skills-codex/paper-writing/SKILL.md').is_file())
                self.assertEqual(setup.check(project)['status'], 'configured')
                setup.uninstall(project)
                # Existing installer preserves user prose, retaining separator newlines.
                remaining = (project / 'CLAUDE.md').read_text()
                self.assertEqual(remaining.rstrip(), original.rstrip())
                self.assertNotIn(setup.BEGIN, remaining)
                self.assertTrue((project / 'aris/LICENSE').is_file())

    def test_cli_reports_bad_paths_and_line_ranges(self):
        for tail in [('missing',), ('skills/nature-writing/SKILL.md', '--start-line', '0')]:
            result = subprocess.run([sys.executable, str(SCRIPT), 'read', 'nature-writing', *tail],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('paper skills:', result.stderr)


if __name__ == '__main__':
    unittest.main()
