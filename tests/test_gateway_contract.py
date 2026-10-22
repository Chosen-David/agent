"""Discovery metadata is not model execution evidence; all network calls are fixtures."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import setup
from agent_runtime.model_routing import resolve

spec = importlib.util.spec_from_file_location('gateway_discovery', setup.REPO / 'scripts/discover_models.py')
discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(discovery)


def host_inventory():
    policy = setup.load_json(setup.REPO / 'config/role_model_policy.json')
    return {'schema_version': 1, 'models': [{**policy['models']['opus'],
            'available': True, 'capabilities': ['tools', 'vision'], 'transport': 'native'}]}


class GatewayContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='gateway contract ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        env = patch.dict(os.environ, {}, clear=True)
        env.start()
        self.addCleanup(env.stop)

    def cli(self, *args):
        return subprocess.run([sys.executable, str(setup.REPO / 'scripts/discover_models.py'), *map(str, args)],
                              capture_output=True, text=True, timeout=20, check=False)

    def test_names_never_assert_availability_or_capabilities(self):
        result = discovery.build_inventory(['claude-opus-5-5', 'gpt-5-text-only', 'unverified-model'])
        for entry in result['models']:
            with self.subTest(model=entry['model']):
                self.assertFalse(entry['available'])
                self.assertEqual(entry['capabilities'], [])
        policy = setup.load_json(setup.REPO / 'config/role_model_policy.json')
        self.assertTrue(resolve(policy, 'research-write', result)['fallback'])

    def test_inventory_cli_preserves_explicit_host_declarations(self):
        value = host_inventory()
        value['models'][0].update(available=False, capabilities=['vision'], transport='adapter')
        path = self.root / 'explicit.json'
        path.write_text(json.dumps(value), encoding='utf-8')
        original = path.read_bytes()
        result = self.cli('--from-inventory', path, '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), value)
        self.assertEqual(path.read_bytes(), original)

    def test_inventory_cli_does_not_add_tools_to_explicit_empty_capabilities(self):
        value = host_inventory()
        value['models'][0]['capabilities'] = []
        path = self.root / 'explicit.json'
        path.write_text(json.dumps(value), encoding='utf-8')
        output = self.root / 'normalized.json'
        result = self.cli('--from-inventory', path, '--output', output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(output.read_text(encoding='utf-8')), value)

    def test_invalid_explicit_inventory_is_controlled_and_does_not_write(self):
        path = self.root / 'invalid.json'
        output = self.root / 'output.json'
        for raw in ('[]', 'null', '{bad', '{"schema_version":1,"models":[{"model":"claude"}]}'):
            with self.subTest(raw=raw):
                path.write_text(raw, encoding='utf-8')
                result = self.cli('--from-inventory', path, '--output', output)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn('Traceback', result.stderr)
                self.assertFalse(output.exists())

    def test_fetch_accepts_supported_envelopes_and_deduplicates(self):
        for payload in ({'data': [{'id': 'claude-opus-5-5'}, {'id': 'claude-opus-5-5'}]},
                        [{'id': 'claude-opus-5-5'}]):
            with self.subTest(payload=payload), patch('urllib.request.urlopen', return_value=io.BytesIO(json.dumps(payload).encode())) as call:
                ids = discovery.fetch_models('https://fixture.invalid', None, timeout=3)
                self.assertEqual(len(discovery.build_inventory(ids)['models']), 1)
                self.assertEqual(call.call_args.kwargs['timeout'], 3)

    def test_fetch_rejects_malformed_and_nonstring_ids(self):
        for payload in (b'{bad', b'\xff', b'{"data":[],"data":[{"id":"x"}]}',
                        b'{"data":[{"id":7}]}', b'{"data":[null]}',
                        b'{"data":[{"id":""}]}', b'{"data":42}', b'{"data":NaN}'):
            with self.subTest(payload=payload), patch('urllib.request.urlopen', return_value=io.BytesIO(payload)):
                with self.assertRaises(RuntimeError):
                    discovery.fetch_models('https://fixture.invalid', None)

    def test_fetch_has_response_byte_bound(self):
        class Response(io.BytesIO):
            def read(self, size=-1):
                self.requested = size
                return super().read(size)
        response = Response(b'x' * (1024 * 1024 + 2))
        with patch('urllib.request.urlopen', return_value=response):
            with self.assertRaises(RuntimeError):
                discovery.fetch_models('https://fixture.invalid', None)
        self.assertEqual(response.requested, 1024 * 1024 + 1)

    def test_main_empty_gateway_is_controlled(self):
        with patch.object(sys, 'argv', ['discover_models.py', '--base-url', 'https://fixture.invalid']), patch.object(
                discovery, 'fetch_models', return_value=[]), contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertNotEqual(discovery.main(), 0)
        self.assertNotIn('Traceback', err.getvalue())
        self.assertIn('zero models', err.getvalue())

    def test_cli_rejects_nonpositive_timeout_without_traceback(self):
        for value in ('0', '-1'):
            with self.subTest(value=value):
                result = self.cli('--timeout', value, '--from-inventory', self.root / 'missing')
                self.assertEqual(result.returncode, 2)
                self.assertNotIn('Traceback', result.stderr)
                self.assertIn('positive', result.stderr)

    def test_invalid_gateway_url_never_echoes_credentials_or_calls_network(self):
        url = '//user:fixture-password-sentinel@fixture.invalid'
        with patch.object(sys, 'argv', ['discover_models.py', '--base-url', url]), patch(
                'urllib.request.urlopen') as network, contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertNotEqual(discovery.main(), 0)
        network.assert_not_called()
        self.assertNotIn('fixture-password-sentinel', err.getvalue())
        self.assertNotIn(url, err.getvalue())

    def test_invalid_http_request_errors_do_not_echo_auth_or_url(self):
        import http.client
        for failure in (ValueError('Invalid header value fixture-auth-sentinel'),
                        http.client.InvalidURL('fixture-url-password-sentinel')):
            with self.subTest(kind=type(failure).__name__), patch.object(sys, 'argv', [
                    'discover_models.py', '--base-url', 'https://fixture.invalid',
                    '--auth-token', 'fixture-auth-sentinel']), patch(
                    'urllib.request.urlopen', side_effect=failure), contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertNotEqual(discovery.main(), 0)
                self.assertNotIn('fixture-auth-sentinel', err.getvalue())
                self.assertNotIn('fixture-url-password-sentinel', err.getvalue())
                self.assertNotIn('Traceback', err.getvalue())

    def test_actual_install_and_dispatch_fallback_then_host_verified_route(self):
        model = host_inventory()['models'][0]['model']
        setup.install(self.root, model_inventory=discovery.build_inventory([model]))
        command = [sys.executable, str(setup.REPO / 'scripts/run_role.py'),
                   '--project', str(self.root), '--role', 'research-write', '--dry-run']
        preview = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertTrue(json.loads(preview.stdout)['fallback'])
        setup.install(self.root, model_inventory=host_inventory())
        preview = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(json.loads(preview.stdout)['model'], model)
        self.assertFalse(json.loads(preview.stdout)['fallback'])

    def test_tmux_failures_keep_diagnostics_and_never_claim_applied(self):
        for failure in (FileNotFoundError('fixture missing'), subprocess.TimeoutExpired(['tmux'], 5),
                        subprocess.CompletedProcess([], 7, '', 'fixture denied')):
            with self.subTest(failure=type(failure).__name__), patch.dict(os.environ, {'TMUX': 'fixture'}):
                kwargs = {'side_effect': failure} if isinstance(failure, Exception) else {'return_value': failure}
                with patch('subprocess.run', **kwargs) as run:
                    report = setup.doctor(self.root)
                run.assert_called_once_with(['tmux', 'source-file', str(setup.REPO / 'agent_runtime/tmux.conf')],
                                            capture_output=True, text=True, timeout=5, check=False)
                self.assertEqual(report['status'], 'needs_setup')
                self.assertTrue(report['doctor']['warnings'])
                self.assertFalse(report['doctor']['fixes_applied'])

    def test_tmux_success_has_no_warning(self):
        with patch.dict(os.environ, {'TMUX': 'fixture'}), patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, '', '')):
            report = setup.doctor(self.root)
        self.assertEqual(report['doctor']['warnings'], [])
        self.assertEqual(report['doctor']['fixes_applied'], ['Applied tmux.conf (mouse/clipboard/256color)'])

    def test_no_tmux_has_no_tmux_subprocess(self):
        with patch('subprocess.run') as run:
            report = setup.doctor(self.root)
        run.assert_not_called()
        self.assertEqual(report['doctor']['warnings'], [])


if __name__ == '__main__':
    unittest.main()
