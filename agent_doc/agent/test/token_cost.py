"""Measure serialized verification payloads, not model billing or reasoning tokens."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import tiktoken
    encoding = tiktoken.get_encoding('o200k_base')
    here = Path(__file__).resolve().parent
    root = Path(os.environ["AGENT_TEST_PROJECT_ROOT"])
    output = args.output.resolve()
    if output.is_relative_to(root):
        parser.error('evidence must be outside the repository')
    output.mkdir(parents=True, exist_ok=False)
    script = here / 'compile_structure.py'
    code = script.read_text()
    original = (root / 'agent_runtime/core.py').read_text()
    rows = []
    with tempfile.TemporaryDirectory(dir=output) as directory:
        fixture = Path(directory)
        runtime = fixture / 'agent_runtime'
        runtime.mkdir()
        for name, suffix, expected, marker in (
                ('clean', '', 0, 'dependency boundary passed'),
                ('syntax', '\ndef broken(:\n', 1, 'compile failure'),
                ('dependency', '\nimport scripts.project_test\n', 1, 'core must not import CLI scripts')):
            (runtime / 'core.py').write_text(original + suffix)
            prefix = 'AGENT_TEST_PROJECT_ROOT=' + shlex.quote(str(fixture)) + ' ' + shlex.quote(sys.executable) + ' -B '
            commands = {'inline_equivalent': prefix + "- <<'PY'\n" + code + '\nPY\n',
                        'reuse': prefix + shlex.quote(str(script)) + '\n'}
            observations = {}
            for mode, command in commands.items():
                result = subprocess.run(['bash', '-c', command], capture_output=True, text=True, timeout=20)
                transcript = result.stdout + result.stderr
                (output / (name + '-' + mode + '.command.txt')).write_text(command)
                (output / (name + '-' + mode + '.log')).write_text(transcript)
                if result.returncode != expected or marker not in transcript:
                    raise RuntimeError(f'{name}/{mode}: unexpected check outcome')
                observations[mode] = {'exit': result.returncode,
                    'command_tokens': len(encoding.encode(command)),
                    'result_tokens': len(encoding.encode(transcript)),
                    'output_sha256': hashlib.sha256(transcript.encode()).hexdigest()}
            if observations['inline_equivalent']['output_sha256'] != observations['reuse']['output_sha256']:
                raise RuntimeError('paired checks returned different evidence')
            rows.append({'scenario': name, 'observations': observations})
    report = {'encoding': encoding.name, 'tiktoken_version': tiktoken.__version__,
              'scope': 'paired shell payload tokenization; inline uses identical existing code, not a second LLM generation',
              'excluded': ['shared prompt/history', 'reasoning', 'provider framing', 'cached-token billing', 'initial script authoring and maintenance'],
              'script_sha256': hashlib.sha256(code.encode()).hexdigest(),
              'cold_manifest_tokens': len(encoding.encode((here / 'suite.json').read_text())),
              'rows': rows}
    (output / 'measurement.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
