"""Public finite-alphabet checks; exact Fractions, entropy sanity floats only."""
import itertools,json,math,sys,time
from pathlib import Path
from fractions import Fraction as F
BASE=Path(__file__).resolve().parent

def entropy(p):return -sum(float(x)*math.log2(float(x)) for x in p if x)
def solve(p,C,z):
 best=F(0);runs=0;bestenc=None
 for enc in itertools.product(range(C),repeat=len(p)):
  joint={}
  for i,pr in enumerate(p):joint.setdefault((z[i],enc[i]),[]).append(pr)
  success=sum((max(v) for v in joint.values()),F(0));runs+=1
  if success>best:best,bestenc=success,enc
 return best,runs,bestenc

def main():
 start=time.perf_counter();cfg=json.loads((BASE/'fixtures.json').read_text());rows=[]
 for f in cfg['cases']:
  if f['id']=='F6':
   assert len(set(f['alphabet']))==f['expected_cardinality']==3
   rows.append({'id':f['id'],'cardinality':3,'maximum_symbol_length':1,'fixed_one_bit_claim':'reject','passed':True});continue
  p=list(map(F,f['prior']));assert sum(p)==1 and len(p)==f['labels'];z=[i//2 for i in range(len(p))] if 'side_information' in f else [0]*len(p)
  best,n,enc=solve(p,f['messages'],z);assert best==F(f['expected_success'])
  post={}
  for i,pr in enumerate(p):post.setdefault(z[i],[]).append(pr)
  bound=sum((sum(sorted(v,reverse=True)[:f['messages']],F(0)) for v in post.values()),F(0));assert best==bound
  grouped={}
  for i,pr in enumerate(p):grouped.setdefault((z[i],enc[i]),[]).append(pr)
  hy=sum(float(sum(v))*entropy([a/sum(v) for a in v]) for v in grouped.values())
  pe=1-best;rhs=entropy([pe,1-pe])+float(pe)*math.log2(len(p)-1) if len(p)>1 else 0
  assert hy<=rhs+1e-12
  rows.append({'id':f['id'],'success':str(best),'posterior_topC_bound':str(bound),'encoder_count':n,'conditional_entropy_bits':hy,'sharp_fano_rhs_bits':rhs,'passed':True,'single_label_handling':'separate/no-log-division' if len(p)==1 else 'M>=2'})
 out={'visibility':'public development fixtures, not model/unseen acceptance','rows':rows,'exact_cases':len(rows),'seconds':time.perf_counter()-start,'entropy_tolerance':1e-12,'general_proof':'informal card proof; finite examples are not proof','model_calls':0,'model_token_cost':'not measured; no model invocation'}
 dest=Path(sys.argv[1]) if len(sys.argv)>1 else BASE;dest.mkdir(parents=True,exist_ok=True);(dest/'raw.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'cases':len(rows),'passed':all(x['passed'] for x in rows),'seconds':out['seconds']}))
if __name__=='__main__':main()
