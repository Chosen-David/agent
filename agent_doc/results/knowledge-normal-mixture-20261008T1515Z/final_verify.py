"""Independent final artifact audit; reads frozen outputs, does not rerun producer suites."""
import json, hashlib, subprocess, sys, datetime
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore
START='b93e66c6f65cbc3a82c14472b9f657d8a38279d2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
checks=[]
def check(name,ok,detail):checks.append(dict(name=name,passed=bool(ok),detail=detail))
receipts={}; hashes={}
for phase in ('baseline','candidate'):
    rows=json.loads((P/f'{phase}-commands.json').read_text());receipts[phase]=rows
    check(phase+' complete command sequence',[x['name'] for x in rows]==['validate','sync','sync-check','index','original','original-context8','round2','round2-context8','morphology','full-tests','reader-tests','diff-check'],len(rows))
    for r in rows:
        check(phase+' '+r['name']+' raw log hash',sha(P/r['log'])==r['sha256'],r['sha256'])
        expected=1 if r['name'] in ('original','original-context8','round2','round2-context8','morphology') else 0
        check(phase+' '+r['name']+' exit preserved',r['exit_code']==expected,r['exit_code'])
comparisons=[]
for suite,fixture in [('original','queries'),('round2','round2-queries'),('morphology','morphology-queries'),('original-context8','queries'),('round2-context8','round2-queries')]:
    datasets=[json.loads((P/f'{phase}-{suite}.json').read_text()) for phase in ('baseline','candidate')]
    cases=json.loads((ROOT/f'evals/knowledge/{fixture}.json').read_text())['cases']
    check(suite+' context limit unchanged',datasets[0]['context_candidate_limit']==datasets[1]['context_candidate_limit'],datasets[1]['context_candidate_limit'])
    for backend in ('files','sqlite'):
        bb,aa=[d['backends'][backend]['queries'] for d in datasets]
        check(suite+' '+backend+' fixture binding',all([(r['case'],r['query'],r['expected']) for r in rr]==[(c['id'],c['query'],c['expected']) for c in cases] for rr in (bb,aa)),len(cases))
        for b,a in zip(bb,aa):
            for label,r in [('baseline',b),('candidate',a)]:
                hit=[k for k in r['expected'] if k in r['actual']]
                derived={'recall_at_3':len(hit)/len(r['expected']) if r['expected'] else None,'reciprocal_rank':1/min(r['actual'].index(k)+1 for k in hit) if hit else 0,'context_recall':sum(k in r['context_ids'] for k in r['expected'])/len(r['expected']) if r['expected'] else None,'no_hit_correct':not r['actual'] if not r['expected'] else None}
                check(f'{suite}/{backend}/{r["case"]}/{label} recomputed metrics',all(r[k]==v for k,v in derived.items()),derived)
            metric={k:[b[k],a[k]] for k in derived}
            regress=[k for k,(x,y) in metric.items() if (x is None)!=(y is None) or (x is not None and y<x)]
            comparisons.append(dict(suite=suite,backend=backend,case=b['case'],metrics=metric,regressions=regress))
check('76 per-query comparisons without degradation',len(comparisons)==76 and not any(r['regressions'] for r in comparisons),{'count':len(comparisons),'regressions':[r for r in comparisons if r['regressions']]})
# Every tracked executable, fixture, protected historical item, and guide remains byte-identical.
integration=json.loads((P/'integration.json').read_text())
integrated=integration['integrated_head']
remote_changed=git('diff',START,integrated,'--name-only').decode().splitlines()
check('integrated remote scope',set(remote_changed)<={'agent_doc/results/math-gpu-ranking-contract-20261008/publication_receipt.json','agent_doc/task/TASK.md','agent_doc/task/task_details/MATH-51.md','knowledge/learning_state.json','plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/learning_state.json'},remote_changed)
changed=git('diff',integrated,'--name-only').decode().splitlines()
allowed={'agent_doc/task/TASK.md','knowledge/README.md','knowledge/coverage.json','knowledge/learning_state.json','plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/README.md','plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/coverage.json','plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/learning_state.json'}
check('tracked changes confined to authorized integration metadata',set(changed)<=allowed,changed)
protected=['knowledge/evaluation_holdouts.json','scripts/eval_knowledge.py','evals/knowledge/queries.json','evals/knowledge/round2-queries.json','evals/knowledge/morphology-queries.json']
for rel in protected:
    check(rel+' unchanged since start',(ROOT/rel).read_bytes()==git('show',f'{START}:{rel}'),sha(ROOT/rel))
mirror=ROOT/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge'
files=[p for p in (ROOT/'knowledge').rglob('*') if p.is_file()]
check('complete knowledge mirror',all((mirror/p.relative_to(ROOT/'knowledge')).is_file() and p.read_bytes()==(mirror/p.relative_to(ROOT/'knowledge')).read_bytes() for p in files),len(files))
store=KnowledgeStore(ROOT/'knowledge');entry=store.get('math.normal-mixture-boundary');store.check_refs(entry['knowledge_refs'])
ind=json.loads((P/'independent_results.json').read_text());last=ind['runs'][-1]
check('final independent canonical ref',last['candidate']['knowledge_refs']==entry['knowledge_refs'] and last['snapshot']==store.snapshot and last['machine_pass'],entry['knowledge_refs'])
check('frozen cases hash',last['cases_sha256']==sha(P/'independent_cases.json'),sha(P/'independent_cases.json'))
check('verifier source hash',last['verifier_sha256']==sha(P/'independent_verify.py'),sha(P/'independent_verify.py'))
check('development source hash',json.loads((P/'checks.json').read_text())['source_sha256']==sha(P/'verify.py'),sha(P/'verify.py'))
check('reviewed scientific body unchanged',(ROOT/'knowledge/entries/math.normal-mixture-boundary.md').read_bytes()==(P/'candidate/math.normal-mixture-boundary.md').read_bytes(),sha(ROOT/'knowledge/entries/math.normal-mixture-boundary.md'))
post=json.loads((P/'postintegration.json').read_text())
check('postintegration commands',len(post['commands'])==4 and all(x['exit_code']==0 for x in post['commands']),post['commands'])
check('postintegration snapshot and refs',post['candidate_snapshot']==store.snapshot and post['knowledge_refs']==entry['knowledge_refs'],store.snapshot)
check('215 protected files independently byte-checked',len(post['protected'])==215 and all(sha(ROOT/x['path'])==x['sha256'] and (ROOT/x['path']).read_bytes()==git('show',f"{START}:{x['path']}") for x in post['protected']),len(post['protected']))
old_state=json.loads(git('show',f'{integrated}:knowledge/learning_state.json'))
state=json.loads((ROOT/'knowledge/learning_state.json').read_text())
check('prior source queues and remote completion preserved',all(state[k]==v for k,v in old_state.items() if k!='history') and all(x in state['history'] for x in old_state['history']),[k for k in state if state[k]!=old_state.get(k)])
# Record all evidence bytes except this generated report and source-owned files still being finalized.
for p in sorted(P.rglob('*')):
    if p.is_file() and p.name not in ('final_review.json','final_review.md'):hashes[str(p.relative_to(ROOT))]=sha(p)
for rel in ('knowledge/entries/math.normal-mixture-boundary.json','knowledge/entries/math.normal-mixture-boundary.md','knowledge/evaluation_holdouts.json'):hashes[rel]=sha(ROOT/rel)
out=dict(verdict='usable-with-scope' if all(c['passed'] for c in checks) else 'blocked',reviewer='/root/mixture_final',task='RP-T-20261008-1515',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),start_sha=START,scope='Independent final actual-code/raw-data/canonical scientific-content and integration acceptance; remote push and CI excluded',checks=checks,per_query_comparisons=comparisons,command_receipts=receipts,evidence_hashes=hashes,knowledge_refs=entry['knowledge_refs'],snapshot=store.snapshot,limitations=['Five absolute retrieval evaluator gates remain exit 1 in baseline and candidate; no-degradation is not absolute gate success.','Finite CPU checks and reviewed derivation are not formal verification or model/GPU performance evidence.','Source PDF byte hash/license-link independent retrieval unavailable, recorded in source-review; public fixed-version text reviewed.','Remote fetch, commit, push, SHA readback and CI remain parent-owned.'])
previous=json.loads((P/'final_review.json').read_text()) if (P/'final_review.json').exists() else None
if previous:
    history=previous.pop('prior_audits',[])
    out['prior_audits']=history+[previous]
(P/'final_review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'verdict':out['verdict'],'checks':len(checks),'failures':[x for x in checks if not x['passed']],'comparisons':len(comparisons)},ensure_ascii=False))
