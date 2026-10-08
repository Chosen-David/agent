"""Compare every old query without altering fixtures or acceptance thresholds."""
import json,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
OLD=OUT.parent/'knowledge-freedman-20261008T0915Z'
phase=sys.argv[1]
rows=[]
for label,folder,prefix,context8 in [('start38d',OLD,'baseline',True),('concurrent59ad',OLD,'integrated-baseline',True),('start2325',OUT,'baseline',False),('start2325-context8',OUT,'baseline',True)]:
    for suite in ['original','round2','morphology']:
        suffix='-context8' if context8 and folder==OUT and suite!='morphology' else ''
        before=json.loads((folder/f'{prefix}-{suite}{suffix}.json').read_text())
        after_suffix='-context8' if context8 and suite!='morphology' else ''
        after=json.loads((OUT/f'{phase}-{suite}{after_suffix}.json').read_text())
        assert before['context_candidate_limit']==after['context_candidate_limit']
        for backend,b in before['backends'].items():
            lookup={q['case']:q for q in after['backends'][backend]['queries']}
            for q in b['queries']:
                r=lookup[q['case']]
                assert q['query']==r['query'] and q['expected']==r['expected']
                changes={m:dict(before=q[m],after=r[m]) for m in ['recall_at_3','context_recall','reciprocal_rank','no_hit_correct'] if q[m]!=r[m]}
                regressions=[m for m,c in changes.items() if c['before'] is not None and c['after']<c['before']]
                rows.append(dict(baseline=label,suite=suite,backend=backend,case=q['case'],changes=changes,regressions=regressions,before=q['actual'],after=r['actual']))
result=dict(phase=phase,comparisons=len(rows),regressions=[r for r in rows if r['regressions']],changes=[r for r in rows if r['changes']],rows=rows)
(OUT/f'{phase}-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
