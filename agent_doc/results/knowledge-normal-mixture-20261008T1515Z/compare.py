"""Per-query matched baseline comparison; no fixture/threshold edits."""
from pathlib import Path
import json,sys
P=Path(__file__).resolve().parent
phase=sys.argv[1];rows=[]
for suite in ['original','round2','morphology','original-context8','round2-context8']:
    before=json.loads((P/('baseline-'+suite+'.json')).read_text())
    after=json.loads((P/(phase+'-'+suite+'.json')).read_text())
    assert before['context_candidate_limit']==after['context_candidate_limit']
    assert set(before['backends'])==set(after['backends'])
    for backend,block in before['backends'].items():
        b={r['case']:r for r in block['queries']};a={r['case']:r for r in after['backends'][backend]['queries']}
        assert len(b)==len(block['queries']) and len(a)==len(after['backends'][backend]['queries']) and set(b)==set(a)
        for key,q in b.items():
            r=a[key];assert q['query']==r['query'] and q['expected']==r['expected']
            metrics={m:{'before':q[m],'after':r[m]} for m in ['recall_at_3','reciprocal_rank','context_recall','no_hit_correct']}
            regressions=[m for m,v in metrics.items() if v['before'] is not None and (v['after'] is None or v['after']<v['before'])]
            rows.append(dict(suite=suite,backend=backend,case=key,query=q['query'],expected=q['expected'],before=q['actual'],after=r['actual'],metrics=metrics,regressions=regressions,before_seconds=q['seconds'],after_seconds=r['seconds']))
out=dict(phase=phase,comparisons=len(rows),regressions=[r for r in rows if r['regressions']],rows=rows)
(P/(phase+'-comparison.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'comparisons':len(rows),'regressions':out['regressions']},ensure_ascii=False))
