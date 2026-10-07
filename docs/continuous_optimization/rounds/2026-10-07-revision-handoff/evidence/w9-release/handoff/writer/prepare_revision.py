from pathlib import Path
import hashlib,json,csv,sys
from fractions import Fraction
R=Path.cwd(); H=R/'docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/w9-release/handoff'; W=H/'writer'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 p=W/n
 with p.open('x') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
ctx=json.loads((H/'host-context.json').read_text());req=json.loads((H/'review-initial/revision-request.json').read_text());incoming=json.loads((W/'inbox-before.json').read_text())[0]
assert incoming['seq']==2
assert sha(H/'inputs/manuscript.md')==req['original_manuscript_sha256']
assert sha(H/'inputs/measurements.csv')==req['original_csv_sha256']
rows=list(csv.DictReader((H/'inputs/measurements.csv').open())); calc=[]
for row in rows:
 b,c=int(row['baseline_ms']),int(row['candidate_ms']); ratio=Fraction(b,c); change=100*Fraction(c-b,b)
 calc.append(dict(row,speedup_exact=str(ratio),speedup=float(ratio),latency_change_pct_exact=str(change),latency_change_pct=float(change)))
assert [x['speedup_exact'] for x in calc]==['5/4','6/5','10/11','2']
assert calc[2]['latency_change_pct_exact']=='10'
save('calculation-checks.json',{'calculations':calc,'formulae':{'speedup':'baseline_ms/candidate_ms','latency_change_pct':'100*(candidate_ms-baseline_ms)/baseline_ms'},'checks':'Four rows, scopes, ratios and latency changes recalculated using exact rational arithmetic. No addition of kernel-only and end-to-end timings.','new_experiments':False})
text='''# Synthetic manuscript: Selective execution — corrected working draft

This is a synthetic fixture, not a published paper or a report of new experiments. This bounded revision uses only the supplied manuscript and measurements.csv; no external citations are supplied or added. All performance statements below describe the supplied single-run CPU records.

## Abstract

The supplied synthetic records describe replacement of a selected kernel under the same CPU process and input configuration. End-to-end latency changes from 100 to 80 ms for the small workload, from 120 to 100 ms for the medium workload, and from 200 to 220 ms for the large workload. The corresponding baseline-to-candidate speedup ratios are 1.25×, 1.20×, and approximately 0.90909×: the small and medium records have latency reductions of 20.0% and approximately 16.7%, while the large record has a 10.0% latency regression. Separately timed kernel-only latency changes from 20 to 10 ms, a 2.00× kernel-only speedup. The kernel is already included in the end-to-end paths, so its timing must not be added to end-to-end timing or its speedup presented as an end-to-end result. Each value represents one run without independent repeats. Variance and output quality were not measured, and no GPU measurement was made. These descriptive observations establish neither repeatable performance improvement nor quality preservation or a uniform gain across workloads.

## Method and measurement scope

The supplied method replaces a selected kernel. All supplied measurements use the same CPU process and input configuration. The available evidence does not specify the kernel implementation, CPU model, software configuration, warmup procedure, run ordering, or timing-instrumentation details; this draft does not invent them. No GPU measurement has been made.

The measurements comprise three end-to-end baseline/candidate pairs and one independently timed kernel-only pair. The kernel-only pair is included in the end-to-end paths; these timing scopes must remain separate. Each numerical value represents a single run, with no independent repeats. We calculate the descriptive speedup ratio as baseline latency divided by candidate latency, and latency change as 100 × (candidate latency − baseline latency) / baseline latency. A ratio below one indicates increased latency. The arithmetic below is a re-expression of the supplied records, not a new benchmark.

## Results

Table 1 reports all supplied rows, including the negative result. Latencies are in milliseconds; ratios and percentages are derived from the two latency columns. Positive latency change means a regression. Rounded percentages do not express statistical precision.

| Workload | Scope | Baseline (ms) | Candidate (ms) | Speedup ratio | Latency change |
|---|---|---:|---:|---:|---:|
| small | end_to_end | 100 | 80 | 1.25× | −20.0% |
| medium | end_to_end | 120 | 100 | 1.20× | −16.7% |
| large | end_to_end | 200 | 220 | 0.90909× | +10.0% |
| kernel | kernel_only | 20 | 10 | 2.00× | −50.0% |

In these single-run CPU records, the small and medium workloads have lower candidate latency, while the large workload has higher candidate latency. Thus the records do not support a claim of 2× end-to-end speedup on every workload or absence of regression. The 2.00× ratio applies only to the separately timed kernel pair. The available evidence does not establish why the large workload regresses or how the kernel change contributes to each end-to-end difference; no overhead decomposition or causal mechanism is inferred.

## Evidence limits

There are no independent repeats, so the supplied values do not permit an estimate of run-to-run variance or support a confidence interval, a significance claim, or a repeatability claim. Absence of such evidence does not establish that the observed differences are noise or that the methods are equivalent. Output quality was not measured, so correctness or quality preservation is not established. CPU observations provide no GPU performance evidence. No conclusion about unmeasured workloads, configurations, or hardware is asserted.

## Appendix A: Retained regression disclosure and scope consistency

The original Appendix A already disclosed that the large workload regresses from 200 ms to 220 ms. That disclosure is retained here; this revision corrects the inconsistent abstract and scopes its conclusions, rather than repairing an alleged hidden or omitted result. The large-workload speedup ratio is 200/220 = 10/11 ≈ 0.90909×, and the latency increase is (220 − 200)/200 = 10.0%. For consistency with the abstract and Results, the other end-to-end ratios are 100/80 = 1.25× for small and 120/100 = 1.20× for medium. The kernel-only ratio is 20/10 = 2.00×, not an end-to-end ratio; it is never added to an end-to-end latency. Quality and variance remain unmeasured, there are no independent repeats, and no GPU measurement has been made.
'''
with (W/'manuscript-revised.md').open('x') as f:f.write(text)
lines=text.splitlines()
def span(heading):
 start=next(i for i,l in enumerate(lines,1) if l==heading);end=next((i-1 for i,l in enumerate(lines,1) if i>start and l.startswith('## ')),len(lines));return {'heading':heading,'lines':[start,end]}
old=sha(H/'inputs/manuscript.md');new=sha(W/'manuscript-revised.md');data=sha(H/'inputs/measurements.csv')
mapping={'run_id':ctx['plan']['run_id'],'input_version':ctx['plan']['input_version'],'task_id':'REV-03','revision':1,'original_manuscript':{'path':'inputs/manuscript.md','sha256':old},'new_manuscript':{'path':'writer/manuscript-revised.md','sha256':new},'unchanged_csv':{'path':'inputs/measurements.csv','sha256':data},'finding_mapping':[{'finding_id':'REV-F001','original_status':'confirmed','old_location':'inputs/manuscript.md line4, Abstract; CSV lines2–5','new_locations':[span('## Abstract'),span('## Results'),span('## Appendix A: Retained regression disclosure and scope consistency')],'change':'Replaced universal2x/no-regression statement with all scoped observed ratios; included large10% regression and separate kernel2x; never sums scopes.','evidence':'inputs/measurements.csv lines2–5; writer/calculation-checks.json','writer_response':'revision_provided_for_recheck','closure_decision':None},{'finding_id':'REV-F002','original_status':'confirmed','old_location':'inputs/manuscript.md lines6,8,10','new_locations':[span('## Abstract'),span('## Method and measurement scope'),span('## Results'),span('## Evidence limits'),span('## Appendix A: Retained regression disclosure and scope consistency')],'change':'Scoped all performance conclusions to supplied single-run descriptive CPU records; preserved no repeats and unmeasured variance/quality/GPU; no new tests, CI, significance or repeatability claims.','evidence':'inputs/manuscript.md lines6,8,10','writer_response':'existing_data_resolution_provided_for_recheck','closure_decision':None},{'finding_id':'REV-F003','original_status':'rejected','old_location':'inputs/manuscript.md Appendix A line10; CSV line4','new_locations':[span('## Appendix A: Retained regression disclosure and scope consistency')],'change':'Retained original regression disclosure and original finding rejection; explicitly states regression was not hidden or omitted.','evidence':'inputs/manuscript.md line10 explicitly discloses200→220ms','writer_response':'original_rejection_preserved_no_repair_claim','closure_decision':None}], 'recheck_owner':'research-review','scientific_findings_closed_by_writer':False}
save('evidence-mapping.json',mapping)
loaded=['AGENTS.md','prompts/decision_review.md','workflows/agent_communication_workflow.md','plugins/research-assistant/skills/research-write/SKILL.md','plugins/research-assistant/skills/research-write/references/execution.md','plugins/research-assistant/skills/research-write/references/workflow.md','agent_runtime/communication.py','docs/handoff_validation.md']
save('provenance.json',{'run_id':ctx['plan']['run_id'],'input_version':ctx['plan']['input_version'],'role':'research-write','incoming_seq':2,'incoming_event_id':incoming['event']['event_id'],'decision':'EXECUTE within parent-authorized fixed local synthetic handoff; no fetch/pull or production edits to alter the frozen candidate','loaded_role_and_protocol_files':[{'path':str(R/p),'sha256':sha(R/p)} for p in loaded],'input_verification':[{'path':'inputs/manuscript.md','sha256':old,'expected_sha256':req['original_manuscript_sha256'],'match':True,'actually_read_content':(H/'inputs/manuscript.md').read_text()},{'path':'inputs/measurements.csv','sha256':data,'expected_sha256':req['original_csv_sha256'],'match':True,'actually_read_content':(H/'inputs/measurements.csv').read_text()}],'authority':'Parent explicitly assigned sole research-write consumer of seq2 for bounded local REV-03 handoff. No independent Engine lease was supplied; this is host collaboration, not a deployed Engine adapter.','limits':['Synthetic working manuscript only','No new experiments/network/resources/Word/PDF/citations','No inferred hardware details, statistics or quality findings','Original reviewer decides closure; ACK records handling only'],'python_version':sys.version,'findings_closed':False})
refs=[{'id':id,'path':'writer/'+p,'sha256':sha(W/p)} for id,p in [('manuscript','manuscript-revised.md'),('mapping','evidence-mapping.json'),('calculations','calculation-checks.json'),('provenance','provenance.json')]]
manifest={'schema_version':1,'run_id':ctx['plan']['run_id'],'role':'research-write','input_version':ctx['plan']['input_version'],'status':'completed','limitations':['Completed only the assigned bounded manuscript revision; independent reviewer acceptance remains pending.','No new evidence or experiment; single-run synthetic CPU records.'],'artifacts':refs,'checks':[{'criterion':'Original hashes preserved and descriptive arithmetic recalculated','status':'pass','artifact_ids':['calculations','provenance']},{'criterion':'Per-finding change mapping supplied with old/new hashes','status':'pass','artifact_ids':['mapping','manuscript']}],'tasks':[{'task_id':'REV-03','depends_on':[],'status':'done','evidence':['manuscript','mapping','calculations','provenance']}]}
save('handoff.json',manifest)
event={'event_id':'w9-write-revision-001','run_id':ctx['plan']['run_id'],'input_version':ctx['plan']['input_version'],'sender':'research-write','task_id':'REV-03','kind':'artifact','summary':'Bounded corrected synthetic working manuscript; REV-F001 and REV-F002 revision responses supplied; REV-F003 rejection and original regression disclosure preserved.','action':'research-review: independently read old/new manuscript and unchanged CSV, recheck each original finding against its acceptance criteria, then record handling. Writer makes no scientific closure claim.','refs':[{'id':'handoff','path':'writer/handoff.json','sha256':sha(W/'handoff.json')}]+refs}
receipt={'status':'consumed','reason':'Read seq2 and verified immutable review/input refs; supplied complete bounded corrected manuscript and per-finding mapping, successfully delivered as w9-write-revision-001 before acknowledging this request. Original research-review owns independent recheck; this receipt closes no scientific finding.'}
save('outgoing-event.json',event);save('incoming-receipt.json',receipt)
intent={'db':ctx['db'],'plan':ctx['plan'],'artifact_root':ctx['artifact_root'],'recipient':'research-write','incoming_seq':2,'original_event_id':incoming['event']['event_id'],'finding_ids':req['finding_ids'],'original_manuscript_sha256':old,'original_csv_sha256':data,'revised_manuscript_sha256':new,'event':event,'receipt':receipt,'authority':'Parent-authorized single research-write consumer; publish revision before ACK seq2; no scientific closure.'}
save('immutable-intent.json',intent)
print(json.dumps({'prepared':True,'new_manuscript_sha256':new,'handoff_sha256':sha(W/'handoff.json'),'outgoing_event_id':event['event_id'],'incoming_seq':2,'mailbox_mutation':False},indent=2))
