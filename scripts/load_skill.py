#!/usr/bin/env python3
"""Read one installed Skill for the current main agent; never launch a model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_role import bootstrap


def load_skill(project, name):
    installer = bootstrap()
    project = installer.installation_root(project)
    status = installer.check(project)
    if status['errors']:
        raise ValueError('installation needs setup')
    roles = {role['id']: source for role, source, _ in installer.catalog()}
    if name not in roles:
        raise ValueError('unknown Skill')
    relative = '.claude/skills/' + name
    source = roles[name]
    manifest = installer.validate_installation_manifest(installer.load_json(
        installer.checked_target(project, '.claude/agent-workflows/installation.json')))
    expected = installer._installed_text(source, 'SKILL.md')
    path = installer.checked_skill_link(project, relative)
    if relative in manifest.get('skill_copies', {}):
        content = installer._installed_text(project, relative + '/SKILL.md')
        if content != expected:
            raise ValueError('installed Skill changed after check')
    else:
        if not path.is_symlink() or path.resolve() != source:
            raise ValueError('installed Skill link changed after check')
        content = expected
    return {'schema_version': 1, 'execution_mode': 'single-main', 'launched': False,
            'project_root': str(project), 'skill': name,
            'source': str(path / 'SKILL.md'), 'content': content}


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--skill', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(load_skill(args.project, args.skill), ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print('Skill load rejected: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
