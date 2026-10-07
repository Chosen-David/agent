"""Independent exact references and scoped rerun; writes only independent/."""
from pathlib import Path
from fractions import Fraction as Q
from functools import reduce
from operator import mul
import hashlib, json, subprocess, sys, shutil, platform, importlib.metadata
import tiktoken

ROOT = Path(__file__).resolve().parents[4]
D = Path(__file__).parent
RUN = D.parent
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name, data): (D/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
manifest = read(RUN/'manifest.json')
bindings = {manifest['validation_plan']['path']: manifest['validation_plan']['sha256']}
for refs in manifest['artifacts'].values():
    for ref in refs: bindings[ref['path']] = ref['sha256']
assert sha(RUN/'manifest.json') == '5dc9adee81f059ce1014bbfcba3931cbf532d8c1868885b2a4180789850368e2'
for p,h in bindings.items(): assert sha(ROOT/p) == h, p
corpus = read(RUN/'retrieval-corpus.json')['files']
actual = sorted(str(p.relative_to(ROOT)) for p in (ROOT/'knowledge/entries').rglob('*') if p.is_file() and p.suffix in ('.json','.md'))
assert sorted(r['path'] for r in corpus) == actual
for ref in corpus: assert sha(ROOT/ref['path']) == ref['sha256']

# Direct signed difference convolution is independent of producer's x/y trajectory.
raw = read(RUN/'raw.json')
prod = lambda values: reduce(mul, values, Q(1))
stage_count = 0
zero_gains = zero_defects = 0
for expected_id, row in enumerate(raw['cases']):
    assert row['case'] == expected_id and row['n'] == len(row['stages']) == expected_id % 7
    delta = [Q(0),Q(0)]  # Initial signed vector is deliberately not recorded.
    gains, eps = [], []
    for k, stage in enumerate(row['stages']):
        a,b,c = [[Q(v) for v in stage[key]] for key in ('a','b','c')]
        assert len(a) == len(b) == len(c) == 2
        gains.append(max(map(abs,a))); eps.append(max(map(abs,b)))
        zero_gains += gains[-1] == 0; zero_defects += eps[-1] == 0
        B = prod(gains)*Q(row['e0']) + sum(eps[i]*prod(gains[i+1:]) for i in range(k+1))
        assert Q(stage['bound']) == B and 0 <= Q(stage['error']) <= B
        stage_count += 1
    B = prod(gains)*Q(row['e0'])+sum(eps[i]*prod(gains[i+1:]) for i in range(row['n']))
    assert B == Q(row['expanded'])
assert len(raw['cases']) == 56 and stage_count == 168
for row in raw['contractions']:
    rho,n = Q(row['rho']),row['n']
    expected = rho**n*Q(1,5) + sum(rho**k*Q(1,10) for k in range(n))
    assert expected == Q(row['value'])
assert len({(r['rho'],r['n']) for r in raw['contractions']}) == len(raw['contractions']) == 28

# Reexecute exact original bytes with identical seed/config, isolated outputs.
replay = D/'replay'; replay.mkdir(exist_ok=True)
for name in ('verify.py','config.json'): shutil.copyfile(RUN/name,replay/name)
subprocess.run([sys.executable,str(replay/'verify.py')],cwd=ROOT,check=True)
assert (replay/'raw.json').read_bytes() == (RUN/'raw.json').read_bytes()
s, rs = read(RUN/'summary.json'),read(replay/'summary.json')
for key in ('cases','contraction_cases','assertions','scope'): assert s[key] == rs[key]
assert s['assertions'] == stage_count+56+3+28 == 255

# Actually evaluate literal boundary fixtures and additional premises.
F = [lambda x:Q(0),lambda x:Q(0)]
G = [lambda x:Q(1,10),lambda x:100*x]
x=y=Q(0); teacher=[]; approximate=[]
for f,g in zip(F,G):
    teacher.append(abs(g(x)-f(x))); approximate.append(abs(g(y)-f(y)))
    x,y=f(x),g(y)
assert abs(y-x) == 10 and teacher == [Q(1,10),Q(0)] and approximate == [Q(1,10),Q(10)]
assert 100*teacher[0]+teacher[1] == 10
square_error = abs(Q(1,10)**2-Q(0)**2)
assert square_error == Q(1,100) and square_error <= Q(1,5)*Q(1,10)
y = Q(0)+Q(1,10)-Q(1,10)
assert y == 0 and abs(Q(1,10))+abs(-Q(1,10)) == Q(1,5)
checks = {'teacher_actual':'10','teacher_false_bound':'0','square_actual':'1/100','square_segment_bound':'1/50','point_jacobian_false_bound':'0','cancellation_error':'0','cancellation_bound':'1/5','early_error':'1/10','late_error':'1/100','relative_drift_before':'1','relative_drift_after':'1/50','absolute_drift_before':'1','absolute_drift_after':'2'}
for k,v in checks.items(): assert Q(raw['boundaries'][k]) == Q(v)
# Zero defect and e0 propagation, zero gain, and heterogeneous normed spaces.
assert prod([Q(2),Q(0),Q(4)])*Q(3) == 0
assert prod([])*Q(3)+sum([]) == 3
assert abs((1-Q(1,2))*Q(4)) <= (1+Q(1,2))*Q(4)
x,y=Q(2),Q(3)
fx,fy=(x,-x),(y,-y)
assert max(abs(fy[j]-fx[j]) for j in range(2)) == abs(y-x)
assert abs(sum(fy)-sum(fx)) <= 2*max(abs(fy[j]-fx[j]) for j in range(2))
# Changing downstream gain makes frozen proxy rank reverse: local eps .1 vs .2.
assert Q(1,10)<Q(1,5) and 100*Q(1,10)>Q(1,5)
# Same local score mapping with a changed cache loses the fixed-input guarantee.
fixed_cache = lambda query,cache: query*cache
assert fixed_cache(Q(1),Q(1)) == fixed_cache(Q(1),Q(1))
assert abs(fixed_cache(Q(1),Q(2))-fixed_cache(Q(1),Q(1))) == 1

def cli(*args):
    return json.loads(subprocess.check_output([sys.executable,'-m','agent_runtime.knowledge','--root','knowledge',*args],cwd=ROOT))
index = D/'search.sqlite'; indexed = cli('index','--db',str(index))
usage=read(RUN/'knowledge-usage.json'); searches=[]
for record in usage['retrieval']:
    args=['search',record['input']['query'],'--domain',record['domain'],'--limit','3']
    if record['backend']=='sqlite': args += ['--index',str(index)]
    out=cli(*args)
    assert out == record['result']
    assert out['results'][0]['id'] == 'math.perturbation-propagation'
    searches.append({'backend':record['backend'],'query':record['input']['query'],'top_id':out['results'][0]['id'],'snapshot':out['snapshot']})
show=cli('show','math.perturbation-propagation')
assert show['knowledge_refs']==usage['knowledge_refs'] and len(show['knowledge_refs'])==1
assert show['knowledge_refs'][0]['sha256']=='2d6cdb1a0fa413d3dc37caa0e64ba20e517f6c71d82cc05bf626806bca010381'
encoded=tiktoken.get_encoding('cl100k_base').encode(json.dumps(show,ensure_ascii=False))
cost=read(RUN/'cost.json')
assert len(encoded)==cost['body_package_cl100k_base_tokens']==3943
assert cost['retrieval_cli_calls']==8 and not cost['token_saving_claim'] and cost['model_AB_calls']==0
for p,h in bindings.items(): assert sha(ROOT/p)==h, p
index.unlink()  # Rebuildable cache is not a delivered or bound evidence artifact.
write('observations.json',{'status':'pass','manifest_sha256':sha(RUN/'manifest.json'),'artifact_hashes':bindings,'corpus_files_checked':len(corpus),'corpus_exact_inventory':True,'original_raw_rerun_byte_identical':True,'case_count':56,'stage_count':stage_count,'contraction_count':28,'producer_assertions_confirmed':255,'zero_gain_random_stages':zero_gains,'zero_defect_random_stages':zero_defects,'boundary_fixture_values':checks,'extra_executed_checks':['teacher swap under both decompositions','Jacobian at zero versus finite perturbation','signed cancellation','zero gain and zero layers','zero defect initial error','residual triangle bound','1D to 2D to 1D normed spaces','config dependent downstream gain rank reversal','changed cache invalidates fixed mapping'],'retrieval':searches,'retrieval_exact_replay':True,'show_tokens':len(encoded),'index':indexed,'environment':{'python':sys.version,'platform':platform.platform(),'tiktoken':importlib.metadata.version('tiktoken'),'sqlite':__import__('sqlite3').sqlite_version},'timing_scope':'Producer elapsed_seconds is unreplicated incidental whole-script wall time, not accepted latency/performance data.'})
print(json.dumps({'pass':True,'cases':56,'stages':168,'contractions':28,'tokens':len(encoded),'corpus_files':len(corpus)}))
