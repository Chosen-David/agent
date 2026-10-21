"""New independent current-source acceptance; no historical pass is consumed."""
import sys,os,json,hashlib,subprocess,zipfile,base64,tempfile,sqlite3
from pathlib import Path
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
BASE=ROOT/'agent_doc/results/token10-20261021-final'
sys.path[:0]=[str(ROOT),str(ROOT/'.agent-runs/memory-index96-deps')]
os.environ['TIKTOKEN_CACHE_DIR']=str(ROOT/'.agent-runs/memory-index96-token-cache')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def write(p,v):p.write_bytes((dump(v)+'\n').encode())
def inv(home):return {p.relative_to(home).as_posix():sha(p) for p in sorted(home.rglob('*')) if p.is_file()}
def reject(fn):
 try:fn()
 except ValueError:return
 raise AssertionError('missing expected refusal')
m=json.loads((BASE/'manifest.json').read_bytes());c=json.loads((BASE/'contract.json').read_bytes())
bindings={c['validation_plan']['path']:c['validation_plan']['sha256']}
for refs in m['artifacts'].values():
 for r in refs:bindings[r['path']]=r['sha256']
for p,h in bindings.items():assert sha(ROOT/p)==h,p
raw=json.loads((BASE/'raw.json').read_bytes());assert len(raw)==30
assert [(r['round'],r['case']) for r in raw]==[(n,case) for n in range(1,11) for case in (('large','small','fresh-mailbox') if n==1 else ('large','small','rejected'))]
import tiktoken
assert tiktoken.__version__=='0.12.0';enc=tiktoken.get_encoding('o200k_base');count=lambda s:len(enc.encode(s,disallowed_special=()))
ranks=hashlib.sha256()
for token,rank in sorted(enc._mergeable_ranks.items(),key=lambda p:p[1]):
 ranks.update(len(token).to_bytes(4,'big'));ranks.update(token);ranks.update(rank.to_bytes(4,'big'))
environment=json.loads((BASE/'environment.json').read_bytes());assert ranks.hexdigest()==environment['ranks_sha256']
assert {p.name:sha(p) for p in Path(tiktoken.__file__).parent.glob('*.pyd')}==environment['tokenizer_binary']
COLS=['id','status','depends_on','artifact_ids','knowledge_ids','memory_ids','assumptions']
MEM=['id','kind','content','source','scope','evidence','status','created_at','document_refs','deps']
def restore(text):
 value=json.loads(text);fmt=value.pop('context_format',None)
 if fmt:
  assert fmt in ('claims-table/v1','basis-tables/v1')
  for name,cols in [('evidence_claims',COLS)]+([('memory_entries',MEM)] if fmt=='basis-tables/v1' else []):
   table=value[name];assert table['columns']==cols
   value[name]=[dict(zip(cols,row,strict=True)) for row in table['rows']]
 return value
def candidates(value):
 a=deepcopy(value);opts=[dump(a)]
 a['context_format']='claims-table/v1';a['evidence_claims']={'columns':COLS,'rows':[[x[k] for k in COLS] for x in value['evidence_claims']]};opts.append(dump(a))
 a['context_format']='basis-tables/v1';a['memory_entries']={'columns':MEM,'rows':[[x[k] for k in MEM] for x in value['memory_entries']]};opts.append(dump(a))
 return opts
from agent_runtime.handoff_encoding import choose_basis_payload
first=json.loads((ROOT/'agent_doc/results/token10-20261021-01/raw.json').read_bytes())
observed=[]
for row,golden in zip(raw[:2],first[:2],strict=True):
 value=restore(golden['before']);opts=candidates(value)
 expected=min(enumerate(opts),key=lambda x:(count(x[1]),len(x[1]),x[0]))[1]
 text,t=choose_basis_payload(value,count);assert text==expected==golden['after'] and dump(restore(text))==dump(value)
 assert row['before_tokens']==count(golden['before']) and row['after_tokens']==count(text)==t
 observed.append({'round':1,'case':row['case'],'candidate_tokens':[count(x) for x in opts],'before':row['before_tokens'],'after':t})
home=Path(tempfile.mkdtemp(prefix='mailbox-',dir=OUT))
with zipfile.ZipFile(BASE/'fresh-mailbox.zip') as z:z.extractall(home)
from agent_runtime.communication import Mailbox
from agent_runtime.handoff_basis import make_token_counter
from agent_runtime.project_memory import MemoryLedger
with sqlite3.connect(home/'mail.sqlite') as db:event=json.loads(db.execute('SELECT body FROM communication_events WHERE seq=1').fetchone()[0])
plan=json.loads((home/'plan.json').read_bytes());box=Mailbox(home/'independent.sqlite',plan,home);box.publish(event)
request={'schema_version':1,'input_version':'v1','tasks':[{'task_id':'T1'}],'knowledge_refs':[],
 'memory_refs':['m3'],'memory_required':True,'knowledge_required':False,'context_format':'auto-lossless/v1'}
counter=make_token_counter('o200k_base');actual=box.prepare_context('auto',1,request,token_counter=counter,max_chars=200000)
assert dump(actual)==dump(raw[2]['auto'])
assert dump(restore(actual['payload']))==dump(json.loads(raw[2]['plain']['payload']))
assert count(actual['payload'])==raw[2]['after_tokens'] and count(raw[2]['plain']['payload'])==raw[2]['before_tokens']
for cap in ({'max_chars':1},{'max_tokens':1}):reject(lambda:box.prepare_context('auto',1,request,token_counter=counter,**cap))
reject(lambda:box.prepare_context('auto',1,request))
reject(lambda:box.prepare_context('auto',1,{**request,'context_max_chars':1},token_counter=counter))
MemoryLedger(home).correct('m0','m0-new','corrected','synthetic:final-independent','stale boundary')
reject(lambda:box.prepare_context('auto',1,request,token_counter=counter))
observed.append({'round':1,'case':'fresh-mailbox','before':raw[2]['before_tokens'],'after':raw[2]['after_tokens'],'closure_entries':len(restore(actual['payload'])['memory_entries']),'budget_immutable_counter_correction_rejections':True})
env={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(ROOT)}
host=[]
def wsl(code,*args):
 p=subprocess.run(['wsl','--exec','python3','-X','utf8','-c',code,*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 host.append(p.stderr.hex());assert p.returncode==0,p.stderr
 return json.loads(p.stdout)
inspect='''import pathlib,hashlib,os,json,sys,platform,sqlite3
source=pathlib.Path(sys.argv[1]);root=pathlib.Path(sys.argv[2]);files={};links={}
for p in sorted(root.rglob('*')):
 if p.is_symlink():links[p.relative_to(root).as_posix()]={'target':str(p.resolve()),'link':os.readlink(p)}
 elif p.is_file():files[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
print(json.dumps({'fixture':{'files':files,'symlinks':links},'source':{p:hashlib.sha256((source/p).read_bytes()).hexdigest() for p in json.loads(sys.argv[3])},'env':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version}}))'''
subject='''import sys,subprocess,os,json,base64
p=subprocess.run([sys.executable,'-X','utf8',sys.argv[1]+'/scripts/run_role.py','--project',sys.argv[2],'--dry-run','--role',sys.argv[3],*sys.argv[4:]],cwd=sys.argv[1],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1'},stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(json.dumps({'out':base64.b64encode(p.stdout).decode(),'err':base64.b64encode(p.stderr).decode(),'code':p.returncode}))'''
commands=0;fixture_count=0
for n in range(2,11):
 suffix='-04-v2' if n==4 else ('-09-v3' if n==9 else f'-{n:02d}')
 run=ROOT/('agent_doc/results/token10-20261021'+suffix)
 original=json.loads((run/'raw.json').read_bytes());inp=json.loads((run/'inputs.json').read_bytes())
 home=inp['fixture_root'] if n==9 else Path(inp['fixture_root'])
 if n==9:
  source=inp['source_root'];paths=[r['path'] for r in inp['source_files']]
  current={r['path']:sha(ROOT/r['path']) for r in inp['source_files']}
  assert current=={r['path']:r['sha256'] for r in inp['source_files']}
  before=wsl(inspect,source,str(home),json.dumps(paths))
  assert before['source']==current and before['fixture']==inp['after_sha256']
  linux=json.loads((run/'linux-fixture.json').read_bytes());assert before['env']=={k:linux[k] for k in ('python','executable','platform','sqlite')}
  with zipfile.ZipFile(run/'source.zip') as z:assert {p:hashlib.sha256(z.read(p)).hexdigest() for p in z.namelist()}==current
 else:before=inv(home);assert before==inp['after_sha256']
 with zipfile.ZipFile(run/'fixture.zip') as z:
  assert {p:hashlib.sha256(z.read(p)).hexdigest() for p in z.namelist()}==(before['fixture']['files'] if n==9 else before)
 for old in original:
  row=next(r for r in raw if r['round']==n and r['case']==old['case']);pair=[]
  for kind in ('before','after'):
   data=row[kind];assert dump(data)==dump(old[kind])
   if n==9:
    role=('research-implement-optimize','research-write','missing')[('large','small','rejected').index(row['case'])]
    got=wsl(subject,source,str(home),role,*(['--compact'] if kind=='after' else []))
    output=base64.b64decode(got['out'],validate=True);error=base64.b64decode(got['err'],validate=True);code=got['code'];assert b'\r' not in output
   else:
    p=subprocess.run(data['command'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
    output,error,code=p.stdout,p.stderr,p.returncode
   commands+=1;text=output.decode('utf-8');err=error.decode('utf-8')
   assert (text,err,code)==(data['stdout'],data['stderr'],data['exit'])
   assert len(output)==data['bytes'] and count(text)==data['tokens']==row[kind+'_tokens']
   pair.append((text,error,code))
  assert pair[0][1:]==pair[1][1:]
  try:a=json.loads(pair[0][0]);b=json.loads(pair[1][0])
  except ValueError:assert pair[0][0]==pair[1][0]
  else:assert dump(a)==dump(b)
  observed.append({'round':n,'case':row['case'],'before':row['before_tokens'],'after':row['after_tokens'],'exit':pair[0][2]})
 if n==9:assert wsl(inspect,source,str(home),json.dumps(paths))==before
 else:assert inv(home)==before
 fixture_count+=1
metrics={r['name']:r['value'] for r in m['metrics']};assert len(metrics)==60
for row in raw:
 for kind in ('before','after'):assert metrics[f"{row['round']:02d}:{row['case']}:{kind}"]==row[kind+'_tokens']
assert commands==54 and fixture_count==9
for p,h in bindings.items():assert sha(ROOT/p)==h,p
obs={'result_id':m['result_id'],'independent_subject_commands':commands,'readonly_fixture_trees':fixture_count,
 'rows':observed,'current_bound_code_files':len(m['artifacts']['code']),'all_bound_hashes_before_after_equal':True,
 'counter_ranks_sha256':ranks.hexdigest(),'WSL_host_diagnostics_hex':host,
 'source_review':'Reviewed all ten production diffs and actual CLI branches during this batch; final current hashes equal declared126-code union. New final script directly re-executed54 subject commands, not old pass files. Auto oracle reconstructed literal columns; fresh Mailbox delivery replay retained exact saved artifacts/ledger in isolated root and checked stale/immutable/counter/budget gates.'}
write(OUT/'observations.json',obs)
archive='agent_doc/results/token10-20261021-final/independent/'
evidence=[{'path':archive+f,'sha256':sha(OUT/f)} for f in ('observations.json','reproduce.py')]
reasons={
 'implementation':'Current126-code union and all impacting artifacts hash-checked before/after; reviewed actual producer integration and previously read production branches. No semantic/source mutation arose; direct54-command replay exercises current CLI integration.',
 'reference_boundary':'Independent literal-column auto candidate oracle and isolated fresh Mailbox budget/counter/immutable/correction rejection checks; full JSON scalar type/value equality for all27 CLI pairs. Negative/zero-gain controls retained.',
 'data_integrity':'All30 cases and60 metric names checked, all10 frozen input sets/current bindings inspected. Nine complete archives equal actual readonly fixture bytes; WSL16links/source snapshot and25file identities unchanged.',
 'numerical_sanity':'Recounted every payload/complete CLI stdout token plus27pair UTF8 bytes from actual output. Counts finite and exact; no aggregate heterogeneous-token savings invented; zero-gain/refusal examples preserved.',
 'measurement_validity':'Actual Windows CRLF output or explicitly scoped09 WSL LF bytes measured. Pinned0.12.0/o200k ranks/pyd hashes and WSL subject environment match. Base64/host diagnostics excluded, no model/cash/QA/latency claims.',
 'reproducibility':'Independent new owner-node replayed54 actual CLI subject commands including direct WSL bypass of producer bridge, all30 row counts, auto enumeration and fresh isolated Mailbox; all9 readonly trees andcurrentsource bindings unchanged.'}
review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(BASE/'manifest.json'),'artifact_hashes':bindings,
 'validation_plan_sha256':c['validation_plan']['sha256'],'scope':m['scope'],
 'verifier':{'actor':'/root/token10_verifier','independent':True,'source':'native independent agent tools and manual production/integration review',
 'run_id':'token10-review-final-v1','method':'new current-source54-subprocess replay plus independent counter/oracle/fresh Mailbox and all artifact/source/fixture checks'},
 'limitations':['Only declared synthetic local payload/CLI transport cases; no total session/model tokens, cash, QA, timing, online backend or universal/full-library correctness claim.',
 'Round07 success controls duplicate one capabilities shape; zero-gain controls remain. Round09 measured real WSL Linux LF subject, native Windows symlink failure and stale tmp-root v2 remain unaccepted history.',
 'Historical Windows regression cleanup failures and WSL retry scope remain recorded; final measurement does not claim native full-unit-suite success. Fresh Mailbox archive is root-bound; exact envelope rebuilt in isolated delivery DB while retaining artifact/ledger bytes.'],
 'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()}}
write(OUT/'review.json',review)
print(dump({'status':'usable-with-scope','commands':commands,'rows':len(observed),'files':{f:sha(OUT/f) for f in ('review.json','observations.json','reproduce.py')}}))
