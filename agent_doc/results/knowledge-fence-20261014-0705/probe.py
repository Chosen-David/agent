"""Fixed CommonMark fence boundary oracle; baseline AST is sections-only."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from agent_runtime.knowledge_index import sections
from agent_runtime.knowledge import KnowledgeStore

CASES = [
    ('backtick_info_closer', '```py\n``` text\n# hidden\n```\n# visible\n', [5]),
    ('tilde_info_closer', '~~~py\n~~~ text\n# hidden\n~~~\n# visible\n', [5]),
    ('invalid_backtick_info', '```py`bad\n# visible\n', [2]),
    ('tilde_backtick_info', '~~~py`ok\n# hidden\n~~~\n# visible\n', [4]),
    ('ordinary', '```py\n# hidden\n```\n# visible\n', [4]),
    ('long_closer', '```\n# hidden\n`````\n# visible\n', [4]),
    ('short_closer', '````\n```\n# hidden\n````\n# visible\n', [5]),
    ('different_character', '```\n~~~\n# hidden\n```\n# visible\n', [5]),
    ('ascii_suffix', '```\n# hidden\n``` \t\n# visible\n', [4]),
    ('unicode_suffix', '```\n```\u00a0\n# hidden\n```\n# visible\n', [5]),
    ('crlf', '```py\r\n``` info\r\n# hidden\r\n```\t\r\n# visible\r\n', [5]),
    ('unclosed', '```\n# hidden\n', []),
    ('three_space', '   ~~~py\n# hidden\n   ~~~\n# visible\n', [4]),
    ('four_space', '    ```\n# visible\n', [2]),
    ('eof_close', '```\n# hidden\n```', []),
    ('plain_tree', '# visible\n## child\nbody\n', [1, 2]),
]

def oracle(content, starts):
    lines = content.splitlines(keepends=True)
    out, stack = [], []
    for idx, start in enumerate(starts, 1):
        line = lines[start - 1].strip()
        level = len(line.split()[0])
        while stack and stack[-1]['level'] >= level:
            stack.pop()
        node = dict(node=f's{idx}', title=line.lstrip('#').strip(), level=level,
                    start_line=start, parent=stack[-1]['node'] if stack else None)
        out.append(node)
        stack.append(node)
    if not out or out[0]['start_line'] > 1:
        out.insert(0, dict(node='intro', title='Fixture', level=0, start_line=1, parent=None))
    return [dict(node, end_line=(out[i+1]['start_line']-1 if i+1<len(out) else len(lines)),
                 text=''.join(lines[node['start_line']-1:(out[i+1]['start_line']-1 if i+1<len(out) else len(lines))]))
            for i, node in enumerate(out)]

tree = ast.parse(Path(__file__).with_name('baseline.py').read_text())
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'sections')
namespace = {'re': re}
exec(compile(ast.Module(body=[fn], type_ignores=[]), '<baseline-sections>', 'exec'), namespace)
baseline = namespace['sections']
rows = []
for name, content, starts in CASES:
    record = dict(title='Fixture', content=content)
    expected = oracle(content, starts)
    before, after = baseline(record), sections(record)
    rows.append(dict(name=name, input_sha256=hashlib.sha256(content.encode()).hexdigest(),
                     expected=expected, baseline=before, candidate=after,
                     baseline_pass=before == expected, candidate_pass=after == expected))
store = KnowledgeStore(ROOT / 'knowledge')
changed = [kid for kid, rec in store.records.items() if baseline(rec) != sections(rec)]
print(json.dumps(dict(python=sys.version, optimized=sys.flags.optimize, cases=rows,
                     baseline_pass=sum(r['baseline_pass'] for r in rows),
                     candidate_pass=sum(r['candidate_pass'] for r in rows),
                     corpus_records=len(store.records), corpus_changed=changed), ensure_ascii=False, indent=2))
