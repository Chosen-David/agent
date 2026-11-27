import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

from check_video import need, number, validate


def timestamp(seconds, comma=False):
    ms = round(seconds * 1000)
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}{"," if comma else "."}{ms % 1000:03}'


def build(source, base, fps=30):
    need(isinstance(source, dict), 'recordings must be an object')
    need(type(fps) is int and 1 <= fps <= 120, 'fps must be 1..120')
    segments = source.get('segments')
    need(isinstance(segments, list) and segments, 'segments missing')
    scenes = []
    end = 0
    for segment in segments:
        need(isinstance(segment, dict), 'segment must be an object')
        for key in ('audio', 'question', 'narration', 'visual_action'):
            need(isinstance(segment.get(key), str) and segment[key].strip(), key + ' missing')
        lead, pause = segment.get('lead_seconds', 0.25), segment.get('pause_seconds', 0.8)
        for label, value in (('lead_seconds', lead), ('pause_seconds', pause)):
            need(number(value) and 0 <= value <= 30, label + ' must be 0..30 seconds')
        audio = (base / segment['audio']).resolve(strict=True)
        result = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_type:format=duration', '-of', 'json', str(audio)],
            capture_output=True, text=True, encoding='utf-8', timeout=30)
        need(result.returncode == 0, 'ffprobe rejected recording: ' + result.stderr[-300:])
        metadata = json.loads(result.stdout)
        need(bool(metadata.get('streams')), 'recording audio stream missing')
        duration = float(metadata.get('format', {}).get('duration', 'nan'))
        need(math.isfinite(duration) and duration > 0, 'recording duration invalid')
        stop = end + math.ceil((lead + duration + pause) * fps) / fps
        scenes.append(dict(start=end, end=stop, question=segment['question'],
            narration=segment['narration'], visual_action=segment['visual_action'],
            captions=[dict(start=end + lead, end=end + lead + duration, text=segment['narration'])]))
        end = stop
    return validate(dict(example=source.get('example'), width=source.get('width'),
                         height=source.get('height'), duration=end, scenes=scenes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('recordings', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--fps', type=int, default=30)
    args = parser.parse_args()
    try:
        plan = build(json.loads(args.recordings.read_text(encoding='utf-8')),
                     args.recordings.resolve().parent, args.fps)
        srt, vtt = [], ['WEBVTT', '']
        for index, scene in enumerate(plan['scenes'], 1):
            caption = scene['captions'][0]
            a, b, text = caption['start'], caption['end'], caption['text']
            srt.extend([str(index), f'{timestamp(a, True)} --> {timestamp(b, True)}', text, ''])
            vtt.extend([f'{timestamp(a)} --> {timestamp(b)}', text, ''])
        args.out.mkdir(parents=True, exist_ok=True)
        for name, content in [('plan.json', json.dumps(plan, ensure_ascii=False, indent=2)),
                              ('subtitles.srt', '\n'.join(srt)), ('subtitles.vtt', '\n'.join(vtt))]:
            (args.out / name).write_text(content, encoding='utf-8')
    except (ValueError, OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps(dict(status='rejected', reason=str(exc)), ensure_ascii=False))
        return 2
    print(json.dumps(dict(status='timeline-built', duration=plan['duration'],
        voice_review='pending', scope='recorded duration and explicit pauses; no speech-content or naturalness certification')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
