#!/usr/bin/env python3
"""Deprecated role runner: offline routing diagnostics only.

Use scripts/load_skill.py to read a Skill in the current main agent. Historical
host helper functions remain import-compatible; this CLI never launches them.
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
DEFAULT_REQUEST_BYTES = 128 * 1024
sys.path.insert(0, str(REPO))
from agent_runtime.context_serialization import render_context
from agent_runtime.external_json import load_json, strict_json
from agent_runtime.model_routing import EMPTY_INVENTORY, dispatch, resolve, validate_inventory


def bootstrap():
    spec = importlib.util.spec_from_file_location('agent_bootstrap', REPO / 'setup.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def role_definition(project, role, policy, *, installer=None):
    installer = installer if installer is not None else bootstrap()
    manifest = installer.validate_installation_manifest(load_json(
        installer.checked_target(project, '.claude/agent-workflows/installation.json')))
    inventory = validate_inventory(manifest.get('model_inventory', EMPTY_INVENTORY))
    files, links = installer.expected_files(inventory)
    expected_policy = json.loads(files['.claude/agent-workflows/model-policy.json'])
    if json.dumps(policy, sort_keys=True) != json.dumps(expected_policy, sort_keys=True):
        raise ValueError('installed role policy changed after setup check')
    if role not in expected_policy['roles']:
        raise ValueError('unknown role')

    def managed_text(relative):
        text = installer._installed_text(project, relative)
        if text != files[relative]:
            raise ValueError('installed role definition changed after setup check')
        return text

    if role in ('planner-main', 'review-main'):
        text = managed_text('.claude/agent-workflows/' + role.replace('-', '_') + '.md')
    else:
        text = managed_text('.claude/agents/agent-' + role + '.md')
        text = text.split('---', 2)[2].strip()
        relative = '.claude/skills/' + role
        skill_root = installer.checked_skill_link(project, relative)
        source = Path(links[relative])
        expected_skill = installer._installed_text(source, 'SKILL.md')
        if relative in manifest.get('skill_copies', {}):
            skill_text = installer._installed_text(project, relative + '/SKILL.md')
            if skill_text != expected_skill:
                raise ValueError('installed Skill changed after setup check')
        else:
            if not skill_root.is_symlink() or skill_root.resolve() != source:
                raise ValueError('installed Skill link changed after setup check')
            # Use the accepted source snapshot, not a second read through the alias.
            skill_text = expected_skill
        skill = skill_root / 'SKILL.md'
        text += '\n\nSkill source (resolve its references relative to this directory): ' + str(skill) + '\n' + skill_text
    # The host default must override any installed pinned-model setting.
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
    return subprocess.run(argv, input=request['prompt'].encode('utf-8'), cwd=request['project_root'],
                          timeout=timeout, check=False).returncode


def adapter_run(command, request, timeout):
    return subprocess.run(command, input=json.dumps(request, ensure_ascii=False, separators=(',', ':')).encode('utf-8'),
                          cwd=request['project_root'], timeout=timeout, check=False).returncode


class RoleInputError(ValueError):
    pass


def check_request(request, max_bytes, *, max_tokens=None, counter=None):
    """Bound the canonical local request, including instructions and route.

    Host-added context, tools and provider billing are outside this boundary.
    Never truncate instructions or a task to make a budget appear satisfied.
    """
    wire = json.dumps(request, ensure_ascii=False, separators=(',', ':'))
    if len(wire.encode('utf-8')) > max_bytes:
        raise RoleInputError('complete request exceeds --max-request-bytes; use file references or explicitly raise the limit')
    if max_tokens is not None:
        count = counter(wire)
        if type(count) is not int or count < 0:
            raise RoleInputError('token counter must return a nonnegative integer')
        if count > max_tokens:
            raise RoleInputError('complete request exceeds --max-input-tokens')


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    if hasattr(sys.stdin, 'reconfigure'):
        sys.stdin.reconfigure(newline='')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--compact', action='store_true', help='preserve all JSON fields without formatting whitespace')
    parser.add_argument('--role', required=True)
    parser.add_argument('--adapter', help='Explicit trusted executable; never loaded from model policy')
    parser.add_argument('--adapter-arg', action='append', default=[], help='Trusted adapter argument, e.g. a Python wrapper path')
    parser.add_argument('--claude', default='claude', help='Native Claude CLI executable')
    parser.add_argument('--claude-arg', action='append', default=[], help='Trusted native command argument, e.g. a Python wrapper path')
    parser.add_argument('--inventory', help='Explicit fresh host inventory JSON (cannot combine with --adapter)')
    parser.add_argument('--require', action='append', choices=('tools', 'vision'), default=[])
    parser.add_argument('--timeout', type=int, default=600, help='Task seconds; timeout does not trigger retry')
    parser.add_argument('--dry-run', action='store_true', help='Offline route preview; no adapter/model calls')
    parser.add_argument('--max-request-bytes', type=int, default=DEFAULT_REQUEST_BYTES,
                        help='Complete local request UTF-8 byte cap (default 131072); not a provider/session token budget')
    parser.add_argument('--max-input-tokens', type=int, help='Optional complete local request token cap; requires --tokenizer')
    parser.add_argument('--tokenizer', help='Explicit optional tiktoken encoding; never inferred from model name')
    args = parser.parse_args()
    if not args.dry_run:
        print('Single-main execution: load the Skill with scripts/load_skill.py in the current agent. No role launched.', file=sys.stderr)
        return 2
    if args.inventory and args.adapter:
        parser.error('choose --inventory or --adapter')
    if args.adapter_arg and not args.adapter:
        parser.error('--adapter-arg requires --adapter')
    if not 1 <= args.max_request_bytes <= 16 * 1024 * 1024:
        parser.error('--max-request-bytes must be between 1 and 16777216')
    if ((args.max_input_tokens is None) != (args.tokenizer is None) or
            args.max_input_tokens is not None and args.max_input_tokens < 1):
        parser.error('positive --max-input-tokens and --tokenizer must be supplied together')
    if not 1 <= args.timeout <= 86400:
        parser.error('--timeout must be between 1 and 86400')
    try:
        project = Path(args.project).resolve()
        installer = bootstrap()
        if installer.check(project)['errors']:
            raise ValueError('installation needs setup; run setup.py --check')
        directory = project / '.claude/agent-workflows'
        policy = load_json(directory / 'model-policy.json')
        inventory = validate_inventory(load_json(args.inventory) if args.inventory else
                                       load_json(directory / 'installation.json').get('model_inventory', EMPTY_INVENTORY))
        route = resolve(policy, args.role, inventory, adapter_available=False, requires=args.require)
        print(render_context(route, compact=True) if args.compact else json.dumps(route, ensure_ascii=False, indent=2))
        return 0
    except RoleInputError as exc:
        print(f'Role input rejected: {exc}. No task launched.', file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print('Task timed out; effects may have occurred. No fallback or retry was launched.', file=sys.stderr)
        return 124
    except (OSError, ValueError):
        print('Role dispatch failed; check installation, role, inventory and executable. No task retry.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
