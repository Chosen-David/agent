"""Actual host child route_bind_verify independent verification; no runtime edits."""
import ast,difflib,hashlib,importlib.util,io,json,math,platform,sqlite3,statistics,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];D=Path(__file__).parent
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return dict(path=str(p.relative_to(ROOT)),sha256=digest(p))
def module(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def properties():
    oracle=module(D.parent/'comm20-20261009/independent_properties.py','independent_public')
    extra=module(D/'independent_route_properties.py','independent_route')
    for label in ['baseline','strong_baseline','candidate']:
        cls=oracle.load(D/(label+'.py'));result=oracle.run(cls);assert result['ok'] and result['count']==61
        (D/('independent_properties_'+label+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        result=extra.run(cls);(D/('independent_route_'+label+'.json')).write_text(json.dumps(result,indent=2)+'\n')
        for src,tag in [(ROOT/'tests/test_communication_regressions.py','regressions'),(D/'integration_tests.py','integration')]:
            m=module(src,'independent_'+tag+'_'+label);m.Mailbox=cls;stream=io.StringIO()
            r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(m))
            (D/('independent_'+tag+'_'+label+'.log')).write_text(stream.getvalue());assert r.wasSuccessful() and r.testsRun==2
    (D/'independent_environment.json').write_text(json.dumps(dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform()),indent=2)+'\n')

def pairs(rows,n,nested=False):
    assert len(rows)==n
    for row in rows:
        assert set(row)=={'baseline','candidate'}
        for v in row.values():
            values=v.values() if nested else [v]
            if nested:assert set(v)=={'publish_ms','ack_ms'}
            for x in values:assert type(x) in [int,float] and math.isfinite(x) and x>0

def summarize(p):
    raw=json.loads(p.read_text());assert raw['repeats']==31 and raw['warmups']==3
    assert [(c['total'],c['layout'],c['routes']) for c in raw['cases']]==[(100,'single',1),(20000,'single',1),(100,'single',1000)]
    out=[]
    for c in raw['cases']:
        pairs(c['raw'],31);pairs(c['writes'],31,True);pairs(c['reopen'],31);pairs(c['migration'],3)
        med={n:statistics.median(x[n] for x in c['raw']) for n in ['baseline','candidate']};assert med==c['median_ms']
        assert c['storage']['baseline']==c['storage']['candidate']
        assert c['observed']['baseline']==c['observed']['candidate']
        guards={'public_publish':med['candidate']<=1.25*med['baseline'] or med['candidate']-med['baseline']<.2}
        write={}
        for op in ['publish_ms','ack_ms']:
            m={n:statistics.median(x[n][op] for x in c['writes']) for n in med};write[op]=m
            guards[op]=m['candidate']<=1.25*m['baseline'] or m['candidate']-m['baseline']<.2
        out.append(dict(shape=[c['total'],c['layout'],c['routes']],median_ms=med,speedup=med['baseline']/med['candidate'],delta_ms=med['baseline']-med['candidate'],primary=c['routes']==1000,improved=med['baseline']/med['candidate']>=1.25 and med['baseline']-med['candidate']>=.05,guards=guards,guard=all(guards.values()),writes=write,storage=c['storage'],diagnostic={k:{n:statistics.median(x[n] for x in c[k]) for n in med} for k in ['reopen','migration']},range_ms={n:[min(x[n] for x in c['raw']),max(x[n] for x in c['raw'])] for n in med}))
    return out

def validate():
    contract=json.loads((D/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract)
    assert proof['manifest_sha256']=='2f53038adcc54b34380450834f8220da61d6af2397fdec67715c51d77ab151de'
    assert json.loads((D/'independent_before_snapshot.json').read_text())==proof
    (D/'independent_after_snapshot.json').write_text(json.dumps(proof,indent=2)+'\n')
    h=module(ROOT/'scripts/benchmark_communication_candidates_v2.py','routeharness')
    base=(D/'baseline.py').read_text();strong=(D/'strong_baseline.py').read_text();cand=(D/'candidate.py').read_text()
    assert base.encode()==subprocess.check_output(['git','show','0a532bf447936fd7c07d0d97779a600c6a764905:agent_runtime/communication.py'],cwd=ROOT)
    assert strong==h.variant(base,12)
    expected=base.replace("        recipients = sorted({r['recipient'] for r in self.plan['routes']", "        sender, task_id, kind = event['sender'], event['task_id'], event['kind']\n        recipients = sorted({r['recipient'] for r in self.plan['routes']",1).replace("all(r[k] == event[k] for k in ('sender', 'task_id', 'kind'))","r['sender'] == sender and r['task_id'] == task_id and r['kind'] == kind",1)
    assert cand==expected
    trees=[]
    for code in [base,strong,cand]:
        tree=ast.parse(code);box=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Mailbox');box.body=[x for x in box.body if not(isinstance(x,ast.FunctionDef) and x.name=='publish')];trees.append(ast.dump(tree,include_attributes=False))
    assert len(set(trees))==1
    (D/'independent_source.diff').write_text(''.join(difflib.unified_diff(base.splitlines(True),cand.splitlines(True),fromfile='baseline',tofile='candidate')))
    cohorts={name:summarize(D/name/'raw.json') for name in ['producer_current','producer_strong','independent_current','independent_strong']}
    keep=all(c['guard'] and (not c['primary'] or 'strong' in name or c['improved']) for name,rows in cohorts.items() for c in rows)
    profile=json.loads((D/'profile_raw.json').read_text());assert profile['baseline']['route_generator_calls']==2002 and profile['candidate']['route_generator_calls']==profile['strong_baseline']['route_generator_calls']==0
    assert profile['baseline']['published']==profile['candidate']['published']==profile['strong_baseline']['published']
    assert 'AttributeError' in (D/'profile.log').read_text() and 'runctx' in (D/'profile.log').read_text()
    env=json.loads((D/'independent_environment.json').read_text());assert env==json.loads((D/'environment.json').read_text()) or all(env[k]==json.loads((D/'environment.json').read_text())[k] for k in env)
    safety=dict(duplicate_mutated_ref='rejected',changed_valid_manifest='rejected',thread_retry=['accepted']*4)
    for name in cohorts:
        assert json.loads((D/name/'raw.json').read_text())['environment']==env
        assert json.loads((D/name/'safety.json').read_text())==dict(baseline=safety,candidate=safety)
        t=json.loads((D/name/'test_result.json').read_text());assert t['ok'] and t['run']==25 and t['failures']==t['errors']==0
    decision=dict(keep=keep,reason='All frozen current primary gains and all four-cohort public guards passed' if keep else 'Frozen gate failed; preserve current main baseline',cohorts=cohorts,profile=profile)
    (D/'independent_decision.json').write_text(json.dumps(decision,indent=2)+'\n')
    evidence=[ref(p) for p in sorted(D.glob('independent*')) if p.is_file() and p.name not in {'independent_validation.log','validation.json'}]+[ref(p) for name in ['independent_current','independent_strong'] for p in sorted((D/name).iterdir()) if p.is_file()]+[ref(D.parent/'comm20-20261009/independent_properties.py')]
    reasons=dict(implementation='Exact current-main source, exact r12 strong comparator, exact local field binding verified; AST identical outside publish. Current plan routes reread each call; canonical/ref validation, BEGIN IMMEDIATE, duplicate body and all writes remain unchanged.',reference_boundary='61 independent public list/byte properties, two public regressions, two frozen route integration tests on all three sources; independent seeded list oracle checks all three route keys, randomized matched/unmatched fanout, sorted unique recipients, live-plan duplicate authority, invalid envelopes, stale/crossrun and refs.',data_integrity='Frozen native artifact snapshot before and after agrees; exact ordered three shapes,31 alternating pairs,3 warmups,31 guards/reopens,3 migrations in all four cohorts; safety and25 correctness cases; all hashes retained. Initial profile import failure preserved.',numerical_sanity='Every paired timing leaf positive finite ms; exact medians/ratios/absolute gains and all public publish/fresh ACK guards recomputed; SQL VM/changes/traces and storage identical; diagnostic maintenance values retained.',measurement_validity='Full public publish includes ref validation/SQLite connect/transaction/writes; frozen alternation and warmups/all31 samples retained. Strong baseline tested fairly in two cohorts. Out-of-timing profile only confirms route generator elimination. python -P removes unsafe script directory import search before cProfile; unchanged script/source/fixtures and no primary timing changes.',reproducibility='Exactly one independent31pair replay per current and strong comparison, independent three-source properties/regressions/route tests; no retries,tuning,threshold changes or third plan review. Adoption boolean requires both current primary gains and all public guards in all four cohorts.')
    review=dict(schema_version='experiment-validation/v1',**proof,verifier=dict(actor='route-bind-independent-verifier',independent=True,source='actual trusted host child /root/route_bind_verify; parent authenticates task dispatch/start/returned completion',run_id='comm-route-bind-independent-20261009',method='Independent source/read/hash/numeric audit; frozen single31pair replay per comparison; independent public/list oracle and regressions'),limitations=['Local synthetic SQLite public API only; no LLM/network/token/quality benefit measured.','Shared CPU and warm filesystem cache, no affinity; three fixed shapes and four cohorts only.','Finite tests/hashes do not prove universal correctness or self-authenticate reviewer identity; root authenticates actual host actor.','Profile initial import failure before fixtures is preserved; -P import-path-only remedy changes no frozen source/protocol or latency data.','Independent oracle initial helper used duplicate constructor routes, correctly rejected by existing check_plan; preserved attempt1 log and corrected only helper initial fixture. No source, frozen protocol, performance replay or gate changed.'],checks={k:dict(verdict='pass',reason=v,evidence=evidence) for k,v in reasons.items()},decision=decision)
    assert _snapshot(ROOT,contract)[2]==proof
    _review(ROOT,manifest,plan,proof,review)
    (D/'validation.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(dict(status='usable-with-scope',keep=keep,validation_sha256=digest(D/'validation.json'),primary={n:next(c for c in rows if c['primary']) for n,rows in cohorts.items()},failed_guards=[dict(cohort=n,shape=c['shape'],guards=c['guards']) for n,rows in cohorts.items() for c in rows if not c['guard']])))
if __name__=='__main__':
    if sys.argv[1]=='properties':properties()
    elif sys.argv[1]=='validate':validate()
