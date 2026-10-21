"""Fresh current-source integration; old reports remain historical evidence."""
import hashlib,json,os,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import measure_token10 as m
import tiktoken
from agent_runtime.handoff_encoding import choose_basis_payload,decode_basis_payload
from agent_runtime.handoff_basis import make_token_counter
out=Path(__file__).resolve().parent
count=make_token_counter('o200k_base');rows=[];inputs=[];codes={Path(__file__).relative_to(ROOT).as_posix(),'scripts/measure_token10.py'}
env={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(ROOT)}
for n in range(1,11):
 run=ROOT/f'agent_doc/results/token10-20261021-{n:02d}'
 if n==4:run=ROOT/'agent_doc/results/token10-20261021-04-v2'
 if n==9:run=ROOT/'agent_doc/results/token10-20261021-09-v3'
 manifest=json.loads((run/'manifest.json').read_bytes());frozen=json.loads((run/'raw.json').read_bytes())
 if n==9:
  for record in json.loads((run/'source-files.json').read_bytes()):assert m.ref(ROOT/record['path'])==record
 inputs += [m.ref(run/name) for name in ('manifest.json','inputs.json','fixture.zip','raw.json','config.json')]
 codes.update(p['path'] for p in manifest['artifacts']['code'])
 if n==1:
  for row in frozen[:2]:
   value=decode_basis_payload(row['before']);text,tokens=choose_basis_payload(value,count)
   assert m.dump(decode_basis_payload(text))==m.dump(value) and text==row['after'] and tokens==row['after_tokens']
   rows.append({'round':n,'case':row['case'],'before_tokens':count(row['before']),'after_tokens':tokens,'exact_current_reproduction':True})
  home=ROOT/'.agent-runs/token10-20261021/final-mailbox';home.mkdir(exist_ok=False)
  box,record,request=m.mailbox(home,4)
  plain=box.prepare_context('reader',1,request,token_counter=count,max_chars=200000)
  auto=box.prepare_context('auto',1,{**request,'context_format':'auto-lossless/v1'},token_counter=count,max_chars=200000)
  assert m.dump(decode_basis_payload(auto['payload']))==m.dump(json.loads(plain['payload']))
  rejects=[]
  for kwargs in ({'max_chars':1},{'max_tokens':1}):
   try:box.prepare_context('auto',1,{**request,'context_format':'auto-lossless/v1'},token_counter=count,**kwargs)
   except ValueError:rejects.append(kwargs)
   else:raise ValueError('budget bypass')
  rows.append({'round':1,'case':'fresh-mailbox','before_tokens':count(plain['payload']),'after_tokens':count(auto['payload']),'plain':plain,'auto':auto,'rejections':rejects})
  with zipfile.ZipFile(out/'fresh-mailbox.zip','w',zipfile.ZIP_DEFLATED) as z:
   for p in sorted(home.rglob('*')):
    if p.is_file():z.write(p,p.relative_to(home).as_posix())
 else:
  home=Path(json.loads((run/'inputs.json').read_bytes())['fixture_root'])
  def tree():
   if n!=9:return m.inventory(home)
   linux='/mnt/'+run.drive[0].lower()+run.as_posix()[2:]+'/initialize_linux.py'
   p=subprocess.run(['wsl','--exec','python3',linux,'--inspect'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120);p.check_returncode();return json.loads(p.stdout)
  initial=tree()
  if n==9:
   probe="import json,platform,sqlite3,sys;print(json.dumps({'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version}))"
   p=subprocess.run(['wsl','--exec','python3','-c',probe],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120);p.check_returncode()
   info=json.loads((run/'linux-fixture.json').read_bytes());assert json.loads(p.stdout)=={k:info[k] for k in ('python','executable','platform','sqlite')}
  expected=json.loads((run/'inputs.json').read_bytes())['after_sha256'];assert initial==expected
  for row in frozen:
   observed={}
   for kind in ('before','after'):
    old=row[kind];p=subprocess.run(old['command'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
    stdout=p.stdout.decode('utf-8');stderr=p.stderr.decode('utf-8')
    assert (stdout,stderr,p.returncode)==(old['stdout'],old['stderr'],old['exit']),(n,row['case'],kind,'current output differs')
    assert (len(p.stdout),count(stdout))==(old['bytes'],old['tokens'])
    observed[kind]={'stdout':stdout,'stderr':stderr,'exit':p.returncode,'bytes':len(p.stdout),'tokens':count(stdout),'command':old['command']}
   rows.append({'round':n,'case':row['case'],**observed,'before_tokens':observed['before']['tokens'],'after_tokens':observed['after']['tokens'],'exact_current_reproduction':True})
  assert tree()==initial
  inputs.append({'path':str(home),'inventory':initial})
for module in list(sys.modules.values()):
 file=getattr(module,'__file__',None)
 if file:
  p=Path(file).resolve()
  if p.is_relative_to(ROOT) and '.agent-runs' not in p.parts and p.suffix=='.py':codes.add(p.relative_to(ROOT).as_posix())
m.write(out/'raw.json',rows)
m.write(out/'inputs.json',{'round_inputs':inputs,'scope':'Exact unchanged frozen outputs on current source; all nine readonly trees identical. Historical reports are not current-source acceptance.'})
import platform,sqlite3
encoding=tiktoken.get_encoding('o200k_base');assert tiktoken.__version__=='0.12.0'
ranks=hashlib.sha256()
for token,rank in sorted(encoding._mergeable_ranks.items(),key=lambda p:p[1]):
 ranks.update(len(token).to_bytes(4,'big'));ranks.update(token);ranks.update(rank.to_bytes(4,'big'))
current_environment={'python':sys.version,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version,'tiktoken':tiktoken.__version__,'encoding':encoding.name,'ranks_sha256':ranks.hexdigest(),'pattern':encoding._pat_str,'special_tokens':encoding._special_tokens,'newline':repr(os.linesep),'tokenizer_binary':{p.name:m.sha(p.read_bytes()) for p in Path(tiktoken.__file__).parent.glob('*.pyd')}}
assert current_environment==json.loads((ROOT/'agent_doc/results/token10-20261021-10/environment.json').read_bytes())
m.write(out/'environment.json',current_environment)
plan=json.loads((out/'validation_plan.json').read_bytes())
contract={'result_id':out.name,'producer_task_id':'produce-final','producer_actor':'/root','manifest_path':(out/'manifest.json').relative_to(ROOT).as_posix(),'validation_plan':m.ref(out/'validation_plan.json'),'scope':plan['scope']}
artifact_inputs=[m.ref(out/'inputs.json'),m.ref(out/'fresh-mailbox.zip')]
for n in range(1,11):
 run=ROOT/('agent_doc/results/token10-20261021-09-v3' if n==9 else ('agent_doc/results/token10-20261021-04-v2' if n==4 else f'agent_doc/results/token10-20261021-{n:02d}'))
 artifact_inputs += [m.ref(run/name) for name in ('manifest.json','inputs.json','fixture.zip','raw.json','config.json')]
 if n==9:artifact_inputs += [m.ref(run/name) for name in ('source.zip','source-files.json','linux-fixture.json')]
 for record in json.loads((run/'manifest.json').read_bytes())['artifacts']['inputs']:
  if not record['path'].startswith('agent_doc/results/'):
   current=m.ref(ROOT/record['path']);assert current==record;artifact_inputs.append(current)
m.write(out/'manifest.json',{'schema_version':'experiment-result/v1',**contract,'run_id':out.name,'code_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()+'+bound-integration-script','execution':{'command':['python -X utf8 '+Path(__file__).relative_to(ROOT).as_posix()],'environment_description':'Current Windows Python3.12 binary UTF-8 readonly replays (round09 transparent actual WSL Linux subject LF); exact tokenizer and both subject environments checked; no model invocation','seeds':['deterministic-public-v1'],'repeats':1},'artifacts':{'code':[m.ref(ROOT/p) for p in sorted(codes)],'inputs':artifact_inputs,'config':[m.ref(out/'config.json')],'raw_data':[m.ref(out/'raw.json')],'outputs':[m.ref(out/'inputs.json')],'environment':[m.ref(out/'environment.json')]},'metrics':[{'name':f"{r['round']:02d}:{r['case']}:{kind}",'value':r[kind+'_tokens'],'unit':'o200k_base text tokens'} for r in rows for kind in ('before','after')]})
m.write(out/'contract.json',contract)
print(m.dump({'status':'pending-independent-validation','rows':len(rows),'code_files':len(codes)}))
