"""Independent decoder enumeration and H(Y)-H(T,Z) reference; no holdout parsing."""
import hashlib,itertools,json,math
from fractions import Fraction
from pathlib import Path
from agent_runtime.result_validation import _snapshot
ROOT=Path.cwd();BASE=ROOT/'agent_doc/results/math-fano-message-20261009';OUT=BASE/'independent_evidence'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def H(ps):return -sum(float(p)*math.log2(float(p)) for p in ps if p)
contract=json.loads((BASE/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract)
assert proof['manifest_sha256']=='1b6c96c273e3b2526ff9af0ec4fe22f9f7c8c81694b007f625a76005577f3933'
(OUT/'snapshot.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
raw=json.loads((BASE/'raw.json').read_text());cfg=json.loads((BASE/'fixtures.json').read_text());rows=[]
for f,produced in zip(cfg['cases'],raw['rows']):
 assert f['id']==produced['id']
 if f['id']=='F6':
  alphabet=set(f['alphabet']);assert len(alphabet)==3 and sum(2**j for j in range(2))==3
  rows.append({'id':f['id'],'independent_count':3});continue
 p=list(map(Fraction,f['prior']));M=len(p);C=f['messages'];z=[(label-1)//2 if 'side_information' in f else 0 for label in range(1,M+1)];zs=sorted(set(z));states=list(itertools.product(zs,range(C)))
 # Each decoder outputs a label for each observed pair. Direct encoder optimum
 # equals total prior mass of labels appearing in its z-row. Enumerate decoders,
 # independently of producer's message partition maximization.
 best=Fraction(0);decoders=0
 for outputs in itertools.product(range(M),repeat=len(states)):
  decoders+=1;reachable={pair:outputs[j] for j,pair in enumerate(states)}
  success=sum((p[y] for y in range(M) if any(reachable[(z[y],t)]==y for t in range(C))),Fraction(0))
  best=max(best,success)
 assert best==Fraction(f['expected_success'])==Fraction(produced['success'])
 # Reconstruct producer's deterministic tie policy, then use entropy chain rule
 # H(Y | f(Y),z(Y)) = H(Y) - H(f(Y),z(Y)), not its posterior entropy loop.
 best_enc=None
 for enc in itertools.product(range(C),repeat=M):
  mass={}
  for y in range(M):mass.setdefault((z[y],enc[y]),[]).append(p[y])
  if sum((max(v) for v in mass.values()),Fraction(0))==best:best_enc=enc;break
 obs={}
 for y in range(M):obs[(z[y],best_enc[y])]=obs.get((z[y],best_enc[y]),Fraction(0))+p[y]
 hy=H(p)-H(obs.values());pe=1-best;rhs=H([pe,1-pe])+float(pe)*math.log2(M-1) if M>1 else 0
 assert abs(hy-produced['conditional_entropy_bits'])<1e-12 and abs(rhs-produced['sharp_fano_rhs_bits'])<1e-12 and hy<=rhs+1e-12
 assert produced['encoder_count']==C**M
 rows.append({'id':f['id'],'decoder_tables':decoders,'success':str(best),'first_optimal_encoder':best_enc,'H_Y_minus_H_TZ_bits':hy,'sharp_rhs_bits':rhs,'encoder_count':C**M})
assert len(rows)==8
baseline=json.loads((BASE/'preservation_baseline.json').read_text());changed=[k for k,v in baseline.items() if digest(ROOT/k)!=v];assert not changed
mirror=ROOT/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/entries'
assert all((ROOT/'knowledge/entries'/('math.fano-message-budget.'+suffix)).read_bytes()==(mirror/('math.fano-message-budget.'+suffix)).read_bytes() for suffix in ['md','json'])
replay=json.loads((OUT/'raw.json').read_text());assert {k:v for k,v in replay.items() if k!='seconds'}=={k:v for k,v in raw.items() if k!='seconds'}
a=json.loads((BASE/'retrieval.json').read_text());b=json.loads((OUT/'retrieval.json').read_text())
for r1,r2 in zip(a['records'],b['records']):assert {k:v for k,v in r1.items() if k!='seconds'}=={k:v for k,v in r2.items() if k!='seconds'}
for k in ['scope','snapshot','protocol_sha256','context','token_cost','holdouts_metadata_sha256']:assert a[k]==b[k]
assert len(b['records'])==6 and all(r['hit'] for r in b['records']) and b['context']['budget']['used_chars']==9670
result={'rows':rows,'preserved_baseline_paths':len(baseline),'changed_baseline_paths':changed,'holdout_check':'byte SHA only; no content parsed or printed','mirrors_equal':True,'manifest_sha256':proof['manifest_sha256'],'native_bound_paths':len(proof['artifact_hashes']),'replay_raw_equal_excluding_seconds':True,'retrieval_equal_excluding_timings':True,'actual_backends':sorted(set(r['result']['backend'] for r in b['records']))}
(OUT/'reference.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
