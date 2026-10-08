"""Independent reuse/ref/package checks; no scientific cases are presented as unseen."""
import argparse
import copy
import datetime
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=HERE.parent/'knowledge-freedman-20261008T0915Z'
sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore,KnowledgeError
from agent_runtime.knowledge_index import indexed_search


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def changes(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        result=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:
                result.append(path+key)
            else:
                result.extend(changes(a[key],b[key],path+key+'.'))
        return result
    return [] if a==b else [path.rstrip('.')]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--phase',default='candidate')
    args=parser.parse_args()
    kid='math.freedman-variance-budget'
    archived=OLD/'candidate'/f'{kid}.json'
    card=ROOT/'knowledge/entries'/f'{kid}.json'
    body=card.with_suffix('.md')
    prior=json.loads(archived.read_text());current=json.loads(card.read_text())
    checks=[]
    def add(name,passed,**details):
        checks.append({'id':name,'passed':bool(passed),**details})
    changed=changes(prior,current)
    body_expected='014a071af03dc39f71ff874cff3e126d5193463660dc0c59f37f2a59637bda1e'
    add('unchanged-science',changed==['status','verification.checks'] and digest(body)==digest(archived.with_suffix('.md'))==body_expected,
        changed_json_paths=changed,body_sha256=digest(body),scope='Prior audited derivation, assumptions, sources, aliases, examples and refusal cases unchanged; old synthetic tests are reusable seen regressions, not newly unseen tests.')
    old_result=json.loads((OLD/'independent_results.json').read_text())
    old_runs=[*old_result['prior_runs'],old_result]
    source_ok=all(hashlib.sha256(run['archived_verifier_source'].encode()).hexdigest()==run['code_sha256'] for run in old_runs)
    history=json.loads((OLD/'candidate-history-manifest.json').read_text())
    archive_ok=all(digest(OLD/path)==sha for path,sha in history['snapshots_sha256'].items())
    accepted_old_body=any(run['input_hashes'].get('knowledge/entries/'+kid+'.md')==body_expected and all(c['passed'] for c in run['checks'] if c['id'] in ('adaptive-new-law','marginal-not-conditional','stop-joint-not-conditional','one-sided-new-law','root-and-units','stop-domain','recompute-development')) for run in old_runs)
    add('prior-science-evidence-integrity',source_ok and archive_ok and accepted_old_body,
        executed_source_snapshots=len(old_runs),candidate_history_files=len(history['snapshots_sha256']),historical_publication_gate='blocked, not converted to passed',reuse='No unchanged scientific experiment rerun; separate prior code/proof/data review plus exact content identity justifies reuse.')
    store=KnowledgeStore(ROOT/'knowledge');entry=store.get(kid);refs=entry['knowledge_refs']
    valid=store.check_refs(refs)['valid'];rejected=[]
    for key,value in [('sha256','0'*64),('version',current['version']+1)]:
        mutated=copy.deepcopy(refs);mutated[0][key]=value
        try:store.check_refs(mutated)
        except KnowledgeError:rejected.append(key)
    previous_refs=next(c['refs'] for c in old_result['checks'] if c['id']=='refs-navigation')
    try:store.check_refs(previous_refs);old_rejected=False
    except KnowledgeError:old_rejected=True
    relation_ids={x['id'] for x in store.related(kid)['results']}
    required_related={x['id'] for x in current['relations']}
    add('formal-refs-and-dependency-boundary',valid and len(refs)==1 and refs[0]['id']==kid and current['requires']==[] and set(rejected)=={'sha256','version'} and old_rejected and required_related<=relation_ids,
        current_refs=refs,previous_refs_rejected=old_rejected,requires=[],navigation_only=sorted(required_related),corpus_snapshot=store.snapshot)
    known_queries=['已知条件二阶矩 累计误差 停止事件 方差预算','adapted martingale difference predictable quadratic variation budget']
    rows=[]
    for backend in ('files','sqlite'):
        for q in known_queries:
            search=store.search(q,limit=3) if backend=='files' else indexed_search(store,ROOT/'.knowledge-cache/search.sqlite',q,limit=3)
            ctx=store.context(search)
            ids=[r['id'] for r in search['results']]
            context_ids=[r['id'] for r in ctx['entries']]
            rows.append({'backend':backend,'query':q,'ids':ids,'context_ids':context_ids,'passed':kid in ids and kid in context_ids and search['applicability']=='unchecked'})
    add('previously-seen-card-retrieval',all(r['passed'] for r in rows),rows=rows,claim='Replayed prior exposed queries, not new unseen acceptance.')
    mirror=ROOT/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/entries'
    package=ROOT/'plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_index.py'
    same=card.read_bytes()==(mirror/card.name).read_bytes() and body.read_bytes()==(mirror/body.name).read_bytes()
    index_same=(ROOT/'agent_runtime/knowledge_index.py').read_bytes()==package.read_bytes()
    add('package-identity',same and index_same,card_json_and_body_byte_equal=same,index_implementation_byte_equal=index_same)
    missing=[p for p in current['verification']['checks'] if not (ROOT/p).is_file()]
    add('evidence-links',not missing,missing=missing)
    receipts_path=HERE/f'{args.phase}-commands.json'
    receipts=json.loads(receipts_path.read_text()) if receipts_path.exists() else []
    expected={'validate','sync','sync-check','index','original','original-context8','round2','round2-context8','morphology','full-tests','reader-tests','diff-check'}
    received={r['name'] for r in receipts}
    log_hashes=all((HERE/r['log']).is_file() and digest(HERE/r['log'])==r['sha256'] for r in receipts)
    nonretrieval={'validate','sync','sync-check','index','full-tests','reader-tests','diff-check'}
    nonretrieval_ok=all(r['exit_code']==0 for r in receipts if r['name'] in nonretrieval)
    add('integration-command-evidence',received==expected and log_hashes and nonretrieval_ok,phase=args.phase,missing=sorted(expected-received),receipts=[{'name':r['name'],'exit_code':r['exit_code']} for r in receipts],claim='Retrieval exit1 remains an inherited suite failure. This check does not replace independent per-query no-regression and unseen tests.')
    paths=[archived,archived.with_suffix('.md'),card,body,OLD/'independent_results.json',OLD/'independent_review.md',OLD/'candidate-history-manifest.json',ROOT/'agent_runtime/knowledge.py',ROOT/'agent_runtime/knowledge_index.py',mirror/card.name,mirror/body.name,package,HERE/'plan.md',HERE/'run_checks.py',HERE/'compare.py',Path(__file__)]
    if receipts_path.exists():paths += [receipts_path]+[HERE/r['log'] for r in receipts]
    result={'actor':'/root/knowledge_result','executed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':sys.argv,'phase':args.phase,'checks':checks,'input_hashes':{str(p.relative_to(ROOT)):digest(p) for p in paths},'executed_source':Path(__file__).read_text(),'science_reuse':'usable-with-scope' if checks[0]['passed'] and checks[1]['passed'] else 'requires-review','integration_scope':'card refs/package/seen replay and raw command receipts only; retrieval_unseen owns novel tests and engine acceptance','integration_ready':all(c['passed'] for c in checks),'publication':'pending separate retrieval acceptance and final latest-HEAD checks'}
    out=HERE/'integration_results.json'
    if out.exists():
        earlier=json.loads(out.read_text());hist=earlier.pop('prior_runs',[]);result['prior_runs']=[*hist,earlier]
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'science_reuse':result['science_reuse'],'integration_ready':result['integration_ready'],'checks':[{'id':c['id'],'passed':c['passed']} for c in checks]}))

if __name__=='__main__':main()
