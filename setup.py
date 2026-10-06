#!/usr/bin/env python3
"""Project-scoped Claude Code bootstrap (not a setuptools package installer)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parent
BEGIN = '<!-- chosen-david-agent:begin -->'
END = '<!-- chosen-david-agent:end -->'


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=path.name + '.')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(text)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def block():
    return f'''{BEGIN}
## Chosen-David Agent Workflows

@.claude/agent-workflows/orchestrator.md

仓库位置见 `.claude/agent-workflows/installation.json` 的 repository。
主 AI 按导入的通用调度规则执行；其中 prompts/、workflows/、templates/、
config/、scripts/ 与 agent_runtime 均相对该仓库解析，项目输入和 TASK.md 相对当前项目。
根目录 TASK.md 是当前项目唯一活跃总清单；启动/恢复、委派前和逐任务结束都要读取。
用户手动要求编排时合并目标后走同一闭环；总清单由主 AI 串行维护，各 Agent 交接证据。
code-organization 同时管理文件：规划输出目录、产物清单和消费者引用，防止散落和覆盖。
主 AI 负责 Skills、工作 Agent、任务链、定时器及 tmux 监督器的配置、维护和恢复。
执行运行时 CLI 时从仓库目录启动，明确指定当前项目的绝对路径。
需要专业角色时按已安装的 Skill 和匹配的 agent-* 子 Agent 分配工作；简单任务直接处理。
每个结果都对照 TASK.md 的任务、数据、证据和剩余事项；全部可核验且可汇报才收尾。
遵循当前宿主权限和用户约束，不因导入规则而绕过权限。仓库文件存在不代表后台进程运行。
{END}'''


def merge_block(text):
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError('malformed managed block in CLAUDE.md; preserve and repair manually')
    if BEGIN in text:
        start, end = text.index(BEGIN), text.index(END) + len(END)
        if end < start:
            raise ValueError('invalid managed block ordering')
        return text[:start] + block() + text[end:]
    return text + ('\n\n' if text and not text.endswith('\n\n') else '') + block() + '\n'


def catalog():
    roles = json.loads((REPO / 'config/role_registry.json').read_text())['roles']
    result = []
    for role in roles:
        path = REPO / role['skill']
        text = path.read_text()
        match = re.search(r'^description:\s*(.+)$', text, re.M)
        if not match or not (path.parent / 'SKILL.md').is_file():
            raise ValueError('invalid skill: ' + role['id'])
        description = match[1].strip().strip('"')
        result.append((role, path.parent, description))
    return result


def agent_text(role, description):
    name = role['id']
    # JSON strings are also valid quoted YAML scalars; no extra YAML dependency.
    return f'''---
name: agent-{name}
description: {json.dumps(description, ensure_ascii=False)}
skills:
  - {name}
---

按预加载的 {name} Skill 执行主 AI 分配的任务。不得替换用户目标或扩大授权。
先核对交接中的 task_id、TASK.md requirement ID、输入、约束、依赖和验收。
读取 Skill 内 execution/workflow 等所需引用；保留具体数据、单位、日志和产物路径。
向主 AI 返回结论、真实证据、验收状态、未完成项与恢复条件。
不要自行声明全链完成；由主 AI 对照 TASK.md 汇总并维护 tmux 监督器。
'''


def expected_files():
    files = {'.claude/agent-workflows/orchestrator.md': (REPO / 'prompts/orchestrator.md').read_text()}
    links = {}
    for role, source, description in catalog():
        links['.claude/skills/' + role['id']] = str(source)
        files['.claude/agents/agent-' + role['id'] + '.md'] = agent_text(role, description)
    return files, links


def checked_target(target, relative):
    path = target / relative
    if path.is_symlink() or not path.parent.resolve().is_relative_to(target):
        raise ValueError('managed file or parent redirects outside target: ' + relative)
    return path


def install(target):
    target = Path(target).resolve()
    files, links = expected_files()
    manifest_path = checked_target(target, '.claude/agent-workflows/installation.json')
    previous = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if previous and previous.get('repository') != str(REPO):
        raise ValueError('target belongs to another checkout; uninstall that installation first')
    # Preflight all conflicts before changing any files.
    for relative, text in files.items():
        path = checked_target(target, relative)
        if path.exists() and path.read_text() != text:
            if sha(path.read_text()) != previous.get('files', {}).get(relative):
                raise ValueError('preserving existing or locally edited file: ' + relative)
    for relative, source in links.items():
        path = target / relative
        if not path.parent.resolve().is_relative_to(target):
            raise ValueError('skill parent outside project')
        if os.path.lexists(path) and not (path.is_symlink() and path.resolve() == Path(source)):
            raise ValueError('preserving existing skill: ' + relative)
    claude = checked_target(target, 'CLAUDE.md')
    task_file = checked_target(target, 'TASK.md')
    old = claude.read_text() if claude.exists() else ''
    merged = merge_block(old)
    for relative, text in files.items():
        atomic_text(target / relative, text)
    for relative, source in links.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not os.path.lexists(path):
            path.symlink_to(source, target_is_directory=True)
    atomic_text(claude, merged)
    if not task_file.exists():
        atomic_text(task_file, '# 项目任务\n\n'
                    '这是当前项目唯一总任务清单，由主 AI 统一维护。\n'
                    '尚未填写已授权任务；收到用户目标后保留原始要求，拆解为带稳定 ID 的任务与验收。\n'
                    '主 AI 在启动/恢复、委派前、逐任务结束和最终汇报前读取本文件。\n'
                    '各 Agent 交接 task_refs、产物、数据与证据；高频状态放 .agent-runs/<run_id>/。\n\n'
                    '条目格式示例（非待执行任务）：\n\n```text\n'
                    '- [ ] [T1] 用户指定的目标\n  - 验收：实际可核对的条件。\n```\n')
    commit = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
                            capture_output=True, text=True, check=False).stdout.strip()
    manifest = {'schema_version': 1, 'repository': str(REPO), 'commit': commit,
                'files': {name: sha(text) for name, text in files.items()}, 'links': links}
    atomic_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return check(target)


def check(target):
    target = Path(target).resolve()
    files, links = expected_files()
    errors = []
    manifest_path = target / '.claude/agent-workflows/installation.json'
    try:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('repository') != str(REPO):
            errors.append('installation belongs to a different checkout')
    except (OSError, ValueError):
        errors.append('installation manifest missing/invalid')
    for relative, expected in files.items():
        path = target / relative
        if not path.is_file() or path.read_text() != expected:
            errors.append('missing/stale managed file: ' + relative)
    for relative, expected in links.items():
        path = target / relative
        if not path.is_symlink() or path.resolve() != Path(expected) or not (path / 'SKILL.md').is_file():
            errors.append('missing/broken skill link: ' + relative)
    claude = target / 'CLAUDE.md'
    if not claude.is_file() or block() not in claude.read_text():
        errors.append('main AI entry not connected')
    if not (target / 'TASK.md').is_file():
        errors.append('project-root TASK.md missing')
    return {'status': 'configured' if not errors else 'needs_setup', 'target': str(target),
            'skills': len(links), 'subagents': len(links), 'errors': errors,
            'capabilities': {'python': sys.version.split()[0], 'claude_cli': shutil.which('claude'),
                             'tmux': shutil.which('tmux'), 'model_auth': 'not_checked',
                             'supervisor': 'not_started', 'host_adapter': 'project_specific'},
            'next': 'Start/restart Claude Code in target, inspect /memory and /agents, then load TASK.md.'}


def uninstall(target):
    target = Path(target).resolve()
    manifest_path = checked_target(target, '.claude/agent-workflows/installation.json')
    manifest = json.loads(manifest_path.read_text())
    expected, links = expected_files()
    if manifest.get('repository') != str(REPO):
        raise ValueError('installation belongs to a different checkout')
    preserved = []
    for relative, fingerprint in manifest['files'].items():
        if relative not in expected:
            raise ValueError('unexpected managed path')
        path = checked_target(target, relative)
        if path.is_file() and sha(path.read_text()) == fingerprint:
            path.unlink()
        elif path.exists():
            preserved.append(relative)
    for relative, source in manifest['links'].items():
        if relative not in links:
            raise ValueError('unexpected managed link')
        path = target / relative
        if not path.parent.resolve().is_relative_to(target):
            raise ValueError('skill parent outside project')
        if path.is_symlink() and path.resolve() == Path(source):
            path.unlink()
        elif os.path.lexists(path):
            preserved.append(relative)
    claude = checked_target(target, 'CLAUDE.md')
    if claude.exists():
        text = claude.read_text()
        if block() in text:
            atomic_text(claude, text.replace(block(), '', 1))
        elif BEGIN in text:
            preserved.append('CLAUDE.md modified managed block')
    manifest_path.unlink()
    return {'status': 'uninstalled', 'preserved_local_edits': preserved}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', default='.', help='Claude project directory, default current directory')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='read-only installation/host check')
    group.add_argument('--uninstall', action='store_true', help='remove only owned, unmodified generated files')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10+ required')
    try:
        result = check(args.target) if args.check else uninstall(args.target) if args.uninstall else install(args.target)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'setup blocked: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('errors'):
        sys.exit(2)


if __name__ == '__main__':
    main()
