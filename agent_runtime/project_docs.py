"""Project document routing, dependency checks and application-level write guards.

The human-owned guide has highest *project* priority. Its filename is not proof
of authorship or authorization; the trusted host must resolve that from user
context. These guards do not sandbox a shell, editor or hostile filesystem owner.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
from urllib.parse import urlsplit

if __package__:
    from .context_serialization import ContextBudgetError, render_cli_context, render_context
else:
    from context_serialization import ContextBudgetError, render_cli_context, render_context
CANONICAL_TASK = 'agent_doc/task/TASK.md'
DOCUMENT_DIRECTORIES = ('agent_doc/task/task_details', 'agent_doc/advice', 'agent_doc/guide', 'agent_doc/results')
TASK_PATTERN = re.compile(r'^\s*[-*+] \[([ xX])\] \[([A-Za-z0-9][A-Za-z0-9_.-]*)\] (.+)$')
DATE_PATTERN = re.compile(r'^## (\d{4}-\d{2}-\d{2})(?:\s|$)')


class DocumentError(ValueError):
    """Document identity, ownership or dependency requires reconciliation."""


def initialize_project_docs(root):
    """Explicit project bootstrap, independent of workflow checkout or cwd.

    Preflight all layout conflicts before writing. Preserve existing files and
    create no human guide or fabricated task. This is not a filesystem transaction
    against hostile concurrent path changes.
    """
    supplied = Path(root).absolute()
    root = supplied.resolve()
    for candidate in (supplied, root):
        parts = tuple(part.casefold() for part in candidate.parts)
        if any(parts[i] in ('doc', 'agent_doc') and parts[i + 1] == 'guide' for i in range(len(parts) - 1)):
            raise DocumentError('human-only agent_doc/guide cannot be a project initialization target')
    if not root.is_dir():
        raise DocumentError('project root must be an existing directory')
    directories = [_relative(root, name) for name in DOCUMENT_DIRECTORIES]
    task = _relative(root, CANONICAL_TASK)
    assert_ai_writable(root, CANONICAL_TASK)
    for directory in directories:
        for candidate in (directory, *directory.parents):
            if candidate == root:
                break
            if candidate.exists() and not candidate.is_dir():
                raise DocumentError('project document directory conflict: ' + str(candidate))
    if task.exists() and not task.is_file():
        raise DocumentError('canonical task index must be a regular file')
    legacy = _relative(root, 'TASK.md')
    if legacy.exists():
        if not legacy.is_file():
            raise DocumentError('legacy task index must be a regular file')
        if not task.exists():
            raise DocumentError('legacy TASK.md requires explicit inspect/migrate before initialization')
        resolve_task_file(root)  # Reject two active lists; never silently choose.
    created = []
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(directory.relative_to(root).as_posix())
    try:
        # Exclusive creation preserves an index created by another process.
        with task.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write('# 项目任务\n\n'
                         '这是当前项目唯一日期任务索引；尚未填写已授权任务。\n'
                         'AI 按日期和稳定任务 ID 维护索引与 task_details，不导入工作流仓库历史任务。\n'
                         'agent_doc/guide/GUIDE.md 由人类自行编写；AI 不在 agent_doc/guide/ 创建任何文件。\n')
        created.append(CANONICAL_TASK)
    except FileExistsError:
        pass
    return {'status': 'initialized', 'project_root': str(root),
            'task_index': CANONICAL_TASK, 'created': created,
            'next': 'Read this project\'s human guide if present; register authorized tasks before dispatch. '
                    'Initialization alone does not establish a valid execution plan.'}


def _date(value):
    try:
        return dt.date.fromisoformat(value).isoformat()
    except (ValueError, TypeError):
        raise DocumentError('task dates must be YYYY-MM-DD') from None


def _relative(root, path):
    root = Path(root).resolve()
    path = Path(os.path.abspath(root / path))
    if not path.is_relative_to(root):
        raise DocumentError('document path outside project')
    for part in (path, *path.parents):
        if part == root:
            break
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(info.st_mode) or
                getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024)):
            raise DocumentError('document path must not contain symlinks or reparse points')
    return path


def regular_bytes(root, path, *, max_bytes=None):
    path = _relative(root, path)
    if max_bytes is not None and (type(max_bytes) is not int or max_bytes < 0):
        raise DocumentError('document byte bound must be a nonnegative integer')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise DocumentError('document must be a regular file')
            if max_bytes is not None and info.st_size > max_bytes:
                raise DocumentError(f'document exceeds {max_bytes} byte bound')
            data = stream.read() if max_bytes is None else stream.read(max_bytes + 1)
            if max_bytes is not None and len(data) > max_bytes:
                raise DocumentError(f'document exceeds {max_bytes} byte bound')
            return data
    finally:
        os.close(fd)


def regular_digest(root, path, *, max_bytes=None):
    """Hash exact regular-file bytes with bounded scratch space and growth checks."""
    path = _relative(root, path)
    if max_bytes is not None and (type(max_bytes) is not int or max_bytes < 0):
        raise DocumentError('document byte bound must be a nonnegative integer')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    try:
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                raise DocumentError('document must be a regular file')
            if max_bytes is not None and info.st_size > max_bytes:
                raise DocumentError('document exceeds byte bound')
            digest, size = hashlib.sha256(), 0
            while True:
                chunk = stream.read(65536 if max_bytes is None else min(65536, max_bytes-size+1))
                if not chunk:
                    return digest.hexdigest(), size
                size += len(chunk)
                if max_bytes is not None and size > max_bytes:
                    raise DocumentError('document exceeds byte bound')
                digest.update(chunk)
    finally:
        os.close(fd)


def parse_requirements(text, *, canonical=False):
    """Stable IDs outside fences; canonical records bind date and detail path."""
    items, fence, date = [], None, None
    for line in physical_lines(text):
        fence, marker = _fence_transition(line, fence)
        if marker:
            continue
        if fence:
            continue
        heading = DATE_PATTERN.match(line)
        if heading:
            date = _date(heading[1])
        match = TASK_PATTERN.match(line)
        if match:
            item = {'id': match[2], 'title': match[3], 'checked': match[1] != ' '}
            if canonical:
                link = re.fullmatch(r'(.+?) \(\[[^]\n]+\]\(task_details/([A-Za-z0-9][A-Za-z0-9_.-]*)\.md\)\)', item['title'])
                if date is None or link is None or link[2] != item['id']:
                    raise DocumentError('canonical TASK.md requires date headings and matching task_details/ID.md links')
                item.update(title=link[1], date=date, detail=f'task_details/{item["id"]}.md')
            items.append(item)
        elif re.match(r'^\s*[-*+] \[[ xX]\]', line):
            raise DocumentError('every TASK.md checkbox needs a stable [ID] and title')
    if not items or len({t['id'] for t in items}) != len(items):
        raise DocumentError('TASK.md requires nonempty, unique task IDs')
    return items


def resolve_task_file(root):
    """Legacy input is read-only compatibility, never a second active task list."""
    root = Path(root).resolve()
    canonical, legacy = _relative(root, CANONICAL_TASK), _relative(root, 'TASK.md')
    if canonical.exists():
        if legacy.exists():
            # Root pointer may remain for old links; it may not contain tasks.
            text = regular_bytes(root, legacy).decode('utf-8')
            if any(TASK_PATTERN.match(line) or re.match(r'^\s*[-*+] \[[ xX]\]', line)
                   for line in physical_lines(text)):
                raise DocumentError('dual active TASK.md lists; migrate/reconcile before execution')
        return canonical
    if legacy.exists():
        return legacy
    raise DocumentError('missing agent_doc/task/TASK.md (or unmigrated project-root TASK.md)')


def project_root_for_task(task_file):
    path = Path(os.path.abspath(task_file))
    if path.parts[-3:] == ('agent_doc', 'task', 'TASK.md'):
        return path.parents[2]
    return path.parent


def _inventory(root, directory, *, hashes=True):
    path = _relative(root, directory)
    if not path.exists():
        return {}
    if not path.is_dir():
        raise DocumentError(f'{directory} must be a directory')
    result = {}
    for parent, directories, files in os.walk(path, followlinks=False):
        for name in directories:
            _relative(root, Path(parent) / name)
        for name in files:
            item = Path(parent) / name
            item = _relative(root, item)
            result[item.relative_to(root).as_posix()] = regular_digest(root, item)[0] if hashes else None
    return dict(sorted(result.items()))


def snapshot_project_docs(root):
    root = Path(root).resolve()
    path = resolve_task_file(root)
    raw = regular_bytes(root, path)
    canonical = path == root / CANONICAL_TASK
    items = parse_requirements(raw.decode('utf-8'), canonical=canonical)
    details = {}
    if canonical:
        expected = {f'agent_doc/task/{item["detail"]}' for item in items}
        actual = set(_inventory(root, 'agent_doc/task/task_details', hashes=False))
        if actual != expected:
            raise DocumentError('task detail/index mismatch: missing or orphan detail files')
        for item in items:
            rel = f'agent_doc/task/{item["detail"]}'
            data = regular_bytes(root, rel)
            text = data.decode('utf-8').replace('\r\n', '\n')
            planning, _ = split_detail(text)
            if (_field_values(planning, 'Task-ID') != [item['id']] or
                    _field_values(planning, 'Date') != [item['date']]):
                raise DocumentError('task detail identity/date must match TASK.md: ' + item['id'])
            details[item['id']] = {'path': rel, 'sha256': hashlib.sha256(planning.encode('utf-8')).hexdigest()}
    return {'schema_version': 'project-documents/v1', 'layout': 'canonical' if canonical else 'legacy',
            'task_index': {'path': path.relative_to(root).as_posix(), 'sha256': hashlib.sha256(raw).hexdigest()},
            'task_details': details, 'guides': _inventory(root, 'agent_doc/guide'),
            'advice': _inventory(root, 'agent_doc/advice'), 'adopted_advice': {}}


def _field_values(text, name):
    prefix = name + ': '
    return [line[len(prefix):] for _, _, line in outside_fences(text) if line.startswith(prefix)]


def _field_once(text, name):
    """One optional non-authoritative derived field; multiple copies are ambiguous."""
    matches = _field_values(text, name)
    if len(matches) > 1:
        raise DocumentError('detail has multiple ' + name + ' fields')
    if not matches:
        return None
    return matches[0].strip() or None


def _plan_section(text, name):
    """Body of one `### name` plan section, stopping at the next heading."""
    start = None
    for a, b, line in outside_fences(text):
        if start is None:
            if line.rstrip(' \t') == '### ' + name:
                start = b
        elif re.match(r'^#{2,3} ', line):
            return text[start:a].strip() or None
    return text[start:].strip() or None if start is not None else None


def _progress_edges(text, limit):
    """Bounded document-order edges without inferring chronological order."""
    text = text.strip()
    if len(text) <= limit:
        return {'start': text, 'end': None, 'truncated': False}
    start_chars = (limit + 1) // 2
    end_chars = limit - start_chars
    return {'start': text[:start_chars], 'end': text[-end_chars:], 'truncated': True}


def task_navigation(root, *, max_chars=12000, progress_chars=64,
                    include_checked=False, progress_tail_chars=None, task_ids=None, summary_chars=None,
                    limit=None, after_id=None, expected_snapshot=None):
    """Cheap resume/navigation digest for unchecked index rows by default.

    Each selected row carries its detail's derived Status/Owner, `### 摘要`
    and bounded document-order edges of `## Progress`.  The edges deliberately
    make no chronological claim because existing details use both prepend and
    append conventions.  ``include_checked`` opts into historical rows; callers
    will usually also need a larger ``max_chars`` budget.

    Mirrors the tiered "capabilities (read-only minimal) vs full freeze" loading
    pattern: the main AI resumes/navigates from this digest and opens only the
    detail file it is actually advancing, instead of re-reading every full plan
    body on startup/resume/delegation. Derived fields are non-authoritative —
    Status/Owner never supersede the managed ledger or independent validation.
    """
    root = Path(root).resolve()
    index = resolve_task_file(root)
    if index != root / CANONICAL_TASK:
        raise DocumentError('task navigation requires the canonical task index')
    if type(max_chars) is not int or not 1 <= max_chars <= 200000:
        raise DocumentError('invalid navigation character budget')
    if progress_tail_chars is not None:
        if progress_chars != 64:
            raise DocumentError('use only one progress character bound')
        progress_chars = progress_tail_chars
    if type(progress_chars) is not int or not 2 <= progress_chars <= 100000:
        raise DocumentError('invalid progress character bound')
    if type(include_checked) is not bool:
        raise DocumentError('include_checked must be a boolean')
    if summary_chars is not None and (type(summary_chars) is not int or not 0 <= summary_chars <= 100000):
        raise DocumentError('invalid summary bound')
    index_raw = regular_bytes(root, index)
    items = parse_requirements(index_raw.decode('utf-8'), canonical=True)
    selected = items if include_checked else [item for item in items if not item['checked']]
    if task_ids is not None:
        if (not isinstance(task_ids, (list, tuple)) or not task_ids or
                any(type(x) is not str for x in task_ids) or len(set(task_ids)) != len(task_ids) or
                not set(task_ids) <= {x['id'] for x in selected}):
            raise DocumentError('task_ids must select unique available tasks')
        selected = [item for item in selected if item['id'] in task_ids]
    if limit is not None and (type(limit) is not int or not 1 <= limit <= 1000):
        raise DocumentError('invalid task page limit')
    if after_id is not None and (limit is None or expected_snapshot is None):
        raise DocumentError('task continuation requires limit and snapshot')
    if expected_snapshot is not None and (type(expected_snapshot) is not str or re.fullmatch('[0-9a-f]{64}', expected_snapshot) is None):
        raise DocumentError('invalid task snapshot')
    source_digest = hashlib.sha256(index_raw)
    tasks = []
    # Filter from the canonical index before opening details.  The default
    # digest intentionally does not validate omitted checked detail files.
    for item in selected:
        rel = f'agent_doc/task/{item["detail"]}'
        text = regular_bytes(root, rel).decode('utf-8').replace('\r\n', '\n')
        detail_raw = text.encode('utf-8')
        source_digest.update(len(detail_raw).to_bytes(8, 'big'))
        source_digest.update(detail_raw)
        planning, progress = split_detail(text)
        if (_field_values(planning, 'Task-ID') != [item['id']] or
                _field_values(planning, 'Date') != [item['date']]):
            raise DocumentError('task detail identity/date must match TASK.md: ' + item['id'])
        tasks.append({'id': item['id'], 'title': item['title'], 'date': item['date'],
                      'checked': item['checked'],
                      'status': _field_once(planning, 'Status'),
                      'owner': _field_once(planning, 'Owner'),
                      'summary': _plan_section(planning, '摘要'),
                      'progress_edges': _progress_edges(progress, progress_chars),
                      'detail': item['detail']})
    if summary_chars is not None:
        for task in tasks:
            summary = task['summary']
            if summary is not None:
                task['summary_source'] = {'chars': len(summary), 'sha256': hashlib.sha256(summary.encode('utf-8')).hexdigest(), 'truncated': len(summary) > summary_chars}
                task['summary'] = summary[:summary_chars]
    digest = {'schema_version': 'task-navigation/v2', 'project_root': str(root),
              'task_index': index.relative_to(root).as_posix(),
              'selection': 'all' if include_checked else 'unchecked',
              'total_tasks': len(items), 'selected_tasks': len(selected),
              'omitted_checked_tasks': 0 if include_checked else sum(item['checked'] for item in items),
              'tasks': tasks,
              'scope': 'derived navigation digest; unchecked is an index selection, not managed '
                       'active state; omitted checked details are not validated; Status/Owner/summary '
                       'do not replace ledger state, full document audit or independent verification; '
                       'progress edges are document positions with no newer/older guarantee'}
    if limit is not None:
        source_digest.update(json.dumps({'ids': [t['id'] for t in tasks], 'summary_chars': summary_chars, 'progress_chars': progress_chars}, sort_keys=True).encode())
        snapshot = source_digest.hexdigest()
        if expected_snapshot is not None and expected_snapshot != snapshot:
            raise DocumentError('task snapshot changed; restart navigation')
        start = 0
        if after_id is not None:
            position = next((i for i, t in enumerate(tasks) if t['id'] == after_id), None)
            if position is None:
                raise DocumentError('task cursor outside selection')
            start = position + 1
        page = tasks[start:start + limit]
        more = start + len(page) < len(tasks)
        digest.update(snapshot=snapshot, start=start, tasks=page, partial=more,
                      next_after_id=page[-1]['id'] if more and page else None)
    elif expected_snapshot is not None:
        raise DocumentError('snapshot requires task pagination')
    serialized = json.dumps(digest, ensure_ascii=False, separators=(',', ':'))
    if len(serialized) + len(os.linesep) > max_chars:
        raise DocumentError('task navigation exceeds character budget; narrow the digest')
    return digest


def _symmetric_diff(current, previous):
    current, previous = current or {}, previous or {}
    added = sorted(set(current) - set(previous))
    removed = sorted(set(previous) - set(current))
    changed = sorted(key for key in set(current) & set(previous) if current[key] != previous[key])
    return {'added': added, 'removed': removed, 'changed': changed}


def document_delta(current, refs):
    """Fine-grained change set between two project-documents/v1 snapshots.

    Resume/navigation uses this to re-read only changed guides/advice/details
    instead of the whole set — the receipt/remember-vs-recompute pattern. This
    is a symmetric diff over the frozen shape; it never validates a plan binding.
    """
    if not isinstance(current, dict) or not isinstance(refs, dict):
        raise DocumentError('document delta requires two project-documents/v1 snapshots')
    if (current.get('schema_version') != 'project-documents/v1' or
            refs.get('schema_version') != 'project-documents/v1'):
        raise DocumentError('document delta requires project-documents/v1 snapshots')
    layout_changed = current.get('layout') != refs.get('layout')
    task_index_changed = current.get('task_index') != refs.get('task_index')
    groups = {
        'task_details': _symmetric_diff(current.get('task_details'), refs.get('task_details')),
        'guides': _symmetric_diff(current.get('guides'), refs.get('guides')),
        'advice': _symmetric_diff(current.get('advice'), refs.get('advice')),
        'adopted_advice': _symmetric_diff(current.get('adopted_advice'), refs.get('adopted_advice')),
    }
    any_changed = (layout_changed or task_index_changed or
                   any(values['added'] or values['removed'] or values['changed']
                       for values in groups.values()))
    return {'schema_version': 'document-delta/v1', 'layout': {'before': refs.get('layout'),
            'after': current.get('layout'), 'changed': layout_changed},
            'task_index_changed': task_index_changed, 'task_details': groups['task_details'],
            'guides': groups['guides'], 'advice': groups['advice'],
            'adopted_advice': groups['adopted_advice'], 'any_changed': any_changed,
            'scope': 'symmetric SHA-level diff of document snapshots; unchanged entries need no re-read'}


def check_document_refs(root, refs):
    if not isinstance(refs, dict) or refs.get('schema_version') != 'project-documents/v1':
        raise DocumentError('project document dependency snapshot required')
    current = snapshot_project_docs(root)
    changed = [key for key in ('layout', 'task_index', 'guides') if current.get(key) != refs.get(key)]
    if not isinstance(refs.get('task_details'), dict) or any(
            current['task_details'].get(key) != value for key, value in refs.get('task_details', {}).items()):
        changed.append('task_details')
    if not isinstance(refs.get('adopted_advice'), dict) or any(
            current['advice'].get(key) != value for key, value in refs.get('adopted_advice', {}).items()):
        changed.append('adopted_advice')
    if changed:
        raise DocumentError('project documents changed (' + ', '.join(changed) + '); reconcile and version the plan')
    return current


def check_task_documents(root, task):
    refs = task.get('document_refs')
    if refs is None:
        if (Path(root) / CANONICAL_TASK).exists() or _inventory(Path(root).resolve(), 'agent_doc/guide'):
            raise DocumentError('task document dependencies missing; explicitly replan before execution')
        return None
    current = check_document_refs(root, refs)
    task_refs = task.get('task_refs', [])
    if current['layout'] == 'canonical' and (not task_refs or
            set(refs['task_details']) != set(task_refs) or
            any(ref not in current['task_details'] for ref in task_refs)):
        raise DocumentError('task detail planning dependencies omitted or outside task scope')
    ids = {item['id'] for item in parse_requirements(regular_bytes(root, resolve_task_file(root)).decode('utf-8'))}
    validate_guide_reviews(refs, refs.get('guide_reviews', []), ids)
    return current


def validate_advice_assessments(snapshot, assessments, task_ids):
    """Disposition is reasoning evidence only, never permission to act."""
    if not isinstance(assessments, list):
        raise DocumentError('advice_assessments must be a list')
    seen, adopted = set(), {}
    for item in assessments:
        if not isinstance(item, dict):
            raise DocumentError('invalid advice assessment')
        path = item.get('path')
        refs = item.get('task_refs')
        if (path not in snapshot['advice'] or path in seen or item.get('sha256') != snapshot['advice'][path]
                or item.get('disposition') not in ('adopt', 'adapt', 'reject', 'defer')
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()
                or not isinstance(refs, list) or not refs or not all(r in task_ids for r in refs)):
            raise DocumentError('advice assessment requires current hash, linked tasks, disposition and reason')
        if item['disposition'] in ('adopt', 'adapt'):
            if item.get('guide_alignment') != 'compatible':
                raise DocumentError('adopted advice requires resolved guide alignment')
            adopted[path] = item['sha256']
        seen.add(path)
    if seen != set(snapshot['advice']):
        raise DocumentError('unassessed advice; assess applicability before dispatch')
    return adopted



def physical_lines(text, *, keepends=False):
    """Markdown source lines end only at LF, CRLF or CR."""
    lines = [line for line in re.findall(r'[^\r\n]*(?:\r\n|\r|\n|$)', text) if line]
    return lines if keepends else [line.rstrip('\r\n') for line in lines]


def _fence_transition(line, fence):
    """Shared top-level fence grammar; callers choose their EOF policy."""
    marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
    if marker:
        token, tail = marker.groups()
        if fence is None and (token[0] != '`' or '`' not in tail):
            fence = token
        elif fence and token[0] == fence[0] and len(token) >= len(fence) and not tail.strip(' \t'):
            fence = None
    return fence, marker is not None


def outside_fences(text):
    """Yield literal line offsets outside CommonMark-style fenced examples."""
    offset, fence = 0, None
    for raw in physical_lines(text, keepends=True):
        line = raw.rstrip('\r\n')
        fence, marker = _fence_transition(line, fence)
        if not marker and fence is None:
            yield offset, offset + len(raw), line
        offset += len(raw)


def split_detail(text):
    """Only the Progress suffix is mutable runtime output; Plan is required."""
    boundaries = [(a, b) for a, b, line in outside_fences(text) if line == '## Progress']
    if len(boundaries) != 1:
        raise DocumentError('detail requires exactly one ## Progress boundary')
    boundary = boundaries[0]
    planning, progress = text[:boundary[0]], text[boundary[1]:]
    if sum(line == '## Plan' for _, _, line in outside_fences(planning)) != 1:
        raise DocumentError('detail requires one stable ## Plan section before ## Progress')
    return planning, progress


def validate_guide_reviews(snapshot, reviews, task_ids):
    """Audit origin and application; trusted host verifies claims/permissions."""
    if not isinstance(reviews, list):
        raise DocumentError('guide_reviews must be a list')
    seen = set()
    for item in reviews:
        if not isinstance(item, dict):
            raise DocumentError('invalid guide review')
        path, refs = item.get('path'), item.get('task_refs')
        if (path not in snapshot['guides'] or path in seen or item.get('sha256') != snapshot['guides'][path]
                or item.get('origin') not in ('owner_authored', 'owner_approved')
                or item.get('disposition') not in ('applied', 'not_applicable')
                or not all(isinstance(item.get(k), str) and item[k].strip() for k in ('authorization_reference', 'reason'))
                or not isinstance(refs, list) or not refs or not all(r in task_ids for r in refs)):
            raise DocumentError('guide review requires current hash, owner provenance, linked tasks and application reason')
        seen.add(path)
    if seen != set(snapshot['guides']):
        raise DocumentError('human guide review required before dispatch; filenames are not authorization')


def task_document_refs(snapshot, task_refs, assessments=(), guide_reviews=()):
    """Bind only this task's planning inputs and adopted advice, plus all guides."""
    adopted = {item['path']: item['sha256'] for item in assessments
               if item['disposition'] in ('adopt', 'adapt') and set(item['task_refs']) & set(task_refs)}
    # Keep the full discovery/assessment inventory on the global plan. A worker
    # needs only its adopted sources, not another copy of every historical path.
    # Filter before deep-copying so unrelated details/inventory are not copied
    # transiently either. Preserve unknown snapshot fields and all guide inputs.
    scoped = {**snapshot,
              'guide_reviews': guide_reviews,
              'task_details': {key: value for key, value in snapshot['task_details'].items() if key in task_refs},
              'advice': {path: snapshot['advice'][path] for path in adopted},
              'adopted_advice': adopted}
    return json.loads(json.dumps(scoped))


def bind_advice(plan, assessments):
    """Explicitly bind assessed advice to a draft; never refresh stale snapshots."""
    snapshot = plan['project_documents']
    ids = {ref for task in plan['tasks'] for ref in task['task_refs']}
    adopted = validate_advice_assessments(snapshot, assessments, ids)
    plan['advice_assessments'] = json.loads(json.dumps(assessments))
    snapshot['adopted_advice'] = adopted
    for task in plan['tasks']:
        task['document_refs'] = task_document_refs(snapshot, task['task_refs'], assessments, plan.get('guide_reviews', []))
    return plan



def bind_guide_reviews(plan, reviews):
    """Record independently established owner provenance and planning response."""
    ids = {ref for task in plan['tasks'] for ref in task['task_refs']}
    validate_guide_reviews(plan['project_documents'], reviews, ids)
    plan['guide_reviews'] = json.loads(json.dumps(reviews))
    for task in plan['tasks']:
        task['document_refs'] = task_document_refs(plan['project_documents'], task['task_refs'],
                                                  plan.get('advice_assessments', []), reviews)
    return plan

def write_task_progress(root, task_id, progress, *, expected_plan_sha256):
    """Main-AI serialized progress update; cannot replace stable planning inputs."""
    snapshot = snapshot_project_docs(root)
    detail = snapshot['task_details'].get(task_id)
    if detail is None or detail['sha256'] != expected_plan_sha256:
        raise DocumentError('task planning version changed; progress update rejected')
    path = detail['path']
    planning, _ = split_detail(regular_bytes(root, path).decode('utf-8').replace('\r\n', '\n'))
    if not isinstance(progress, str) or any(line == '## Progress' for _, _, line in outside_fences(progress)):
        raise DocumentError('progress must not add another planning boundary')
    atomic_write(root, path, (planning + '## Progress\n' + progress).encode('utf-8'))
    return snapshot_project_docs(root)


def controlled_remove(root, path):
    """Remove only an authorized file or empty directory; never recursive delete."""
    target = assert_ai_writable(root, path)
    if target.is_dir():
        target.rmdir()
    else:
        target.unlink()


def controlled_rename(root, source, destination):
    """Both source removal and destination write are guarded; no overwrite."""
    source = assert_ai_writable(root, source)
    destination = assert_ai_writable(root, destination)
    if destination.exists():
        raise DocumentError('rename destination already exists')
    source.rename(destination)


def _rebase_links(text):
    def target(value):
        if not value or value.startswith(('#', '/', '<')) or urlsplit(value).scheme:
            return value
        return '../../../' + value
    text = re.sub(r'(!?\[[^]\n]*\]\()([^\s)]+)([^)]*\))',
                  lambda match: match[1] + target(match[2]) + match[3], text)
    return re.sub(r'^(\[[^]\n]+\]:\s*)(\S+)',
                  lambda match: match[1] + target(match[2]), text, flags=re.M)

def assert_ai_writable(root, path):
    """Preflight a controlled write, including redirects and hard-linked guides.

    Call before mkdir/open/replace/delete, not after resolving away lexical paths.
    Application guard only; arbitrary third-party tools must implement their own.
    """
    supplied_root = Path(os.path.abspath(root))
    root = supplied_root.resolve()
    target = Path(os.path.abspath(root / path))
    for candidate in (supplied_root, root, target, target.resolve()):
        if any(ancestor.name.casefold() == 'guide' and ancestor.parent.name.casefold() in ('doc', 'agent_doc')
               for ancestor in (candidate, *candidate.parents)):
            raise DocumentError('agent_doc/guide is human-only; rebased roots and aliases cannot grant AI writes')
    if not target.is_relative_to(root):
        raise DocumentError('controlled write outside project')
    for directory in ('agent_doc/guide', 'doc/guide'):
        guide = root / directory
        if target.is_relative_to(guide) or (guide.is_relative_to(target) and
                (directory.startswith('agent_doc/') or guide.exists())):
            raise DocumentError('human-only guide; AI writes are forbidden')
    _relative(root, target)
    if target.exists() and target.is_file() and target.stat().st_nlink > 1:
        for directory in ('agent_doc/guide', 'doc/guide'):
            if (root / directory).exists():
                for name in _inventory(root, directory):
                    if os.path.samefile(target, root / name):
                        raise DocumentError('hard-linked human guide cannot be written by AI')
    return target


def guard_write_path(path):
    """Guard generic runtime writers, even without a project-root argument."""
    path = Path(os.path.abspath(path))
    for candidate in (path, path.resolve()):
        for ancestor in (candidate, *candidate.parents):
            if ancestor.name.casefold() == 'guide' and ancestor.parent.name.casefold() in ('doc', 'agent_doc'):
                raise DocumentError('agent_doc/guide is human-only; AI writes are forbidden')
    # Locate a known project to catch aliases and hardlinks as well.
    for root in path.parents:
        if (root / CANONICAL_TASK).exists() or (root / 'TASK.md').exists() or (root / '.git').exists():
            assert_ai_writable(root, path)
            break
    return path


def atomic_write(root, path, data):
    path = assert_ai_writable(root, path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.close(fd)
        fd = None
        assert_ai_writable(root, path)
        os.replace(temporary, path)
    finally:
        if fd is not None:
            os.close(fd)
        if os.path.exists(temporary):
            os.unlink(temporary)


def migrate(root, date):
    """Explicit legacy migration; preserve exact archive bytes and stable IDs.

    No guide files are created. Root TASK becomes a pointer only. A partial
    migration fails closed at the resolver; rerunning reconciles only exact
    generated files from the still-preserved legacy source, never user edits.
    """
    root, date = Path(root).resolve(), _date(date)
    legacy = _relative(root, 'TASK.md')
    canonical = _relative(root, CANONICAL_TASK)
    if canonical.exists() and legacy.exists() and not any(TASK_PATTERN.match(line)
            for line in physical_lines(regular_bytes(root, legacy).decode('utf-8'))):
        return snapshot_project_docs(root)
    raw = regular_bytes(root, legacy)
    text = raw.decode('utf-8')
    items = parse_requirements(text)
    sha = hashlib.sha256(raw).hexdigest()
    archive = f'agent_doc/task/legacy/TASK.{sha}.md'
    files = {archive: raw, f'agent_doc/task/legacy/migration.{sha}.json':
             (json.dumps({'source': 'TASK.md', 'source_sha256': sha, 'archive': archive,
                          'original_relative_link_base': '.', 'archive_relative_link_base': '../../..'},
                         indent=2) + '\n').encode('utf-8')}
    # Each requirement keeps its original block; all other historical context
    # remains byte-exact in the content-addressed source archive.
    lines = physical_lines(text, keepends=True)
    blocks, dates, task_lines, sections = {}, {}, {}, [(1, date)]
    current, current_date = None, date
    fence = None
    for line_number, line in enumerate(lines, 1):
        marker = re.match(r'(`{3,}|~{3,})', line.lstrip())
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            if current:
                blocks[current].append(line)
            continue
        heading = DATE_PATTERN.match(line) if not fence else None
        match = TASK_PATTERN.match(line) if not fence else None
        if heading:
            current_date = _date(heading[1])
            sections.append((line_number, current_date))
            current = None
        if match:
            current = match[2]
            dates[current] = current_date
            task_lines[current] = line_number
            blocks[current] = [line]
        elif current and not heading:
            blocks[current].append(line)
    groups = {}
    for item in items:
        task_id, task_date = item['id'], dates[item['id']]
        groups.setdefault(task_date, []).append(item)
        section_start = max(start for start, _ in sections if start <= task_lines[task_id])
        section_end = min([start - 1 for start, _ in sections if start > section_start] or [len(lines)])
        body = (f'# [{task_id}] {item["title"]}\n\nTask-ID: {task_id}\nDate: {task_date}\n\n'
                '## Plan\n\n' + item['title'] + '\n\n## Progress\n\n'
                '### Preserved implementation and evidence\n\n' +
                re.sub(r'^## Progress$', '### Legacy Progress',
                       _rebase_links(''.join(blocks[task_id]).rstrip().replace('\r\n', '\n')), flags=re.M) + '\n\n'
                '### Historical context\n\n'
                f'Original task: [line {task_lines[task_id]}](../legacy/TASK.{sha}.md#L{task_lines[task_id]}).\n'
                f'Shared methods, results and evidence: [source section, lines {section_start}–{section_end}]'
                f'(../legacy/TASK.{sha}.md#L{section_start}-L{section_end}).\n'
                f'Source SHA256: {sha}\n'
                'Bare code paths and archive-relative links retain the original project-root base.\n'
                'Migration preserves the original checkbox as history, not independent acceptance.\n'
                'Dates use the nearest dated heading, or the explicitly supplied migration date.\n')
        files[f'agent_doc/task/task_details/{task_id}.md'] = body.encode('utf-8')
    index = '# Project tasks\n\nAI-maintained concise index; implementation and evidence live in linked details.\n'
    for task_date, group in groups.items():
        index += f'\n## {task_date}\n\n'
        for item in group:
            mark = 'x' if item['checked'] else ' '
            index += f'- [{mark}] [{item["id"]}] {item["title"]} ([detail](task_details/{item["id"]}.md))\n'
    files[CANONICAL_TASK] = index.encode('utf-8')
    pointer = ('# Project task index moved\n\n'
               'The single active task list is [agent_doc/task/TASK.md](agent_doc/task/TASK.md).\n'
               f'Historical source is preserved at [legacy TASK](agent_doc/task/legacy/TASK.{sha}.md).\n').encode('utf-8')
    # Validate generated structure before touching the real index/pointer. Legacy
    # headings are excerpts, not new planning boundaries in the derived detail.
    generated_items = parse_requirements(files[CANONICAL_TASK].decode('utf-8'), canonical=True)
    for item in generated_items:
        generated, _ = split_detail(files[f'agent_doc/task/{item["detail"]}'].decode('utf-8'))
        if (re.findall(r'^Task-ID: (.+)$', generated, re.M) != [item['id']] or
                re.findall(r'^Date: (.+)$', generated, re.M) != [item['date']]):
            raise DocumentError('generated task detail identity mismatch; migration aborted')
    # Validate every target before any write, including partial migration conflicts.
    for name, data in files.items():
        target = assert_ai_writable(root, name)
        if target.exists() and regular_bytes(root, name) != data:
            raise DocumentError('migration target exists with different bytes: ' + name)
    expected_details = {name for name in files if name.startswith('agent_doc/task/task_details/')}
    if set(_inventory(root, 'agent_doc/task/task_details')) - expected_details:
        raise DocumentError('orphan task details must be reconciled before migration')
    for directory in ('agent_doc/guide', 'agent_doc/advice'):
        target = _relative(root, directory)
        if target.exists() and not target.is_dir():
            raise DocumentError(directory + ' must be a directory')
    if regular_bytes(root, legacy) != raw:
        raise DocumentError('legacy TASK changed during migration')
    for name, data in files.items():
        if not (root / name).exists():
            atomic_write(root, name, data)
    if regular_bytes(root, legacy) != raw:
        raise DocumentError('legacy TASK changed during migration; reconcile preserved copies')
    atomic_write(root, legacy, pointer)
    # Empty directory bootstrap only; never create .gitkeep/template/guide.md.
    (root / 'agent_doc/guide').mkdir(parents=True, exist_ok=True)
    (root / 'agent_doc/advice').mkdir(parents=True, exist_ok=True)
    return snapshot_project_docs(root)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    formatting = parser.add_mutually_exclusive_group()
    formatting.add_argument('--compact', action='store_true', default=None,
                            help='preserve every field; default for inspect/validate')
    formatting.add_argument('--pretty', dest='compact', action='store_false', help='indent JSON; nav stays compact')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init', help='initialize only the explicitly selected existing project')
    for command in ('inspect', 'validate'):
        viewing = sub.add_parser(command)
        viewing.add_argument('--max-chars', type=int, default=20000,
                             help='complete display character cap including newline (1..1000000)')
    nav = sub.add_parser('nav')
    nav.add_argument('--max-chars', type=int, default=12000)
    nav.add_argument('--progress-chars', '--progress-tail-chars', dest='progress_chars',
                     type=int, default=64)
    nav.add_argument('--include-checked', action='store_true')
    nav.add_argument('--task-id', dest='task_ids', action='append')
    nav.add_argument('--summary-chars', type=int)
    nav.add_argument('--limit', type=int)
    nav.add_argument('--after-id')
    nav.add_argument('--snapshot', dest='expected_snapshot')
    action = sub.add_parser('migrate')
    action.add_argument('--date', required=True)
    sub.add_parser('guard-write').add_argument('paths', nargs='+')
    args = parser.parse_args(argv)
    try:
        bounded_snapshot = args.command in ('inspect', 'validate')
        if bounded_snapshot and not 1 <= args.max_chars <= 1000000:
            raise ContextBudgetError('display max_chars must be 1..1000000')
        if args.command == 'init':
            result = initialize_project_docs(args.root)
        elif args.command == 'migrate':
            result = migrate(args.root, args.date)
        elif args.command == 'guard-write':
            result = {'allowed': [str(assert_ai_writable(args.root, path)) for path in args.paths]}
        elif args.command == 'nav':
            result = task_navigation(args.root, max_chars=args.max_chars,
                                     progress_chars=args.progress_chars,
                                     include_checked=args.include_checked, task_ids=args.task_ids, summary_chars=args.summary_chars, limit=args.limit, after_id=args.after_id, expected_snapshot=args.expected_snapshot)
        else:
            result = snapshot_project_docs(args.root)
        # Navigation's compact serialization is the measured context payload;
        # pretty-printing it would silently exceed the checked character budget.
        if args.command == 'nav':
            rendered = json.dumps(result, ensure_ascii=False, separators=(',', ':'))
        elif bounded_snapshot:
            compact = True if args.compact is None else args.compact
            rendered = render_cli_context(result, compact=compact, indent=2, max_chars=args.max_chars)
        else:
            rendered = (render_context(result, compact=True) if args.compact else json.dumps(result, ensure_ascii=False, indent=2))
        print(rendered)
        return 0
    except ContextBudgetError as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except (OSError, ValueError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
