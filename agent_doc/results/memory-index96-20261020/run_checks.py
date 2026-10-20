"""Capture exact subprocess commands, exit codes and unmodified byte logs."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
focused = ['tests.test_memory_index', 'tests.test_memory_retrieval', 'tests.test_memory_check',
           'tests.test_memory_context_closure', 'tests.test_memory_cli_input']
commands = [('focused-native-O.log', [sys.executable, '-O', '-m', 'unittest', 'tests.test_memory_index']),
            ('focused-wsl.log', ['wsl', '--cd', '/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent',
                                 '--exec', 'python3', '-m', 'unittest', *focused]),
            ('all-wsl.log', ['wsl', '--cd', '/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent',
                             '--exec', 'python3', '-m', 'unittest', 'discover', '-s', 'tests']),
            ('reader-wsl.log', ['wsl', '--cd', '/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent',
                                '--exec', 'python3', '-m', 'unittest', 'discover', '-s', 'apps/paper-reader/tests'])]
records = []
for name, command in commands:
    with (OUT / name).open('wb') as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    records.append({'command': command, 'log': name, 'exit_code': result.returncode})
    (OUT / 'checks.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
    print(name, result.returncode, flush=True)
sys.exit(int(any(row['exit_code'] for row in records)))
