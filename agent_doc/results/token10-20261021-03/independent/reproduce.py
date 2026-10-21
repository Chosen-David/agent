"""Independent byte-preserving subprocess replay, separate from producer harness."""
SOURCE_REVIEW='project_memory.main changes success JSON whitespace only; index keeps canonical budget-aware serializer, stderr exception paths and return2 unchanged; actual refusal is check missing, not invalid show command.'
LIMITATION='Representative list/storage/check-missing CLI cases only; no claim about new memory algorithm or model tokens. Existing index compact format remains unchanged.'
import sys,os,json,hashlib,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
N=int(OUT.name)
BASE=ROOT/f'agent_doc/results/token10-20261021-{N:02d}'
sys.path[:0]=[str(ROOT),str(ROOT/'.agent-runs/memory-index96-deps')]
os.environ['TIKTOKEN_CACHE_DIR']=str(ROOT/'.agent-runs/memory-index96-token-cache')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def write(p,v):p.write_bytes((dump(v)+'\n').encode())
def inv(p):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file()}
m=json.loads((BASE/'manifest.json').read_bytes());c=json.loads((BASE/'contract.json').read_bytes())
bindings={c['validation_plan']['path']:c['validation_plan']['sha256']}
for refs in m['artifacts'].values():
 for r in refs:bindings[r['path']]=r['sha256']
for p,h in bindings.items():assert sha(ROOT/p)==h,p
import tiktoken
assert tiktoken.__version__=='0.12.0'
enc=tiktoken.get_encoding('o200k_base');count=lambda s:len(enc.encode(s,disallowed_special=()))
env_record=json.loads((BASE/'environment.json').read_bytes())
ranks=hashlib.sha256()
for token,rank in sorted(enc._mergeable_ranks.items(),key=lambda x:x[1]):
 ranks.update(len(token).to_bytes(4,'big'));ranks.update(token);ranks.update(rank.to_bytes(4,'big'))
assert ranks.hexdigest()==env_record['ranks_sha256']
raw=json.loads((BASE/'raw.json').read_bytes());inputs=json.loads((BASE/'inputs.json').read_bytes())
assert len(raw)==3 and [r['case'] for r in raw]==inputs['cases']
home=Path(inputs['fixture_root']);before=inv(home)
assert before==inputs['before_sha256']==inputs['after_sha256']
with zipfile.ZipFile(BASE/'fixture.zip') as z:
 archived={name:hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist()}
assert archived==before
env={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(ROOT)}
rows=[]
for r in raw:
 pair=[]
 for side in ('before','after'):
  data=r[side];p=subprocess.run(data['command'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
  text=p.stdout.decode('utf-8');err=p.stderr.decode('utf-8')
  assert text==data['stdout'],(r['case'],side,'stdout')
  assert err==data['stderr'] and p.returncode==data['exit'],(r['case'],side,'exit/stderr')
  assert count(text)==data['tokens'] and len(p.stdout)==data['bytes']
  pair.append((text,err,p.returncode))
 assert pair[0][1:]==pair[1][1:]
 try:a=json.loads(pair[0][0]);b=json.loads(pair[1][0])
 except ValueError:assert pair[0][0]==pair[1][0]
 else:assert dump(a)==dump(b)
 rows.append({'case':r['case'],'exit':pair[0][2],'before_tokens':r['before']['tokens'],
              'after_tokens':r['after']['tokens'],'before_bytes':r['before']['bytes'],
              'after_bytes':r['after']['bytes'],'default_has_crlf':'\r\n' in pair[0][0],
              'compact_has_crlf':'\r\n' in pair[1][0]})
assert any(r['after_tokens']<r['before_tokens'] for r in rows)
assert inv(home)==before
# Re-execute the parent revision's original entry using its original __file__
# and package, so default stdout can be checked against the pre-change code.
first=raw[0]['before']['command']
if first[3]=='-m':
 target=first[4];entry=target.replace('.','/')+'.py'
 if not (ROOT/entry).exists():entry=target.replace('.','/')+'/__main__.py'
 args=first[5:];package=target.rpartition('.')[0]
else:
 entry=Path(first[3]).relative_to(ROOT).as_posix();args=first[4:];package=''
old_revision=m['code_revision'].split('+',1)[0]
old=subprocess.check_output(['git','show',old_revision+':'+entry],cwd=ROOT).decode('utf-8')
oldfile=OUT/'parent-entry.py';oldfile.write_bytes(old.encode('utf-8'))
loader='import sys,pathlib;sys.argv=['+repr(str(ROOT/entry))+']+sys.argv[1:];exec(compile(pathlib.Path('+repr(str(oldfile))+').read_text(encoding="utf-8"),'+repr(str(ROOT/entry))+',"exec"),{"__name__":"__main__","__file__":'+repr(str(ROOT/entry))+',"__package__":'+repr(package)+'})'
p=subprocess.run([sys.executable,'-B','-X','utf8','-c',loader,*args],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=45)
assert p.stdout.decode('utf-8')==raw[0]['before']['stdout'],'old default stdout'
assert p.stderr.decode('utf-8')==raw[0]['before']['stderr'] and p.returncode==raw[0]['before']['exit'],'old default exit/stderr'
assert inv(home)==before
for p,h in bindings.items():assert sha(ROOT/p)==h,p
obs={'result_id':m['result_id'],'rows':rows,'tokenizer_ranks_sha256':ranks.hexdigest(),
     'all_bound_hashes_unchanged':True,'fixture_archive_complete_and_unchanged':True,
     'original_default_bytes_equal_parent_revision':old_revision,'source_review':SOURCE_REVIEW}
write(OUT/'observations.json',obs)
archive=f'agent_doc/results/token10-20261021-{N:02d}/independent/'
evidence=[{'path':archive+f,'sha256':sha(OUT/f)} for f in ('observations.json','reproduce.py')]
reasons={
 'implementation':'Independently read changed real CLI entry and shared renderer; '+SOURCE_REVIEW,
 'reference_boundary':'Type-sensitive canonical JSON comparison preserves all values; small and rejected paths retained, exits/stderr identical. Parent-revision default command yields exact same stdout bytes.',
 'data_integrity':'All three raw paired commands re-executed independently; complete fixture ZIP equals recorded source inventory, unchanged after runs; all manifest artifact hashes match.',
 'numerical_sanity':'Every raw stdout token and UTF-8 byte count recomputed; exact named metrics checked against raw pairs; finite integer values and at least one strict reduction.',
 'measurement_validity':'Actual binary subprocess output includes Windows newlines; pinned tiktoken0.12.0 and o200k_base rank hash match. Full stdout decoded as UTF-8; no envelope/timing/model accounting claim.',
 'reproducibility':'Fresh independent replay of all three before/after commands plus original parent default matches exact output/exit/stderr and fixtures remain unchanged.'}
metrics={v['name']:v['value'] for v in m['metrics']}
for r in raw:
 for side in ('before','after'):
  for metric in ('tokens','bytes'):assert metrics[r['case']+':'+side+':'+metric]==r[side][metric]
review={'schema_version':'experiment-validation/v1','manifest_sha256':sha(BASE/'manifest.json'),
 'artifact_hashes':bindings,'validation_plan_sha256':c['validation_plan']['sha256'],'scope':m['scope'],
 'verifier':{'actor':'/root/token10_verifier','independent':True,'source':'native independent agent source review and tools',
 'run_id':f'token10-review-{N:02d}-v1','method':'manual source and raw-data review; independent complete subprocess replay, counter and old-default comparison'},
 'limitations':['Only three declared synthetic local CLI cases and their exact dependency/configuration scope; no live model, QA, cash, timing or blanket correctness claim.',LIMITATION],
 'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()}}
write(OUT/'review.json',review)
print(dump({'status':'usable-with-scope','rows':rows,'files':{f:sha(OUT/f) for f in ('review.json','observations.json','reproduce.py')}}))
