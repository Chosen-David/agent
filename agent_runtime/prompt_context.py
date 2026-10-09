"""Compose selected trusted entry points; keep standalone sources unchanged."""
import hashlib
from pathlib import Path
import re

ENTRIES = {'decision': 'prompts/decision_review.md',
           'general': 'prompts/orchestrator.md',
           'research': 'prompts/research_orchestrator.md'}
MARKER = '【执行前反思与决策门禁】'


def _read(root, name):
    path = root / name
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError('prompt symlink is not a trusted entry: ' + name)
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError('prompt must be a regular project file: ' + name)
    raw = path.read_bytes()
    if len(raw) > 1000000:
        raise ValueError('prompt source exceeds byte limit')
    return raw.decode('utf-8'), hashlib.sha256(raw).hexdigest()


def _span(text):
    # Ambiguous repeated/quoted markers never establish a shared global scope.
    starts = [i for i in range(len(text)) if text.startswith(MARKER, i)
              and (i == 0 or text[i-1] == '\n')]
    if len(starts) != 1:
        return None
    start = starts[0]
    # Parse outer Markdown fences/comments: an inner ```text example inside
    # ~~~markdown or <!-- ... --> cannot establish global instructions.
    offset, fence, seen_fence, comment = 0, None, False, False
    global_text = False
    for line in text.splitlines(keepends=True):
        if offset == start:
            if comment or fence is None or not global_text:
                return None
            break
        if fence is None:
            if comment or '<!--' in line:
                comment = '-->' not in line
                offset += len(line)
                continue
            match = re.fullmatch(r' {0,3}(`{3,}|~{3,})([^\r\n]*)[\r\n]*',line)
            if match:
                delimiter, info = match.groups()
                fence = (delimiter[0],len(delimiter))
                global_text = not seen_fence and delimiter[0]=='`' and info.strip()=='text'
                seen_fence = True
        elif re.fullmatch(r' {0,3}'+re.escape(fence[0])+r'{'+str(fence[1])+r',}[ \t]*[\r\n]*',line):
            fence, global_text = None, False
        offset += len(line)
    ends = [i for token in ('\n【', '\n```')
            if (i := text.find(token, start + len(MARKER))) >= 0]
    if not ends:
        return None
    block = text[start:min(ends)].rstrip()
    return start, start + len(block)


def compose_entries(root, entries=('decision', 'general', 'research'), *,
                    deduplicate=True, max_chars=100000):
    """Losslessly retain unique text, dedup only this invocation's exact policy.

    Unknown scopes or different policy versions are retained in full. There is
    no disk-based 'already loaded' hint and no cross-thread context cache.
    """
    root = Path(root).resolve(strict=True)
    entries = tuple(entries)
    if not entries or len(set(entries)) != len(entries) or any(e not in ENTRIES for e in entries):
        raise ValueError('select unique known prompt entry IDs')
    if type(max_chars) is not int or not 1 <= max_chars <= 1000000:
        raise ValueError('invalid prompt character cap')
    canonical, _ = _read(root, ENTRIES['decision'])
    span = _span(canonical)
    if span is None:
        raise ValueError('canonical shared decision scope is missing or ambiguous')
    policy = canonical[span[0]:span[1]]
    emitted = False
    rows, parts = [], []
    for entry in entries:
        name = ENTRIES[entry]
        text, digest = _read(root, name)
        location = _span(text)
        disposition = 'retained'
        if location is not None and text[location[0]:location[1]] == policy:
            if deduplicate and emitted:
                text = text[:location[0]] + '【共享决策协议已在前文完整提供，逐条适用】' + text[location[1]:]
                disposition = 'shared-reference'
            else:
                emitted = True
                disposition = 'shared-full'
        rows.append({'entry':entry, 'path':name, 'sha256':digest, 'policy':disposition})
        parts.append('Document: ' + name + '\n' + text)
    prompt = '\n\n'.join(parts)
    if len(prompt) > max_chars:
        raise ValueError('complete prompt exceeds character cap; select fewer entries')
    return {'schema_version':'prompt-context/v1', 'prompt':prompt, 'documents':rows,
            'policy_sha256':hashlib.sha256(policy.encode('utf-8')).hexdigest(),
            'scope':'exact shared policy in selected trusted entries, single current context; no model usage estimate'}
