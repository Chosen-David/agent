import importlib,subprocess,sys
from common import *
case=importlib.import_module(f'case_{MODE}')
assert not B.exists();B.mkdir();(B/'.gitattributes').write_bytes(b'* -text\n')
data=case.build(R)
assert set(data['prompts'])==set(NAMES) and all(len(v)<=2200 for v in data['prompts'].values())
for name,text in data['prompts'].items():(B/(name+'.prompt.txt')).write_bytes(text.encode())
dump(B/'report.json',data['report']);dump(B/'oracle.json',data['oracle'])
dump(B/'external-events.json',{'due':False,'evidence_version':'pending-v1'})
def schema(v):
 if type(v) is bool:return {'type':'boolean'}
 if type(v) is str:return {'type':'string'}
 if type(v) is int:return {'type':'integer'}
 if type(v) is list:return {'type':'array','items':schema(v[0]) if v else {'type':'string'},'maxItems':20}
 return {'type':'object','properties':{k:schema(x) for k,x in v.items()},'required':list(v),'additionalProperties':False}
dump(B/'schema.json',schema(data['oracle']))
settings=read(R/'agent_doc/results/token-010-maintenance-20261011/settings.json')
settings['config']['skills.config']=[{'path':str(Path.home()/'.agents/skills'/r['id']/'SKILL.md'),'enabled':False} for r in read(R/'config/role_registry.json')['roles']]
settings['config']['mcp_servers.cua_repl.enabled']=False
dump(B/'settings.json',settings)
procedures={
 'implementation':'Exact opt-in adapter source/archive equality; independent CPU regression tests and native candidate reconstruction.',
 'reference_boundary':'Independent deterministic replay of selected data and declared oracles, plus failure/budget/scope tests.',
 'data_integrity':'Exact original-to-redacted RPC checks; separate fresh threads, all paid calls, full usage and source/config binding.',
 'numerical_sanity':'Finite exact provider token sums; positive total-token saving including output and all calls; cache not subtracted.',
 'measurement_validity':'Identical model, effort, observable non-task instructions, tools and settings; no rerouting, no tools or retries; same oracle.',
 'reproducibility':'Pre-dispatch frozen plan, input and host verifier; distinct owner host process, exact history/controls and CPU replay.'}
plan={'schema_version':'experiment-validation-plan/v1','scope':case.SCOPE,'criteria':{k:{'procedure':v,'acceptance':v,'allow_not_applicable':False} for k,v in procedures.items()},'controls':{'max_invocations':len(NAMES),'retries':0,'max_supplied_characters':2200,'per_call_total_cap':25000,'all_call_total_cap':50000,'saving_requires':'baseline_total > candidate_total'}}
dump(B/'validation-plan.json',plan)
sources=required_source_paths(case)
rows=[]
for path in dict.fromkeys(sources):
 dest=B/'code_snapshot'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((R/path).read_bytes())
 rows.append({'path':path,'sha256':sha(R/path),'archive_path':dest.relative_to(R).as_posix()})
dump(B/'source-inventory.json',{'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'files':rows})
dump(B/'config.json',{'binary_sha256':sha(EXE),'user_config_sha256':sha(Path.home()/'.codex/config.toml'),'model':'gpt-6.1-sol','effort':'high','mechanism':case.MECHANISM,'tests':case.TESTS,'expected_tests':case.COUNT,'scope':case.SCOPE})
bindings={x['path']:x['sha256'] for x in rows}
for f in B.iterdir():
 if f.is_file():bindings[f.relative_to(R).as_posix()]=sha(f)
dump(B/'freeze.json',{'hashes':bindings,'verifier_sha256':sha(P/'verify.py')})
p=subprocess.run([sys.executable,'-X','utf8','-m','unittest',*case.TESTS,'-q'],cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=60)
(B/'producer-tests.log').write_bytes((p.stdout+p.stderr).encode())
assert p.returncode==0 and f'Ran {case.COUNT} tests' in p.stderr
dump(B/'producer-cpu.json',{'actor':'native-token-ten-producer','pid':__import__('os').getpid(),'tests':case.COUNT,'replay':case.replay(R)})
print(json.dumps({'frozen':B.name,'prompt_chars':{k:len(v) for k,v in data['prompts'].items()},'tests':case.COUNT,'model_calls':0}))
