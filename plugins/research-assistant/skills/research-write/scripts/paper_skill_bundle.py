#!/usr/bin/env python3
"""Offline access to pinned paper skills; never execute bundled helpers."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile

ASSETS = Path(__file__).resolve().parents[1] / 'assets/paper-skills'


def load(package, assets=ASSETS):
    record = json.loads((assets / 'sources.lock.json').read_text())['packages'][package]
    raw = (assets / record['archive']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != record['sha256']:
        raise ValueError('archive hash mismatch')
    result = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:*') as archive:
        for member in archive:
            name = PurePosixPath(member.name)
            if (not member.isfile() or name.is_absolute() or '..' in name.parts
                    or '\\' in member.name or str(name) != member.name
                    or member.name in result or member.size > 16 * 1024 * 1024):
                raise ValueError('unsafe archive member: ' + member.name)
            stream = archive.extractfile(member)
            with stream:
                data = stream.read()
            if hashlib.sha256(data).hexdigest() != record['members'].get(member.name):
                raise ValueError('member hash mismatch: ' + member.name)
            result[member.name] = data
    if set(result) != set(record['members']):
        raise ValueError('archive member inventory mismatch')
    return record, result


def extract(files, destination):
    destination = Path(destination).absolute()
    for candidate in (destination, destination.resolve()):
        parts = tuple(p.casefold() for p in candidate.parts)
        if any(parts[i] in ('agent_doc', 'doc') and parts[i + 1] == 'guide'
               for i in range(len(parts) - 1)):
            raise ValueError('human-only guide cannot be an extraction target')
    if not destination.parent.is_dir():
        raise ValueError('destination parent must already exist')
    # mkdir is the no-overwrite claim, including an existing empty directory.
    destination.mkdir()
    try:
        for name, data in files.items():
            path = destination / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                stream.write(data)
    except OSError as exc:
        raise ValueError('incomplete extraction retained at ' + str(destination)) from exc
    return destination


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('list', 'read', 'extract'))
    parser.add_argument('package', choices=('aris', 'nature-writing'))
    parser.add_argument('path', nargs='?')
    parser.add_argument('--prefix', default='')
    parser.add_argument('--start-line', type=int, default=1)
    parser.add_argument('--end-line', type=int)
    parser.add_argument('--dest', type=Path)
    args = parser.parse_args(argv)
    try:
        record, files = load(args.package)
        if args.action == 'list':
            print(json.dumps({'commit': record['commit'], 'paths': [p for p in files
                              if p.startswith(args.prefix)]}, ensure_ascii=False))
        elif args.action == 'read':
            if args.path not in files:
                raise ValueError('unknown bundled path')
            lines = files[args.path].decode('utf-8').splitlines(keepends=True)
            end = args.end_line if args.end_line is not None else len(lines)
            if args.start_line < 1 or end < args.start_line:
                raise ValueError('invalid line range')
            print(''.join(lines[args.start_line - 1:end]), end='')
        else:
            if args.dest is None:
                raise ValueError('extract requires --dest (new directory)')
            destination = extract(files, args.dest)
            print(json.dumps({'destination': str(destination), 'commit': record['commit'],
                              'files': len(files), 'executed_helpers': False}))
    except (OSError, ValueError, KeyError, UnicodeError, tarfile.TarError) as exc:
        parser.exit(1, 'paper skills: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
