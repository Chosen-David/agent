#!/usr/bin/env python3
"""Verify archived artifacts and rehydrate pinned Git snapshots; no model calls."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('archive', type=Path)
p.add_argument('--repo', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--runner', type=Path, required=True)
a = p.parse_args()
a.out.mkdir(parents=True, exist_ok=False)
with tarfile.open(a.archive, 'r:gz') as archive:
    for item in archive:
        name = PurePosixPath(item.name)
        if name.is_absolute() or '..' in name.parts or not item.isfile():
            raise ValueError('archive must contain only safe relative regular files')
        destination = a.out.joinpath(*name.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(archive.extractfile(item).read())
spec = importlib.util.spec_from_file_location('recorded_pipeline', a.runner.resolve())
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
reports = {}
for path in sorted(a.out.glob('*/manifest.json')):
    run = path.parent
    manifest = json.loads(path.read_text())
    for name, expected in manifest['snapshot_hashes'].items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('unsafe snapshot path')
        data = subprocess.check_output(['git', '-C', str(a.repo.resolve()), 'show',
                                        manifest['revision'] + ':' + name])
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError('pinned source hash mismatch: ' + name)
        target = run / 'snapshot' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    reports[run.name] = runner.report(run)
print(json.dumps(reports, ensure_ascii=False, indent=2))
if not reports or any(not value['complete'] for value in reports.values()):
    raise SystemExit(1)
