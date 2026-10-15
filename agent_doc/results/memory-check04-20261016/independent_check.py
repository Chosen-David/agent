import hashlib
import itertools
import json
from pathlib import Path
import sqlite3
import subprocess
import tempfile
from unittest.mock import patch

from agent_runtime import project_memory as after
from agent_runtime.project_docs import migrate

BASE = '2d7ddc46b13b24ecc0c3611b1d8dcb63df7e6b10'
ns = {'__name__': 'agent_runtime._independent_baseline', '__package__': 'agent_runtime'}
exec(compile(subprocess.check_output(['git', 'show', BASE + ':agent_runtime/project_memory.py']), BASE, 'exec'), ns)
Before = ns['MemoryLedger']
count = 0
records = []

def outcome(cls, root, refs):
    calls = []
    original = cls._get
    def get(db, ref):
        calls.append(ref)
        return original(db, ref)
    with patch.object(cls, '_get', staticmethod(get)):
        try:
            result = ('ok', cls(root).check(refs))
        except Exception as exc:
            result = ('error', type(exc).__name__, str(exc))
    return result, calls

def compare(root, refs, label):
    global count
    a, b = outcome(Before, root, refs), outcome(after.MemoryLedger, root, refs)
    assert a == b, (label, refs, a, b)
    count += 1
    return a

def populate(root, nodes, edges):
    ledger = after.MemoryLedger(root, create=True)
    with ledger._connect(write=True) as db:
        db.executemany('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?)',
            [(str(i), 'claim', 'payload'*9, 'synthetic', '[]', 'verified', 'active', '2026-10-16') for i in range(nodes)])
        db.executemany('INSERT INTO dependencies VALUES(?,?)', [(str(c), str(p)) for c,p in edges])
    return ledger

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    ledger = populate(root, 3, [])
    possible = list(itertools.product(range(3), repeat=2))
    roots = [list(p) for size in (1,2,3) for p in itertools.permutations(['0','1','2'], size)]
    for mask in range(512):
        with ledger._connect(write=True) as db:
            db.execute('DELETE FROM dependencies')
            db.executemany('INSERT INTO dependencies VALUES(?,?)',
                [(str(c),str(p)) for bit,(c,p) in enumerate(possible) if mask & (1 << bit)])
        for refs in roots:
            compare(root, refs, 'all-directed-three-node-graphs')
    records.append({'group':'exhaustive directed graphs with self/cycles', 'cases':512*15})
    with ledger._connect(write=True) as db:
        db.execute('DELETE FROM dependencies')
        db.executemany('INSERT INTO dependencies VALUES(?,?)', [('2','1'),('1','0')])
    class S(str):
        pass
    for refs in (None, [], (), '2', ['2','2'], ['missing'], ['bad id'], [1], { '2' }, [S('2')], (S('2'),'0')):
        compare(root, refs, 'refs boundary')
    for sql in ("UPDATE entries SET status='stale' WHERE id='0'",
                "UPDATE entries SET status='candidate' WHERE id='1'",
                "UPDATE entries SET status='superseded' WHERE id='2'"):
        with ledger._connect(write=True) as db:
            db.execute(sql)
        compare(root, ['2','0'], 'first-status-error')
    records.append({'group':'refs/subclass and status error order', 'cases':14})

malformed = [
    ["UPDATE entries SET scope='{' WHERE id='1'"],
    ["INSERT INTO document_dependencies VALUES('1','{')"],
    ["INSERT INTO document_dependencies VALUES('1','{}')"],
    ["DROP TABLE document_dependencies"],
    ["DROP TABLE dependencies"],
    ["DROP TABLE entries"],
    ["DELETE FROM dependencies", "INSERT INTO dependencies VALUES('2','missing')"],
    ["DROP TABLE dependencies", "CREATE TABLE dependencies(child,parent)", "INSERT INTO dependencies VALUES('2',NULL)"],
    ["DROP TABLE dependencies", "CREATE TABLE dependencies(child,parent)", "INSERT INTO dependencies VALUES('2',123)"],
    ["DROP TABLE dependencies", "CREATE TABLE dependencies(child,parent)", "INSERT INTO dependencies VALUES('2',X'3031')"],
    ["DROP TABLE dependencies", "CREATE TABLE dependencies(child,parent)", "INSERT INTO dependencies VALUES('2','1')", "INSERT INTO dependencies VALUES('2','1')"],
]
for i, statements in enumerate(malformed):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        ledger = populate(root,3,[(2,1),(1,0)])
        db = sqlite3.connect(ledger.path)
        for statement in statements:
            db.execute(statement)
        db.commit()
        db.close()
        for refs in (['2'], ['0','2'], ['2','1']):
            compare(root, refs, 'isolated malformed db '+str(i))
records.append({'group':'malformed/legacy/schema/JSON/deps', 'cases':33})

with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root/'TASK.md').write_text('## 2026-10-16\n- [ ] [T1] Initial task\n')
    snapshot = migrate(root,'2026-10-16')
    ledger = after.MemoryLedger(root,create=True)
    ledger.add('bound','claim','bound','synthetic',evidence='verified',document_refs=snapshot)
    ledger.add('leaf','claim','leaf','synthetic',deps=['bound'],evidence='verified')
    compare(root,['leaf','bound'],'document valid')
    task = root/'agent_doc/task/TASK.md'
    original = task.read_text()
    task.write_text(original.replace('Initial','Changed'))
    compare(root,['leaf'],'document changed')
    task.write_text(original)
    compare(root,['leaf'],'document restored')
    result = ledger.check(['leaf'])
    result[0]['content'] = 'mutated'
    result[0]['deps'].clear()
    compare(root,['leaf'],'return mutation isolation')
    ledger.correct('bound','bound2','new','user','fixture correction',document_refs=snapshot)
    compare(root,['leaf'],'correction freshness')
    database = ledger.path
    backup = database.with_suffix('.bak')
    database.rename(backup)
    database.symlink_to(backup)
    compare(root,['bound2'],'path symlink freshness')
records.append({'group':'actual document/correction/mutation/path freshness','cases':6})

depths = []
for n in (1024,1200):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        populate(root,n,[(i,i-1) for i in range(1,n)])
        a, b = outcome(Before,root,[str(n-1)]), outcome(after.MemoryLedger,root,[str(n-1)])
        assert a[0][0]=='error' and a[0][1]=='RecursionError', a[0]
        assert b[0][0]=='ok' and len(b[1])==n, b[0]
        depths.append({'nodes':n, 'baseline':a[0][:2], 'candidate':'success', 'candidate_reads':len(b[1])})

raw = json.loads(Path('.agent-runs/memory-check04-20261016/raw-primary.json').read_text())
config = Path('.agent-runs/memory-check04-20261016/plan.json').read_bytes()
assert raw['config_sha256'] == hashlib.sha256(config).hexdigest()
assert raw['candidate_source_sha256'] == hashlib.sha256(Path(after.__file__).read_bytes()).hexdigest()
import statistics
for case in raw['cases']:
    for kind,n in [('wall',21),('traced',7)]:
        assert len(case[kind])==n
        for pair in case[kind]:
            assert sorted(pair['order'])==['after','before']
            assert pair['after'] > 0 and pair['before'] > 0
        med = {arm:statistics.median(p[arm] for p in case[kind]) for arm in ['before','after']}
        assert med['before']==case[kind+'_summary']['before']
        assert med['after']==case[kind+'_summary']['after']
        assert 1-med['after']/med['before']==case[kind+'_summary']['reduction']
report = {'ordinary_differential_cases':count, 'groups':records,'depth_reliability':depths,
          'primary_raw_recomputed':True, 'scope':'synthetic SQLite ordinary parity and depth extension; no model benefit'}
Path('.agent-runs/memory-check04-20261016/reviewer/checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
