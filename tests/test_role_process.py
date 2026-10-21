"""Real UTF-8 process boundaries using Python fixtures on Windows and Unix."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


runner = module('role_process_runner', ROOT / 'scripts/run_role.py')


class RoleProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='role 中文 space ')
        cls.project = Path(cls.temp.name).resolve()
        module('role_process_setup', ROOT / 'setup.py').install(cls.project, copy_skills=True)
        policy = json.loads((ROOT / 'config/role_model_policy.json').read_text(encoding='utf-8'))
        inventory = {'schema_version': 1, 'models': [{**policy['models']['opus'],
                     'available': True, 'transport': 'adapter', 'capabilities': ['tools', 'vision']}]}
        cls.fake = cls.project / 'fixture.py'
        cls.fake.write_text('''import json,sys
from pathlib import Path
mode=sys.argv[1]
raw=sys.stdin.buffer.read()
if mode=='native':
    value={'stdin':raw.decode('utf-8'),'argv':sys.argv[2:]}
else:
    request=json.loads(raw.decode('utf-8'))
    with Path('calls').open('ab') as log:log.write((request['operation']+'\\n').encode())
    if request['operation']=='inventory':value=INVENTORY
    elif mode=='adapter-fail':sys.exit(17)
    else:value=request
sys.stdout.buffer.write(json.dumps(value,ensure_ascii=False).encode('utf-8'))
'''.replace('INVENTORY', repr(inventory)), encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        (self.project / 'calls').unlink(missing_ok=True)

    def run_role(self, *args, prompt='修复并验证𐀀，保留约束\n'):
        env = dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='cp936')
        return subprocess.run([sys.executable, '-X', 'utf8=0', str(ROOT / 'scripts/run_role.py'),
                               '--project', str(self.project), '--role', 'research-write', *args],
                              input=prompt.encode('utf-8') if isinstance(prompt, str) else prompt,
                              capture_output=True, env=env, timeout=30)

    def adapter(self, mode='adapter'):
        return ['--adapter', sys.executable, '--adapter-arg', str(self.fake), '--adapter-arg', mode]

    def calls(self):
        path = self.project / 'calls'
        return path.read_bytes().splitlines() if path.exists() else []

    def test_native_non_gbk_unicode_and_role_definition(self):
        prompt = '修复并验证𐀀，保留约束\n原始行尾\r\n'
        run = self.run_role('--claude', sys.executable, '--claude-arg', str(self.fake), '--claude-arg', 'native', prompt=prompt)
        self.assertEqual(run.returncode, 0, run.stderr.decode('utf-8'))
        result = json.loads(run.stdout.decode('utf-8'))
        self.assertEqual(result['stdin'], prompt)
        definitions = json.loads(result['argv'][result['argv'].index('--agents') + 1])
        self.assertIn('不得替换用户目标', definitions['routed-research-write']['prompt'])

    def test_adapter_inventory_then_single_utf8_run(self):
        run = self.run_role(*self.adapter())
        self.assertEqual(run.returncode, 0, run.stderr.decode('utf-8'))
        request = json.loads(run.stdout.decode('utf-8'))
        self.assertEqual(request['prompt'], '修复并验证𐀀，保留约束\n')
        self.assertEqual(self.calls(), [b'inventory', b'run'])

    def test_invalid_empty_and_oversized_tasks_never_discover_backend(self):
        for prompt in ('', b'\xff', 'x' * (1024 * 1024 + 1)):
            with self.subTest(prompt_bytes=len(prompt)):
                run = self.run_role(*self.adapter(), prompt=prompt)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(self.calls(), [])
        run = self.run_role(*self.adapter(), '--max-request-bytes', '100')
        self.assertEqual(run.returncode, 2)
        self.assertIn(b'--max-request-bytes', run.stderr)
        self.assertEqual(self.calls(), [])

    def test_final_route_is_included_in_budget(self):
        policy = json.loads((self.project / '.claude/agent-workflows/model-policy.json').read_text(encoding='utf-8'))
        request = {'schema_version': 1, 'project_root': str(self.project), 'role': 'research-write',
                   'definition': runner.role_definition(self.project, 'research-write', policy), 'prompt': 'task'}
        base_size = len(json.dumps(request, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
        run = self.run_role(*self.adapter(), '--max-request-bytes', str(base_size), prompt='task')
        self.assertEqual(run.returncode, 2)
        self.assertEqual(self.calls(), [b'inventory'])

    def test_failed_execution_has_no_retry(self):
        run = self.run_role(*self.adapter('adapter-fail'))
        self.assertEqual(run.returncode, 17)
        self.assertEqual(self.calls(), [b'inventory', b'run'])

    def test_dry_run_is_utf8_and_never_reads_or_executes_adapter(self):
        run = self.run_role(*self.adapter(), '--dry-run', prompt=b'\xff')
        self.assertEqual(run.returncode, 0, run.stderr.decode('utf-8'))
        self.assertEqual(json.loads(run.stdout.decode('utf-8'))['transport'], 'native')
        self.assertEqual(self.calls(), [])

    def test_canonical_request_budget_exact_boundary(self):
        request = {'prompt': '中文𐀀', 'definition': {'required': 'keep'}, 'route': {'model': None}}
        size = len(json.dumps(request, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))
        runner.check_request(request, size, max_tokens=3, counter=lambda text: 3)
        with self.assertRaises(runner.RoleInputError):runner.check_request(request, size - 1)
        with self.assertRaises(runner.RoleInputError):runner.check_request(request, size, max_tokens=2, counter=lambda text: 3)
        with self.assertRaises(runner.RoleInputError):runner.check_request(request, size, max_tokens=2, counter=lambda text: True)


if __name__ == '__main__':
    unittest.main()
