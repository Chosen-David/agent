import math,json
from pathlib import Path
base=Path('/tmp/knowledge-forward-a')
epsilon=.025*3
print('score_error_bound =',epsilon,'generic_gap_threshold =',2*epsilon)
print('0.18 guaranteed:',.18>2*epsilon,'0.10 generic guarantee:',.10>2*epsilon)
print('sharper spectral gap threshold =',math.sqrt(2)*epsilon)
theta=math.pi/4-.1
v1=(math.sin(theta),math.cos(theta)); v2=(math.cos(theta),-math.sin(theta))
q=(math.sqrt(9-2.99**2),2.99)
tail_gap=.025*q[1]*(v2[0]-v2[1])
sigma1=(tail_gap-.10)/(q[0]*(v1[1]-v1[0]))
K=[[sigma1*x for x in v1],[.025*x for x in v2]]
s=[sum(K[j][i]*q[j] for j in range(2)) for i in range(2)]
shat=[K[0][i]*q[0] for i in range(2)]
assert sigma1>.025
assert abs(sum(x*x for x in q)-9)<1e-12
assert abs(sum(x*y for x,y in zip(v1,v2)))<1e-12
assert abs((s[0]-s[1])-.1)<1e-12
assert s[0]>s[1] and shat[0]<shat[1]
print('Exact SVD construction: U=I; V^T rows=v1,v2; sigma=',[sigma1,.025])
print('K=',K,'q=',q,'qnorm=',math.sqrt(sum(x*x for x in q)))
print('original_scores=',s,'rank1_scores=',shat,'original_gap=',s[0]-s[1],'rank1_gap=',shat[0]-shat[1])
# Unchanged example with all stated numeric bounds: q uses only retained direction.
K_stable=[[.1/3,0],[0,.025]]; q_stable=[3,0]
assert .1/3>.025
print('0.10 unchanged example: K=',K_stable,'q=',q_stable,'scores_before_after=',[.1,0])
for gap in [.18,.1]:
 s=[gap,0]+[-1]*18
 shat=[gap-.1,.1]+[-1]*18
 mae=sum(abs(a-b) for a,b in zip(s,shat))/len(s)
 assert abs(mae-.01)<1e-12 and shat[0]<shat[1]
 print('Average-only failure: n=20, gap=',gap,'MAE=',mae,'boundary_scores_before=',s[:2],'after=',shat[:2])
refs={}
for name in ['math.low-rank-svd','math.topk-margin','math.cauchy-schwarz']:
 for ref in json.loads((base/(name+'.json')).read_text())['knowledge_refs']:
  refs[ref['id']]=ref
(base/'refs.json').write_text(json.dumps({'task_id':'knowledge-forward-a','task_refs':['report.md','evidence.txt'],'knowledge_root':'skill/assets/knowledge','knowledge_refs':list(refs.values())},indent=2)+'\n')
print('All concrete checks passed; refs.json generated from actual show outputs.')
