import hashlib, importlib.util, json, os, pathlib, re, subprocess, sys, tempfile
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(__file__).parent
sys.path.insert(0,str(ROOT));os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.dont_write_bytecode=True
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
from agent_runtime.text_dictionary import text_view,restore_text_view
from agent_runtime.reference_context import _wire
source=ROOT/'.agent-runs/token-fifty-06/fixture.md'
raw=source.read_bytes(); text=raw.decode('utf-8')
ids=re.findall(r'^Issue-(\d{3}):',text,re.M)
assert ids==[f'{i:03}' for i in range(32)]
assert 'metric_unit=tokens' in text and 'pending' in text
parts=text.split('\n');lines=[p+'\n' for p in parts[:-1]]+([parts[-1]] if parts[-1] else [])
assert len(lines)==65 and len(set(lines))==34
with tempfile.TemporaryDirectory() as tmp:
 r=pathlib.Path(tmp).resolve(); f=r/'source.md';f.write_bytes(raw);sha=H(f)
 baseline=text_view(r,'source.md',sha,full=True);candidate=text_view(r,'source.md',sha)
 table=[];order=[]
 for line in lines:
  if line not in table:table.append(line)
  order.append(table.index(line))
 assert candidate['dictionary']==table and candidate['order']==order
 assert baseline['text'].encode('utf-8')==raw
 assert b''.join(candidate['dictionary'][i].encode('utf-8') for i in candidate['order'])==raw
 for packet in (baseline,candidate):assert restore_text_view(r,_wire(packet),'source.md',sha).encode('utf-8')==raw
 assert len(_wire(candidate))<len(_wire(baseline))
spec=importlib.util.spec_from_file_location('case6',ROOT/'.agent-runs/token-fifty-06/case_6.py');case=importlib.util.module_from_spec(spec);spec.loader.exec_module(case)
public=ROOT/'agent_doc/results/token-fifty-06-20261012/fixture.md'
assert public.exists() and public.read_bytes()==raw
data=case.build(ROOT)
assert data['oracle']['issue_ids']==['Issue-'+i for i in ids]
assert data['oracle']=={'issue_ids':['Issue-'+i for i in ids],'issue_count':32,'last_status':'pending','unit':'tokens','publish':False}
actual_rows=re.findall(r'^Issue-(\d{3}): status=(\w+); owner=reviewer-(\d+)\.$',text,re.M)
assert actual_rows==[(f'{i:03}','pending',str(i%3)) for i in range(32)]
before={str(f):H(f) for f in (public,source)}
assert case.replay(ROOT)['all65line_indexes_retained']
assert before=={str(f):H(f) for f in (public,source)}
result=ROOT/'agent_doc/results/token-fifty-06-20261012'
repair=json.loads((result/'generated-repair.json').read_text())
assert repair['new_optimization_count']==0 and len(repair['files'])==2
for row in repair['files']:
 src=ROOT/row['source'];dst=ROOT/row['generated']
 assert H(src)==H(dst)==row['sha256']
 gitraw=subprocess.check_output(['git','show','HEAD:'+row['source']],cwd=ROOT)
 assert gitraw==src.read_bytes() or gitraw==src.read_bytes().replace(b'\r\n',b'\n')
canonical19=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r','cd489e449cac78f99ad5ad8f8cd70f77d97796f2'],cwd=ROOT).decode().splitlines()
changed=subprocess.check_output(['git','diff','HEAD','--name-only','--',*canonical19],cwd=ROOT).decode().splitlines()
assert not changed,changed
sync=subprocess.run([sys.executable,'scripts/sync_plugin_references.py','--check'],cwd=ROOT,capture_output=True)
assert sync.returncode==0,(sync.stdout+sync.stderr).decode(errors='replace')
test=subprocess.run(['wsl.exe','-d','Ubuntu-26.04','--cd','/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent-token-fifty','--exec','/usr/bin/env','PYTHONDONTWRITEBYTECODE=1','/usr/bin/python3','-m','unittest','tests.test_text_dictionary','-q'],cwd=ROOT,capture_output=True)
test_raw=test.stdout+test.stderr
(OUT/'round06-preflight-tests.raw').write_bytes(test_raw)
log=test_raw.decode('utf-8',errors='replace')
(OUT/'round06-preflight-tests.log').write_text(log,encoding='utf-8')
assert test.returncode==0 and 'Ran 16 tests' in log and '\nOK' in log and 'skipped=' not in log,log
paths=['agent_runtime/text_dictionary.py','scripts/text_dictionary.py','tests/test_text_dictionary.py','agent_runtime/reference_context.py','agent_runtime/maintenance_observer.py','agent_runtime/record_context.py','agent_runtime/advice_poll.py','agent_runtime/context_serialization.py','agent_runtime/token_usage.py','.agent-runs/token-fifty-06/case_6.py','.agent-runs/token-fifty-06/freeze.py','.agent-runs/token-fifty-06/native.py','.agent-runs/token-fifty-06/common.py','.agent-runs/token-fifty-06/fixture.md']
control={'schema_version':'independent-preflight-control/v1','actor':'/root/token_review','tests':{'unique':16,'passed':16,'skipped':0,'platform':'WSL Ubuntu-26.04','log_sha256':H(OUT/'round06-preflight-tests.log'),'raw_sha256':H(OUT/'round06-preflight-tests.raw')},'fixture':{'sha256':H(source),'physical_lf_lines':len(lines),'unique_lines':len(table),'exact_independent_table_and_index_restoration':True,'oracle':data['oracle'],'prompt_characters':{n:len(p) for n,p in data['prompts'].items()}},'generated_repair':{'official_check_exit':sync.returncode,'exact_unchanged_canonical_source_and_generated_bytes':True,'canonical_concurrent_paths_preserved':len(canonical19),'optimization_count':0},'source_hashes':{p:H(ROOT/p) for p in paths},'profile_sha256':H(result/'native-profile.json'),'schema_sha256':H(result/'ThreadStartParams.json'),'model_calls':0}
with (OUT/'round06-preflight-control.json').open('x',encoding='utf-8') as f:json.dump(control,f,indent=2);f.write('\n')
print(json.dumps({'tests':control['tests'],'fixture_sha256':H(source),'oracle_count':len(ids),'prompt_chars':control['fixture']['prompt_characters'],'canonical_paths':len(canonical19),'generated_check':sync.returncode,'control_sha256':H(OUT/'round06-preflight-control.json')}))
