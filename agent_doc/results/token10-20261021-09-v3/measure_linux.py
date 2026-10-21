"""Actual Linux dry-run output; pinned Windows tokenizer, no model dispatch."""
import json,os,platform,sqlite3,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'));import measure_token10 as m
import tiktoken
assert tiktoken.__version__=='0.12.0';encoding=tiktoken.get_encoding('o200k_base');count=lambda s:len(encoding.encode(s,disallowed_special=()))
linux_path='/mnt/'+out.drive[0].lower()+out.as_posix()[2:]+'/initialize_linux.py'
def inspect():
 p=subprocess.run(['wsl','--exec','python3',linux_path,'--inspect'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
 p.check_returncode();return json.loads(p.stdout),p.stderr
initial,host=inspect();info=json.loads((out/'linux-fixture.json').read_bytes());assert initial==info['fixture']
env={**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'}
commands=[[sys.executable,'-X','utf8',str(out/'replay.py'),'--role',role] for role in ('research-implement-optimize','research-write','missing')]
raw=[];log=ROOT/'.agent-runs/token10-20261021/wsl09-host.log';offset=log.stat().st_size if log.exists() else 0
for case,command in zip(('large','small','rejected'),commands):
 pair=[]
 for compact in (False,True):
  actual=command+(['--compact'] if compact else []);p=subprocess.run(actual,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
  text=p.stdout.decode('utf-8');stderr=p.stderr.decode('utf-8');pair.append({'command':actual,'stdout':text,'stderr':stderr,'exit':p.returncode,'tokens':count(text),'bytes':len(p.stdout)})
 assert (pair[0]['exit'],pair[0]['stderr'])==(pair[1]['exit'],pair[1]['stderr'])
 if pair[0]['stdout']:assert m.dump(json.loads(pair[0]['stdout']))==m.dump(json.loads(pair[1]['stdout']))
 else:assert not pair[1]['stdout']
 raw.append({'case':case,'before':pair[0],'after':pair[1]})
final,host2=inspect();assert final==initial
(out/'host-diagnostics.bin').write_bytes(host+log.read_bytes()[offset:]+host2)
m.write(out/'raw.json',raw);m.write(out/'inputs.json',{'commands':commands,'fixture_root':info['project'],'source_root':info['source'],'subject_platform':'WSL Linux, LF','before_sha256':initial,'after_sha256':final,'source_files':json.loads((out/'source-files.json').read_bytes())})
windows=json.loads((ROOT/'agent_doc/results/token10-20261021-08/environment.json').read_bytes())
assert windows['python']==sys.version and windows['tiktoken']==tiktoken.__version__ and windows['encoding']==encoding.name
m.write(out/'environment.json',{'subject':{k:info[k] for k in ('python','platform','executable','sqlite')},'counter':windows,'bridge':'transparent byte/stdout/stderr/exit forwarding; base64/host diagnostics excluded from subject costs'})
plan=json.loads((out/'validation_plan.json').read_bytes());contract={'result_id':out.name,'producer_task_id':'produce-09-v2','producer_actor':'/root','manifest_path':(out/'manifest.json').relative_to(ROOT).as_posix(),'validation_plan':m.ref(out/'validation_plan.json'),'scope':plan['scope']}
source_refs=json.loads((out/'source-files.json').read_bytes());code=[r for r in source_refs if r['path'].endswith('.py')]+[m.ref(out/name) for name in ('replay.py','initialize_linux.py','measure_linux.py')]+[m.ref(ROOT/'scripts/measure_token10.py')]
inputs=[m.ref(out/name) for name in ('source.zip','source-files.json','fixture.zip','linux-fixture.json','inputs.json')]+[r for r in source_refs if not r['path'].endswith('.py')]+[m.ref(ROOT/'agent_doc/results/token10-20261021-09'/name) for name in ('failure.json','reproduce_measurement.py','role-inputs.zip')]
m.write(out/'manifest.json',{'schema_version':'experiment-result/v1',**contract,'run_id':out.name,'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()+'+exact-bound-WSL-source','execution':{'command':['wsl --exec python3 '+linux_path,'python -X utf8 '+Path(__file__).relative_to(ROOT).as_posix()],'environment_description':'Real WSL Linux install/symlinks and run_role --dry-run; whole subject UTF8 stdout LF measured with Windows tiktoken0.12.0/o200k_base; no model or adapter','seeds':['deterministic-public-v2'],'repeats':1},'artifacts':{'code':code,'inputs':inputs,'config':[m.ref(out/'config.json')],'raw_data':[m.ref(out/'raw.json'),m.ref(out/'tests.txt'),m.ref(out/'initialize-stdout.txt'),m.ref(out/'initialize-host-stderr.bin'),m.ref(out/'host-diagnostics.bin')],'outputs':[m.ref(out/'inputs.json')],'environment':[m.ref(out/'environment.json')]},'metrics':[{'name':r['case']+':'+kind+':'+metric,'value':r[kind][metric],'unit':'o200k_base text tokens' if metric=='tokens' else 'UTF-8 bytes'} for r in raw for kind in ('before','after') for metric in ('tokens','bytes')]})
m.write(out/'contract.json',contract)
print([(r['case'],r['before']['tokens'],r['after']['tokens'],r['before']['exit']) for r in raw])
