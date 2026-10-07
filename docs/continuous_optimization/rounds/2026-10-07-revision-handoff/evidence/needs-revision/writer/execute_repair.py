import csv, hashlib, json, statistics, sys, subprocess
from pathlib import Path
sys.path.insert(0, '/workspace/scratch/c12f3d9f92bd/agent')
from agent_runtime.communication import Mailbox
BASE = Path('/workspace/scratch/c12f3d9f92bd')
INPUT = BASE / 'revision-w7-writer-run/cases/recovery-writer/inputs'
OUT = Path(__file__).resolve().parent
ROOT = BASE / 'agent/docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/needs-revision'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
log = []
def record(operation, result):
    log.append({'operation':operation, 'result':result})
    save('operations.log.json', log)
box = Mailbox(BASE / 'revision-w7-private/messages.sqlite', json.loads((ROOT / 'communication-plan.json').read_text()), ROOT)
inbox = box.inbox('research-write')
save('inbox-before.json', inbox)
record('Mailbox.inbox(research-write)', inbox)
msg = next(m for m in inbox if m['seq'] == 2)
event = msg['event']
assert event == json.loads((INPUT / 'request.json').read_text())
verified = []
for ref in event['refs']:
    p = (ROOT / ref['path']).resolve()
    assert p.is_relative_to(ROOT)
    digest = sha(p)
    assert digest == ref['sha256']
    content = p.read_text()
    verified.append({'id':ref['id'], 'path':str(p), 'expected_sha256':ref['sha256'], 'actual_sha256':digest, 'read':True})
    findings = json.loads(content)
assert findings == json.loads((INPUT / 'findings.json').read_text())
for name, digest in findings['snapshot']['input_sha256'].items():
    assert sha(INPUT / name) == digest
record('verify and read original review refs and bound input hashes', verified)
# Re-run the supplied calculation logic in assigned output paths only.
source = (ROOT / 'initial-review/calculate.py').read_text()
adapted = source.replace('INPUT = ROOT / "cases/recovery-initial/inputs"', 'INPUT = Path(' + repr(str(INPUT)) + ')')
assert adapted != source
(OUT / 'calculate.py').write_text(adapted)
result = subprocess.run([sys.executable, str(OUT / 'calculate.py')], capture_output=True, text=True)
(OUT / 'calculation.log').write_text(result.stdout + result.stderr)
assert result.returncode == 0
calcs = json.loads((OUT / 'calculation-results.json').read_text())
original_calcs = json.loads((ROOT / 'initial-review/calculation-results.json').read_text())
assert calcs['results'] == original_calcs['results']
record('rerun original calculate.py logic with input/output paths adapted to assigned scope', {'returncode':result.returncode, 'results_match_original':True, 'calculation_source_sha256':sha(ROOT / 'initial-review/calculate.py')})
original = (INPUT / 'manuscript.md').read_text()
old = 'Our cache-guided batching method accelerates request processing by 30% across workload sizes and demonstrates reliable gains.'
new = 'For the invented CPU timing fixtures, the candidate has 30% lower mean latency for the small synthetic workload (100 ms baseline versus 70 ms candidate), but 20% higher mean latency for the large synthetic workload (200 ms versus 240 ms). These percentages use the baseline mean as denominator and describe only these fixtures; reliability, accuracy equivalence, statistical significance, and deployment generalization remain unevaluated.'
assert original.count(old) == 1
revised = original.replace(old, new)
rows = list(csv.DictReader((INPUT / 'measurements.csv').open()))
table = '\n\n**Table 1. Invented CPU timing fixtures from measurements.csv (milliseconds).**\n\n| Workload | Trial | Baseline (ms) | Candidate (ms) |\n| --- | --- | --- | --- |\n' + ''.join('| ' + ' | '.join(r[k] for k in ('workload','trial','baseline_ms','candidate_ms')) + ' |\n' for r in rows)
summary = '\nAcross the three trials per workload, mean latency falls from 100 to 70 ms for small requests and rises from 200 to 240 ms for large requests. Relative mean latency change is 100 × (candidate mean − baseline mean) / baseline mean: −30% for small and +20% for large. These descriptive fixture values do not establish reliability or deployment performance.\n'
anchor = 'There are no accuracy or statistical-significance measurements.'
revised = revised.replace(anchor, anchor + table + summary)
(OUT / 'manuscript-revised.md').write_text(revised)
# Preserve unrelated complete sections exactly.
def section(text, name):
    return text.split('## ' + name + '\n', 1)[1].split('\n## ', 1)[0].strip()
for name in ('Method', 'Limitations', 'Background'):
    assert section(revised, name) == section(original, name)
assert revised.startswith(original.split('## Abstract')[0])
for row in rows:
    assert '| ' + ' | '.join(row[k] for k in ('workload','trial','baseline_ms','candidate_ms')) + ' |' in revised
assert 'across workload sizes' not in revised and 'demonstrates reliable gains' not in revised
checks = {'input_sha256':{p.name:sha(p) for p in INPUT.iterdir() if p.is_file()}, 'verified_review_refs':verified, 'source_snapshot_id':findings['snapshot']['id'], 'calculations_match_original':True, 'csv_unchanged':sha(INPUT / 'measurements.csv') == findings['snapshot']['input_sha256']['measurements.csv'], 'preserved_sections':['Method','Limitations','Background'], 'table_rows_match_csv':len(rows), 'pdf':'not requested; not built', 'new_experiments':False}
save('verification.json', checks)
response = {'schema_version':'1.0', 'task_id':'REV-03', 'input_version':'synthetic-repair-v1', 'source_event_id':event['event_id'], 'source_seq':2, 'source_snapshot_id':findings['snapshot']['id'], 'status':'draft_complete_pending_original_reviewer_recheck', 'manuscript':{'path':'writer/manuscript-revised.md','sha256':sha(OUT / 'manuscript-revised.md')}, 'findings':[
{'finding_id':'REV-F001','status':'repair_proposed_pending_recheck','location':'Abstract; Results','change':'Replaced universal acceleration with workload-specific synthetic mean latency reduction of 30% for small and increase of 20% for large, with baseline-mean denominator defined.','evidence':'Existing six CSV rows; re-executed supplied calculation logic matches original results.'},
{'finding_id':'REV-F002','status':'repair_proposed_pending_recheck','location':'Abstract; Results','change':'Removed reliable-gains assertion; explicitly states reliability, accuracy equivalence, significance and deployment generalization remain unevaluated. Retained original provenance and absence of accuracy/statistical measurements.','evidence':'Invented fixtures contain no independent experimental design; no inferential statistics or new experiments added.'},
{'finding_id':'REV-F003','status':'repair_proposed_pending_recheck','location':'Results, Table 1','change':'Added labeled Table 1 with all six existing timing rows, unchanged.','evidence':'Table rows checked exactly against measurements.csv.'}], 'preserved':['Title and synthetic provenance','Method','Limitations','Background','measurements.csv and all other input files'], 'checks':checks, 'limitations':['Synthetic working draft only; not a real benchmark.','Original reviewer must recheck REV-F001/F002/F003; writer has not closed findings.','Mailbox consumed acknowledgement records handling only, not scientific acceptance.'], 'next_owner':'original_research_review'}
save('response.json', response)
writer = ROOT / 'writer'
writer.mkdir(exist_ok=True)
for name in ('manuscript-revised.md','response.json'):
    (writer / name).write_bytes((OUT / name).read_bytes())
    assert (writer / name).read_bytes() == (OUT / name).read_bytes()
record('write and verify identical canonical/live artifacts', {name:sha(writer/name) for name in ('manuscript-revised.md','response.json')})
published = {'event_id':'w7-repair-artifact-v1','run_id':event['run_id'],'input_version':'synthetic-repair-v1','sender':'research-write','task_id':'REV-03','kind':'artifact','summary':'Complete synthetic draft repaired for REV-F001/F002/F003; findings remain open pending original reviewer recheck.','action':'Original research-review: read revised manuscript and response, verify hashes, and recheck all three original findings against the unchanged timing fixtures; ACK alone is not acceptance.','refs':[{'id':'w7-repaired-manuscript','path':'writer/manuscript-revised.md','sha256':sha(writer/'manuscript-revised.md')},{'id':'w7-repair-response','path':'writer/response.json','sha256':sha(writer/'response.json')}]}
save('artifact-event.json', published)
publish_return = box.publish(published)
save('publish-return.json', publish_return)
record('Mailbox.publish(w7-repair-artifact-v1)', publish_return)
receipt = {'status':'consumed','reason':'Verified and read original findings SHA and source snapshot; repaired full draft and response and published w7-repair-artifact-v1 for original reviewer recheck. Findings remain open; consumption is not scientific acceptance.'}
save('receipt.json', receipt)
ack_return = box.acknowledge('research-write', 2, receipt)
save('ack-return.json', {'return':ack_return,'acknowledged':True,'seq':2,'recipient':'research-write'})
record('Mailbox.acknowledge(research-write, 2, consumed), after successful artifact publication', {'return':ack_return,'acknowledged':True})
status = box.status()
save('mailbox-status.json', status)
record('Mailbox.status()', status)
print(json.dumps({'publish':publish_return,'acknowledged_seq':2,'outputs':str(OUT),'live_artifacts':[str(writer/n) for n in ('manuscript-revised.md','response.json')], 'findings_closed_by_writer':False}, indent=2))
