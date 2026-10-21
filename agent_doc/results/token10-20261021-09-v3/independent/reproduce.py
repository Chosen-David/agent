"""Independent direct WSL subject replay; producer bridge is not invoked."""
import sys,os,json,hashlib,subprocess,zipfile,base64
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).parent
BASE=ROOT/'agent_doc/results/token10-20261021-09-v3'
sys.path[:0]=[str(ROOT),str(ROOT/'.agent-runs/memory-index96-deps')]
os.environ['TIKTOKEN_CACHE_DIR']=str(ROOT/'.agent-runs/memory-index96-token-cache')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def write(p,v):p.write_bytes((dump(v)+'\n').encode())
m=json.loads((BASE/'manifest.json').read_bytes());c=json.loads((BASE/'contract.json').read_bytes())
bindings={c['validation_plan']['path']:c['validation_plan']['sha256']}
for refs in m['artifacts'].values():
 for r in refs:bindings[r['path']]=r['sha256']
for p,h in bindings.items():assert sha(ROOT/p)==h,p
inp=json.loads((BASE/'inputs.json').read_bytes());raw=json.loads((BASE/'raw.json').read_bytes())
source=inp['source_root'];home=inp['fixture_root'];hostlog=[]
assert inp['subject_platform']=='WSL Linux, LF'
with zipfile.ZipFile(BASE/'source.zip') as z:
 assert {p:hashlib.sha256(z.read(p)).hexdigest() for p in z.namelist()}=={r['path']:r['sha256'] for r in inp['source_files']}
with zipfile.ZipFile(BASE/'fixture.zip') as z:
 assert {p:hashlib.sha256(z.read(p)).hexdigest() for p in z.namelist()}==inp['before_sha256']['files']
def wsl(code,*args):
 p=subprocess.run(['wsl','--exec','python3','-X','utf8','-c',code,*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
 hostlog.append(p.stderr.hex());assert p.returncode==0,p.stderr
 return json.loads(p.stdout)
inspect_code='''import pathlib,hashlib,os,json,sys
source=pathlib.Path(sys.argv[1]);root=pathlib.Path(sys.argv[2]);files={};links={}
for p in sorted(root.rglob('*')):
 if p.is_symlink():links[p.relative_to(root).as_posix()]={'target':str(p.resolve()),'link':os.readlink(p)}
 elif p.is_file():files[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
print(json.dumps({'files':files,'symlinks':links,'source':{p:hashlib.sha256((source/p).read_bytes()).hexdigest() for p in json.loads(sys.argv[3])}}))'''
paths=[r['path'] for r in inp['source_files']]
before=wsl(inspect_code,source,home,json.dumps(paths))
assert before['source']=={r['path']:r['sha256'] for r in inp['source_files']}
assert {k:before[k] for k in ('files','symlinks')}==inp['before_sha256']==inp['after_sha256']
assert len(before['symlinks'])==16
for rel,link in before['symlinks'].items():assert link['target'].startswith(source+'/plugins/')
import tiktoken
assert tiktoken.__version__=='0.12.0';enc=tiktoken.get_encoding('o200k_base');count=lambda s:len(enc.encode(s,disallowed_special=()))
env=json.loads((BASE/'environment.json').read_bytes());ranks=hashlib.sha256()
for token,rank in sorted(enc._mergeable_ranks.items(),key=lambda p:p[1]):
 ranks.update(len(token).to_bytes(4,'big'));ranks.update(token);ranks.update(rank.to_bytes(4,'big'))
assert ranks.hexdigest()==env['counter']['ranks_sha256']
subject='''import sys,subprocess,os,json,base64
p=subprocess.run([sys.executable,'-X','utf8',sys.argv[1]+'/scripts/run_role.py','--project',sys.argv[2],'--dry-run','--role',sys.argv[3],*sys.argv[4:]],cwd=sys.argv[1],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1'},stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(json.dumps({'out':base64.b64encode(p.stdout).decode(),'err':base64.b64encode(p.stderr).decode(),'code':p.returncode}))'''
rows=[]
for row,role in zip(raw,('research-implement-optimize','research-write','missing'),strict=True):
 outputs=[]
 for side in ('before','after'):
  got=wsl(subject,source,home,role,*(['--compact'] if side=='after' else []));d=row[side]
  out=base64.b64decode(got['out'],validate=True);err=base64.b64decode(got['err'],validate=True)
  text=out.decode('utf-8');assert text==d['stdout'] and err.decode()==d['stderr'] and got['code']==d['exit']
  assert b'\r' not in out and count(text)==d['tokens'] and len(out)==d['bytes']
  outputs.append((text,err,got['code']))
 assert outputs[0][1:]==outputs[1][1:]
 if outputs[0][0]:assert dump(json.loads(outputs[0][0]))==dump(json.loads(outputs[1][0]))
 else:assert not outputs[1][0]
 rows.append({'role':role,'before_tokens':row['before']['tokens'],'after_tokens':row['after']['tokens'],'exit':row['before']['exit'],'LF':True})
assert any(r['after_tokens']<r['before_tokens'] for r in rows)
oldrev=m['code_revision'].split('+',1)[0]
old=subprocess.check_output(['git','show',oldrev+':scripts/run_role.py'],cwd=ROOT)
oldfile=OUT/'parent-entry.py';oldfile.write_bytes(old)
linuxold='/mnt/'+oldfile.drive[0].lower()+oldfile.as_posix()[2:]
oldloader='''import sys,subprocess,os,base64,json
loader="import pathlib,sys;sys.argv=[sys.argv[1]]+sys.argv[3:];exec(compile(pathlib.Path("+repr(sys.argv[3])+").read_text(encoding='utf-8'),"+repr(sys.argv[1]+'/scripts/run_role.py')+",'exec'),{'__name__':'__main__','__file__':"+repr(sys.argv[1]+'/scripts/run_role.py')+"})"
p=subprocess.run([sys.executable,'-X','utf8','-c',loader,sys.argv[1]+'/scripts/run_role.py',sys.argv[3],'--project',sys.argv[2],'--dry-run','--role','research-implement-optimize'],cwd=sys.argv[1],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print(json.dumps({'out':base64.b64encode(p.stdout).decode(),'err':base64.b64encode(p.stderr).decode(),'code':p.returncode}))'''
got=wsl(oldloader,source,home,linuxold)
assert base64.b64decode(got['out']).decode()==raw[0]['before']['stdout']
assert base64.b64decode(got['err']).decode()==raw[0]['before']['stderr'] and got['code']==raw[0]['before']['exit']
after=wsl(inspect_code,source,home,json.dumps(paths));assert after==before
for p,h in bindings.items():assert sha(ROOT/p)==h,p
metrics={v['name']:v['value'] for v in m['metrics']}
for row in raw:
 for side in ('before','after'):
  for key in ('tokens','bytes'):assert metrics[row['case']+':'+side+':'+key]==row[side][key]
obs={'result_id':m['result_id'],'rows':rows,'source_archive_and_live_WSL_source_match':True,
 'fixture_files':len(before['files']),'symlinks':len(before['symlinks']),'fixture_before_after_same':True,
 'parent_default_bytes_match':oldrev,'counter_ranks_sha256':ranks.hexdigest(),'host_diagnostics_hex':hostlog,
 'source_review':'run_role main returns immediately after dry-run route print, before stdin read and dispatch; adapter inventory condition excludes dry-run. New flag only dry-run output and selected-route stderr whitespace; request/native subprocess forwarding unchanged.'}
write(OUT/'observations.json',obs)
archive='agent_doc/results/token10-20261021-09-v3/independent/'
evidence=[{'path':archive+f,'sha256':sha(OUT/f)} for f in ('observations.json','reproduce.py')]
reasons={
 'implementation':'Read actual run_role/bootstrap/definition/resolve/dry-run control flow; source archive/live WSL/current bound files match. Dry-run returns before adapter/native dispatch; flag only metadata formatting.',
 'reference_boundary':'Independent direct inner WSL CLI commands bypass producer bridge; two valid roles and missing role preserve types/values/exits/stderr. Parent-revision default byte comparison matches.',
 'data_integrity':'All six subject outputs and metrics verified, LF asserted, source archive complete; 25 fixture files and16 symlink identities/targets match before and after; native Win1314 failure remains bound.',
 'numerical_sanity':'Recounted every subject text token/UTF8 byte metric, including zeros; implement87to52 and write84to49, unknownexit2; no base64 or host diagnostic token counting.',
 'measurement_validity':'Versioned plan explicitly scopes Linux LF subject output and pinned Windows0.12.0/o200k_base counter. BPE rank hash matches; host diagnostics separately recorded and excluded.',
 'reproducibility':'Independent WSL subprocess replay using actual frozen source/install roots, plus original default code and pre/post full file/symlink/source inventory, all matched.'}
review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(BASE/'manifest.json'),'artifact_hashes':bindings,
 'validation_plan_sha256':c['validation_plan']['sha256'],'scope':m['scope'],
 'verifier':{'actor':'/root/token10_verifier','independent':True,'source':'native independent agent tools/source inspection',
 'run_id':'token10-review-09-v3-v1','method':'direct independent WSL byte/exit replay, source/archive and symlink checks, parent-default comparison and pinned counter'},
 'limitations':['WSL Linux LF subject stdout only; native Windows installation failed required symlink privilege and remains failed evidence.',
 'Two installed-role dry-run previews and missing-role boundary; no live model, authenticated backend, task dispatch, QA, cash or latency claim.',
 'Earlier v2 temporary WSL root vanished and was not accepted; this review binds v3 persistent Linux source/project and fresh measurements only.'],
 'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()}}
write(OUT/'review.json',review)
print(dump({'status':'usable-with-scope','rows':rows,'files':{f:sha(OUT/f) for f in ('review.json','observations.json','reproduce.py')}}))
