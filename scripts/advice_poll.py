#!/usr/bin/env python3
"""Observe advice changes without loading full advice bodies into a model."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agent_runtime.advice_poll import _root, _safe, encode, observe_advice, validate_snapshot
from agent_runtime.project_docs import assert_ai_writable


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', required=True)
    p.add_argument('--baseline')
    p.add_argument('--baseline-sha256')
    p.add_argument('--snapshot-out', help='New project-relative .agent-runs path; never overwrites or acknowledges')
    a = p.parse_args(argv)
    try:
        root = _root(a.root)
        if bool(a.baseline) != bool(a.baseline_sha256):
            raise ValueError('baseline requires its independently supplied byte SHA256')
        baseline = None
        if a.baseline:
            path = _safe(root, root / a.baseline)
            if not path.is_file(): raise ValueError('baseline must be a regular file')
            with path.open('rb') as stream: raw = stream.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024 or hashlib.sha256(raw).hexdigest() != a.baseline_sha256:
                raise ValueError('baseline byte bound or SHA256 mismatch')
            baseline = json.loads(raw)
            validate_snapshot(root, baseline)
        navigation, snapshot = observe_advice(root, baseline)
        if a.snapshot_out:
            if (not a.snapshot_out.startswith('.agent-runs/') or
                    any(c in a.snapshot_out for c in ('\\', ':', '\x00')) or
                    any(x in ('', '.', '..') for x in a.snapshot_out.split('/'))):
                raise ValueError('snapshot-out must be a new project-relative .agent-runs file')
            path = assert_ai_writable(root, _safe(root, root / a.snapshot_out))
            if path.relative_to(root).parts[0] != '.agent-runs':
                raise ValueError('snapshot-out escaped .agent-runs')
            path.parent.mkdir(parents=True, exist_ok=True)
            _safe(root, path)
            with path.open('xb') as stream: stream.write(encode(snapshot))
            navigation['snapshot_ref'] = {'path': path.relative_to(root).as_posix(), 'sha256': navigation['inventory_sha256']}
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False)); return 1
    print(json.dumps(navigation, ensure_ascii=False, separators=(',', ':')))
    return 0


if __name__ == '__main__': raise SystemExit(main())
