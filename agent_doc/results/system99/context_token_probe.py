"""Offline tokenizer measurements; not model usage, cost or quality evidence."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tiktoken
from agent_runtime.prompt_context import compose_entries, _span, ENTRIES
from agent_runtime.task_context import task_view

ROOT = Path.cwd()
OUT = ROOT / '.agent-runs/system99/context-tokens.json'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
source = ROOT / 'agent_doc/task/TASK.md'
raw = source.read_bytes()
view = task_view(ROOT, ['SYSTEM-99'], sha(raw), max_chars=1000000)
full = compose_entries(ROOT, deduplicate=False)
compact = compose_entries(ROOT, deduplicate=True)
canonical = (ROOT / ENTRIES['decision']).read_text()
start, end = _span(canonical)
policy = canonical[start:end]
expanded = compact['prompt'].replace('【共享决策协议已在前文完整提供，逐条适用】', policy)
if expanded != full['prompt']:
    raise AssertionError('current compact prompt does not expand to original bytes')
payloads = {
    'three_prompts_full_text': full['prompt'],
    'three_prompts_deduplicated_text': compact['prompt'],
    'three_prompts_full_json': json.dumps(full, ensure_ascii=False),
    'three_prompts_deduplicated_json': json.dumps(compact, ensure_ascii=False),
    'task_index_full_text': raw.decode(),
    'task_view_SYSTEM99_text': view['text'],
    'task_view_SYSTEM99_json': json.dumps(view, ensure_ascii=False),
}
advice = []
for p in sorted((ROOT / 'agent_doc/advice').glob('*.md')):
    if p.is_symlink() or not p.is_file():
        raise ValueError('nonregular advice')
    data = p.read_bytes()
    if len(data) > 1000000:
        raise ValueError('advice source over cap')
    advice.append((p.relative_to(ROOT).as_posix(), data))
if sum(len(data) for _, data in advice) > 16000000:
    raise ValueError('advice corpus over cap')
payloads['advice_top_level_full_text'] = '\n\n'.join(
    'Document: ' + path + '\n' + data.decode() for path, data in advice)
result = {
    'schema_version': 'offline-context-count/v1',
    'code_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
    'probe_sha256': sha(Path(__file__).read_bytes()),
    'python': platform.python_version(),
    'platform': platform.platform(),
    'tokenizer': 'tiktoken==' + tiktoken.__version__,
    'method': 'encode_ordinary, plain UTF-8 text; no chat framing, cache or model call',
    'authority': 'offline tokenizer counts only; task/advice scope differs, not an equivalent-quality comparison',
    'selected_task_ids': view['selected_task_ids'],
    'exact_prompt_expansion_equal': True,
    'omitted_task_rows': view['omitted_task_rows'],
    'prompt_sources': full['documents'],
    'task_source_sha256': sha(raw),
    'advice_sources': [{'path': path, 'sha256': sha(data)} for path, data in advice],
    'measurements': {},
}
for name, text in payloads.items():
    row = {'utf8_sha256': sha(text.encode()), 'characters': len(text)}
    for encoding in ('cl100k_base', 'o200k_base'):
        tokenizer = tiktoken.get_encoding(encoding)
        ids = tokenizer.encode_ordinary(text)
        if tokenizer.decode(ids) != text:
            raise AssertionError('tokenizer round-trip failed')
        row[encoding + '_tokens'] = len(ids)
    result['measurements'][name] = row
cache = os.environ.get('TIKTOKEN_CACHE_DIR')
result['encoding_cache_sha256'] = (
    {p.name: sha(p.read_bytes()) for p in sorted(Path(cache).iterdir()) if p.is_file()}
    if cache else None)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'measurements': result['measurements'],
                  'advice_files': len(advice), 'omitted_task_rows': view['omitted_task_rows']},
                 ensure_ascii=False, indent=2))
