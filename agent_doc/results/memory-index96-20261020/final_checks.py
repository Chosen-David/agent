"""Test the exact candidate bytes on an isolated WSL-native filesystem."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE_FILES = ['agent_runtime/project_memory.py', 'tests/test_memory_index.py',
                'tests/test_memory_cli_input.py', 'workflows/project_memory_workflow.md',
                'CODEMAP.md', 'agent_doc/task/TASK.md', 'agent_doc/task/task_details/MEM-INDEX-96.md']
SOURCE_FILES += [str(path.relative_to(ROOT)).replace('\\', '/') for path in
                 ROOT.glob('plugins/research-assistant/skills/*/references/project_memory_workflow.md')]


def native_prepare():
    scratch = ROOT / '.agent-runs/memory-index96-final-checks'
    scratch.mkdir(exist_ok=True)
    subprocess.run(['git', 'archive', 'HEAD', '--format=tar', '--output', str(scratch / 'baseline.tar')],
                   cwd=ROOT, check=True)
    with tarfile.open(scratch / 'candidate.tar', 'w') as archive:
        for relative in SOURCE_FILES:
            archive.add(ROOT / relative, arcname=relative, recursive=False)
        archive.add(OUT, arcname=OUT.relative_to(ROOT).as_posix())
    # WSL stderr includes a host network notice; preserve it separately.
    cmd = ['wsl', '--exec', 'python3', '/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent/'
           'agent_doc/results/memory-index96-20261020/final_checks.py', '--linux']
    with (OUT / 'final-check-launch.log').open('wb') as stream:
        result = subprocess.run(cmd, stdout=stream, stderr=subprocess.STDOUT)
    print('final isolated checks exit', result.returncode)
    return result.returncode


def linux_run():
    scratch = ROOT / '.agent-runs/memory-index96-final-checks'
    checkout = Path(tempfile.mkdtemp(prefix='agent-memory-index96-final-'))
    for name in ('baseline.tar', 'candidate.tar'):
        with tarfile.open(scratch / name) as archive:
            archive.extractall(checkout, filter='data')
    bindings = {relative: hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() for relative in SOURCE_FILES}
    for relative, digest in bindings.items():
        if hashlib.sha256((checkout / relative).read_bytes()).hexdigest() != digest:
            raise AssertionError('candidate byte mismatch: ' + relative)
    subprocess.run(['git', 'init', '-q'], cwd=checkout, check=True)
    subprocess.run(['git', 'add', '.'], cwd=checkout, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(['git', '-c', 'user.name=Isolated regression', '-c', 'user.email=local@example.invalid',
                    'commit', '-qm', 'isolated candidate snapshot for tests'], cwd=checkout, check=True)
    records = []
    commands = [('final-focused-wsl.log', [sys.executable, '-m', 'unittest', 'tests.test_memory_index',
                                         'tests.test_memory_cli_input', 'tests.test_memory_retrieval',
                                         'tests.test_memory_check', 'tests.test_memory_context_closure']),
                ('final-all-wsl.log', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v']),
                ('final-reader-wsl.log', [sys.executable, '-m', 'unittest', 'discover', '-s', 'apps/paper-reader/tests', '-v'])]
    for name, command in commands:
        with (OUT / name).open('wb') as stream:
            result = subprocess.run(command, cwd=checkout, stdout=stream, stderr=subprocess.STDOUT)
        records.append({'command': command, 'cwd': str(checkout), 'log': name, 'exit_code': result.returncode})
        receipt = {'snapshot_root': str(checkout), 'project_root': str(ROOT), 'source_sha256': bindings,
                   'commands': records, 'scope': 'isolated source snapshot; synthetic git HEAD only for fixture preparation, not source publication',
                   'cleanup': 'temporary checkout retained pending independent review; no live project paths moved'}
        (OUT / 'final-checks.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        print(name, result.returncode, flush=True)
    return int(any(record['exit_code'] for record in records))


if __name__ == '__main__':
    raise SystemExit(linux_run() if '--linux' in sys.argv else native_prepare())
