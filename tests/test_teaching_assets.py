import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'plugins/research-assistant/skills/explain-research-concepts/scripts'


class TeachingAssetTests(unittest.TestCase):
    def run_tool(self, name, *args):
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS / name), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertIn(result.returncode, (0, 2), result.stderr)
        return result, json.loads(result.stdout)

    def test_real_html_entry_and_broken_asset_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            html = root / 'index.html'
            source = ('<!doctype html><html lang="zh-CN"><head><title>分片</title>'
                      '<meta name="viewport" content="width=device-width,initial-scale=1">'
                      '</head><body><h1>分片</h1><label for="p">参数量</label>'
                      '<input id="p" type="range"><button>复位</button><a href="#more">细节</a>'
                      '<details id="more"><summary>细节</summary>正文</details>'
                      '<video controls poster="poster.png"><source src="lesson.mp4" type="video/mp4">'
                      '<track kind="captions" src="captions.vtt" srclang="zh"></video>'
                      '<a href="narration.md">文字稿</a></body></html>')
            for name in ('poster.png', 'lesson.mp4', 'captions.vtt', 'narration.md'):
                (root / name).write_bytes(b'fixture')
            html.write_text(source, encoding='utf-8')
            result, payload = self.run_tool('check_page.py', html, '--offline', '--with-video')
            self.assertEqual(result.returncode, 0, payload)
            self.assertEqual(payload['status'], 'structural-pass')
            self.assertEqual(payload['visual_review'], 'pending')
            for old, new, reason in [
                ('poster.png', 'missing.png', 'missing local asset'),
                ('#more', '#absent', 'missing anchor'),
                ('<button>复位', '<button>', 'unlabelled button'),
                ('for="p"', 'for="wrong"', 'unlabelled control'),
                (' controls ', ' ', 'video controls missing'),
                ('src="captions.vtt"', 'src=""', 'empty asset URL'),
                ('poster.png', 'https://example.com/poster.png', 'remote offline asset'),
                ('lesson.mp4', '../outside.mp4', 'asset outside delivery root'),
            ]:
                html.write_text(source.replace(old, new), encoding='utf-8')
                result, payload = self.run_tool('check_page.py', html, '--offline', '--with-video')
                with self.subTest(reason=reason):
                    self.assertEqual(result.returncode, 2, payload)
                    self.assertIn(reason, payload['reason'])

    def test_data_uri_and_remote_navigation(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'index.html'
            source = ('<html lang="zh"><head><title>示例</title>'
                      '<meta name="viewport" content="width=device-width"></head><body>'
                      '<img alt="示意" src="data:image/png;base64,Zm9v">'
                      '<a href="https://docs.pytorch.org/">官方来源</a></body></html>')
            path.write_text(source, encoding='utf-8')
            result, payload = self.run_tool('check_page.py', path, '--offline')
            self.assertEqual(result.returncode, 0, payload)
            path.write_text(source.replace('<img alt=', '<a href="https://example.com/a.png">来源</a><img alt=').replace('data:image/png;base64,Zm9v', 'https://example.com/a.png'), encoding='utf-8')
            result, payload = self.run_tool('check_page.py', path, '--offline')
            self.assertEqual(result.returncode, 2)
            self.assertIn('remote offline asset', payload['reason'])
            path.write_text(source.replace('Zm9v', '!!!'), encoding='utf-8')
            result, payload = self.run_tool('check_page.py', path, '--offline')
            self.assertEqual(result.returncode, 2)
            self.assertIn('invalid data URI', payload['reason'])

    def test_original_figure_bytes_and_explanatory_mapping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            image = root / 'fig1.png'
            image.write_bytes(b'original-figure-fixture')
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            source = ('<html lang="zh"><head><title>读图</title><meta name="viewport" '
                      'content="width=device-width"></head><body><figure data-paper-figure="original" '
                      'data-source-url="https://example.org/paper" data-source-version="v1" '
                      'data-source-location="p.3 Fig.1" data-original-sha256="' + digest + '">'
                      '<img src="fig1.png" alt="原图" width="640" height="320">'
                      '<figcaption>Fig.1：比较三种方法</figcaption>'
                      '<dl data-figure-legend><dt>纵轴</dt><dd>成功率，百分比</dd></dl>'
                      '</figure></body></html>')
            page = root / 'index.html'
            page.write_text(source, encoding='utf-8')
            result, payload = self.run_tool('check_page.py', page, '--offline', '--paper-figures')
            self.assertEqual(result.returncode, 0, payload)
            self.assertEqual(payload['bound_original_figures'], 1)
            self.assertEqual(payload['figure_semantics'], 'pending')
            image.write_bytes(b'redrawn-not-original')
            result, payload = self.run_tool('check_page.py', page, '--offline', '--paper-figures')
            self.assertEqual(result.returncode, 2)
            self.assertIn('original figure digest mismatch', payload['reason'])
            image.write_bytes(b'original-figure-fixture')
            for before, after, reason in [
                ('data-source-version="v1"', '', 'figure source metadata missing'),
                ('<dd>成功率，百分比</dd>', '<dd></dd>', 'figure legend missing'),
                ('data-paper-figure="original"', 'data-paper-figure="reconstruction"', 'original paper figure missing'),
            ]:
                page.write_text(source.replace(before, after), encoding='utf-8')
                result, payload = self.run_tool('check_page.py', page, '--offline', '--paper-figures')
                with self.subTest(reason=reason):
                    self.assertEqual(result.returncode, 2, payload)
                    self.assertIn(reason, payload['reason'])

    def test_installed_package_routes_and_canonical_script_copy(self):
        skill = SCRIPTS.parent
        self.assertIn('scripts/narration_timeline.py', (skill / 'SKILL.md').read_text(encoding='utf-8'))
        self.assertIn('scripts/check_page.py', (skill / 'SKILL.md').read_text(encoding='utf-8'))
        for name in ('static_frontend_workflow.md', 'video_explanation_workflow.md'):
            self.assertTrue((skill / 'references' / name).is_file())
        twin = skill.parent / 'research-implement-optimize/scripts/check_page.py'
        self.assertEqual((SCRIPTS / 'check_page.py').read_bytes(), twin.read_bytes())

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'media backend unavailable')
    def test_recorded_duration_drives_timeline_and_rejects_bad_pauses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                'sine=frequency=440:duration=1.2', str(root / 'voice.wav')], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            source = dict(example='八卡分片', width=1280, height=720, segments=[dict(
                question='分给谁？', narration='每卡两块。', visual_action='色块分到四张卡',
                audio='voice.wav', lead_seconds=0.25, pause_seconds=0.8)] * 2)
            manifest = root / 'recordings.json'
            manifest.write_text(json.dumps(source), encoding='utf-8')
            result, payload = self.run_tool('narration_timeline.py', manifest, '--out', root / 'out')
            self.assertEqual(result.returncode, 0, payload)
            plan = json.loads((root / 'out/plan.json').read_text())
            self.assertAlmostEqual(plan['duration'], 4.5333333333)
            self.assertEqual(plan['scenes'][0]['captions'][0]['start'], 0.25)
            self.assertAlmostEqual(plan['scenes'][0]['captions'][0]['end'], 1.45)
            self.assertIn('00:00:00,250 --> 00:00:01,450', (root / 'out/subtitles.srt').read_text())
            self.assertEqual(payload['voice_review'], 'pending')
            source['segments'][0]['pause_seconds'] = -1
            manifest.write_text(json.dumps(source), encoding='utf-8')
            result, payload = self.run_tool('narration_timeline.py', manifest, '--out', root / 'bad')
            self.assertEqual(result.returncode, 2)
            self.assertIn('pause_seconds', payload['reason'])
            self.assertFalse((root / 'bad/plan.json').exists())


if __name__ == '__main__':
    unittest.main()
