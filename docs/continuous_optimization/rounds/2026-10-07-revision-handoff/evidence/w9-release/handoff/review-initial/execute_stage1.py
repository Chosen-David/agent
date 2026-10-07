import json,hashlib,pathlib,subprocess,sys,csv
from agent_runtime.communication import Mailbox
REPO=pathlib.Path.cwd(); H=REPO/'docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/w9-release/handoff'; O=H/'review-initial'; C=json.loads((H/'host-context.json').read_text()); B=Mailbox(C['db'],C['plan'],C['artifact_root'])
ORIG=pathlib.Path('/workspace/scratch/c12f3d9f92bd/revision-candidate-v3-roles-run/cases/research-review')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (O/n).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2)
inbox=B.inbox('research-review');save('incoming.json',inbox);save('status-before.json',B.status())
assert len(inbox)==1 and inbox[0]['seq']==1
incoming=inbox[0];event=incoming['event'];assert event['run_id']==C['plan']['run_id'] and event['input_version']==C['plan']['input_version']
verified=[]
for ref in event['refs']:
 p=H/ref['path'];old=ORIG/'inputs'/p.name
 assert sha(p)==ref['sha256']==sha(old)
 text=p.read_text();verified.append(dict(path=ref['path'],sha256=sha(p),matches_original=str(old),actually_read_content=text))
original=ORIG/'attempts/0001/outputs/findings.yaml';findings=json.loads(original.read_text())
assert [f['status'] for f in findings['findings']]==['confirmed','confirmed','rejected']
(O/'original-findings.yaml').write_bytes(original.read_bytes())
computed=[]
for r in csv.DictReader((H/'inputs/measurements.csv').open()):
 b,c=float(r['baseline_ms']),float(r['candidate_ms']);computed.append(dict(workload=r['workload'],scope=r['scope'],baseline_ms=b,candidate_ms=c,speedup=b/c,latency_change_pct=100*(c/b-1)))
save('evidence.json',dict(run_id=event['run_id'],input_version=event['input_version'],incoming_seq=incoming['seq'],refs=verified,original_findings=dict(path=str(original),sha256=sha(original)),calculations=computed,unchanged_judgment=True))
request=dict(run_id=event['run_id'],input_version=event['input_version'],task_id='REV-03',original_manuscript_sha256=findings['snapshot_id'],original_csv_sha256=sha(H/'inputs/measurements.csv'),finding_ids=['REV-F001','REV-F002','REV-F003'],owner='research-write',recheck_owner='research-review',scope='Complete bounded corrected working manuscript using existing synthetic material only; no new experiment or outside claim.',requests=[dict(finding_id='REV-F001',status='confirmed',action='Replace universal 2x end-to-end/no-regression claim; state small 1.25x, medium 1.20x, large 0.90909x with 10% latency regression, and kernel-only 2x. Keep included kernel timing separate; never add scopes.',acceptance=findings['findings'][0]['acceptance']),dict(finding_id='REV-F002',status='confirmed',action='Choose existing-data resolution: scope every performance conclusion to one-run descriptive CPU observations. Explicitly preserve no independent repeats, variance/quality unmeasured, and no GPU measurement. No CI/significance/quality-preservation/repeatability assertion.',acceptance=findings['findings'][1]['acceptance']),dict(finding_id='REV-F003',status='rejected',action='Keep original rejection: Appendix A already discloses regression. Retain that disclosure; do not claim the revision repaired a hidden/omitted result.',acceptance=findings['findings'][2]['acceptance'])],deliverables=['Complete corrected working manuscript','Per-finding evidence/change mapping with old/new hashes, exact locations and preserved CSV identity'],protocol='Successfully publish revision artifact refs before consuming review request. Reviewer later independently reads old/new/data and evaluates original acceptance; no receipt closes findings.',limits=['No new experiments/network/resources','No modification of frozen original artifacts','At most two revisions; report unresolved instead of invented closure'])
save('revision-request.json',request)
(O/'revision-request.md').write_text('# Bounded revision request · REV-03\n\nOriginal independent findings are preserved verbatim in original-findings.yaml. See evidence.json for identical original/new-input hashes and re-read contents.\n\nREV-F001: correct the Abstract and synchronize Results/Appendix with 1.25x, 1.20x, 0.90909x end-to-end ratios; 2x belongs only to kernel-only. Large latency regresses 10%.\n\nREV-F002: retain only descriptive one-run CPU observations, with no quality/variance/GPU/repeatability claim. Existing disclosures are strengths; no fresh experiment is authorized.\n\nREV-F003 remains rejected: Appendix A already reports large regression. No repair is required for that rejected allegation.\n\nOwner: research-write. Recheck owner: original research-review. Return the complete corrected working manuscript and per-finding evidence mapping, bind old/new hashes and unchanged data. Successfully deliver before consuming the request. Findings remain confirmed/rejected as originally judged until original-reviewer recheck; receipt is not closure.\n')
refs=[dict(id='revision_request',path='review-initial/revision-request.json',sha256=sha(O/'revision-request.json')),dict(id='original_findings',path='review-initial/original-findings.yaml',sha256=sha(O/'original-findings.yaml')),dict(id='evidence',path='review-initial/evidence.json',sha256=sha(O/'evidence.json'))]
outgoing=dict(event_id='w9-review-v1-revision-request-001',run_id=event['run_id'],input_version=event['input_version'],sender='research-review',task_id='REV-03',kind='review',summary='REV-F001 and REV-F002 confirmed; REV-F003 rejected by Appendix evidence. Exact original independent judgment retained.',action='research-write: produce complete bounded corrected manuscript and per-finding mapping using provided synthetic data; publish new hashes before consuming this request; original reviewer will recheck.',refs=refs)
receipt=dict(status='needs_revision',reason='REV-F001 abstract contradicts paired end-to-end observations; REV-F002 requires descriptive one-run CPU scope. REV-F003 is rejected because Appendix A already discloses regression. Revision request w9-review-v1-revision-request-001 must be successfully delivered before this receipt; no scientific finding is closed.')
intent=dict(db=C['db'],plan=C['plan'],artifact_root=C['artifact_root'],recipient='research-review',incoming_seq=incoming['seq'],event=outgoing,receipt=receipt,original_event_id=event['event_id'],finding_ids=request['finding_ids'],original_manuscript_sha256=findings['snapshot_id'],original_csv_sha256=sha(H/'inputs/measurements.csv'),authority='Root explicitly authorized this single-owner bounded local diagnostic; no Engine/model restart or concurrent adapter implied.')
save('outgoing-event.json',outgoing);save('incoming-receipt.json',receipt);save('immutable-intent.json',intent)
for n in ['outgoing-event.json','incoming-receipt.json','immutable-intent.json']:(O/n).chmod(0o444)
intent_sha=sha(O/'immutable-intent.json')
driver=REPO/'docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/needs-revision/recover_intent.py'
cmd=[sys.executable,str(driver),'--intent',str(O/'immutable-intent.json'),'--repo',str(REPO)]
p=subprocess.run(cmd+['--interrupt-after-publish'],capture_output=True,text=True)
save('interrupted-child.json',dict(command=cmd+['--interrupt-after-publish'],returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
state=B.status();save('status-after-publish-interruption.json',state)
assert p.returncode==73
assert next(r for r in state if r['seq']==incoming['seq'] and r['recipient']=='research-review')['receipt'] is None
published=[r for r in state if r['recipient']=='research-write'];assert len(published)==1 and published[0]['receipt'] is None
assert sha(O/'immutable-intent.json')==intent_sha
p=subprocess.run(cmd,capture_output=True,text=True)
save('replay-child.json',dict(command=cmd,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
state=B.status();save('status-after-replay.json',state)
assert p.returncode==0
result=json.loads(p.stdout);assert result['duplicate'] is True and result['seq']==published[0]['seq']
assert next(r for r in state if r['seq']==incoming['seq'] and r['recipient']=='research-review')['receipt']==receipt
assert len([r for r in state if r['recipient']=='research-write'])==1
assert sha(O/'immutable-intent.json')==intent_sha
save('stage1-result.json',dict(status='request_delivered_then_original_acknowledged',incoming_delivery=dict(seq=incoming['seq'],recipient='research-review',event_id=event['event_id'],receipt=receipt),outgoing_delivery=dict(seq=result['seq'],recipient='research-write',event_id=outgoing['event_id'],receipt=None),interrupt_returncode=73,replay=result,intent_sha256=intent_sha,findings_closed=[],writer_outputs_read=False,limits='Owned local diagnostic only; not model/Engine restart, not exactly-once external effects, not scientific closure.',driver_sha256=sha(driver),runtime_sha256=sha(REPO/'agent_runtime/communication.py')))
print(json.dumps(dict(incoming_seq=incoming['seq'],outgoing_seq=result['seq'],interrupt_returncode=73,replay=result,status=state),ensure_ascii=False,indent=2))
