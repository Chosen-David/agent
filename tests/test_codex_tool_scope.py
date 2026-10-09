import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from agent_runtime.codex_tool_scope import check_scoped_catalog,resolve_tool_scope

class ToolScopeChecks(unittest.TestCase):
    def contract(self,complete=True,required=None):
        return {'schema_version':'codex-tool-scope/v1','requirements_complete':complete,
                'external_tool_requirements':[] if required is None else required}

    def test_only_explicit_complete_empty_requirements_narrow_catalog(self):
        result=resolve_tool_scope(self.contract())
        self.assertEqual(result['config_overrides'],{'mcp_servers.node_repl.enabled':False,'features.apps':False})
        for c in (self.contract(False),self.contract(True,['web/search']),self.contract(False,['github/read'])):
            self.assertEqual(resolve_tool_scope(c)['config_overrides'],{})
        self.assertNotIn('approval_policy',result['config_overrides'])

    def test_ambiguous_or_malformed_contract_cannot_disable_tools(self):
        for value in (None,{},self.contract(0),self.contract('false'),self.contract(True,'none'),
                      self.contract(True,['x','x']),self.contract(True,[' ']),self.contract(True,['x']*65),
                      {**self.contract(),'approval_policy':'never'},
                      {**self.contract(),'schema_version':'unknown'}):
            with self.assertRaises(ValueError):resolve_tool_scope(value)

    def test_unexpected_tools_failure_and_pagination_stop_dispatch(self):
        check_scoped_catalog('no-external-tools',[{'tools':{}}])
        check_scoped_catalog('host-default',[{'tools':{'search':{}}}])
        for name,servers,more in (('no-external-tools',[{'tools':{'unexpected':{}}}],False),
                                  ('no-external-tools',[{'tools':{},'toolsError':'startup failed'}],False),
                                  ('no-external-tools',[],True),('unknown',[],False)):
            with self.assertRaises(ValueError):check_scoped_catalog(name,servers,has_more=more)

    def test_cli_reads_bounded_project_contract_without_changing_config(self):
        script=Path(__file__).resolve().parents[1]/'scripts/codex_tool_scope.py'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);contract=root/'task.json';contract.write_text(json.dumps(self.contract()))
            before=contract.read_bytes()
            result=subprocess.run([sys.executable,str(script),'--root',str(root),'--contract',str(contract)],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['profile'],'no-external-tools')
            self.assertEqual(contract.read_bytes(),before)
            for bad in (b'x'*8193,b'{"schema_version":"codex-tool-scope/v1","requirements_complete":false,"requirements_complete":true,"external_tool_requirements":[]}'):
                contract.write_bytes(bad)
                rejected=subprocess.run([sys.executable,str(script),'--root',str(root),'--contract',str(contract)],capture_output=True)
                self.assertNotEqual(rejected.returncode,0)
