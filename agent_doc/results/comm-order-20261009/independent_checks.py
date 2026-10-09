import hashlib,json,math,statistics,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from agent_runtime.communication import Mailbox,canonical
from scripts.benchmark_communication_inbox import load_baseline
root=Path(__file__).resolve().parents[3]; folder=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((folder/'manifest.json').read_text());bindings={m['validation_plan']['path']:m['validation_plan']['sha256']}
for refs in m['artifacts'].values():
 for ref in refs:
  assert sha(root/ref['path'])==ref['sha256'],ref['path'];bindings[ref['path']]=ref['sha256']
base=folder/'baseline_communication.py'; assert base.read_bytes()==subprocess.check_output(['git','show','ffe7f9def00ca9275a023c55ad55d916deb5301e:agent_runtime/communication.py'],cwd=root)
assert (root/'agent_runtime/communication.py').read_text()==base.read_text().replace('ORDER BY e.seq LIMIT ?','ORDER BY d.seq LIMIT ?')
rows=[]
for file,n in [('raw.json',21),('independent_raw.json',5)]:
 r=json.loads((folder/file).read_text()); assert len(r['cases'])==12;assert r['config']['warmups']==3 and r['config']['repeats']==n
 assert {(c['total'],c['layout']) for c in r['cases']}=={(t,l) for t in [100,1000,20000] for l in ['single','interleaved','last','absent']}
 summaries=[]
 for c in r['cases']:
  t,l=c['total'],c['layout']; ids=[i for i in range(1,t+1) if l=='single' or l=='interleaved' and i%4==0 or l=='last' and i>t-5][:20]
  expected=[{'seq':i,'event':{'event_id':str(i),'run_id':'target','payload':'界'*32}} for i in ids];assert c['expected']==expected
  assert len(c['raw'])==n
  med={k:statistics.median(x[k] for x in c['raw']) for k in ['baseline','candidate']}
  ranges={k:[min(x[k] for x in c['raw']),max(x[k] for x in c['raw'])] for k in med}
  assert med==c['median_ms'] and ranges==c['range_ms']
  assert all(set(x)==set(med) and all(math.isfinite(v) and v>0 for v in x.values()) for x in c['raw'])
  s=dict(total=t,layout=l,vm=c['vm'],median_ms=med,range_ms=ranges,vm_ratio=c['vm']['baseline']/c['vm']['candidate'],latency_ratio=med['baseline']/med['candidate'])
  if t==20000 and l in ['single','interleaved']:assert s['vm_ratio']>=10 and s['latency_ratio']>=2
  if t==100: assert med['candidate']<=2*med['baseline'] or med['candidate']-med['baseline']<1
  if 'overhead' in c:
   assert all(len(c['overhead'][k])==n for k in med)
   ov={k:{metric:statistics.median(x[metric] for x in c['overhead'][k]) for metric in ['publish_ms','ack_ms']} for k in med}
   for metric in ['publish_ms','ack_ms']:
    b,v=ov['baseline'][metric],ov['candidate'][metric];assert v<=2*b or v-b<1
    assert all(math.isfinite(x[metric]) and x[metric]>0 for k in med for x in c['overhead'][k])
   s['overhead_median_ms']=ov
  assert 'ORDER BY '+('e' if file=='' else 'd')+'.seq' in c['queries']['candidate']['sql']
  summaries.append(s)
 if file=='raw.json':assert summaries==json.loads((folder/'summary.json').read_text())['cases']
 rows.append(dict(file=file,summary=summaries))
checks=0
with tempfile.TemporaryDirectory() as tmp:
 for cls in [load_baseline(base),Mailbox]:
  p=Path(tmp)/cls.__module__.replace('.','_');p.mkdir(); data='artifact界'.encode();(p/'artifact').write_bytes(data)
  refs=[dict(id='artifact',path='artifact',sha256=hashlib.sha256(data).hexdigest())]
  boxes={}; oracle=[]
  for run in ['a','b','c','d']:
   plan=dict(schema_version=1,run_id=run,input_version='v1',max_events=1000,routes=[dict(sender='code',recipient=x,task_id='T1',kind='artifact') for x in ['reader','reviewer']])
   boxes[run]=cls(p/'box.db',plan,p)
  # Valid public publishes, gaps introduced via intervening runs, both recipients.
  for i in range(520):
   run=['a','b','c','d'][i%4];event=dict(event_id=str(i),run_id=run,input_version='v1',sender='code',task_id='T1',kind='artifact',summary='unicode界',action='read',refs=refs)
   sent=boxes[run].publish(event);oracle.append(dict(run=run,seq=sent['seq'],event=event));checks+=1
  a=boxes['a']; usage=a.usage();before_schema=None
  with a.connect() as db:before_schema=[tuple(x) for x in db.execute("SELECT type,name,sql FROM sqlite_master ORDER BY type,name")]
  for stage in range(3):
   for run,box in boxes.items():
    for recipient in ['reader','reviewer']:
     for limit in [1,20,100]:
      exp=[dict(seq=x['seq'],event=x['event']) for x in oracle if x['run']==run and not(stage>0 and recipient=='reader' and x['seq']%5==1)][:limit]
      assert box.inbox(recipient,limit=limit)==exp;checks+=1
   if stage==0:
    for x in oracle:
     if x['seq']%5==1:boxes[x['run']].acknowledge('reader',x['seq'],dict(status='consumed',reason='verified'))
   if stage==1: boxes={k:cls(v.path,v.plan,v.root) for k,v in boxes.items()}
  for invalid in [0,101,True,1.0,None]:
   try:a.inbox('reader',limit=invalid)
   except ValueError:checks+=1
   else:raise AssertionError(invalid)
  try:a.inbox('unknown')
  except ValueError:checks+=1
  else:raise AssertionError('unknown recipient accepted')
  other=next(x for x in oracle if x['run']=='b')
  try:a.acknowledge('reader',other['seq'],dict(status='consumed',reason='cross-run'))
  except ValueError:checks+=1
  else:raise AssertionError('cross-run ACK accepted')
  assert a.usage()==usage;checks+=1
  with a.connect() as db:
   assert [tuple(x) for x in db.execute("SELECT type,name,sql FROM sqlite_master ORDER BY type,name")]==before_schema
   for run,box in boxes.items():
    ev=[x for x in oracle if x['run']==run];b=sum(len(canonical(x['event']).encode()) for x in ev);u=box.usage()
    assert (u['events'],u['envelope_bytes'],u['deliveries'],u['delivery_bytes'])==(130,b,260,2*b);checks+=1
out=dict(status='pass',bindings=bindings,baseline_exact_revision='ffe7f9def00ca9275a023c55ad55d916deb5301e',runtime_diff='only ORDER BY e.seq -> d.seq',property_checks=checks,metrics=rows,knowledge=dict(query='SQLite inbox ordering equality index',rejected=['ds.faiss-exact-vector','ds.hnsw-recall-budget','math.convex-projection-certificate'],reason='weak lexical hits lack SQLite ordered equality-join applicability',adopted_refs=[]))
(folder/'independent_checks.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n'); print(json.dumps(dict(status='pass',property_checks=checks,primary=[{k:s[k] for k in ['layout','vm_ratio','latency_ratio','median_ms']} for s in rows[1]['summary'] if s['total']==20000 and s['layout'] in ['single','interleaved']])))
