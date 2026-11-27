import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/research-assistant/skills/explain-research-concepts/scripts/check_video.py'
spec = importlib.util.spec_from_file_location('video_check', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def plan():
    return dict(example='单位向量旋转', duration=2, width=320, height=180, scenes=[dict(
        start=0, end=2, question='长度变了吗？', narration='方向改变，长度保持。',
        visual_action='旋转箭头，保留单位圆', captions=[dict(start=0, end=2, text='长度不变')])])


class VideoExplanationTests(unittest.TestCase):
    def test_declared_timeline_controls(self):
        self.assertEqual(checker.validate(plan()), plan())
        for field in ('example', 'duration', 'width'):
            bad = plan()
            bad[field] = None
            with self.subTest(field=field), self.assertRaises(ValueError):
                checker.validate(bad)
        for field in ('question', 'narration', 'visual_action'):
            bad = plan()
            bad['scenes'][0][field] = ''
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                checker.validate(bad)

    def test_timing_faults_rejected(self):
        for value in (-1, 0.1, float('nan'), True):
            bad = plan()
            bad['scenes'][0]['start'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'scene timing'):
                checker.validate(bad)
        bad = plan()
        bad['scenes'][0]['captions'].append(dict(start=1, end=2, text='重叠'))
        with self.assertRaisesRegex(ValueError, 'caption timing'):
            checker.validate(bad)
        bad = plan()
        bad['scenes'][0]['captions'][0]['end'] = 3
        with self.assertRaisesRegex(ValueError, 'caption timing'):
            checker.validate(bad)

    def test_skill_routes_to_packaged_workflow(self):
        skill = SCRIPT.parents[1]
        self.assertIn('references/video_explanation_workflow.md', (skill / 'SKILL.md').read_text())
        reference = (skill / 'references/video_explanation_workflow.md').read_text()
        self.assertIn('teaching_review=pending', reference)
        self.assertIn('3Blue1Brown', reference)
        html = (skill / 'references/static_frontend_workflow.md').read_text()
        self.assertIn('video controls', html)
        self.assertIn('WebVTT', html)
        self.assertIn('references/static_frontend_workflow.md', (skill / 'SKILL.md').read_text())

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'media backend unavailable')
    def test_real_encoded_media_and_missing_audio_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = root / 'plan.json'
            manifest.write_text(json.dumps(plan(), ensure_ascii=False), encoding='utf-8')
            video = root / 'video.mp4'
            result = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                'testsrc2=size=320x180:rate=24:duration=2', '-f', 'lavfi', '-i',
                'sine=frequency=440:duration=2', '-c:v', 'mpeg4', '-c:a', 'aac',
                '-shortest', str(video)], capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            command = [sys.executable, '-B', str(SCRIPT), str(manifest), '--media']
            result = subprocess.run(command + [str(video)], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)['teaching_review'], 'pending')
            silent = root / 'silent.mp4'
            result = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-an',
                                     '-c:v', 'copy', str(silent)], capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run(command + [str(silent)], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertIn('audio stream missing', result.stdout)
            bad = copy.deepcopy(plan())
            bad['width'] = 640
            manifest.write_text(json.dumps(bad), encoding='utf-8')
            result = subprocess.run(command + [str(video)], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 2)
            self.assertIn('dimensions mismatch', result.stdout)


if __name__ == '__main__':
    unittest.main()
