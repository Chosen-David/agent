"""Explicit task-row navigation. Never a global-completion or priority proof."""
import hashlib
import json
import re
from .advice_poll import _root
from .maintenance_observer import read_bound
from .project_docs import TASK_PATTERN, parse_requirements


def task_view(root, task_ids, expected_sha256, *, max_chars=20000):
    root = _root(root)
    if (not isinstance(task_ids, (list, tuple)) or not task_ids or
            any(type(t) is not str for t in task_ids) or len(set(task_ids)) != len(task_ids)):
        raise ValueError('nonempty distinct explicit task IDs required')
    if type(expected_sha256) is not str or re.fullmatch('[0-9a-f]{64}', expected_sha256) is None:
        raise ValueError('source SHA256 binding required')
    if type(max_chars) is not int or not 1 <= max_chars <= 1000000:
        raise ValueError('invalid display budget')
    path = 'agent_doc/task/TASK.md'
    data = read_bound(root, path)
    if hashlib.sha256(data).hexdigest() != expected_sha256:
        raise ValueError('TASK changed; refresh explicit selection')
    text = data.decode('utf-8')
    items = parse_requirements(text, canonical=True)
    if set(task_ids) - {t['id'] for t in items}:
        raise ValueError('unknown task ID; no silent omission')
    kept, numbers, fence = [], [], None
    for number, line in enumerate(text.splitlines(keepends=True), 1):
        marker = re.match(r'(`{3,}|~{3,})', line.lstrip())
        if marker:
            token = marker[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            match = None
        else:
            match = TASK_PATTERN.match(line) if fence is None else None
        if match is None or match[2] in task_ids:
            kept.append(line); numbers.append(number)
    value = {'schema_version': 'task-view/v1', 'project_root': str(root),
             'source': {'path': path, 'sha256': expected_sha256},
             'selected_task_ids': list(task_ids), 'omitted_task_rows': len(items) - len(task_ids),
             'source_lines': numbers, 'text': ''.join(kept),
             'scope': 'explicit task rows and all other text; reread details/dependencies; no global clearance'}
    if len(json.dumps(value, ensure_ascii=False)) > max_chars:
        raise ValueError('view exceeds budget; select another scope, never truncate')
    return value
