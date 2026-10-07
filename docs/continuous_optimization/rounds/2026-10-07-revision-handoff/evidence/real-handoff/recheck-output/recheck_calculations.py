from pathlib import Path
import csv,json,hashlib,statistics
base=Path(__file__).resolve().parents[3]; inp=base/'inputs'; out=Path(__file__).resolve().parent
root=Path('/workspace/scratch/c12f3d9f92bd/agent/docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/real-handoff')
initial=Path('/workspace/scratch/c12f3d9f92bd/revision-w5-model-run/cases/revision-review-initial')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=inp/'manuscript.md'; revised=root/'writer-artifacts/manuscript-revised.md'; source=inp/'measurements.csv'
assert revised.read_bytes()==(inp/'manuscript-revised.md').read_bytes()
assert old.read_bytes()==(initial/'inputs/manuscript.md').read_bytes()
assert source.read_bytes()==(initial/'inputs/measurements.csv').read_bytes()
assert (inp/'findings.json').read_bytes()==(initial/'attempts/0001/outputs/findings.json').read_bytes()
assert (root/'writer-artifacts/response.json').read_bytes()==(inp/'response.json').read_bytes()
rows=list(csv.DictReader(source.open())); calc={}
for w in ['small','large']:
 rr=[r for r in rows if r['workload']==w]; b=statistics.mean(float(r['baseline_ms']) for r in rr); c=statistics.mean(float(r['candidate_ms']) for r in rr)
 calc[w]=dict(n_rows=len(rr),baseline_mean_ms=b,candidate_mean_ms=c,time_reduction_percent=(b-c)/b*100,speedup=b/c,paired_differences_ms=[float(r['candidate_ms'])-float(r['baseline_ms']) for r in rr])
text=revised.read_text(); original=old.read_text()
expected=[[r['workload'],r['trial'],r['baseline_ms'],r['candidate_ms']] for r in rows]
actual=[[s.strip() for s in line.strip('|').split('|')] for line in text.splitlines() if line.startswith('| small |') or line.startswith('| large |')]
assert actual==expected
preserved={}
for name in ['Method','Limitations','Background']:
 def section(t):return t.split('## '+name+'\n',1)[1].split('\n## ',1)[0].strip()
 preserved[name]=section(text)==section(original); assert preserved[name]
for line in [original.splitlines()[0],original.splitlines()[2],original.splitlines()[11]]:
 assert line in text
checks=dict(original_sha256=sha(old),revised_sha256=sha(revised),csv_sha256=sha(source),initial_findings_sha256=sha(inp/'findings.json'),initial_findings_unchanged=True,csv_unchanged=True,mailbox_input_copies_equal=True,calculated_groups=calc,table_all_six_rows_exact=True,preserved_sections=preserved,synthetic_declaration_and_results_paragraph_preserved=True,paired_rows=rows)
(out/'calculations.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
