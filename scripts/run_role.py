#!/usr/bin/env python3
"""Dispatch an installed role once, using host inventory or the host default.

An optional trusted executable accepts JSON on stdin: operation=inventory is
read-only; operation=run owns the authenticated agent/tool loop. No shell eval.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from agent_runtime.context_serialization import render_context
from agent_runtime.external_json import load_json, strict_json
from agent_runtime.model_routing import EMPTY_INVENTORY, dispatch, resolve, validate_inventory


def bootstrap():
    spec = importlib.util.spec_from_file_location('agent_bootstrap', REPO / 'setup.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def role_definition(project, role, policy):
    if role not in policy['roles']:
        raise ValueError('unknown role')
    if role in ('planner-main', 'review-main'):
        text = (project / '.claude/agent-workflows' / (role.replace('-', '_') + '.md')).read_text()
    else:
        text = (project / '.claude/agents' / ('agent-' + role + '.md')).read_text()
        text = text.split('---', 2)[2].strip()
        skill = project / '.claude/skills' / role / 'SKILL.md'
        text += '\n\nSkill source (resolve its references relative to this directory): ' + str(skill) + '\n' + skill.read_text()
    # Never load the installed agent's pinned model when falling back. The
    # invocation-local definition overrides any project-level agent setting.
    return {'description': 'Run the assigned ' + role + ' task', 'prompt': text, 'model': 'inherit'}


def adapter_inventory(command, project, timeout=10):
    request = {'schema_version': 1, 'operation': 'inventory', 'project_root': str(project)}
    # Keep host diagnostic/credential output out of reports. Bound readback and
    # time; the adapter must also bound its own subprocesses and provider calls.
    with tempfile.TemporaryFile() as output:
        completed = subprocess.run(command, input=json.dumps(request).encode(), stdout=output,
                                   stderr=subprocess.DEVNULL, cwd=project, timeout=timeout, check=False)
        output.seek(0)
        data = output.read(1024 * 1024 + 1)
    if completed.returncode or len(data) > 1024 * 1024:
        raise ValueError('adapter inventory unavailable')
    return validate_inventory(strict_json(data))


def native_run(command, request, timeout):
    name = 'routed-' + request['role']
    argv = [*command, '-p', '--agents', json.dumps({name: request['definition']}, ensure_ascii=False),
            '--agent', name]
    if request['route']['model'] is not None:
        argv.extend(['--model', request['route']['model']])
    return subprocess.run(argv, input=request['prompt'], text=True, cwd=request['project_root'],
                          timeout=timeout, check=False).returncode


def adapter_run(command, request, timeout):
    return subprocess.run(command, input=json.dumps(request, ensure_ascii=False), text=True,
                          cwd=request['project_root'], timeout=timeout, check=False).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--compact', action='store_true', help='preserve all JSON fields without formatting whitespace')
    parser.add_argument('--role', required=True)
    parser.add_argument('--adapter', help='Explicit trusted executable; never loaded from model policy')
    parser.add_argument('--claude', default='claude', help='Native Claude CLI executable')
    parser.add_argument('--inventory', help='Explicit fresh host inventory JSON (cannot combine with --adapter)')
    parser.add_argument('--require', action='append', choices=('tools', 'vision'), default=[])
    parser.add_argument('--timeout', type=int, default=600, help='Task seconds; timeout does not trigger retry')
    parser.add_argument('--dry-run', action='store_true', help='Offline route preview; no adapter/model calls')
    args = parser.parse_args()
    if args.inventory and args.adapter:
        parser.error('choose --inventory or --adapter')
    if not 1 <= args.timeout <= 86400:
        parser.error('--timeout must be between 1 and 86400')
    try:
        project = Path(args.project).resolve()
        installer = bootstrap()
        status = installer.check(project)
        if status['errors']:
            raise ValueError('installation needs setup; run setup.py --check')
        directory = project / '.claude/agent-workflows'
        policy = load_json(directory / 'model-policy.json')
        inventory = validate_inventory(load_json(args.inventory) if args.inventory else
                                       load_json(directory / 'installation.json').get('model_inventory', EMPTY_INVENTORY))
        definition = role_definition(project, args.role, policy)
        command = [str(Path(args.adapter).resolve())] if args.adapter else None
        if command and not args.dry_run:
            try:
                inventory = adapter_inventory(command, project)
            except (OSError, ValueError, subprocess.TimeoutExpired):
                inventory = EMPTY_INVENTORY
                print('Model inventory unavailable; using host default before task launch.', file=sys.stderr)
        route = resolve(policy, args.role, inventory,
                        adapter_available=command is not None and not args.dry_run, requires=args.require)
        if args.dry_run:
            print((render_context(route, compact=True) if args.compact else json.dumps(route, ensure_ascii=False, indent=2)))
            return 0
        prompt = sys.stdin.read(1024 * 1024 + 1)
        if not prompt.strip() or len(prompt.encode('utf-8')) > 1024 * 1024:
            raise ValueError('provide a nonempty task on stdin, at most 1 MiB')
        print((render_context({'selected_route': route}, compact=True) if args.compact else json.dumps({'selected_route': route}, ensure_ascii=False)), file=sys.stderr)
        request = {'schema_version': 1, 'project_root': str(project), 'role': args.role,
                   'definition': definition, 'prompt': prompt}
        _, code = dispatch(policy, args.role, inventory, request,
                           native=lambda r: native_run([args.claude], r, args.timeout),
                           adapter=(lambda r: adapter_run(command, r, args.timeout)) if command else None,
                           requires=args.require)
        return code
    except subprocess.TimeoutExpired:
        print('Task timed out; effects may have occurred. No fallback or retry was launched.', file=sys.stderr)
        return 124
    except (OSError, ValueError):
        print('Role dispatch failed; check installation, role, inventory and executable. No task retry.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
