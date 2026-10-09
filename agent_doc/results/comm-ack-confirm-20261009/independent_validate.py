"""Confirmation verifier owned by actual independent host child context."""
import ast, difflib, hashlib, importlib.util, json, math, statistics, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
D = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from agent_runtime.result_validation import _snapshot, _review

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ref(path):
    return dict(path=str(path.relative_to(ROOT)), sha256=digest(path))

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def public_checks():
    old = D.parent/'comm20-20261009'
    props = module(old/'independent_properties.py', 'ackpublicprops')
    extra = module(D/'independent_ack_properties.py', 'ackextra')
    for label in ('baseline', 'candidate'):
        cls = props.load(D/(label+'.py'))
        result = props.run(cls)
        assert result['count'] == 61 and result['ok']
        (D/('independent_properties_'+label+'.json')).write_text(json.dumps(result, indent=2)+'\n')
        regression = module(ROOT/'tests/test_communication_regressions.py', 'ackregression_'+label)
        regression.Mailbox = cls
        import io, unittest
        stream=io.StringIO()
        run=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(regression))
        (D/('independent_regressions_'+label+'.log')).write_text(stream.getvalue())
        assert run.wasSuccessful() and run.testsRun==2
        extra_result=extra.run(cls)
        (D/('independent_ack_properties_'+label+'.json')).write_text(json.dumps(extra_result,indent=2)+'\n')
    import platform, sqlite3
    (D/'independent_environment.json').write_text(json.dumps(dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform()),indent=2)+'\n')

def numeric(value):
    assert type(value) in (int,float) and math.isfinite(value) and value > 0, value

def paired(rows, n, nested=False):
    assert len(rows) == n
    for pair in rows:
        assert set(pair) == {'baseline','candidate'}
        for value in pair.values():
            if nested:
                assert set(value) == {'publish_ms','ack_ms'}
                for leaf in value.values(): numeric(leaf)
            else: numeric(value)

def summarize(raw):
    assert raw['repeats'] == 31 and raw['warmups'] == 3
    shapes = [(100,'single',1),(20000,'single',1),(100,'single',1000)]
    assert [(c['total'],c['layout'],c['routes']) for c in raw['cases']] == shapes
    out = []
    for c in raw['cases']:
        paired(c['raw'],31); paired(c['writes'],31,True)
        paired(c['reopen'],31); paired(c['migration'],3)
        m = {n:statistics.median(x[n] for x in c['raw']) for n in ('baseline','candidate')}
        assert m == c['median_ms']
        assert set(c['first_open_ms']) == set(m) and set(c['storage']) == set(m)
        for v in c['first_open_ms'].values(): numeric(v)
        for v in c['storage'].values(): assert type(v) is int and v > 0
        vm = {n:c['observed'][n]['vm'] for n in m}
        assert all(type(v) is int and v>0 for v in vm.values())
        assert c['observed']['baseline']['changes']==1 and c['observed']['candidate']['changes']==0
        assert c['storage']['baseline']==c['storage']['candidate']
        for n in m:
            sql=c['observed'][n]['sql']
            # observe removes its trace callback before connect's context exit/commit.
            assert any(q=='BEGIN IMMEDIATE' for q in sql)
            assert not any(q.lstrip().upper().startswith(('CREATE','ALTER','DROP')) for q in sql)
            assert sum(q.lstrip().upper().startswith('UPDATE COMMUNICATION_DELIVERIES') for q in sql)==(1 if n=='baseline' else 0)
        b,v=m['baseline'],m['candidate']; reduction=1-c['observed']['candidate']['changes']/c['observed']['baseline']['changes']
        primary=c['routes']==1 and c['total'] in (100,20000)
        improvement=(b/v>=1.25 and b-v>=.05) or (reduction>=.2 and v<=b)
        guards = {'ack_duplicate':v<=1.25*b or v-b<.2}
        detail={}
        for op in ('publish_ms','ack_ms'):
            g={n:statistics.median(p[n][op] for p in c['writes']) for n in m}
            detail[op]=g
            guards[op]=g['candidate']<=1.25*g['baseline'] or g['candidate']-g['baseline']<.2
        # Source comparison guarantees no maintenance changes; auxiliary timings retained.
        diagnostic={key:{n:statistics.median(p[n] for p in c[key]) for n in m} for key in ('reopen','migration')}
        out.append(dict(total=c['total'],layout=c['layout'],routes=c['routes'],primary=primary,improved=improvement,median_ms=m,speedup=b/v,delta_ms=b-v,vm=vm,reduction=reduction,guards=guards,guard=all(guards.values()),writes=detail,diagnostic=diagnostic,range_ms={n:[min(p[n] for p in c['raw']),max(p[n] for p in c['raw'])] for n in m}))
    return out

def validate():
    contract=json.loads((D/'contract.json').read_text())
    manifest, plan, proof = _snapshot(ROOT,contract)
    assert proof['manifest_sha256']=='d3452d9cbede33f73e4db7350bbb517a45ffea80bc2b548629eda14e680080b9'
    assert digest(D/'task_dag_v2.json')=='508b39fa0942bcf1413c404cab7fc00619782c0a69f5ca0551e765a78c1800f3'
    assert digest(D/'plan_review_v2.json')=='4bd22d08fccb2b82e017c6e6436b05bfe3152a6c48b0df19aa3186d807bb37b6'
    assert json.loads((D/'independent_before_snapshot.json').read_text())==proof
    (D/'independent_after_snapshot.json').write_text(json.dumps(proof,indent=2)+'\n')
    ready=json.loads((D/'ready.json').read_text())
    assert ready['manifest']['sha256']==proof['manifest_sha256']
    baseline=(D/'baseline.py').read_bytes(); candidate=(D/'candidate.py').read_bytes()
    assert baseline==subprocess.check_output(['git','show','f044ef39413f2adb47cf720d3a8f58ed6666f861:agent_runtime/communication.py'],cwd=ROOT)
    harness=module(ROOT/'scripts/benchmark_communication_candidates_v2.py','ackharness')
    assert candidate.decode()==harness.variant(baseline.decode(),10)
    trees=[]
    for code in (baseline,candidate):
        tree=ast.parse(code); box=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Mailbox')
        box.body=[x for x in box.body if not(isinstance(x,ast.FunctionDef) and x.name=='acknowledge')]
        trees.append(ast.dump(tree,include_attributes=False))
    assert trees[0]==trees[1], 'Only acknowledge may differ; DDL/init/other paths unchanged'
    diff=''.join(difflib.unified_diff(baseline.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='baseline',tofile='candidate'))
    (D/'independent_source.diff').write_text(diff)
    cohorts={name:summarize(json.loads(path.read_text())) for name,path in [('producer',D/'raw.json'),('independent',D/'independent_replay/raw.json')]}
    config=json.loads((D/'config_v2.json').read_text())
    assert config['repeats']==config['independent_repeats']==31 and config['warmups']==3 and config['operation']=='ack'
    summary=json.loads((D/'summary.json').read_text())
    assert summary['cases']==3 and summary['repeats']==31 and summary['test_result']==json.loads((D/'test_result.json').read_text())
    assert manifest['metrics']==[dict(name='case_count',value=3,unit='dimensionless')]
    env=json.loads((D/'environment.json').read_text())
    ownenv=json.loads((D/'independent_environment.json').read_text())
    for key in ('python','sqlite','platform'):
        assert env[key]==ownenv[key]
        for path in (D/'raw.json',D/'independent_replay/raw.json'):
            assert json.loads(path.read_text())['environment'][key]==env[key]
    for p in (D/'test_result.json',D/'independent_replay/test_result.json'):
        r=json.loads(p.read_text()); assert r['ok'] and r['run']==25 and r['failures']==r['errors']==0
    safety_expected=dict(duplicate_mutated_ref='rejected',changed_valid_manifest='rejected',thread_retry=['accepted']*4)
    for path in (D/'safety.json',D/'independent_replay/safety.json'):
        assert json.loads(path.read_text())==dict(baseline=safety_expected,candidate=safety_expected)
    for label in ('baseline','candidate'):
        assert json.loads((D/('independent_properties_'+label+'.json')).read_text())['count']==61
    assert all(json.loads((D/('independent_ack_properties_'+label+'.json')).read_text())['ok'] for label in ('baseline','candidate'))
    keep=all(c['guard'] and (not c['primary'] or c['improved']) for rows in cohorts.values() for c in rows)
    decision=dict(keep=keep,reason='All frozen primary improvements and public guards confirmed in both cohorts' if keep else 'Primary or public guard gate not confirmed; preserve baseline',**cohorts)
    (D/'independent_decision.json').write_text(json.dumps(decision,indent=2)+'\n')
    evidence=[ref(p) for p in [D/'independent_validate.py',D/'independent_before_snapshot.json',D/'independent_after_snapshot.json',D/'independent_validation_attempt1.log',D/'independent_source.diff',D/'independent_decision.json',D/'independent_environment.json',D/'independent_properties_baseline.json',D/'independent_properties_candidate.json',D/'independent_ack_properties_baseline.json',D/'independent_ack_properties_candidate.json',D/'independent_ack_properties.py',D/'independent_regressions_baseline.log',D/'independent_regressions_candidate.log',D/'independent_replay/raw.json',D/'independent_replay/safety.json',D/'independent_replay/tests.log',D/'independent_replay.log',D.parent/'comm20-20261009/independent_properties.py']]
    reasons=dict(implementation='Exact current-main baseline and exact historical r10 transformation verified; AST equality outside acknowledge. Canonical validation/budget, BEGIN IMMEDIATE, run/recipient lookup and conflict checks precede return; first UPDATE unchanged.',reference_boundary='61 independent public list/byte properties each source; two regressions each source; extra ACK tests each source cover all statuses, reordered keys, invalid and oversized receipts, conflicts, missing/crossrun/recipient, concurrent first/duplicate, reopen and counters.',data_integrity='Native artifact snapshot before and after; exact three ordered shapes,31 pairs/3 warmups each cohort;31 writes/reopens and3 migrations; exact safety and25 correctness tests; consistent Python/SQLite/platform.',numerical_sanity='All paired nested timing leaves positive finite milliseconds; recalculated exact medians, ratios, change reduction, publish/fresh ACK guards and diagnostic maintenance medians; duplicate candidate0changes/base1, storage equal.',measurement_validity='Full public ACK including SQLite connection and BEGIN IMMEDIATE lock;31 alternating pairs following3 warmups. All samples retained; separate first ACK/publish guards; no DDL changes, maintenance diagnostics retained. Shared CPU/warm cache limits claims.',reproducibility='One independent31-pair frozen-source replay plus independent public and ACK properties/regressions; no retries or selected subsets. Adoption gate applied to EACH primary shape in BOTH cohorts.')
    review=dict(schema_version='experiment-validation/v1',**proof,verifier=dict(actor='ack-independent-verifier',independent=True,source='actual host child /root/ack_verify; parent authenticates returned message',run_id='comm-ack-independent-20261009',method='Exact source/harness review; independent public and ACK properties; one31pair replay and complete numeric/hash audit'),limitations=['Local synthetic SQLite/filesystem public APIs only; no model/network/token claim.','Shared host CPU,warm cache,no affinity; performance is scoped to three fixed cases and two cohorts.','Finite checks and hashes do not prove universal correctness or standalone reviewer authentication.','Reduction measures logical UPDATE statements and sqlite3 total_changes, not physical disk writes; duplicate ACK still acquires BEGIN IMMEDIATE.','Initial helper-only SQL trace COMMIT assertion corrected because observer disables callback before connection context commits; failed helper log preserved. No performance rerun or frozen gate change.'],checks={k:dict(verdict='pass',reason=v,evidence=evidence) for k,v in reasons.items()},decision=decision)
    assert _snapshot(ROOT,contract)[2]==proof
    _review(ROOT,manifest,plan,proof,review)
    (D/'validation.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(dict(status='usable-with-scope',keep=keep,validation_sha256=digest(D/'validation.json'),failures=[dict(cohort=n,case=(c['total'],c['layout']),guards=c['guards']) for n,rows in cohorts.items() for c in rows if not c['guard'] or(c['primary'] and not c['improved'])])))

if __name__=='__main__':
    if sys.argv[1]=='properties': public_checks()
    elif sys.argv[1]=='validate': validate()
    else: raise ValueError('explicit phase required')
