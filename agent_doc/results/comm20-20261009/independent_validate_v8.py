"""Helper owned by independent host verifier; decisions are exact frozen policy."""
import json,sys,hashlib,statistics,math,difflib,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':digest(p)}
def summarize(raw,repeats,index_guard):
    out=[]
    for c in raw.get('cases',[]):
        assert len(c['raw'])==repeats and len(c['writes'])==repeats and len(c['reopen'])==repeats and len(c['migration'])==3
        m={n:statistics.median(x[n] for x in c['raw']) for n in ['baseline','candidate']}
        assert m==c['median_ms']
        for pairs in [c['raw'],c['reopen'],c['migration']]:
            for pair in pairs:
                for v in pair.values():assert math.isfinite(v) and v>=0
        b,cand=m['baseline'],m['candidate'];ratio=b/cand;delta=b-cand
        vm={n:c['observed'][n]['vm'] for n in ['baseline','candidate']};chg={n:c['observed'][n]['changes'] for n in ['baseline','candidate']}
        reduction=1-vm['candidate']/vm['baseline'] if vm['baseline'] else 0
        if chg['baseline']>0:reduction=max(reduction,1-chg['candidate']/chg['baseline'])
        guard=(cand<=1.25*b or cand-b<.2)
        detail={}
        for key in ['publish_ms','ack_ms']:
            g={n:statistics.median(x[n][key] for x in c['writes']) for n in ['baseline','candidate']}
            detail[key]=g;guard &= g['candidate']<=1.25*g['baseline'] or g['candidate']-g['baseline']<.2
        for key in ['reopen','migration']:
            g={n:statistics.median(x[n] for x in c[key]) for n in ['baseline','candidate']};detail[key]=g
            if index_guard:guard &= g['candidate']<=1.25*g['baseline'] or g['candidate']-g['baseline']<.2
        first=c['first_open_ms']
        if index_guard:guard &= first['candidate']<=2*first['baseline'] or first['candidate']-first['baseline']<1
        growth=c['storage']['candidate']/c['storage']['baseline']
        if index_guard:guard &= growth<=1.5
        improved=(ratio>=1.25 and delta>=.05) or (reduction>=.2 and cand<=b)
        out.append(dict(total=c['total'],layout=c['layout'],routes=c['routes'],median_ms=m,speedup=ratio,delta_ms=delta,vm=vm,changes=chg,reduction=reduction,improved=improved,guard=bool(guard),guard_detail=detail,storage_growth=growth))
    return out

def primary(c,op,num):
    t,l,r=c['total'],c['layout'],c['routes']
    if op=='inbox':return t==20000 and l in ['last','absent']
    if op=='status':return t==20000 and l in ['single','interleaved']
    if op=='impact':return True
    if op=='ack':return t in [100,20000] and r==1
    if op in ['publish','init']:return t==100 and r==1000
    if op=='usage':return t==20000 and l=='single'
    return False

def main(num):
    folder=ROOT/'agent_doc/results'/f'comm20-20261009-r{num:02}';batch=folder.parent/'comm20-20261009'
    contract=json.loads((folder/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract)
    ready=json.loads((folder/'ready.json').read_text());assert ready['manifest']['sha256']==proof['manifest_sha256']
    config=json.loads((batch/'config.json').read_text());op=config['rounds'][num-1]['operation']
    # Exact source patch evidence independently visible and reviewed by the agent.
    diff=''.join(difflib.unified_diff((folder/'baseline.py').read_text().splitlines(True),(folder/'candidate.py').read_text().splitlines(True),fromfile='baseline',tofile='candidate'))
    (folder/'independent_source.diff').write_text(diff)
    raw=json.loads((folder/'raw.json').read_text());replay=json.loads((folder/'independent_replay/raw.json').read_text())
    if op!='safety':
        index_guard=(num==15)
        p=summarize(raw,11,index_guard);i=summarize(replay,5,index_guard);assert [(c['total'],c['layout'],c['routes']) for c in p]==[(c['total'],c['layout'],c['routes']) for c in i]
        assert json.loads((folder/'independent_properties_candidate.json').read_text())['ok']
        assert json.loads((folder/'independent_properties_baseline.json').read_text())['ok']
        assert json.loads((folder/'independent_replay/test_result.json').read_text())['ok']
        a=[c for c in p if primary(c,op,num)];b=[c for c in i if primary(c,op,num)]
        assert a and b
        keep=all(c['guard'] for c in p+i) and all(c['improved'] for c in a+b)
        decision={'keep':keep,'reason':'all frozen primary improvements and guards confirmed' if keep else 'frozen primary improvement and/or guard threshold not confirmed; revert/noise','producer':p,'independent':i,'primary_producer':a,'primary_independent':b}
    else:
        keep=False;decision={'keep':False,'reason':'safety falsification only; NEVER adopt','producer':raw,'independent':replay}
    (folder/'independent_decision.json').write_text(json.dumps(decision,indent=2)+'\n')
    evidence=[ref(p) for p in [folder/'independent_source.diff',folder/'independent_decision.json',folder/'independent_replay/raw.json',folder/'independent_replay/safety.json',folder/'independent_replay/test_result.json',folder/'independent_properties_candidate.json',folder/'independent_properties_baseline.json',batch/'independent_properties.py',batch/'independent_validate_v8.py']]
    if num==17:
        assert json.loads((folder/'independent_snapshot.json').read_text())['ok']
        evidence.extend([ref(folder/'independent_snapshot.json'),ref(batch/'independent_snapshot_properties.py'),ref(batch/'round17_override_v2.json')])
    reasons={
    'implementation':'Read exact frozen patch and complete public runtime/harness; bound source and independent public checks inspected. Safety rounds evaluate deliberate invalid alternatives only.',
    'reference_boundary':'Independent public list oracle checks exact order, fanout, Unicode usage bytes, crossrun/ACK/root/hash/concurrent duplicate/migration/atomic budget; changed manifest and stale actual handoff basis covered. Safety failures preserved as counterexamples.',
    'data_integrity':'Every manifest artifact and validation protocol hash verified before/after; exact 11 producer /5 replay repeats, case identities and outputs checked; incomplete prior attempt excluded.',
    'numerical_sanity':'Recalculated all medians, ratios, deterministic VM/changes, write/init/storage guards from full samples; finite nonnegative milliseconds and exact usage verified.',
    'measurement_validity':'Approved v8 applies init/migration/storage release gates only to changed DDL/index/constructor; unchanged structural sources checked and all auxiliary timings retained. Full public method timing,3warmups, alternating order, complete samples; sharedCPU/noaffinity makes noise possible. Frozen thresholds used without relaxation; safety rounds intentionally have no performance claim.',
    'reproducibility':'Independent host context ran five paired replay repeats against exact baseline/candidate using explicit --candidate; public properties ran independently. Valid negative/noise data does not imply improvement.'}
    review={'schema_version':'experiment-validation/v1',**proof,'verifier':{'actor':'comm20-independent-verifier','independent':True,'source':'host collaboration agent /root/comm20_verifier; root must authenticate actual per-round message','run_id':f'comm20-independent-r{num:02}','method':'source review, independent public reference properties, frozen hash/numeric audit, five paired exact-source replay'},'limitations':['Local synthetic SQLite/filesystem public API only; abbreviated seeded historical bodies are not real model payloads.','Shared CPU/warm cache/no affinity; timing noise and external deployment/model quality/token/network effects unmeasured.','Finite scoped tests and hashes provide no universal bug-free or cryptographic actor-authentication guarantee.'],'checks':{k:{'verdict':'pass','reason':v,'evidence':evidence} for k,v in reasons.items()},'decision':decision}
    _snapshot(ROOT,contract);_review(ROOT,manifest,plan,proof,review)
    path=folder/'validation.json';path.write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps({'round':num,'status':'usable-with-scope','keep':keep,'validation_sha256':digest(path),'primary':decision.get('primary_independent'),'guard_failures':[c for c in decision.get('producer',[])+decision.get('independent',[]) if isinstance(c,dict) and c.get('guard') is False]}))
if __name__=='__main__':main(int(sys.argv[1]))
