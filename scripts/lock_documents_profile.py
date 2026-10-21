#!/usr/bin/env python3
"""Refresh the explicit documents wheel lock from PyPI; never installs packages."""
import argparse
from email.parser import BytesParser
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile


def build(wheelhouse):
    entries = []
    for path in sorted(Path(wheelhouse).glob('*.whl')):
        with zipfile.ZipFile(path) as archive:
            metadata = BytesParser().parsebytes(archive.read(next(
                n for n in archive.namelist() if n.endswith('.dist-info/METADATA'))))
            wheel = BytesParser().parsebytes(archive.read(next(
                n for n in archive.namelist() if n.endswith('.dist-info/WHEEL'))))
        name, version = metadata['Name'], metadata['Version']
        name = {'pillow': 'Pillow', 'typing_extensions': 'typing-extensions',
                'xlsxwriter': 'XlsxWriter'}.get(name, name)
        with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{version}/json', timeout=30) as response:
            release = json.load(response)
        remote = next(item for item in release['urls'] if item['filename'] == path.name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != remote['digests']['sha256']:
            raise ValueError(f'PyPI hash mismatch: {path.name}')
        entries.append(dict(name=name, version=version, filename=path.name,
                            tags=wheel.get_all('Tag'), sha256=digest, url=remote['url'],
                            license=metadata['License-Expression'] or metadata['License'] or
                            release['info'].get('license') or
                            {'Jinja2': 'BSD-3-Clause', 'markdown-it-py': 'MIT',
                             'mdurl': 'MIT'}.get(name, 'See distribution license'),
                            requires_dist=metadata.get_all('Requires-Dist', [])))
    return dict(schema_version='documents-profile/v1', profile='documents-linux-cp312-v1',
                python='3.12', system='Linux', machine='x86_64', glibc_min='2.28', packages=entries)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('wheelhouse')
    args = parser.parse_args()
    print(json.dumps(build(args.wheelhouse), ensure_ascii=False, indent=2))
