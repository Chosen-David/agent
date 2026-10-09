"""Single frozen communication candidate producer; independent host owns acceptance."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import hashlib, importlib.util, io, json, platform, sqlite3, statistics, subprocess, sys, tempfile, time, types, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.communication import canonical
ROOT=Path(__file__).resolve().parents[1]

def replace(source,old,new,count=1):
    if source.count(old)<count: raise ValueError('variant source precondition failed: '+old[:70])
    return source.replace(old,new,count)

def variant(source,number):
    index="                CREATE INDEX IF NOT EXISTS comm20_event_run_seq ON communication_events(run_id,seq);\n"
    anchor='                CREATE INDEX IF NOT EXISTS communication_pending_recipient'
    old="""SELECT e.seq,e.body FROM communication_events e
                JOIN communication_deliveries d ON e.seq=d.seq
                WHERE e.run_id=? AND d.recipient=? AND d.receipt IS NULL
                ORDER BY d.seq LIMIT ?"""
    if number==1:
        return replace(source,anchor,"                CREATE INDEX IF NOT EXISTS comm20_delivery_cover ON communication_deliveries(recipient,receipt,seq);\n"+anchor)
    if number in (2,3,4,8): source=replace(source,anchor,index+anchor)
    if number==2 or number==8:return source
    if number==3:return replace(source,old,old.replace('ORDER BY d.seq','ORDER BY e.seq'))
    if number==4:return replace(source,old,old.replace('JOIN communication_deliveries','CROSS JOIN communication_deliveries').replace('ORDER BY d.seq','ORDER BY e.seq'))
    if number==5:return replace(source,old,"""SELECT e.seq,e.body FROM communication_events e
                WHERE e.run_id=? AND EXISTS (SELECT 1 FROM communication_deliveries d
                    WHERE d.seq=e.seq AND d.recipient=? AND d.receipt IS NULL)
                ORDER BY e.seq LIMIT ?""")
    if number==6:return replace(source,old,"""SELECT e.seq,e.body FROM communication_events e
                WHERE e.run_id=? AND e.seq IN (SELECT d.seq FROM communication_deliveries d
                    WHERE d.recipient=? AND d.receipt IS NULL)
                ORDER BY e.seq LIMIT ?""")
    if number==7:return replace(source,'ORDER BY e.seq,d.recipient','ORDER BY d.seq,d.recipient')
    if number==9:return replace(source,'ORDER BY b.seq,b.recipient','ORDER BY e.seq,b.recipient')
    if number==10:return replace(source,"            db.execute('UPDATE communication_deliveries SET receipt=? WHERE seq=? AND recipient=?',","            if row['receipt'] == body:\n                return\n            db.execute('UPDATE communication_deliveries SET receipt=? WHERE seq=? AND recipient=?',")
    if number==11:return replace(source,'UPDATE communication_deliveries SET receipt=? WHERE seq=? AND recipient=?','UPDATE communication_deliveries SET receipt=? WHERE seq=? AND recipient=? AND receipt IS NULL')
    if number==12:return replace(source,"all(r[k] == event[k] for k in ('sender', 'task_id', 'kind'))","r['sender'] == event['sender'] and r['task_id'] == event['task_id'] and r['kind'] == event['kind']")
    if number==13:
        old="all(r[k] == event[k] for k in ('sender', 'task_id', 'kind'))"
        if old not in source:old="r['sender'] == event['sender'] and r['task_id'] == event['task_id'] and r['kind'] == event['kind']"
        return replace(source,old,"(r['sender'],r['task_id'],r['kind']) == (event['sender'],event['task_id'],event['kind'])")
    if number==14:
        source=replace(source,"        body = canonical(event)\n", "        body = canonical(event)\n        body_bytes = len(body.encode('utf-8'))\n")
        return source.replace("len(body.encode('utf-8')) > self.plan.get('max_message_bytes', 8192)","body_bytes > self.plan.get('max_message_bytes', 8192)",1).replace("spent + len(body.encode('utf-8')) * len(recipients)","spent + body_bytes * len(recipients)")
    if number==15:
        source=replace(source,"        self.plan = json.loads(canonical(plan))","        plan_body = canonical(plan)\n        self.plan = json.loads(plan_body)")
        return replace(source,'canonical(self.plan)', 'plan_body',2)
    if number==16:return replace(source,'SELECT * FROM communication_usage_v1 WHERE run_id=?','SELECT events,envelope_bytes,deliveries,delivery_bytes FROM communication_usage_v1 WHERE run_id=?')
    if number==17:return replace(source,"        with self.connect() as db:\n            rows = db.execute(\'\'\'SELECT e.seq,e.body", "        with self.connect() as db:\n            if db.execute('SELECT events FROM communication_usage_v1 WHERE run_id=?',(self.run_id,)).fetchone()['events'] == 0:\n                return []\n            rows = db.execute(\'\'\'SELECT e.seq,e.body")
    if number==18:
        start=source.index('        errors = validate(',source.index('    def publish'))
        end=source.index('        with self.connect() as db:',start)
        block=source[start:end]
        source=source[:start]+source[end:]
        anchor2="            usage = db.execute('SELECT events,delivery_bytes"
        return replace(source,anchor2,''.join('    '+line+'\n' for line in block.rstrip().splitlines())+anchor2)
    if number==19:
        start=source.index('        errors = validate(',source.index('    def consume_handoff'))
        end=source.index('        record = _load_json',start)
        return source[:start]+source[end:]
    if number==20:
        source=replace(source,'        db = sqlite3.connect(self.path, timeout=30)',"        if not hasattr(self, '_shared_db'):\n            self._shared_db = sqlite3.connect(self.path, timeout=30)\n        db = self._shared_db")
        return replace(source,'            db.close()','            pass')
    raise ValueError(number)

def load(path):
    m=types.ModuleType('agent_runtime.comm20_'+hashlib.sha256(str(path).encode()).hexdigest()[:8]);m.__package__='agent_runtime'
    exec(compile(Path(path).read_text(),str(path),'exec'),m.__dict__)
    return m

def fixtures(cls,root,total,layout,routes=1):
    root.mkdir(parents=True)
    plan=dict(schema_version=1,run_id='target',input_version='v1',max_events=50000,max_message_bytes=8192,max_delivery_bytes=1000000000,
              routes=[dict(sender='code' if i==0 else 'other',recipient='reader' if i==0 else 'unused'+str(i),task_id='T1',kind='artifact') for i in range(routes)])
    started=time.perf_counter_ns();box=cls(root/'messages.db',plan,root);box._first_open_ms=(time.perf_counter_ns()-started)/1e6
    events=[];deliveries=[];expected=[];status=[]
    ack=canonical(dict(status='consumed',reason='read'))
    for i in range(1,total+1):
        run='target' if layout in ('single','history') or (layout=='interleaved' and i%4==0) or (layout=='last' and i>total-5) else 'other'
        event=dict(event_id=str(i),run_id=run,payload='界'*32)
        receipt=ack if layout=='history' and i<=total-5 else None
        events.append((i,run,str(i),canonical(event)));deliveries.extend([(i,'reader',receipt),(i,'unrelated',None)])
        if run=='target':
            if receipt is None and len(expected)<20:expected.append(dict(seq=i,event=event))
            status.extend([dict(seq=i,recipient='reader',receipt=json.loads(ack) if receipt else None),dict(seq=i,recipient='unrelated',receipt=None)])
    with box.connect() as db:
        db.executemany('INSERT INTO communication_events VALUES (?,?,?,?)',events)
        db.executemany('INSERT INTO communication_deliveries VALUES (?,?,?)',deliveries)
    (root/'ref.txt').write_bytes(b'valid evidence')
    event=dict(event_id='public',run_id='target',input_version='v1',sender='code',task_id='T1',kind='artifact',summary='界'*1800,action='read evidence',refs=[dict(id='reference',path='ref.txt',sha256=hashlib.sha256(b'valid evidence').hexdigest())])
    return box,expected,status,event

def observe(box,action):
    original=box.connect;count=[0];traces=[];changes=[]
    @contextmanager
    def traced():
        with original() as db:
            before=db.total_changes
            db.set_progress_handler(lambda:count.__setitem__(0,count[0]+1) or 0,1)
            db.set_trace_callback(traces.append)
            try:yield db
            finally:
                changes.append(db.total_changes-before);db.set_progress_handler(None,0);db.set_trace_callback(None)
    box.connect=traced
    try:value=action()
    finally:box.connect=original
    return dict(vm=count[0],changes=sum(changes),sql=traces),value

def tests(cls):
    paths=['tests/test_communication.py','tests/test_communication_usage.py']
    stream=io.StringIO();suite=unittest.TestSuite()
    for path in paths:
        spec=importlib.util.spec_from_file_location('comm20test_'+Path(path).stem,ROOT/path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.Mailbox=cls
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(m))
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    return dict(run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),ok=result.wasSuccessful()),stream.getvalue()

def measured(operation,base,candidate,out,repeats):
    report=dict(environment=dict(python=sys.version,sqlite=sqlite3.sqlite_version,platform=platform.platform()),warmups=3,repeats=repeats,cases=[])
    shapes=[(100,'single',1),(20000,'single',1),(20000,'interleaved',1),(20000,'last',1),(20000,'absent',1),(20000,'history',1)]
    if operation=='inbox':shapes.append((0,'absent',1))
    if operation=='publish':shapes=[(100,'single',1),(20000,'single',1),(100,'single',1000)]
    if operation=='ack':shapes=[(100,'single',1),(20000,'single',1),(100,'single',1000)]
    if operation=='impact':shapes=[(5,'single',1),(100,'single',1)]
    if operation=='init':shapes=[(100,'single',1),(20000,'single',1),(100,'single',1000)]
    with tempfile.TemporaryDirectory() as temp:
        for ci,(total,layout,routes) in enumerate(shapes):
            boxes={};expected={};events={};allstatus={}
            for name,cls in [('baseline',base),('candidate',candidate)]:
                boxes[name],expected[name],allstatus[name],events[name]=fixtures(cls,Path(temp)/f'{ci}-{name}',total,layout,routes)
            if operation=='impact':
                for name,b in boxes.items():
                    # Real public validated handoffs, nonempty basis records.
                    (b.root/'data.txt').write_text('validated data')
                    data=dict(id='data',path='data.txt',sha256=hashlib.sha256(b'validated data').hexdigest())
                    record=dict(schema_version=1,run_id='target',role='code',input_version='v1',status='completed',limitations=[],artifacts=[data],checks=[dict(criterion='data checked',status='pass',artifact_ids=['data'])],tasks=[dict(task_id='T1',status='done',depends_on=[],evidence=['data'])])
                    raw=canonical(record).encode();(b.root/'handoff.json').write_bytes(raw)
                    request=dict(schema_version=1,input_version='v1',tasks=[dict(task_id='T1')])
                    for k in range(total):
                        seq=b.publish(dict(events[name],event_id='handoff-'+str(k),refs=[dict(id='handoff',path='handoff.json',sha256=hashlib.sha256(raw).hexdigest())]))['seq']
                        b.consume_handoff('reader',seq,request)
                    # All records sharing the changed artifact become stale; both methods must agree.
                    (b.root/'data.txt').write_text('changed data')
            if operation=='ack':
                for box in boxes.values():box.acknowledge('reader',1,dict(status='consumed',reason='retry'))
            def action(name,j=0):
                b=boxes[name]
                if operation=='inbox':return b.inbox('reader')
                if operation=='status':return b.status()
                if operation=='usage':return b.usage()
                if operation=='impact':return b.impact()
                if operation=='init':
                    c=type(b)(b.path,b.plan,b.root);return c.plan
                if operation=='ack':b.acknowledge('reader',1,dict(status='consumed',reason='retry'));return None
                if operation=='publish':return b.publish(dict(events[name],event_id='new-'+str(j)))
                raise ValueError(operation)
            c=dict(total=total,layout=layout,routes=routes,observed={},raw=[],first_open_ms={n:b._first_open_ms for n,b in boxes.items()})
            for name in boxes:
                obs,value=observe(boxes[name],lambda:action(name,-1));c['observed'][name]=obs
                if operation=='inbox':assert value==expected[name]
                if operation=='status':assert value==allstatus[name]
            for j in range(repeats+3):
                pair={};values={}
                for name in (['baseline','candidate'] if j%2==0 else ['candidate','baseline']):
                    start=time.perf_counter_ns();values[name]=action(name,j);pair[name]=(time.perf_counter_ns()-start)/1e6
                assert values['baseline']==values['candidate'],(operation,ci,j)
                if j>=3:c['raw'].append(pair)
            c['median_ms']={n:statistics.median(r[n] for r in c['raw']) for n in boxes}
            # A shared write guard for index changes; outside primary timing.
            c['writes']=[];c['reopen']=[];c['migration']=[]
            for j in range(repeats):
                pair={};opens={}
                for n in (['baseline','candidate'] if j%2==0 else ['candidate','baseline']):
                    b=boxes[n];start=time.perf_counter_ns();sent=b.publish(dict(events[n],event_id='guard-'+str(j)));publish_ms=(time.perf_counter_ns()-start)/1e6
                    start=time.perf_counter_ns();b.acknowledge('reader',sent['seq'],dict(status='consumed',reason='guard'));ack_ms=(time.perf_counter_ns()-start)/1e6
                    pair[n]=dict(publish_ms=publish_ms,ack_ms=ack_ms)
                    start=time.perf_counter_ns();opened=type(b)(b.path,b.plan,b.root);opens[n]=(time.perf_counter_ns()-start)/1e6
                    assert opened.inbox('reader')==b.inbox('reader')
                c['writes'].append(pair);c['reopen'].append(opens)
            # Clone same populated baseline database for paired migration trials.
            for j in range(3):
                pair={}
                for n in (['baseline','candidate'] if j%2==0 else ['candidate','baseline']):
                    b=boxes[n];target=b.root/f'migration-{j}.sqlite'
                    with sqlite3.connect(boxes['baseline'].path) as source,sqlite3.connect(target) as dest:source.backup(dest)
                    start=time.perf_counter_ns();opened=type(b)(target,b.plan,boxes['baseline'].root);pair[n]=(time.perf_counter_ns()-start)/1e6
                    assert opened.inbox('reader')==b.inbox('reader')
                c['migration'].append(pair)
            with boxes['baseline'].connect() as db:
                base_usage=[tuple(r) for r in db.execute('SELECT * FROM communication_usage_v1 ORDER BY run_id')]
            with boxes['candidate'].connect() as db:
                cand_usage=[tuple(r) for r in db.execute('SELECT * FROM communication_usage_v1 ORDER BY run_id')]
            assert base_usage==cand_usage
            c['storage']={n:boxes[n].path.stat().st_size for n in boxes}
            report['cases'].append(c)
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    return report

def safety(cls):
    from concurrent.futures import ThreadPoolExecutor
    result={}
    with tempfile.TemporaryDirectory() as temp:
        b,_,_,event=fixtures(cls,Path(temp)/'safety',0,'absent')
        b.publish(event);(b.root/'ref.txt').write_text('changed evidence')
        try:b.publish(event);result['duplicate_mutated_ref']='accepted'
        except (ValueError,sqlite3.Error):result['duplicate_mutated_ref']='rejected'
        (b.root/'ref.txt').write_bytes(b'valid evidence')
        data=event['refs'][0]
        record=dict(schema_version=1,run_id='target',role='code',input_version='v1',status='completed',limitations=[],artifacts=[data],checks=[dict(criterion='checked',status='pass',artifact_ids=['reference'])],tasks=[dict(task_id='T1',status='done',depends_on=[],evidence=['reference'])])
        raw=canonical(record).encode();(b.root/'handoff.json').write_bytes(raw)
        seq=b.publish(dict(event,event_id='handoff',refs=[dict(id='handoff',path='handoff.json',sha256=hashlib.sha256(raw).hexdigest())]))['seq']
        record['limitations']=['valid modified envelope'];(b.root/'handoff.json').write_text(canonical(record))
        try:b.consume_handoff('reader',seq,dict(schema_version=1,input_version='v1',tasks=[dict(task_id='T1')]));result['changed_valid_manifest']='accepted'
        except (ValueError,sqlite3.Error):result['changed_valid_manifest']='rejected'
        def retry(_):
            try:b.publish(event);return 'accepted'
            except (ValueError,sqlite3.Error):return 'rejected'
        with ThreadPoolExecutor(max_workers=2) as pool:result['thread_retry']=list(pool.map(retry,range(4)))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,required=True);ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--operation',required=True);ap.add_argument('--repeats',type=int,default=11);ap.add_argument('--candidate',type=Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    if a.candidate:cp=a.candidate
    else:cp=a.out/'candidate.py';cp.write_text(variant(a.baseline.read_text(),a.round))
    base=load(a.baseline);cand=load(cp)
    checks=dict(baseline=safety(base.Mailbox),candidate=safety(cand.Mailbox));(a.out/'safety.json').write_text(json.dumps(checks,indent=2))
    r,log=tests(cand.Mailbox);(a.out/'tests.log').write_text(log);(a.out/'test_result.json').write_text(json.dumps(r,indent=2))
    if r['ok'] and a.operation!='safety':measured(a.operation,base.Mailbox,cand.Mailbox,a.out/'raw.json',a.repeats)
    else:(a.out/'raw.json').write_text(json.dumps(dict(correctness=r,performance='not evaluated: safety challenge or failed correctness'),indent=2))
    print(json.dumps(dict(round=a.round,tests=r,raw=str(a.out/'raw.json'))))
if __name__=='__main__':main()
