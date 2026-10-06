import json, math
from pathlib import Path
p=Path(__file__).parent
Q, delta, gap=4., .02, .14
eta=Q*delta
threshold=math.sqrt(2)*eta
assert gap>threshold
assert gap<2*eta
# Independent one-row real matrix realization of extremal cross-boundary error.
# K=(.035,0), q=4; ||K-Khat||_2 is the Euclidean norm of its row.
r=delta/math.sqrt(2)
K=[.035,0.]
Khat=[K[0]-r,K[1]+r]
s=[Q*x for x in K]; shat=[Q*x for x in Khat]
assert math.isclose(math.hypot(*(a-b for a,b in zip(K,Khat))),delta)
assert shat[0]>shat[1]
assert math.isclose(shat[0]-shat[1],gap-threshold)
# A full-population mean absolute error of .005 already permits failure.
# It is stronger evidence than a sampled mean: 32 scores, two errors .08.
s_mean=[.14,0.]+[-1.]*30
shat_mean=[.06,.08]+[-1.]*30
mae=sum(abs(a-b) for a,b in zip(s_mean,shat_mean))/len(s_mean)
assert math.isclose(mae,.005)
assert max(range(32),key=s_mean.__getitem__)==0
assert max(range(32),key=shat_mean.__getitem__)==1
# This replacement-premise counterexample does NOT satisfy the spectral bound.
counter_spectral=math.hypot(.08/4,.08/4)
assert counter_spectral>delta
ctx=json.loads((p/'context-focused.json').read_text())
roles={e['id']:e['selection_reason'] for e in ctx['entries']}
assert ctx['retrieved_ids']==['math.score-difference-bound']
assert roles['math.cauchy-schwarz']=='prerequisite'
assert roles['math.topk-margin']=='related'
assert roles['math.low-rank-svd']=='related'
assert ctx['status']=='ready'
assert not ctx['skipped']
assert ctx['budget']['used_chars']<=ctx['budget']['max_chars']
for e in ctx['entries']:
    for dep in e['requires']:
        assert dep['id'] in roles
refs=json.loads((p/'refs.json').read_text())['knowledge_refs']
assert {r['id'] for r in refs}=={'math.score-difference-bound','math.topk-margin','math.cauchy-schwarz'}
tiny=json.loads((p/'context-tiny.json').read_text())
assert tiny['status']=='partial'
assert tiny['entries']==[] and tiny['knowledge_refs']==[]
assert tiny['budget']['used_chars']==0
assert set(tiny['retrieved_ids'])<=set(s['id'] for s in tiny['skipped'])
assert all('complete prerequisite bundle' in s['reason'] for s in tiny['skipped'])
results={'status':'pass','eta':eta,'joint_threshold':threshold,'guaranteed_remaining_gap':gap-threshold,'naive_threshold':2*eta,'extremal_matrix_scores':shat,'mean_absolute_error_counterexample':mae,'counterexample_matrix_spectral_error':counter_spectral,'focused_context_selection':roles,'tiny_status':tiny['status'],'checks':'numeric realization, mean-error failure, prerequisite closure, role distinction, explicit budget incompleteness; no formal proof or performance benchmark'}
(p/'checks.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
