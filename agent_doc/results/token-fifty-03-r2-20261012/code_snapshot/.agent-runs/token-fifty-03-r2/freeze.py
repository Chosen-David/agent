import ast,importlib.util,platform,subprocess,sys
from common import *
import case_3 as case
assert not (B/'freeze.json').exists()
data=case.build(R);limits=read(B/'validation-plan.json')['controls']
for n,p in data['prompts'].items():
    assert len(p)<=limits['max_supplied_characters']
    (B/(n+'.prompt.txt')).write_bytes(p.encode())
dump(B/'oracle.json',data['oracle']);dump(B/'report.json',data['report']);dump(B/'packets.json',data['packets'])
(B/'fixture.json').write_bytes(case.TEXT.encode());(B/'.gitattributes').write_bytes(b'* -text\n')
def schema(v):
    if type(v) is bool:return {'type':'boolean'}
    if type(v) is int:return {'type':'integer'}
    if type(v) is str:return {'type':'string'}
    if type(v) is list:return {'type':'array','items':schema(v[0]) if v else {'type':'string'},'maxItems':20}
    return {'type':'object','properties':{k:schema(x) for k,x in v.items()},'required':list(v),'additionalProperties':False}
dump(B/'schema.json',schema(data['oracle']))
settings=read(R/'agent_doc/results/token-010-maintenance-20261011/settings.json');settings['cwd']=str(R)
settings['config']['skills.config']=[{'path':str(Path.home()/'.agents/skills'/r['id']/'SKILL.md'),'enabled':False} for r in read(R/'config/role_registry.json')['roles']]
settings['config']['mcp_servers.cua_repl.enabled']=False
settings['config']['mcp_servers.cua_repl.command']='C:/Windows/System32/cmd.exe'
dump(B/'settings.json',settings)
seeds=case.SOURCES+['.agent-runs/token-fifty-03-r2/'+n for n in ('common.py','native.py','case_3.py','freeze.py')]
needed=set(seeds);pending=list(seeds)
while pending:
    path=pending.pop();tree=ast.parse((R/path).read_bytes())
    for ancestor in Path(path).parents:
        candidate=(ancestor/'__init__.py').as_posix()
        if (R/candidate).is_file() and candidate not in needed:needed.add(candidate);pending.append(candidate)
    package='.'.join(Path(path).parts[:-1]) if path.startswith(('agent_runtime/','tests/','scripts/')) else ''
    for node in ast.walk(tree):
        names=[]
        if isinstance(node,ast.Import):names=[a.name for a in node.names]
        elif isinstance(node,ast.ImportFrom):
            if node.level and not package:continue
            name=importlib.util.resolve_name('.'*node.level+(node.module or ''),package) if node.level else (node.module or '')
            names=[name]+[name+'.'+a.name for a in node.names if a.name!='*']
        for name in names:
            if not name.startswith(('agent_runtime.','scripts.','tests.')):continue
            candidate=name.replace('.','/')+'.py'
            if (R/candidate).is_file() and candidate not in needed:needed.add(candidate);pending.append(candidate)
rows=[]
for path in sorted(needed):
    dest=B/'code_snapshot'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((R/path).read_bytes())
    rows.append({'path':path,'sha256':sha(R/path),'archive_path':dest.relative_to(R).as_posix()})
dump(B/'source-inventory.json',{'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'files':rows})
dump(B/'environment.json',{'platform':platform.platform(),'python':sys.version,'executable':sys.executable,'binary_sha256':sha(EXE),'binary_version':subprocess.check_output([str(EXE),'--version'],text=True).strip(),'cpu':platform.processor(),'fixture':'synthetic deterministic no RNG; provider stochastic'})
dump(B/'config.json',{'binary_sha256':sha(EXE),'user_config_sha256':sha(Path.home()/'.codex/config.toml'),'model':settings['model'],'effort':'high','mechanism':case.MECHANISM,'tests':case.TESTS,'expected_tests':case.COUNT,'observational_caps':limits})
bindings={x['path']:x['sha256'] for x in rows}
for f in B.iterdir():
    if f.is_file():bindings[f.relative_to(R).as_posix()]=sha(f)
dump(B/'freeze.json',{'hashes':bindings,'actual_plan_sha256':sha(B/'task-chain.json'),'independent_plan_review_sha256':sha(P/'reviews/round03-plan-review.json')})
p=subprocess.run([sys.executable,'-X','utf8','-m','unittest',*case.TESTS,'-q'],cwd=R,capture_output=True,text=True,encoding='utf-8',timeout=60)
(B/'producer-tests.log').write_bytes((p.stdout+p.stderr).encode())
assert p.returncode==0 and f'Ran {case.COUNT} tests' in p.stderr
dump(B/'producer-cpu.json',{'actor':'root-native-producer','pid':__import__('os').getpid(),'tests':case.COUNT,'replay':case.replay(R)})
print(json.dumps({'frozen':B.name,'prompt_chars':{k:len(v) for k,v in data['prompts'].items()},'source_files':len(rows),'tests':case.COUNT,'model_calls':0}))
