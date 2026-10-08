"""Capture read-only CPU diagnostic commands; no compiler or GPU execution."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
skill = root / 'plugins/research-assistant/skills/research-implement-optimize'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
commands = [
    ('prior-results', [sys.executable, 'scripts/result_store.py', '--root', str(root), 'search', 'PTXAS H100 spill', '--limit', '5', '--max-scan', '200']),
    ('knowledge-search', [sys.executable, '-m', 'agent_runtime.knowledge', '--root', 'knowledge', 'search', 'PTXAS register spilling H100 CUDA', '--limit', '3']),
    ('compiler-feedback', [sys.executable, str(skill / 'scripts/compiler_feedback.py'), str(out.parent / 'forward-input.log')]),
    ('revision', ['git', 'rev-parse', 'HEAD']),
    ('status', ['git', 'status', '--short']),
    ('task-check', ['rg', '-n', 'KERNEL-FEEDBACK', 'agent_doc/task/TASK.md']),
]
trace = []
for name, command in commands:
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    item = {'name': name, 'argv': command, 'cwd': str(root), 'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    trace.append(item)
    if name in ('prior-results', 'knowledge-search', 'compiler-feedback'):
        (out / (name + '.json')).write_text(json.dumps(json.loads(result.stdout), ensure_ascii=False, indent=2) + '\n')
(out / 'tool-trace.json').write_text(json.dumps(trace, ensure_ascii=False, indent=2) + '\n')
paths = [
    root / 'AGENTS.md', root / 'prompts/decision_review.md', root / 'workflows/project_document_workflow.md',
    out.parent / 'forward-task.md', out.parent / 'forward-input.log',
    skill / 'SKILL.md', skill / 'scripts/compiler_feedback.py',
    *[skill / 'references' / name for name in ('workflow.md', 'execution.md', 'engineering_reuse.md', 'kernel_optimization_feedback.md', 'knowledge_access_workflow.md', 'result_reuse_workflow.md', 'result_validation_workflow.md')],
]
lock = {'scope': 'synthetic diagnostic CPU file analysis; not a GPU compilation or performance experiment', 'files': [{'path': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in paths], 'validation': 'pending independent review by parent; no self-certification'}
(out / 'input-lock.json').write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'commands': len(commands), 'output_dir': str(out), 'parser_exit': trace[2]['returncode'], 'compile_success': json.loads(trace[2]['stdout'])['compile_success'], 'gpu_executed': False}))
