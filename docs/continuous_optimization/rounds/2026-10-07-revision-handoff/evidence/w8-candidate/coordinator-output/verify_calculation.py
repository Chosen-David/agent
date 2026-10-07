from pathlib import Path
from fractions import Fraction
import csv,json,hashlib
out=Path(__file__).parent
inp=out.parents[2]/'inputs'
source=list(csv.DictReader((inp/'measurements.csv').open()))
r=json.loads((out/'results.json').read_text())
for s,v in zip(source,r['per_workload']):
 b=Fraction(s['baseline_ms']);c=Fraction(s['candidate_ms'])
 assert s['workload']==v['workload'] and s['scope']==v['scope']
 assert abs(float(b/c)-v['speedup_baseline_over_candidate'])<1e-12
 assert abs(float(100*(b-c)/b)-v['latency_reduction_pct'])<1e-12
 assert float(c-b)==v['candidate_minus_baseline_ms']
b=sum(Fraction(s['baseline_ms']) for s in source if s['scope']=='end_to_end')
c=sum(Fraction(s['candidate_ms']) for s in source if s['scope']=='end_to_end')
assert (b,c)==(420,400)
assert abs(float(b/c)-r['end_to_end_equal_once_diagnostic']['speedup'])<1e-12
assert abs(float(100*(b-c)/b)-r['end_to_end_equal_once_diagnostic']['latency_reduction_pct'])<1e-12
chain=json.loads((out/'task_chain.json').read_text());nodes={t['task_id']:t for t in chain['tasks']}
assert len(nodes)==len(chain['tasks'])
visited=set();stack=set()
def visit(id):
 assert id in nodes
 if id in visited:return
 assert id not in stack
 stack.add(id)
 for dep in nodes[id]['depends_on']:visit(dep)
 stack.remove(id);visited.add(id)
for id,t in nodes.items():
 visit(id)
 assert t['task_refs'] and t['inputs'] and t['action'] and t['done_when']
 if t['status']=='done':
  assert all(nodes[d]['status']=='done' for d in t['depends_on'])
  for file in t['outputs']:
   if file != 'verification.json': assert (out/file).is_file(),file
 if t['status']=='blocked':assert t['status_reason']
for rec in json.loads((out/'loaded_references.json').read_text())['loaded']:
 assert hashlib.sha256(Path(rec['path']).read_bytes()).hexdigest()==rec['sha256']
report={'status':'passed','evidence_kind':'derived from synthetic source','checks':['independent Fraction recomputation of all four rows','scope-filtered equal-once aggregate','all done node output files present','all done dependencies done','task_refs and action/acceptance fields present','all dependency IDs exist and DAG acyclic','blocked reasons explicit','loaded frozen reference hashes unchanged'],'tolerance':1e-12,'independence':'Separate verifier code executed by same coordinator; no independent scientific reviewer or host acceptance claimed','scope':'Local numeric/structural verification only; does not validate pending figure, final paragraph, absent background or actual mailbox recovery'}
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
assert (out/'verification.json').is_file()
print(json.dumps(report,ensure_ascii=False))
