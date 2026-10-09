from pathlib import Path
from fractions import Fraction as F
import hashlib,json,sys,tempfile,subprocess
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from agent_runtime.result_validation import _snapshot
c=json.loads((B/'contract.json').read_text());m,p,pf=_snapshot(R,c)
(B/'independent_snapshot.json').write_text(json.dumps(pf,ensure_ascii=False,indent=2)+'\n')
cfg=json.loads((B/'cases.json').read_text());q=[F(0)]
for l in cfg['lengths']:q.append(q[-1]+F(l))
L=max(map(F,cfg['lengths']));grid=[F(i,cfg['grid_denominator']) for i in range(25)]
def scan(x):
 answer=F(0)
 for boundary in q:
  if boundary<=x:answer=boundary
 return answer
rows=[]
def emit(id,values):rows.append(dict(id=id,values=values))
emit('residue-boundary',dict(Q=q,grid=grid,P=[scan(x) for x in grid],gaps=[x-scan(x) for x in grid]))
emit('shifted-boundary-lower',dict(observations=[[a,y,scan(a+y),a+max(F(0),y-L)] for a in q for y in grid if a+y<=q[-1]]))
emit('threshold-sets',dict(sets=[dict(boundary=a,fluid_set=[x for x in grid if x>=a],complete_set=[x for x in grid if scan(x)>=a]) for a in q]))
a=F(1);r=F(2);finish=[a+q[i]/r for i in (1,2)];df=r*(F(2)-a);dc=scan(df)
emit('fifo-record-stream',dict(arrive=a,finish=finish,Df_at2=df,Dc_at2=dc,Bf=q[2]-df,Bc=q[2]-dc,last_boundary_delay_fluid=finish[-1]-a,last_boundary_delay_complete=finish[-1]-a))
emit('nonboundary-target',dict(length=F(2),rate=F(1),partial_hit=F(1),complete_hit=F(2),decision='reject nonboundary equality'))
emit('outoforder-workers',dict(lengths=[F(100),F(1)],second_finished_work=F(1),original_prefix_packetizer=F(0),decision='reject FIFO mapping'))
emit('visibility-stage',dict(compute_finish=F(2),visible_finish=F(3),decision='reject immediate visibility;separate stage'))
emit('tandem-storeforward',dict(length=q[1],rate=r,arrival=a,fluid_tandem_end=a+q[1]/r,intermediate_packetized_end=a+2*q[1]/r,extra_delay=q[1]/r,decision='reject terminal invariance for changed intermediate system'))
emit('never-completes',dict(target=q[1],constant_processed=F(0),fluid_hit_set='empty',complete_hit_set='empty',both_delays='infinity'))
T=F(1);tau=T+L/r
emit('weakened-rate-latency',dict(R=r,T=T,L=L,weakened_parameter=tau,values=[[h,r*max(F(0),h-T),max(F(0),r*max(F(0),h-T)-L)] for h in grid],interpretation='service lower bound parameter;not actual added terminal delay'))
def ser(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,list):return [ser(v) for v in x]
 if isinstance(x,dict):return {k:ser(v) for k,v in x.items()}
 return x
actual=json.loads((B/'raw.json').read_text());expected=ser(rows)
assert expected==actual['records'];assert [row['id'] for row in rows]==cfg['cases']
assert all(0<=x-scan(x)<L for x in grid)
assert all(v[2]>=v[3] for v in rows[1]['values']['observations'])
assert all(v['fluid_set']==v['complete_set'] for v in rows[2]['values']['sets'])
assert all(max(F(0),r*max(F(0),h-T)-L)==r*max(F(0),h-tau) for h in grid)
(B/'independent_exact.json').write_text(json.dumps(dict(method='Fraction linear boundary scan and direct event-time reconstruction; no bisect or producer import',records=expected,all_ten_agree=True),ensure_ascii=False,indent=2)+'\n')
def ref(path):return dict(path=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest())
mirror=R/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge';source=R/'knowledge';pairs=[]
for path in sorted(source.rglob('*')):
 if path.is_file():
  dst=mirror/path.relative_to(source);assert dst.is_file() and path.read_bytes()==dst.read_bytes();pairs.append(dict(source=ref(path),mirror=ref(dst)))
assert len(pairs)==230
assert {p.relative_to(mirror) for p in mirror.rglob('*') if p.is_file()}=={p.relative_to(source) for p in source.rglob('*') if p.is_file()}
candidates=json.loads((B/'candidate_baseline.json').read_text())
for x in candidates:assert ref(R/x['path'])==x
assert len(candidates)==10
(B/'independent_preservation.json').write_text(json.dumps(dict(knowledge_pairs=pairs,candidate_refs=candidates,all_byte_equal=True,preexisting_candidates=5),ensure_ascii=False,indent=2)+'\n')
logs=[]
with tempfile.TemporaryDirectory() as tmp:
 temp=Path(tmp)
 for name in ['cases.json','retrieval_protocol.json']:(temp/name).write_bytes((B/name).read_bytes())
 verify=(B/'verify.py').read_text().replace('B=Path(__file__).resolve().parent;',f'B=Path({str(temp)!r});')
 retrieve=(B/'retrieve.py').read_text().replace('ROOT=Path(__file__).resolve().parents[3]',f'ROOT=Path({str(R)!r})').replace('BASE=Path(__file__).resolve().parent',f'BASE=Path({str(temp)!r})')
 for name,code in [('verify.py',verify),('retrieve.py',retrieve)]:
  (temp/name).write_text(code);res=subprocess.run([sys.executable,str(temp/name)],cwd=R,capture_output=True,text=True);assert res.returncode==0,(res.stdout,res.stderr);logs.append(dict(command=[sys.executable,'redirected-'+name],returncode=res.returncode,stdout=res.stdout,stderr=res.stderr))
 replay=json.loads((temp/'raw.json').read_text());replay.pop('elapsed_seconds');original=dict(actual);original.pop('elapsed_seconds');assert replay==original
 retr=json.loads((temp/'retrieval.json').read_text());orig=json.loads((B/'retrieval.json').read_text())
 for obj in (retr,orig):
  obj.pop('load_seconds');obj.pop('index_build_seconds')
  for row in obj['records']:row.pop('seconds')
 assert retr==orig
 assert len(retr['records'])==6 and all(x['hit'] for x in retr['records'])
 assert retr['context']['retrieved_ids']==['math.packetized-completion']
 card=(R/'knowledge/entries/math.packetized-completion.md').read_text()
 assert card in json.dumps(retr['context'],ensure_ascii=False).replace('\\n','\n').replace('\\\\','\\') or card in str(retr['context']) or retr['context']['entries'][0].get('content')==card
 (B/'independent_replay_summary.json').write_text(json.dumps(dict(exact_records_match=True,retrieval_without_times_match=True,six_hits=True,context_budget=retr['context']['budget'],knowledge_refs_checked_by_frozen_retrieve=True,tokens='unmeasured'),ensure_ascii=False,indent=2)+'\n')
cmd=[sys.executable,'-m','unittest','tests.test_knowledge','tests.test_knowledge_handoff','tests.test_knowledge_index','tests.test_knowledge_math','tests.test_knowledge_reuse','-v']
res=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'independent_regression.log').write_text(res.stdout+res.stderr);assert res.returncode==0 and 'Ran 53 tests' in res.stderr;logs.append(dict(command=cmd,returncode=res.returncode))
assert _snapshot(R,c)[2]==pf
for pair in pairs:
 for x in pair.values():assert ref(R/x['path'])==x
for x in candidates:assert ref(R/x['path'])==x
book=Path('/tmp/network-calculus.pdf');assert hashlib.sha256(book.read_bytes()).hexdigest()=='4b822851782ca5039a8b774f65f3a8809b48ed5e533d086cb82a6023405cd1ee'
(B/'independent_integrity.json').write_text(json.dumps(dict(snapshot_unchanged=True,artifact_count=len(pf['artifact_hashes']),knowledge_pairs=230,candidates_unchanged=5,source_pdf_sha256=hashlib.sha256(book.read_bytes()).hexdigest(),holdout_content_not_inspected=True),indent=2)+'\n')
(B/'independent_commands.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2)+'\n');print('Independent all10 exact, six retrievals,230 byte mirrors,5 candidates,53 regressions passed; frozen snapshot unchanged')
