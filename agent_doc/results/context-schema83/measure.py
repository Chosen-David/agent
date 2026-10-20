"""Complete basis_context; baseline closure loaded from the pinned commit."""
import ast
import hashlib
import json
from pathlib import Path
import platform
import random
import sqlite3
import statistics
import subprocess
import tempfile
import time
from agent_runtime import project_memory as m
from agent_runtime.handoff_basis import basis_context

base='fad3bd48ba108b90a8e36ecafd5bf2462207c8bd'
source=subprocess.check_output(['git','show',base+':agent_runtime/project_memory.py'],text=True)
cls=next(n for n in ast.parse(source).body if isinstance(n,ast.ClassDef) and n.name=='MemoryLedger')
fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_context_closure')
ns=dict(vars(m)); exec(compile(ast.Module(body=[fn],type_ignores=[]),'baseline','exec'),ns)
before=ns['_context_closure']; after=m.MemoryLedger._context_closure
randomizer=random.Random(83)
cases=[]
for count in (1,32,256,512):
    with tempfile.TemporaryDirectory() as root:
        ledger=m.MemoryLedger(root,create=True)
        rows=[(f'm{i}','claim','x'*128,'synthetic','[]','verified','active','2026-10-20') for i in range(count)]
        edges=[(f'm{i}',f'm{i-1}') for i in range(1,count)]
        with ledger._connect(write=True) as db:
            db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',rows)
            db.executemany('INSERT INTO dependencies VALUES(?,?)',edges)
        record={'input_version':'v1','memory_refs':[f'm{count-1}'],'artifacts':[]}
        arms={'before':before,'after':after}; values={}; samples={k:[] for k in arms}
        try:
            for name,method in arms.items():
                m.MemoryLedger._context_closure=method
                values[name]=basis_context(root,record,{},max_chars=200000)
                for _ in range(3): basis_context(root,record,{},max_chars=200000)
            if values['before']!=values['after']: raise RuntimeError('payload mismatch')
            for _ in range(21):
                order=list(arms); randomizer.shuffle(order)
                for name in order:
                    m.MemoryLedger._context_closure=arms[name]
                    start=time.perf_counter_ns()
                    for _ in range(5): value=basis_context(root,record,{},max_chars=200000)
                    samples[name].append((time.perf_counter_ns()-start)/5)
                    if value!=values['before']: raise RuntimeError('timed payload mismatch')
        finally:
            m.MemoryLedger._context_closure=after
        medians={k:statistics.median(v) for k,v in samples.items()}
        cases.append({'nodes':count,'samples_ns':samples,'medians_ns':medians,
                      'input_sha256':hashlib.sha256(json.dumps([rows,edges,record],sort_keys=True).encode()).hexdigest(),
                      'reduction':1-medians['after']/medians['before']})
print(json.dumps({'baseline':base,'candidate_sha256':hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest(),
 'python':platform.python_version(),'platform':platform.platform(),'sqlite':sqlite3.sqlite_version,
 'cases':cases,'gate':all(c['reduction']>=(.05 if c['nodes']>=256 else -.10) for c in cases)},indent=2))
