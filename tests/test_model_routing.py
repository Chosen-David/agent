"""Offline routing contracts; fake executables exercise actual process boundaries."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agent_runtime.model_routing import EMPTY_INVENTORY, dispatch, resolve, validate_inventory

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('routing_setup', ROOT / 'setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)
POLICY = json.loads((ROOT / 'config/role_model_policy.json').read_text())


def inventory(candidate='opus', transport='native', available=True, capabilities=('tools', 'vision')):
    return {'schema_version': 1, 'models': [{**POLICY['models'][candidate], 'transport': transport,
                                          'available': available, 'capabilities': list(capabilities)}]}


class RoutingTests(unittest.TestCase):
    def test_all_registered_roles_and_main_profiles_have_preferences(self):
        ids = {r['id'] for r in json.loads((ROOT / 'config/role_registry.json').read_text())['roles']}
        ids |= {r['id'] for r in json.loads((ROOT / 'config/main_registry.json').read_text())['profiles']}
        self.assertEqual(set(POLICY['roles']), ids)

    def test_each_candidate_is_selected_only_when_eligible(self):
        for role, value in POLICY['roles'].items():
            with self.subTest(role=role):
                candidate = value['candidates'][0]
                result = resolve(POLICY, role, inventory(candidate))
                self.assertEqual(result['model'], POLICY['models'][candidate]['model'])
                self.assertFalse(result['fallback'])
                self.assertTrue(resolve(POLICY, role, inventory(candidate, available=False))['fallback'])
                self.assertTrue(resolve(POLICY, role)['fallback'])

    def test_adapter_missing_and_missing_vision_fall_back(self):
        self.assertTrue(resolve(POLICY, 'research-read-pdf', inventory('kimi', 'adapter'))['fallback'])
        result = resolve(POLICY, 'research-read-pdf', inventory('kimi', 'adapter'), adapter_available=True)
        self.assertEqual(result['transport'], 'adapter')
        result = resolve(POLICY, 'research-read-pdf', inventory('kimi', capabilities=('tools',)))
        self.assertTrue(result['fallback'])
        self.assertEqual(result['skipped'][0]['reason'], 'missing_capability')
        self.assertTrue(resolve(POLICY, 'explain-research-concepts',
                                inventory('deepseek-reasoning', capabilities=('tools',)), requires=['vision'])['fallback'])

    def test_bad_inventory_and_unknown_roles_rejected(self):
        for data in ({}, {'schema_version': True, 'models': []},
                     {**inventory(), 'api_key': 'SECRET'},
                     {'schema_version': 1, 'models': inventory()['models'] * 2}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate_inventory(data)
        data = inventory(); data['models'][0]['api_key'] = 'SECRET'
        with self.assertRaises(ValueError): validate_inventory(data)
        with self.assertRaises(ValueError): resolve(POLICY, 'typo', inventory())

    def test_execution_failure_is_never_retried(self):
        calls = []
        def fail(request):
            calls.append(request)
            raise RuntimeError('may have committed a side effect')
        with self.assertRaises(RuntimeError):
            dispatch(POLICY, 'research-write', inventory('opus', 'adapter'), {},
                     native=lambda r: self.fail('fallback after dispatch'), adapter=fail)
        self.assertEqual(len(calls), 1)


class InstallationRoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='routing project ')
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)

    def test_snapshot_persists_without_discovery_and_can_be_reset(self):
        setup.install(self.project, model_inventory=inventory())
        agent = self.project / '.claude/agents/agent-research-write.md'
        self.assertIn('model: "claude-opus-5-5"', agent.read_text())
        before = agent.read_bytes()
        setup.install(self.project)
        self.assertEqual(before, agent.read_bytes())
        with patch('subprocess.run', side_effect=AssertionError('offline check must not call host')):
            self.assertEqual(setup.check(self.project)['status'], 'configured')
        setup.install(self.project, model_inventory=EMPTY_INVENTORY)
        self.assertIn('model: "inherit"', agent.read_text())
        setup.uninstall(self.project)
        self.assertFalse(agent.exists())

    def test_external_preference_never_becomes_unroutable_native_model(self):
        setup.install(self.project, model_inventory=inventory('glm', 'adapter'))
        agent = self.project / '.claude/agents/agent-research-implement-optimize.md'
        self.assertIn('model: "inherit"', agent.read_text())
        route = setup.check(self.project)['model_routing']['routes']['research-implement-optimize']
        self.assertEqual(route['skipped'][0]['reason'], 'adapter_missing')

    def test_local_policy_edits_preserved_on_upgrade_and_uninstall(self):
        setup.install(self.project)
        policy = self.project / '.claude/agent-workflows/model-policy.json'
        policy.write_text('local edits')
        with self.assertRaisesRegex(ValueError, 'locally edited'):
            setup.install(self.project, model_inventory=inventory())
        self.assertEqual(policy.read_text(), 'local edits')
        self.assertIn(str(policy.relative_to(self.project)), setup.uninstall(self.project)['preserved_local_edits'])

    def test_old_installation_manifest_upgrades_without_inventory(self):
        setup.install(self.project)
        path = self.project / '.claude/agent-workflows/installation.json'
        manifest = json.loads(path.read_text())
        del manifest['model_inventory']
        for name in ('model-policy', 'model-routing'):
            relative = '.claude/agent-workflows/' + name + '.json'
            del manifest['files'][relative]
            (self.project / relative).unlink()
        path.write_text(json.dumps(manifest))
        self.assertEqual(setup.install(self.project)['status'], 'configured')

    def executable(self, name, body):
        path = self.project / name
        path.write_text('#!' + sys.executable + '\n' + body)
        path.chmod(0o700)
        return str(path)

    def run_role(self, role, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/run_role.py'),
                               '--project', str(self.project), '--role', role, *args],
                              input='TASK CONTENT', capture_output=True, text=True, timeout=20)

    def test_cli_native_default_ignores_previously_pinned_agent(self):
        setup.install(self.project, model_inventory=inventory())
        empty = self.project / 'empty.json'; empty.write_text(json.dumps(EMPTY_INVENTORY))
        cli = self.executable('fake-claude', 'import json,sys,os\nprint(json.dumps({"argv":sys.argv[1:],"stdin":sys.stdin.read(),"cwd":os.getcwd()}))\n')
        for role in ('research-write', 'planner-main', 'review-main'):
            result = self.run_role(role, '--inventory', str(empty), '--claude', cli)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            self.assertNotIn('--model', output['argv'])
            definition = json.loads(output['argv'][output['argv'].index('--agents') + 1])
            self.assertEqual(definition['routed-' + role]['model'], 'inherit')
            self.assertTrue(definition['routed-' + role]['prompt'])
            self.assertEqual(output['cwd'], str(self.project))
            self.assertEqual(output['stdin'], 'TASK CONTENT')

    def test_cli_adapter_protocol_and_no_retry_after_side_effect(self):
        setup.install(self.project)
        data = repr(inventory('glm', 'adapter'))
        adapter = self.executable('fake-adapter', 'import json,sys,pathlib\nr=json.load(sys.stdin)\n'
            'if r["operation"]=="inventory":\n'
            ' assert "prompt" not in r\n print(json.dumps(' + data + '))\n'
            'else:\n pathlib.Path("effect").write_text(json.dumps(r))\n sys.exit(7)\n')
        cli = self.executable('must-not-run', 'raise AssertionError("unexpected native retry")\n')
        result = self.run_role('research-implement-optimize', '--adapter', adapter, '--claude', cli)
        self.assertEqual(result.returncode, 7, result.stderr)
        request = json.loads((self.project / 'effect').read_text())
        self.assertEqual(request['route']['provider'], 'zai')
        self.assertEqual(request['route']['model'], 'glm-5.3')
        self.assertEqual(request['prompt'], 'TASK CONTENT')

    def test_bad_adapter_inventory_defaults_and_dry_run_never_executes(self):
        setup.install(self.project, model_inventory=inventory())
        adapter = self.executable('bad-adapter', 'import pathlib\npathlib.Path("called").write_text("1")\nprint("bad JSON SECRET")\n')
        result = self.run_role('research-write', '--adapter', adapter, '--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.project / 'called').exists())
        cli = self.executable('default-cli', 'import json,sys\nprint(json.dumps(sys.argv[1:]))\n')
        result = self.run_role('research-write', '--adapter', adapter, '--claude', cli)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('--model', json.loads(result.stdout))
        self.assertNotIn('SECRET', result.stderr + result.stdout)


if __name__ == '__main__':
    unittest.main()
