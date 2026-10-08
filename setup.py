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



def installation_root(path):
    """Never reinterpret a human-only guide subtree as a writable new project."""
    path = Path(path).absolute()
    for candidate in (path, path.resolve()):
        parts = tuple(part.casefold() for part in candidate.parts)
        if any(parts[i:i + 2] == ('doc', 'guide') for i in range(len(parts) - 1)):
            raise ValueError('Human-only doc/guide cannot be an installer target')
    return path.resolve()


def atomic_text(path, text):
    installation_root(path)  # Also protect every resolved atomic write destination.
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

工作流源码位置见 `.claude/agent-workflows/installation.json` 的 repository；目标项目见 project_root。
Project A 的指南、任务、建议和结果全部属于 Project A/doc；仅维护工作流库自身时才使用该库的 doc。
缺少当前项目指南或任务不能回退到工作流库的 doc；调用源码目录中的 CLI 也不改变目标项目。
切换项目重新读取其指南、任务、项目记忆与证据；委派和恢复核对 project_root，不沿用上一项目约束。
受管复杂任务使用 planner-main 和独立新上下文 review-main；入口见 .claude/agent-workflows/planner_main.md 与 review_main.md。
安装不启动第二模型；缺真实宿主 reviewer/认证器时不得把自审当独立批准。
主 AI 按导入的通用调度规则执行；其中 prompts/、workflows/、templates/、
config/、scripts/、knowledge/ 与 agent_runtime 均相对该仓库解析，项目输入和 doc/task/TASK.md 相对当前项目。
doc/task/TASK.md 是当前项目唯一日期任务索引，详情 doc/task/task_details/*.md 由 AI 维护方法/进度/证据。
启动/恢复、委派前和逐任务结束先读人类指南、索引/详情及建议取舍；固定 Plan 与可追加 Progress 分开。
人类发布且来源已核实的 doc/guide/GUIDE.md 是最高项目规划依据；AI 绝不创建、编辑、删除或移动 doc/guide/ 内文件。
doc/advice/ 是人类/AI可编辑建议，必须核验并记录 adopt/adapt/reject/defer 与理由，不能当授权。
用户手动要求编排时合并目标后走同一闭环；总清单由主 AI 串行维护，各 Agent 交接证据。
code-organization 同时管理文件：规划输出目录、产物清单和消费者引用，防止散落和覆盖。
主 AI 负责 Skills、工作 Agent、任务链、定时器及 tmux 监督器的配置、维护和恢复。
执行运行时 CLI 时从仓库目录启动，明确指定当前项目的绝对路径。
需要专业角色时按已安装的 Skill 和匹配的 agent-* 子 Agent 分配工作；简单任务直接处理。
项目新指令先按 result_reuse_workflow.md 检索 doc/results/，核对代码/输入/配置/环境/指标及当前验证，再规划新增实验。
新数据进入 doc/results/<run_id>/；复用不跳过明确复现或必要独立验证。
每轮测试/实验数据须经独立 verify_experiment_result 节点后才能进入消费者/结论；失败或过期需修复重测。
通过仅代表 usable-with-scope，不能保证绝对无bug；角色读取包内 result_validation_workflow.md。
每个结果都对照 doc/task/TASK.md 的任务、数据、证据和剩余事项；全部可核验且可汇报才收尾。
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
先核对交接中的 task_id、doc/task/TASK.md requirement ID、document_refs、输入、约束、依赖和验收。
先读本 Skill 的 references/result_reuse_workflow.md，检索 doc/results/ 并核对适用条件和当前独立验证后再决定新增实验。
读取本 Skill 的 references/project_document_workflow.md；先核对人类指南和建议取舍，AI 永不写 doc/guide/。
只维护分配给本角色的 task_details 详情和输出，不并发修改总清单；建议不构成授权。
读取 Skill 内 execution/workflow 等所需引用；保留具体数据、单位、日志和产物路径。
测试/实验数据须按 references/result_validation_workflow.md 经独立 verify_experiment_result；未通过不用于结论。
向主 AI 返回结论、真实证据、验收状态、未完成项与恢复条件。
不要自行声明全链完成；由主 AI 对照 doc/task/TASK.md 汇总并维护 tmux 监督器。
'''


def expected_files():
    files = {'.claude/agent-workflows/orchestrator.md': (REPO / 'prompts/orchestrator.md').read_text()}
    for profile in ('planner_main', 'review_main'):
        files['.claude/agent-workflows/' + profile + '.md'] = (REPO / ('prompts/' + profile + '.md')).read_text()
    files['.claude/agent-workflows/dual_main_workflow.md'] = (REPO / 'workflows/dual_main_workflow.md').read_text()
    links = {}
    for role, source, description in catalog():
        links['.claude/skills/' + role['id']] = str(source)
        files['.claude/agents/agent-' + role['id'] + '.md'] = agent_text(role, description)
    return files, links


def checked_target(target, relative):
    path = target / relative
    if path.is_symlink() or not path.parent.resolve().is_relative_to(target):
        raise ValueError('managed file or parent redirects outside target: ' + relative)
    # Even an in-project alias could redirect a task write into human-only guide/.
    for parent in path.parents:
        if parent == target:
            break
        if parent.is_symlink():
            raise ValueError('managed parent is a symbolic link: ' + relative)
    return path



def checked_skill_link(target, relative):
    """Validate link parents without rejecting the intentionally linked leaf."""
    path = target / relative
    if not path.parent.resolve().is_relative_to(target):
        raise ValueError('skill parent outside project: ' + relative)
    for parent in path.parents:
        if parent == target:
            break
        if parent.is_symlink():
            raise ValueError('skill parent is a symbolic link: ' + relative)
    return path


def project_document_layout(target):
    """Read-only preflight; never create a second task list or touch guide files."""
    task = checked_target(target, 'doc/task/TASK.md')
    directories = [checked_target(target, relative) for relative in
                   ('doc/task/task_details', 'doc/advice', 'doc/guide', 'doc/results')]
    for directory in directories:
        for candidate in (directory, *directory.parents):
            if candidate == target:
                break
            if candidate.exists() and not candidate.is_dir():
                raise ValueError('project document directory conflict: ' + str(candidate))
    if task.exists() and not task.is_file():
        raise ValueError('canonical task index is not a regular file: doc/task/TASK.md')
    legacy = checked_target(target, 'TASK.md')
    if legacy.exists():
        if not legacy.is_file():
            raise ValueError('legacy TASK.md is not a regular file; preserve for review')
        if not task.exists():
            raise ValueError('Legacy TASK.md requires explicit migration first: '
                             'python scripts/project_docs.py --root PROJECT migrate --date YYYY-MM-DD')
        # A migrated root file may be a pointer, but never another checkbox list.
        if re.search(r'^\s*[-*+]\s+\[[ xX]\]', legacy.read_text(encoding='utf-8'), re.M):
            raise ValueError('Two active task lists; preserve and reconcile TASK.md and doc/task/TASK.md')
    return task, directories


def install(target):
    target = installation_root(target)
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
        path = checked_skill_link(target, relative)
        if os.path.lexists(path) and not (path.is_symlink() and path.resolve() == Path(source)):
            raise ValueError('preserving existing skill: ' + relative)
    claude = checked_target(target, 'CLAUDE.md')
    task_file, document_directories = project_document_layout(target)
    old = claude.read_text() if claude.exists() else ''
    merged = merge_block(old)
    for relative, text in files.items():
        atomic_text(target / relative, text)
    for relative, source in links.items():
        path = checked_skill_link(target, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        if not os.path.lexists(path):
            path.symlink_to(source, target_is_directory=True)
    atomic_text(claude, merged)
    # mkdir is the only initialization permitted in human-owned doc/guide/.
    for directory in document_directories:
        directory.mkdir(parents=True, exist_ok=True)
    if not task_file.exists():
        atomic_text(task_file, '# 项目任务\n\n'
                    '这是当前项目唯一日期任务索引，由主 AI 串行维护。\n'
                    '尚未填写已授权任务；收到用户目标后保留原始要求，按日期登记稳定 ID 与详情链接。\n'
                    '每项方法、验收、进度、证据与下一步由 AI 维护在 task_details/<ID>.md。\n'
                    '人类指南 doc/guide/GUIDE.md 只读；建议 doc/advice/ 须核验并记录取舍理由。\n'
                    '高频状态放 .agent-runs/<run_id>/，不另建活跃根 TASK.md。\n')
    commit = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
                            capture_output=True, text=True, check=False).stdout.strip()
    manifest = {'schema_version': 1, 'repository': str(REPO), 'project_root': str(target), 'commit': commit,
                'files': {name: sha(text) for name, text in files.items()}, 'links': links}
    atomic_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return check(target)


def check(target):
    target = installation_root(target)
    files, links = expected_files()
    errors = []
    manifest_path = target / '.claude/agent-workflows/installation.json'
    try:
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('repository') != str(REPO):
            errors.append('installation belongs to a different checkout')
        if manifest.get('project_root', str(target)) != str(target):
            errors.append('installation belongs to a different project')
    except (OSError, ValueError):
        errors.append('installation manifest missing/invalid')
    for relative, expected in files.items():
        path = target / relative
        if not path.is_file() or path.read_text() != expected:
            errors.append('missing/stale managed file: ' + relative)
    for relative, expected in links.items():
        try:
            path = checked_skill_link(target, relative)
            if not path.is_symlink() or path.resolve() != Path(expected) or not (path / 'SKILL.md').is_file():
                errors.append('missing/broken skill link: ' + relative)
        except ValueError as exc:
            errors.append(str(exc))
    claude = target / 'CLAUDE.md'
    if not claude.is_file() or block() not in claude.read_text():
        errors.append('main AI entry not connected')
    try:
        task_file, document_directories = project_document_layout(target)
        if not task_file.is_file():
            errors.append('canonical doc/task/TASK.md missing')
        for directory in document_directories:
            if not directory.is_dir():
                errors.append('project document directory missing: ' + str(directory.relative_to(target)))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    return {'status': 'configured' if not errors else 'needs_setup', 'target': str(target),
            'skills': len(links), 'subagents': len(links), 'errors': errors,
            'capabilities': {'python': sys.version.split()[0], 'claude_cli': shutil.which('claude'),
                             'tmux': shutil.which('tmux'), 'model_auth': 'not_checked',
                             'supervisor': 'not_started', 'host_adapter': 'project_specific'},
            'next': 'Start/restart Claude Code in target, inspect /memory and /agents, then read human guide, doc/task/TASK.md, task details and assessed advice.'}


def uninstall(target):
    target = installation_root(target)
    manifest_path = checked_target(target, '.claude/agent-workflows/installation.json')
    manifest = json.loads(manifest_path.read_text())
    expected, links = expected_files()
    if manifest.get('repository') != str(REPO):
        raise ValueError('installation belongs to a different checkout')
    # Preflight every removal before deleting any owned file. A newly redirected
    # skills parent must never cause removals inside human-owned doc/guide/.
    for relative in manifest['files']:
        if relative not in expected:
            raise ValueError('unexpected managed path')
        checked_target(target, relative)
    for relative in manifest['links']:
        if relative not in links:
            raise ValueError('unexpected managed link')
        checked_skill_link(target, relative)
    checked_target(target, 'CLAUDE.md')
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
        path = checked_skill_link(target, relative)
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
