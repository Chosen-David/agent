import sys,types,json,time,random,hashlib,tempfile,sqlite3,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime import handoff_basis as candidate
from agent_runtime.project_memory import MemoryLedger
RUN=Path(__file__).parent.parent

def module(name,path):
    m=types.ModuleType(name);m.__package__='agent_runtime';exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def main():
    bm=module('agent_runtime._base_memory10',RUN/'baseline_project_memory.py')
    baseline=module('agent_runtime._base_basis10',RUN/'baseline_handoff_basis.py');baseline.MemoryLedger=bm.MemoryLedger
    rng=random.Random(81610);raw=[]
    with tempfile.TemporaryDirectory() as tmp:
        for scenario,n,branch in [('chain96',96,False),('shared96',96,True),('small3',3,False),('no_memory',0,False)]:
            root=Path(tmp)/scenario;root.mkdir();ledger=MemoryLedger(root,create=True)
            for i in range(n):
                deps=[f'm{i-1:03}'] if i else []
                if branch and i>1:deps.append(f'm{i-2:03}')
                ledger.add(f'm{i:03}','claim',f'complete immutable evidence {i}','synthetic:fixture',deps=deps,evidence='verified')
            refs=[f'm{n-1:03}'] if n else []
            record={'input_version':'v1','artifacts':[],'memory_refs':refs};request={}
            with sqlite3.connect(ledger.path) as db:
                data={t:db.execute('SELECT * FROM '+t+' ORDER BY rowid').fetchall() for t in ('entries','dependencies','events','document_dependencies')}
            digest=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
            args={'max_chars':200000}
            if n:args['known_memory_ids']=[refs[0]]
            expected=baseline.basis_context(root,record,request,**args)
            assert candidate.basis_context(root,record,request,**args)==expected
            output_hash=hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest()
            for _ in range(3):
                baseline.basis_context(root,record,request,**args);candidate.basis_context(root,record,request,**args)
            for pair in range(21):
                order=['baseline','candidate'];rng.shuffle(order)
                for arm in order:
                    fun=baseline.basis_context if arm=='baseline' else candidate.basis_context
                    start=time.perf_counter_ns();out=fun(root,record,request,**args);elapsed=time.perf_counter_ns()-start
                    if out!=expected:raise RuntimeError('complete packet mismatch')
                    raw.append({'scenario':scenario,'pair':pair,'order':order,'arm':arm,'wall_ns':elapsed,'input_sha256':digest,'output_sha256':output_hash})
    value={'seed':81610,'warmup_pairs':3,'pairs_per_scenario':21,'samples':raw,'environment':{'python':sys.version,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version},'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'agent_runtime/handoff_basis.py',ROOT/'agent_runtime/project_memory.py']},'scope':'complete basis_context warm local CPU wall; read-only same DB per pair; equality outside timing; no model or KV serving'}
    (RUN/'reviewer/raw.json').write_text(json.dumps(value,indent=2))
    import statistics
    summary={}
    for s in ('chain96','shared96','small3','no_memory'):
        med={a:statistics.median([r['wall_ns'] for r in raw if r['scenario']==s and r['arm']==a]) for a in ('baseline','candidate')}
        summary[s]={**med,'reduction':1-med['candidate']/med['baseline']}
    (RUN/'reviewer/summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
if __name__=='__main__':main()
