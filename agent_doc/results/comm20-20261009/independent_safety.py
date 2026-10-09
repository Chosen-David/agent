"""Five independent public trust/isolation counterexamples, no timing claim."""
import json,hashlib,tempfile,sys,sqlite3,importlib.util
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
spec=importlib.util.spec_from_file_location('props',Path(__file__).with_name('independent_properties.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def run(cls):
    trials=[]
    for repeat in range(5):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'data').write_bytes(b'evidence');ref={'id':'data','path':'data','sha256':hashlib.sha256(b'evidence').hexdigest()}
            plan={'schema_version':1,'run_id':'safety','input_version':'v1','max_events':100,'routes':[{'sender':'s','recipient':'r','task_id':'T','kind':'artifact'}]}
            b=cls(root/'db',plan,root)
            ev={'event_id':'retry','run_id':'safety','input_version':'v1','sender':'s','task_id':'T','kind':'artifact','summary':'read','action':'inspect','refs':[dict(ref)]}
            b.publish(ev);(root/'data').write_bytes(b'modified')
            def observe(f):
                try:f();return 'accepted'
                except (ValueError,sqlite3.Error) as exc:return 'rejected:'+type(exc).__name__
            duplicate=observe(lambda:b.publish(ev));(root/'data').write_bytes(b'evidence')
            record={'schema_version':1,'run_id':'safety','role':'s','input_version':'v1','status':'completed','limitations':[],'artifacts':[dict(ref)],'checks':[{'criterion':'verified','status':'pass','artifact_ids':['data']}],'tasks':[{'task_id':'T','status':'done','depends_on':[],'evidence':['data']}]}
            raw=json.dumps(record,sort_keys=True,separators=(',',':')).encode();(root/'manifest').write_bytes(raw)
            hev=dict(ev,event_id='handoff',refs=[{'id':'handoff','path':'manifest','sha256':hashlib.sha256(raw).hexdigest()}]);seq=b.publish(hev)['seq']
            record['limitations']=['valid changed manifest'];(root/'manifest').write_text(json.dumps(record))
            manifest=observe(lambda:b.consume_handoff('r',seq,{'schema_version':1,'input_version':'v1','tasks':[{'task_id':'T'}]}))
            with ThreadPoolExecutor(max_workers=2) as pool:threaded=list(pool.map(lambda _:observe(lambda:b.publish(ev)),range(4)))
            trials.append({'repeat':repeat,'duplicate_mutated_ref':duplicate,'changed_valid_manifest':manifest,'thread_retry':threaded})
    return {'repeats':5,'trials':trials}
if __name__=='__main__':
    result={n:run(m.load(sys.argv[k])) for k,n in [(1,'baseline'),(2,'candidate')]};print(json.dumps(result,indent=2))
