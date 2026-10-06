from pathlib import Path
import csv,hashlib,importlib.util,json
B=Path('/workspace/scratch/c12f3d9f92bd/coherence-design');R=B.parent/'agent';H=B.parent/'scaling-role-replay';O=B/'historical-gate-replay-v2';O.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('candidate',R/'scripts/agent_eval_pipeline.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
revision='e8ee3dca5dc8cd076fc031dd4510dabde214e046'
results=[]
for label in ['writer-run','writer-corrected-run','settlement-original','settlement-corrected']:
 writer=label.startswith('writer')
 old=H/(label if writer else 'run')
 tasks=json.loads((old/'tasks.json').read_text());rubric=json.loads((old/'rubric.json').read_text())
 cid='chain-writer' if writer else 'smoke-main-general'
 task=next(x for x in tasks['cases'] if x['id']==cid);criteria=rubric['criteria'][cid]
 sources={str(old/'tasks.json'):sha(old/'tasks.json'),str(old/'rubric.json'):sha(old/'rubric.json')}
 if writer:
  inp=old/'cases/chain-writer/inputs';a=inp/'aggregate.csv';sources[str(a)]=sha(a)
  rows=list(csv.DictReader(a.open()));actual={r['workload']:('parity' if float(r['baseline_median_ms'])==float(r['candidate_median_ms']) else 'regression' if float(r['candidate_median_ms'])>float(r['baseline_median_ms']) else 'improvement') for r in rows}
  # Explicit independent test-controller correspondence for the two known criteria, not NLP.
  expected={'small':'improvement','medium':'regression' if label=='writer-run' else 'parity','large':'regression'}
  valid=actual==expected
 else:
  inp=None;actual=[54,36,0]
  transfers=[(1,0,6),(2,0,24)] if label.endswith('original') else [(2,0,24),(2,1,6)]
  if label.endswith('corrected'):criteria=['each roommate owes30; C transfers24 to user and6 to B or equivalent correct settlement',criteria[1]]
  for a,b,v in transfers:actual[a]+=v;actual[b]-=v
  valid=actual==[30,30,30]
 tp=O/(label+'-tasks.json');rp=O/(label+'-rubric.json');tp.write_text(json.dumps({'cases':[task]}));rp.write_text(json.dumps({'criteria':{cid:criteria}}))
 run=O/label;m=p.prepare_run(R,revision,run,tp,rp,inp,{'name':'mock'},require_material_review=True)
 oracle=O/(label+'-oracle.json');oracle.write_text(json.dumps({'scope':'synthetic controller program replay; not independent model execution','actual':actual,'correspondence_supported':valid}))
 review={'schema_version':1,'reviewer_actor':'test-independent-reviewer','material_hashes':p.material_bindings(run,m),'cases':{cid:[{'criterion':c,'kind':'factual','status':'supported' if valid else 'not_supported','verification':'executable_oracle','reason':'Explicit historical criterion-to-computed-fixture comparison; no natural language parser.','evidence':[{'path':str(oracle),'sha256':sha(oracle),'location':'actual and correspondence_supported'}]} for c in criteria]}}
 rv=O/(label+'-review.json');rv.write_text(json.dumps(review));trust={'path':str(rv),'sha256':sha(rv),'reviewer_actor':'test-independent-reviewer'}
 receipt=O/(label+'-receipt.json');receipt.write_text(json.dumps({'event_id':'test-'+label,'kind':'start','actor':'test-worker','adapter':'mock','case_id':cid,'attempt':1}))
 calls=0;error=None
 try:
  p.authorize_dispatch(run,cid,'test-worker',material_review=trust)
  calls+=1 # spy only; no actual host/model invocation
  p.record_start(run,cid,'test-worker',receipt,material_review=trust)
 except ValueError as e:error=str(e)
 assert calls==int(valid),(label,error)
 assert all(sha(Path(path))==digest for path,digest in sources.items())
 results.append({'case':label,'expected':valid,'authorized':bool(calls),'spy_dispatch_calls':calls,'actual_host_calls':0,'attempt_directories':len(list((run/'cases'/cid/'attempts').iterdir())),'reason':error,'derived':actual,'historical_hashes':sources,'material_bindings':p.material_bindings(run,m)})
result={'scope':'actual historical files through candidate authorization and recorder; synthetic controller oracle judgments, no model execution','cases':results,'correct':len(results),'total':len(results),'rejected_contradictory':sum(not x['authorized'] for x in results),'accepted_corrected':sum(x['authorized'] for x in results),'historical_unchanged':True,'candidate_sha256':sha(R/'scripts/agent_eval_pipeline.py')}
(O/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
