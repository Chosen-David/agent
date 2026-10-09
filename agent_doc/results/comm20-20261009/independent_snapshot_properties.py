"""Independent post-ledger-read public writer snapshot and release checks."""
import sys,json,tempfile,hashlib,sqlite3,threading
from pathlib import Path
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from agent_runtime.communication import canonical
import importlib.util
spec=importlib.util.spec_from_file_location('ownprops',Path(__file__).with_name('independent_properties.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def run(cls):
    results=[]
    for journal in ['WAL','DELETE']:
        for initial in [0,1,4]:
            with tempfile.TemporaryDirectory() as temp:
                root=Path(temp);(root/'data').write_bytes(b'x');ref={'id':'data','path':'data','sha256':hashlib.sha256(b'x').hexdigest()}
                plan={'schema_version':1,'run_id':'snapshot','input_version':'v1','max_events':100,'routes':[{'sender':'s','recipient':'r','task_id':'T','kind':'artifact'}]}
                box=cls(root/'db',plan,root)
                with sqlite3.connect(box.path) as db:assert db.execute('PRAGMA journal_mode='+journal).fetchone()[0].upper()==journal
                def ev(i):return dict(event_id=str(i),run_id='snapshot',input_version='v1',sender='s',task_id='T',kind='artifact',summary='sample',action='read',refs=[dict(ref)])
                for i in range(initial):box.publish(ev(i))
                old=box.inbox('r',limit=3);original=box.connect;triggered=[False];started=threading.Event();future=[]
                def writer():
                    started.set()
                    return [box.publish(ev(i)) for i in range(initial,initial+5)]
                pool=ThreadPoolExecutor(max_workers=1)
                class Cursor:
                    def __init__(self,c):self.c=c
                    def fetchone(self):
                        value=self.c.fetchone()
                        if not triggered[0]:
                            triggered[0]=True;future.append(pool.submit(writer));assert started.wait(3)
                            if journal=='WAL':future[0].result(timeout=10)
                        return value
                    def __getattr__(self,k):return getattr(self.c,k)
                class Connection:
                    def __init__(self,c):self.c=c
                    def execute(self,sql,*args):
                        c=self.c.execute(sql,*args)
                        return Cursor(c) if sql.startswith('SELECT events FROM communication_usage_v1') else c
                    def __getattr__(self,k):return getattr(self.c,k)
                @contextmanager
                def connect():
                    with original() as db:yield Connection(db)
                box.connect=connect
                current=box.inbox('r',limit=3);box.connect=original
                assert triggered[0] and current==old,(journal,initial,current,old)
                committed=future[0].result(timeout=10);pool.shutdown()
                nextpoll=box.inbox('r',limit=3);expected=[{'seq':i+1,'event':ev(i)} for i in range(min(3,initial+5))]
                assert nextpoll==expected
                # The read transaction is released even along empty/low/full paths.
                box.publish(ev(initial+10))
                results.append({'journal':journal,'initial_events':initial,'current_old_snapshot':True,'next_poll_new_commit':True,'writer_completed_after_read_release':True,'committed':len(committed)})
    return {'ok':True,'checks':results}
if __name__=='__main__':print(json.dumps(run(m.load(sys.argv[1])),indent=2))
