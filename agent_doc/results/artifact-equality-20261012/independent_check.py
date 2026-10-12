"""Independent CPU public-entry equivalence and timing, no model-cost claims."""
import hashlib, importlib, itertools, json, platform, statistics, subprocess, sys, tempfile, time, types
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
import agent_runtime.artifact_context as candidate
baseline_source = subprocess.check_output(['git','show','bd65a2348e32d8a70af9e003cbc309064363dd9e:agent_runtime/artifact_context.py'], cwd=ROOT).decode()
baseline = types.ModuleType('agent_runtime._independent_baseline')
baseline.__package__ = 'agent_runtime'
exec(compile(baseline_source,'baseline/artifact_context.py','exec'), baseline.__dict__)
candidate_source = Path(candidate.__file__).read_text()
assert 'multi_edit and before != after' in candidate_source, 'candidate not ready'

report = {'baseline':'bd65a2348e32d8a70af9e003cbc309064363dd9e',
          'candidate_sha256':hashlib.sha256(candidate_source.encode()).hexdigest(),
          'python':sys.version,'platform':platform.platform(), 'cases':[], 'timings':[]}
cases = [(x,x) for x in ['', 'a','a\n','\r\n','中\n文\r\n','🙂\n'*8,'line\n'*100,
                         'x'*65536,'x'*65537,'z\n'*2049]]
cases += [('old\n'+str(i)+'\nend\n', 'new\n'+str(i)+'\nend!\n') for i in range(16)]
cases += [('a\r\nb\n','a\r\n新\n'), ('x',''), ('','x'), ('repeat\n'*30,'repeat\n'*29)]
with tempfile.TemporaryDirectory() as td:
    root = Path(td).resolve()
    def save(name,text):
        (root/name).write_bytes(text.encode())
        return {'path':name,'sha256':hashlib.sha256(text.encode()).hexdigest()}
    for index,(old,new) in enumerate(cases):
        refs = [save('before',old),save('after',new)]
        flags_checked = 0
        for full,multi,reuse in itertools.product([False,True], repeat=3):
            kwargs = dict(full=full,multi_edit=multi,reuse_identical=reuse,max_chars=1_000_000)
            for counted in [False,True]:
                seen_old=[];seen_new=[]
                counter_old=(lambda s:seen_old.append(s) or len(s)) if counted else None
                counter_new=(lambda s:seen_new.append(s) or len(s)) if counted else None
                expected = baseline.compare_artifacts(root,*refs,token_counter=counter_old,**kwargs)
                actual = candidate.compare_artifacts(root,*refs,token_counter=counter_new,**kwargs)
                assert actual == expected
                assert seen_new == seen_old
                assert candidate.restore_comparison(root,actual,*refs)==(old,new)
                flags_checked += 1
        report['cases'].append({'index':index,'old_chars':len(old),'new_chars':len(new),'variants':flags_checked})
    refs=[save('before','same\n'),save('after','same\n')]
    with patch.object(candidate,'_edits',side_effect=AssertionError('equal diff invoked')):
        candidate.compare_artifacts(root,*refs,multi_edit=True)
    refs=[save('before','same\n'),save('after','changed\n')]
    with patch.object(candidate,'_edits',wraps=candidate._edits) as diff:
        candidate.compare_artifacts(root,*refs,multi_edit=True)
        assert diff.call_count==1
    refs=[save('before','same\n'),save('after','same\n')]
    (root/'after').write_text('different')
    for module in [baseline,candidate]:
        try: module.compare_artifacts(root,*refs,multi_edit=True,token_counter=lambda _:(_ for _ in ()).throw(AssertionError('stale counted')))
        except ValueError as exc: assert 'stale' in str(exc)
        else: raise AssertionError('stale after accepted')
    text='identical repeated line\n'*2048
    refs=[save('before',text),save('after',text)]
    kwargs=dict(multi_edit=True,max_chars=1_000_000)
    assert baseline.compare_artifacts(root,*refs,**kwargs)==candidate.compare_artifacts(root,*refs,**kwargs)
    candidate.compare_artifacts(root,*refs,**kwargs)
    for i in range(7):
        pair={}
        order=[('baseline',baseline),('candidate',candidate)]
        if i%2: order.reverse()
        for name,module in order:
            begin=time.perf_counter_ns(); module.compare_artifacts(root,*refs,**kwargs)
            pair[name+'_ns']=time.perf_counter_ns()-begin
        report['timings'].append(pair)
report['baseline_median_ns']=statistics.median(p['baseline_ns'] for p in report['timings'])
report['candidate_median_ns']=statistics.median(p['candidate_ns'] for p in report['timings'])
report['reduction']=1-report['candidate_median_ns']/report['baseline_median_ns']
assert report['reduction']>=.5
report['verdict']='usable-with-scope'
(OUT/'independent_raw.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'case_count':len(cases),'payload_variants':sum(c['variants'] for c in report['cases']), 'reduction':report['reduction'],'verdict':report['verdict']}))
