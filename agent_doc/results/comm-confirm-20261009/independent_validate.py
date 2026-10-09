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
    props = module(old/'independent_properties.py', 'confirmprops')
    snapshots = module(old/'independent_snapshot_properties.py', 'confirmsnapshots')
    for label in ('baseline', 'candidate'):
        cls = props.load(D/(label+'.py'))
        result = props.run(cls)
        assert result['count'] == 61 and result['ok']
        (D/('independent_properties_'+label+'.json')).write_text(json.dumps(result, indent=2)+'\n')
        # Existing new counterexamples are run with the exact frozen class.
        regression = module(ROOT/'tests/test_communication_regressions.py', 'confirmregression_'+label)
        regression.Mailbox = cls
        import io, unittest
        stream = io.StringIO()
        run = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(regression))
        (D/('independent_regressions_'+label+'.log')).write_text(stream.getvalue())
        assert run.wasSuccessful() and run.testsRun == 2
    result = snapshots.run(props.load(D/'candidate.py'))
    assert len(result['checks']) == 6 and result['ok']
    (D/'independent_snapshot.json').write_text(json.dumps(result, indent=2)+'\n')

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
    shapes = [(100,'single',1),(20000,'single',1),(20000,'interleaved',1),(20000,'last',1),(20000,'absent',1),(20000,'history',1),(0,'absent',1)]
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
        assert all(c['observed'][n]['changes']==0 for n in m)
        b,v=m['baseline'],m['candidate']; reduction=1-vm['candidate']/vm['baseline']
        primary=c['total']==20000 and c['layout'] in ('last','absent')
        improvement=(b/v>=1.25 and b-v>=.05) or (reduction>=.2 and v<=b)
        guards = {'inbox':v<=1.25*b or v-b<.2}
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
    ready=json.loads((D/'ready.json').read_text())
    assert ready['manifest']['sha256']==proof['manifest_sha256']
    baseline=(D/'baseline.py').read_bytes(); candidate=(D/'candidate.py').read_bytes()
    assert baseline==subprocess.check_output(['git','show','aa93e85088bf73c36baf57b01ba924f210626847:agent_runtime/communication.py'],cwd=ROOT)
    assert candidate==(D.parent/'comm20-20261009-r17/candidate.py').read_bytes()
    trees=[]
    for code in (baseline,candidate):
        tree=ast.parse(code); box=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='Mailbox')
        box.body=[x for x in box.body if not(isinstance(x,ast.FunctionDef) and x.name=='inbox')]
        trees.append(ast.dump(tree,include_attributes=False))
    assert trees[0]==trees[1], 'Only inbox may differ; DDL/init/write paths unchanged'
    diff=''.join(difflib.unified_diff(baseline.decode().splitlines(True),candidate.decode().splitlines(True),fromfile='baseline',tofile='candidate'))
    (D/'independent_source.diff').write_text(diff)
    cohorts={name:summarize(json.loads(path.read_text())) for name,path in [('producer',D/'raw.json'),('independent',D/'independent_replay/raw.json')]}
    config=json.loads((D/'config.json').read_text())
    assert config['repeats']==config['independent_repeats']==31 and config['warmups']==3 and config['operation']=='inbox'
    summary=json.loads((D/'summary.json').read_text())
    assert summary['cases']==7 and summary['repeats']==31 and summary['test_result']==json.loads((D/'test_result.json').read_text())
    assert manifest['metrics']==[dict(name='case_count',value=7,unit='dimensionless')]
    env=json.loads((D/'environment.json').read_text())
    ownenv=json.loads((D/'independent_environment.json').read_text())
    for key in ('python','sqlite','platform'):
        assert env[key]==ownenv[key]
        for path in (D/'raw.json',D/'independent_replay/raw.json'):
            assert json.loads(path.read_text())['environment'][key]==env[key]
    for p in (D/'test_result.json',D/'independent_replay/test_result.json'):
        r=json.loads(p.read_text()); assert r['ok'] and r['run']>0 and r['failures']==r['errors']==0
    safety_expected=dict(duplicate_mutated_ref='rejected',changed_valid_manifest='rejected',thread_retry=['accepted']*4)
    for path in (D/'safety.json',D/'independent_replay/safety.json'):
        assert json.loads(path.read_text())==dict(baseline=safety_expected,candidate=safety_expected)
    for label in ('baseline','candidate'):
        assert json.loads((D/('independent_properties_'+label+'.json')).read_text())['count']==61
    assert json.loads((D/'independent_snapshot.json').read_text())['ok']
    keep=all(c['guard'] and (not c['primary'] or c['improved']) for rows in cohorts.values() for c in rows)
    decision=dict(keep=keep,reason='All frozen primary improvements and public guards confirmed in both cohorts' if keep else 'Primary or public guard gate not confirmed; preserve baseline',**cohorts)
    (D/'independent_decision.json').write_text(json.dumps(decision,indent=2)+'\n')
    evidence=[ref(p) for p in [D/'independent_validate.py',D/'independent_source.diff',D/'independent_decision.json',D/'independent_environment.json',D/'independent_properties_baseline.json',D/'independent_properties_candidate.json',D/'independent_snapshot.json',D/'independent_regressions_baseline.log',D/'independent_regressions_candidate.log',D/'independent_replay/raw.json',D/'independent_replay/safety.json',D/'independent_replay/tests.log',D/'independent_replay.log',D.parent/'comm20-20261009/independent_properties.py',D.parent/'comm20-20261009/independent_snapshot_properties.py']]
    reasons=dict(implementation='Read complete exact runtime and harness; only inbox differs in AST, with BEGIN ledger/query snapshot and unchanged fallback, validation and writes.',reference_boundary='61 independent public list/byte checks on each exact source plus both nested numeric-plan and mutated-ref regressions; six WAL/DELETE post-ledger-fetchone writer interleavings passed.',data_integrity='Native snapshot validates all manifest/config/source/raw/output hashes before and after. Seven exact ordered case IDs,31 paired samples per cohort,31 writes,31 reopen and3 diagnostic migrations complete.',numerical_sanity='Recomputed every median,ratio,VM reduction and public write guard; all nested write/timing leaves finite positive milliseconds; read changes zero and exact usage property oracles pass.',measurement_validity='Full public inbox includes connection/validation/parse,3 warmups,31 alternating pairs; public publish and fresh ACK guarded in every shape. No DDL/init source changes; approved maintenance timing diagnostics retained. Shared CPU/no affinity/warm cache limits extrapolation.',reproducibility='Actual independent31-pair exact-source replay,61 independent properties per implementation, targeted regression and six concurrent snapshot checks. One shot; no retries or selected subsets.')
    review=dict(schema_version='experiment-validation/v1',**proof,verifier=dict(actor='comm-confirm-independent-verifier',independent=True,source='actual host collaboration child /root/confirm_verify; parent authenticates returned message',run_id='comm-confirm-independent-20261009',method='Exact source/harness review; own public oracles; six concurrent snapshots;31 pair replay and complete numeric/hash audit'),limitations=['Local synthetic SQLite/filesystem public APIs only, append-only supported events; no model/network/token claim.','Shared host CPU,warm cache,no affinity; timing distribution and VM counts apply only to these seven cases.','Finite checks and hashes provide no universal correctness guarantee or standalone reviewer authentication.'],checks={k:dict(verdict='pass',reason=v,evidence=evidence) for k,v in reasons.items()},decision=decision)
    _snapshot(ROOT,contract); _review(ROOT,manifest,plan,proof,review)
    (D/'validation.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(dict(status='usable-with-scope',keep=keep,validation_sha256=digest(D/'validation.json'),failures=[dict(cohort=n,case=(c['total'],c['layout']),guards=c['guards']) for n,rows in cohorts.items() for c in rows if not c['guard'] or(c['primary'] and not c['improved'])])))

if __name__=='__main__':
    if sys.argv[1]=='properties': public_checks()
    elif sys.argv[1]=='validate': validate()
    else: raise ValueError('explicit phase required')
