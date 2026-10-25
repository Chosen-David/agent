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

from agent_runtime.external_json import load_json
from agent_runtime.model_routing import EMPTY_INVENTORY, routing_report, validate_inventory, validate_policy

REPO = Path(__file__).resolve().parent
BEGIN = '<!-- chosen-david-agent:begin -->'
END = '<!-- chosen-david-agent:end -->'



def installation_root(path):
    """Never reinterpret a human-only guide subtree as a writable new project."""
    path = Path(path).absolute()
    for candidate in (path, path.resolve()):
        parts = tuple(part.casefold() for part in candidate.parts)
        if any(parts[i] in ('doc', 'agent_doc') and parts[i + 1] == 'guide' for i in range(len(parts) - 1)):
            raise ValueError('Human-only agent_doc/guide cannot be an installer target')
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

简单、目标明确的任务直接完成，仅加载相关 Skill。普通低风险本地修复运行必要回归并汇报结果；不自动建立 DAG、第二 Agent、实验合同或 tmux 监督器。
复杂协作、长期运行或用户明确编排时，先读 `.claude/agent-workflows/orchestrator.md`，再按需读 planner_main.md 与 review_main.md；完整流程不预加载。
工作流源码位置见 `.claude/agent-workflows/installation.json` 的 repository；project_root 是当前项目。源码工具从仓库解析，项目输入和输出始终相对当前项目。
Project A 的指南、任务、建议和结果属于 Project A/agent_doc/；缺失时不回退到工作流库的历史文件。切换项目重新核对指南、任务、记忆和交接中的 project_root。
已核实人类 agent_doc/guide/GUIDE.md 是最高项目规划依据；AI 绝不创建、编辑、删除或移动 agent_doc/guide/ 内文件。
agent_doc/task/TASK.md 是唯一日期索引，关联方法/进度/证据在 agent_doc/task/task_details/*.md；已有内容和 Plan/Progress 边界保留。简单任务不另建文档体系。
agent_doc/advice/ 必须核验并记录 adopt/adapt/reject/defer 与理由，不能当授权；尊重当前宿主权限和用户约束。
实证依据按 Skill 的 references/result_reuse_workflow.md 检索 agent_doc/results/ 并核对适用条件；实验/测量/共享结果按 references/result_validation_workflow.md 独立 verify_experiment_result，原始数据保持 pending 直到 usable-with-scope。用户/指南要求和已建立的实验合同不得降格。
复杂任务的 planner-main/review-main、结果独立验收需要真实宿主支持；安装不启动模型或后台服务，缺后端不得把自审当独立批准。
角色模型/路由见 model-policy.json、model-routing.json；源码 scripts/run_role.py 仅使用可信宿主适配器，缺候选继承默认模型，执行失败不自动换模型重跑。
交付核对实际修改、必要检查和剩余事项；仓库文件存在不证明后台进程运行或模型已遵循规则。
{END}'''


def managed_block(text):
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError('malformed managed block in CLAUDE.md; preserve and repair manually')
    if BEGIN in text:
        start, end_marker = text.index(BEGIN), text.index(END)
        if end_marker <= start:
            raise ValueError('invalid managed block ordering')
        end = end_marker + len(END)
        return text[start:end]
    return None


def merge_block(text):
    existing = managed_block(text)
    if existing is not None:
        return text.replace(existing, block(), 1)
    return text + ('\n\n' if text and not text.endswith('\n\n') else '') + block() + '\n'


def catalog():
    roles = json.loads((REPO / 'config/role_registry.json').read_text(encoding='utf-8'))['roles']
    result = []
    for role in roles:
        path = REPO / role['skill']
        text = path.read_text(encoding='utf-8')
        match = re.search(r'^description:\s*(.+)$', text, re.M)
        if not match or not (path.parent / 'SKILL.md').is_file():
            raise ValueError('invalid skill: ' + role['id'])
        description = match[1].strip().strip('"')
        result.append((role, path.parent, description))
    return result


# Shared agent body — single source of truth for the 11-line instruction block
# generated into every agent-*.md by agent_text(). Keep in sync with the
# "扩展约定" section of prompts/orchestrator.md which documents this contract.
_AGENT_BODY = '''\
默认使用中文回复，除非用户用英文提问或明确要求英文。技术术语/代码/路径保留原文。
回复简洁直接，不废话不客套。代码注释精简，不写显而易见的注释。
按预加载的 {name} Skill 执行主 AI 分配的任务。不得替换用户目标或扩大授权。
先核对交接中的 task_id、agent_doc/task/TASK.md requirement ID、document_refs、输入、约束、依赖和验收。
普通低风险本地修复直接运行必要回归，不自动建立 DAG、第二 Agent 或实验合同。用户/指南要求和既有合同仍有效。
涉及规划实验/测量或复用实证结论时，才读 references/result_reuse_workflow.md 并检索 agent_doc/results/；与当前任务无关则跳过。
涉及项目文档写入或 task_details 维护时，才读 references/project_document_workflow.md；先核对人类指南和建议取舍，AI 永不写 agent_doc/guide/。
只维护分配给本角色的 task_details 详情和输出，不并发修改总清单；建议不构成授权。
按当前任务实际需要选择性读取 Skill 内 execution/workflow 等引用；短问答/简单任务不强制加载全文。
实验/测量数据须按 references/result_validation_workflow.md 经独立 verify_experiment_result；未通过不用于结论。
向主 AI 返回结论、真实证据、验收状态、未完成项与恢复条件。
不要自行声明全链完成；由主 AI 按任务范围汇总。仅向已存在且获授权的监督运行交接状态，不自动创建监督器。'''


def agent_text(role, description, model='inherit'):
    name = role['id']
    # JSON strings are also valid quoted YAML scalars; no extra YAML dependency.
    return f'''---
name: agent-{name}
description: {json.dumps(description, ensure_ascii=False)}
model: {json.dumps(model)}
skills:
  - {name}
---

{_AGENT_BODY.format(name=name)}'''


def expected_files(inventory=None):
    policy = validate_policy(load_json(REPO / 'config/role_model_policy.json'))
    report = routing_report(policy, inventory)
    files = {'.claude/agent-workflows/orchestrator.md': (REPO / 'prompts/orchestrator.md').read_text(encoding='utf-8')}
    for name, value in (('model-policy', policy), ('model-routing', report)):
        files['.claude/agent-workflows/' + name + '.json'] = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    for profile in ('planner_main', 'review_main'):
        files['.claude/agent-workflows/' + profile + '.md'] = (REPO / ('prompts/' + profile + '.md')).read_text(encoding='utf-8')
    files['.claude/agent-workflows/dual_main_workflow.md'] = (REPO / 'workflows/dual_main_workflow.md').read_text(encoding='utf-8')
    links = {}
    for role, source, description in catalog():
        links['.claude/skills/' + role['id']] = str(source)
        route = report['routes'][role['id']]
        files['.claude/agents/agent-' + role['id'] + '.md'] = agent_text(role, description, route['model'] or 'inherit')
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


def skill_snapshot(path, *, follow_directory_links=False):
    """Fingerprint copied bytes; only source trees may follow directory aliases."""
    if path.is_symlink() or not path.is_dir():
        raise ValueError('skill copy is not a regular directory: ' + str(path))
    result = {}
    ancestors = set()

    def visit(directory):
        try:
            resolved_directory = directory.resolve()
        except RuntimeError as error:
            raise ValueError('cyclic directory symbolic link: ' + str(directory)) from error
        if resolved_directory in ancestors:
            raise ValueError('cyclic directory symbolic link: ' + str(directory))
        ancestors.add(resolved_directory)
        for child in sorted(directory.iterdir()):
            if child.name in ('__pycache__', '.DS_Store') or child.name.endswith('.pyc'):
                continue
            relative = child.relative_to(path).as_posix()
            try:
                resolved = child.resolve() if child.is_symlink() else child
            except RuntimeError as error:
                raise ValueError('cyclic symbolic link inside skill copy: ' + str(child)) from error
            if child.is_symlink() and not resolved.exists():
                raise ValueError('broken symbolic link inside skill copy: ' + str(child))
            if resolved.is_file():
                result[relative] = hashlib.sha256(resolved.read_bytes()).hexdigest()
            elif resolved.is_dir():
                if child.is_symlink() and not follow_directory_links:
                    raise ValueError('directory symbolic link inside skill copy: ' + str(child))
                result[relative + '/'] = ''
                visit(child)
            else:
                raise ValueError('unsupported skill entry: ' + str(child))

        ancestors.remove(resolved_directory)

    visit(path)
    return result


def replace_skill_copy(path, source, previous, expected):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent, prefix='.skill-') as stage:
        staged = Path(stage) / 'new'
        shutil.copytree(source, staged, symlinks=False,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        # Bind the materialized generation, even if the source changed back.
        if skill_snapshot(staged) != expected:
            raise ValueError('skill source changed during copy: ' + str(source))
        backup = Path(stage) / 'previous'
        if os.path.lexists(path):
            if path.is_symlink() or skill_snapshot(path) != previous:
                raise ValueError('preserving locally edited skill: ' + str(path))
            path.rename(backup)
        try:
            staged.rename(path)
        except OSError:
            if backup.exists():
                backup.rename(path)
            raise


def project_document_layout(target):
    """Read-only preflight; never create a second task list or touch guide files."""
    task = checked_target(target, 'agent_doc/task/TASK.md')
    directories = [checked_target(target, relative) for relative in
                   ('agent_doc/task/task_details', 'agent_doc/advice', 'agent_doc/guide', 'agent_doc/results')]
    for directory in directories:
        for candidate in (directory, *directory.parents):
            if candidate == target:
                break
            if candidate.exists() and not candidate.is_dir():
                raise ValueError('project document directory conflict: ' + str(candidate))
    if task.exists() and not task.is_file():
        raise ValueError('canonical task index is not a regular file: agent_doc/task/TASK.md')
    legacy = checked_target(target, 'TASK.md')
    if legacy.exists():
        if not legacy.is_file():
            raise ValueError('legacy TASK.md is not a regular file; preserve for review')
        if not task.exists():
            raise ValueError('Legacy TASK.md requires explicit migration first: '
                             'python scripts/project_docs.py --root PROJECT migrate --date YYYY-MM-DD')
        # A migrated root file may be a pointer, but never another checkbox list.
        if re.search(r'^\s*[-*+]\s+\[[ xX]\]', legacy.read_text(encoding='utf-8'), re.M):
            raise ValueError('Two active task lists; preserve and reconcile TASK.md and agent_doc/task/TASK.md')
    return task, directories


def _auto_discover_inventory(target):
    """Try auto-discovery only when there's a usable gateway in the environment.
    Returns None if discovery is not possible (caller falls back to previous/empty)."""
    from subprocess import run, TimeoutExpired
    discover_script = REPO / 'scripts' / 'discover_models.py'
    if not os.environ.get('ANTHROPIC_BASE_URL'):
        return None
    try:
        # Discovery precedes installer preflight; own no paths in the project.
        with tempfile.TemporaryDirectory(prefix='agent-model-discovery-') as directory:
            tmp = Path(directory) / 'inventory.json'
            result = run([sys.executable, str(discover_script), '--output', str(tmp)],
                         capture_output=True, text=True, cwd=str(target), timeout=30, check=False)
            if result.returncode != 0:
                return None
            return load_json(tmp)
    except (OSError, ValueError, TimeoutExpired):
        return None


def install(target, *, model_inventory=None, copy_skills=False):
    target = installation_root(target)
    manifest_path = checked_target(target, '.claude/agent-workflows/installation.json')
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    if previous and previous.get('repository') != str(REPO):
        raise ValueError('target belongs to another checkout; uninstall that installation first')
    if model_inventory is not None:
        inventory = validate_inventory(model_inventory)
    elif previous.get('model_inventory') and previous['model_inventory'].get('models'):
        inventory = validate_inventory(previous['model_inventory'])
    else:
        discovered = _auto_discover_inventory(target)
        inventory = validate_inventory(discovered) if discovered else EMPTY_INVENTORY
    files, links = expected_files(inventory)
    previous_copies = previous.get('skill_copies', {})
    copies = {}
    # Preflight all conflicts before changing any files.
    for relative, text in files.items():
        path = checked_target(target, relative)
        if path.exists() and path.read_text(encoding='utf-8') != text:
            if sha(path.read_text(encoding='utf-8')) != previous.get('files', {}).get(relative):
                raise ValueError('preserving existing or locally edited file: ' + relative)
    for relative, source in links.items():
        path = checked_skill_link(target, relative)
        linked = path.is_symlink() and path.resolve() == Path(source)
        if relative in previous_copies:
            if not path.is_dir() or path.is_symlink() or skill_snapshot(path) != previous_copies[relative]:
                raise ValueError('preserving locally edited skill: ' + relative)
        elif os.path.lexists(path) and not linked:
            raise ValueError('preserving existing skill: ' + relative)
        # Preserve established links; new Windows installs do not require admin
        # or Developer Mode. Explicit copies are also useful for Unix deployments.
        if not linked and (copy_skills or os.name == 'nt' or relative in previous_copies):
            copies[relative] = skill_snapshot(Path(source), follow_directory_links=True)
    claude = checked_target(target, 'CLAUDE.md')
    task_file, document_directories = project_document_layout(target)
    old = claude.read_text(encoding='utf-8') if claude.exists() else ''
    existing_block = managed_block(old)
    owned_block_hash = previous.get('managed_block_sha256')
    if previous and existing_block is None:
        raise ValueError('preserving locally removed managed block in CLAUDE.md')
    if existing_block is not None:
        if owned_block_hash is not None and sha(existing_block) != owned_block_hash:
            raise ValueError('preserving locally edited managed block in CLAUDE.md')
        if previous and owned_block_hash is None and existing_block != block():
            raise ValueError('legacy managed block cannot be safely updated; preserve and reinstall manually')
        if not previous and existing_block != block():
            raise ValueError('preserving existing unmanaged block in CLAUDE.md')
    merged = merge_block(old)
    for relative, text in files.items():
        atomic_text(target / relative, text)
    for relative, source in links.items():
        path = checked_skill_link(target, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        if relative in copies:
            if copies[relative] != previous_copies.get(relative):
                replace_skill_copy(path, source, previous_copies.get(relative), copies[relative])
        elif not os.path.lexists(path):
            path.symlink_to(source, target_is_directory=True)
    atomic_text(claude, merged)
    # mkdir is the only initialization permitted in human-owned agent_doc/guide/.
    for directory in document_directories:
        directory.mkdir(parents=True, exist_ok=True)
    if not task_file.exists():
        atomic_text(task_file, '# 项目任务\n\n'
                    '这是当前项目唯一日期任务索引，由主 AI 串行维护。\n'
                    '尚未填写已授权任务；收到用户目标后保留原始要求，按日期登记稳定 ID 与详情链接。\n'
                    '每项方法、验收、进度、证据与下一步由 AI 维护在 task_details/<ID>.md。\n'
                    '人类指南 agent_doc/guide/GUIDE.md 只读；建议 agent_doc/advice/ 须核验并记录取舍理由。\n'
                    '高频状态放 .agent-runs/<run_id>/，不另建活跃根 TASK.md。\n')
    commit = subprocess.run(['git', '-C', str(REPO), 'rev-parse', 'HEAD'],
                            capture_output=True, text=True, check=False).stdout.strip()
    manifest = {'schema_version': 1, 'repository': str(REPO), 'project_root': str(target), 'commit': commit,
                'files': {name: sha(text) for name, text in files.items()}, 'links': links,
                'skill_copies': copies,
                'managed_block_sha256': sha(block()),
                'model_inventory': inventory}
    atomic_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return check(target)


def check(target):
    target = installation_root(target)
    errors = []
    manifest = {}
    manifest_path = target / '.claude/agent-workflows/installation.json'
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if not isinstance(manifest, dict):
            raise ValueError('invalid installation manifest')
        if manifest.get('repository') != str(REPO):
            errors.append('installation belongs to a different checkout')
        if manifest.get('project_root', str(target)) != str(target):
            errors.append('installation belongs to a different project')
    except (OSError, ValueError):
        manifest = {}
        errors.append('installation manifest missing/invalid')
    try:
        inventory = validate_inventory(manifest.get('model_inventory', EMPTY_INVENTORY))
    except ValueError:
        inventory = EMPTY_INVENTORY
        errors.append('invalid model inventory in installation manifest')
    files, links = expected_files(inventory)
    for relative, expected in files.items():
        path = target / relative
        if not path.is_file() or path.read_text(encoding='utf-8') != expected:
            errors.append('missing/stale managed file: ' + relative)
    for relative, expected in links.items():
        try:
            path = checked_skill_link(target, relative)
            if relative in manifest.get('skill_copies', {}):
                if (skill_snapshot(path) != manifest['skill_copies'][relative] or
                        manifest['skill_copies'][relative] != skill_snapshot(Path(expected), follow_directory_links=True)):
                    errors.append('missing/stale/edited skill copy: ' + relative)
            elif not path.is_symlink() or path.resolve() != Path(expected) or not (path / 'SKILL.md').is_file():
                errors.append('missing/broken skill link: ' + relative)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
    claude = target / 'CLAUDE.md'
    try:
        claude_text = claude.read_text(encoding='utf-8')
        existing_block = managed_block(claude_text)
        owned_block_hash = manifest.get('managed_block_sha256')
        if existing_block is None or block() != existing_block:
            errors.append('main AI entry not connected')
        if owned_block_hash is not None and (
                existing_block is None or sha(existing_block) != owned_block_hash):
            errors.append('CLAUDE.md managed block differs from installation manifest')
    except (OSError, ValueError) as exc:
        errors.append('main AI entry not connected: ' + str(exc))
    try:
        task_file, document_directories = project_document_layout(target)
        if not task_file.is_file():
            errors.append('canonical agent_doc/task/TASK.md missing')
        for directory in document_directories:
            if not directory.is_dir():
                errors.append('project document directory missing: ' + str(directory.relative_to(target)))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    return {'status': 'configured' if not errors else 'needs_setup', 'target': str(target),
            'skills': len(links), 'subagents': len(links), 'errors': errors,
            'skill_storage': 'copy' if manifest.get('skill_copies') else 'symlink',
            'model_routing': routing_report(load_json(REPO / 'config/role_model_policy.json'), inventory),
            'capabilities': {'python': sys.version.split()[0], 'claude_cli': shutil.which('claude'),
                             'tmux': shutil.which('tmux'), 'model_auth': 'not_checked',
                             'supervisor': 'not_started', 'host_adapter': 'project_specific'},
            'next': 'Start/restart Claude Code in target, inspect /memory and /agents, then read human guide, agent_doc/task/TASK.md, task details and assessed advice.'}


def uninstall(target):
    target = installation_root(target)
    manifest_path = checked_target(target, '.claude/agent-workflows/installation.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    # Check every removal loop's input before the first owned file is deleted.
    if (not isinstance(manifest, dict)
            or any(not isinstance(manifest.get(field), dict) for field in ('files', 'links'))
            or not isinstance(manifest.get('skill_copies', {}), dict)
            or any(not isinstance(value, str)
                   for field in ('files', 'links') for value in manifest[field].values())):
        raise ValueError('invalid installation manifest; no files removed')
    expected, links = expected_files()
    if manifest.get('repository') != str(REPO):
        raise ValueError('installation belongs to a different checkout')
    # Preflight every removal before deleting any owned file. A newly redirected
    # skills parent must never cause removals inside human-owned agent_doc/guide/.
    for relative in manifest['files']:
        if relative not in expected:
            raise ValueError('unexpected managed path')
        checked_target(target, relative)
    for relative in manifest['links']:
        if relative not in links:
            raise ValueError('unexpected managed link')
        checked_skill_link(target, relative)
    claude = checked_target(target, 'CLAUDE.md')
    claude_text = claude.read_text(encoding='utf-8') if claude.exists() else None
    existing_block = managed_block(claude_text) if claude_text is not None else None
    preserved = []
    for relative, fingerprint in manifest['files'].items():
        if relative not in expected:
            raise ValueError('unexpected managed path')
        path = checked_target(target, relative)
        if path.is_file() and sha(path.read_text(encoding='utf-8')) == fingerprint:
            path.unlink()
        elif path.exists():
            preserved.append(relative)
    for relative, source in manifest['links'].items():
        if relative not in links:
            raise ValueError('unexpected managed link')
        path = checked_skill_link(target, relative)
        if relative in manifest.get('skill_copies', {}):
            try:
                unchanged = skill_snapshot(path) == manifest['skill_copies'][relative]
            except (OSError, ValueError):
                unchanged = False
            if unchanged:
                shutil.rmtree(path)
            elif os.path.lexists(path):
                preserved.append(relative)
        elif path.is_symlink() and path.resolve() == Path(source):
            path.unlink()
        elif os.path.lexists(path):
            preserved.append(relative)
    if claude_text is not None:
        owned_block_hash = manifest.get('managed_block_sha256')
        if (existing_block is not None and
                ((owned_block_hash is not None and sha(existing_block) == owned_block_hash)
                 or (owned_block_hash is None and existing_block == block()))):
            atomic_text(claude, claude_text.replace(existing_block, '', 1))
        elif existing_block is not None:
            preserved.append('CLAUDE.md modified managed block')
    manifest_path.unlink()
    return {'status': 'uninstalled', 'preserved_local_edits': preserved}


def discover(target):
    """Discover into owned temporary storage, then run installer preflight."""
    target = installation_root(target)
    discover_script = REPO / 'scripts' / 'discover_models.py'
    with tempfile.TemporaryDirectory(prefix='agent-model-discovery-') as directory:
        inventory_path = Path(directory) / 'inventory.json'
        try:
            result = subprocess.run(
                [sys.executable, str(discover_script), '--output', str(inventory_path)],
                capture_output=True, text=True, cwd=str(target), timeout=30, check=False)
        except subprocess.TimeoutExpired as exc:
            raise ValueError('model discovery timed out after 30 seconds') from exc
        if result.returncode != 0:
            raise ValueError('model discovery failed: ' + result.stderr.strip())
        inventory = validate_inventory(load_json(inventory_path))
        return install(target, model_inventory=inventory)


def update_model_inventory(target, inventory):
    """Update owned model files and return whether their contents changed."""
    manifest_path = checked_target(target, '.claude/agent-workflows/installation.json')
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
        raise ValueError('invalid installation manifest')
    if manifest.get('repository') != str(REPO):
        raise ValueError('installation belongs to a different checkout')
    if manifest.get('project_root', str(target)) != str(target):
        raise ValueError('installation belongs to a different project')
    owned = manifest.get('files')
    if not isinstance(owned, dict) or any(
            not isinstance(name, str) or not isinstance(value, str) or
            re.fullmatch(r'[0-9a-f]{64}', value) is None for name, value in owned.items()):
        raise ValueError('invalid installation manifest file fingerprints')
    inventory = validate_inventory(inventory)
    expected, _ = expected_files(inventory)
    models = {name: text for name, text in expected.items()
              if name in ('.claude/agent-workflows/model-policy.json',
                          '.claude/agent-workflows/model-routing.json')
              or name.startswith('.claude/agents/')}
    # Complete preflight before the first write, including later agent conflicts.
    changed = False
    for name, text in models.items():
        path = checked_target(target, name)
        if name not in owned:
            raise ValueError('preserving model file without installation ownership: ' + name)
        previous = path.read_text(encoding='utf-8') if path.exists() else None
        if previous is not None and sha(previous) != owned[name]:
            raise ValueError('preserving locally edited model file: ' + name)
        changed = changed or previous != text
    for name, text in models.items():
        atomic_text(target / name, text)
    manifest['files'] = {**owned, **{name: sha(text) for name, text in models.items()}}
    manifest['model_inventory'] = inventory
    # Each write is atomic; this is not a multi-file transaction on I/O failure.
    atomic_text(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return changed


def doctor(target):
    """Diagnose and auto-fix common environment issues. Idempotent."""
    target = installation_root(target)
    report = check(target)
    fixes = []
    warnings = []
    configs_changed = False

    # 1. Auto-discover models if inventory is empty (only update model files)
    inventory = report.get('model_routing', {})
    routes = inventory.get('routes', {})
    fallback_count = sum(1 for r in routes.values() if r.get('fallback', False))
    manifest_path = target / '.claude/agent-workflows/installation.json'
    if fallback_count == len(routes) and routes and manifest_path.is_file():
        discovered = _auto_discover_inventory(target)
        if discovered:
            configs_changed = update_model_inventory(target, discovered)
            report = check(target)
            fixes.append(f'Auto-discovered {len(discovered["models"])} gateway models (was: all fallback)')
            fixes.append('Updated owned model files and installation inventory')

    # 2. Auto-source tmux config if running inside tmux
    if os.environ.get('TMUX'):
        tmux_conf = REPO / 'agent_runtime' / 'tmux.conf'
        if tmux_conf.is_file():
            try:
                r = subprocess.run(['tmux', 'source-file', str(tmux_conf)],
                                   capture_output=True, text=True, timeout=5, check=False)
            except (OSError, subprocess.TimeoutExpired) as exc:
                warnings.append(f'tmux source-file unavailable: {type(exc).__name__}')
            else:
                if r.returncode == 0:
                    fixes.append('Applied tmux.conf (mouse/clipboard/256color)')
                else:
                    warnings.append(f'tmux source-file failed: {r.stderr.strip()[:100]}')

    # 3. Check Python version
    py_ver = sys.version_info
    py_ok = py_ver >= (3, 9)

    report['doctor'] = {
        'fixes_applied': fixes,
        'warnings': warnings,
        'python_ok': py_ok,
        'python_version': sys.version.split()[0],
        'in_tmux': bool(os.environ.get('TMUX')),
        'needs_restart': configs_changed,
        'restart_scope': 'configuration changes made by this doctor call',
        'restart_hint': (
            'Agent configs updated. Restart Claude Code to load new agent model/language settings.'
            if configs_changed else
            'No agent configuration changed during this doctor call. Current session load state was not checked.'),
    }
    return report


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', default='.', help='Claude project directory, default current directory')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='read-only installation/host check')
    group.add_argument('--uninstall', action='store_true', help='remove only owned, unmodified generated files')
    group.add_argument('--discover', action='store_true',
                       help='Auto-discover gateway models via /v1/models and install with discovered inventory')
    group.add_argument('--doctor', action='store_true',
                       help='Auto-diagnose: discover models + source tmux + report health')
    parser.add_argument('--model-inventory', help='Explicit host-supported model metadata JSON; no credentials')
    parser.add_argument('--copy-skills', action='store_true', help='copy skills (Windows default); preserve existing links')
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        parser.error('Python 3.9+ required. Current: {}.{}'.format(*sys.version_info[:2]))
    if args.model_inventory and (args.check or args.uninstall or args.discover or args.doctor):
        parser.error('--model-inventory conflicts with --check/--uninstall/--discover/--doctor')
    if args.discover and (args.check or args.uninstall):
        parser.error('--discover is mutually exclusive with --check/--uninstall')
    try:
        if args.doctor:
            result = doctor(args.target)
        elif args.discover:
            result = discover(args.target)
        elif args.model_inventory:
            result = install(args.target, model_inventory=load_json(args.model_inventory), copy_skills=args.copy_skills)
        else:
            result = check(args.target) if args.check else uninstall(args.target) if args.uninstall else install(args.target, copy_skills=args.copy_skills)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'setup blocked: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get('errors'):
        sys.exit(2)


if __name__ == '__main__':
    main()
