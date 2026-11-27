import argparse
import json
import math
from pathlib import Path
import subprocess
import sys


def need(condition, message):
    if not condition:
        raise ValueError(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate(plan):
    need(isinstance(plan, dict), 'plan must be an object')
    need(isinstance(plan.get('example'), str) and plan['example'].strip(), '贯穿例子 missing')
    duration = plan.get('duration')
    need(number(duration) and duration > 0, 'duration must be positive seconds')
    for key in ('width', 'height'):
        need(type(plan.get(key)) is int and plan[key] > 0, key + ' must be positive pixels')
    scenes = plan.get('scenes')
    need(isinstance(scenes, list) and scenes, 'scenes missing')
    end = 0
    for scene in scenes:
        need(isinstance(scene, dict), 'scene must be an object')
        start, stop = scene.get('start'), scene.get('end')
        need(number(start) and number(stop) and abs(start - end) < 0.001
             and stop > start and stop <= duration, 'scene timing gap, overlap or bounds')
        for key in ('question', 'narration', 'visual_action'):
            need(isinstance(scene.get(key), str) and scene[key].strip(), key + ' missing')
        captions = scene.get('captions')
        need(isinstance(captions, list) and captions, 'captions missing')
        previous = start
        for caption in captions:
            need(isinstance(caption, dict), 'caption must be an object')
            a, b = caption.get('start'), caption.get('end')
            need(number(a) and number(b) and previous <= a < b <= stop,
                 'caption timing overlap or bounds')
            need(isinstance(caption.get('text'), str) and caption['text'].strip(), 'caption text missing')
            previous = b
        end = stop
    need(abs(end - duration) < 0.001, 'scenes do not cover duration')
    return plan


def check_media(plan, media):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format',
                             '-of', 'json', str(media)], capture_output=True, text=True,
                            encoding='utf-8', timeout=30)
    need(result.returncode == 0, 'ffprobe rejected media: ' + result.stderr[-500:])
    metadata = json.loads(result.stdout)
    streams = metadata.get('streams', [])
    videos = [s for s in streams if s.get('codec_type') == 'video']
    audio = [s for s in streams if s.get('codec_type') == 'audio']
    need(len(videos) == 1, 'exactly one video stream required')
    need(bool(audio), 'narration audio stream missing')
    video = videos[0]
    need((video.get('width'), video.get('height')) == (plan['width'], plan['height']),
         'video dimensions mismatch')
    for label, raw in [('container', metadata.get('format', {}).get('duration')),
                       ('video', video.get('duration')), ('audio', audio[0].get('duration'))]:
        need(raw is not None, label + ' duration unavailable')
        actual = float(raw)
        need(math.isfinite(actual) and abs(actual - plan['duration']) <= 0.25,
             label + ' duration mismatch')
    return metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('plan', type=Path)
    parser.add_argument('--media', type=Path, required=True)
    args = parser.parse_args()
    try:
        plan = validate(json.loads(args.plan.read_text(encoding='utf-8')))
        check_media(plan, args.media)
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status': 'rejected', 'reason': str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({'status': 'technical-pass', 'teaching_review': 'pending',
                      'scope': 'metadata and declared timeline only; listen and inspect rendered frames'}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
