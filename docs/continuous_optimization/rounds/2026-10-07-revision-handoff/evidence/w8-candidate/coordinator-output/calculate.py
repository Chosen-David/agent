from pathlib import Path
import csv,json,hashlib,platform
from decimal import Decimal
BASE=Path('/workspace/scratch/c12f3d9f92bd/revision-candidate-roles-run')
OUT=BASE/'cases/research-assistant/attempts/0001/outputs'
INP=BASE/'cases/research-assistant/inputs'
SKILL=BASE/'snapshot/plugins/research-assistant/skills/research-assistant'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(name,x): (OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
rows=list(csv.DictReader((INP/'measurements.csv').open()))
assert len(rows)==4 and len({r['workload'] for r in rows})==4
metrics=[]
for r in rows:
 b=Decimal(r['baseline_ms']);c=Decimal(r['candidate_ms'])
 assert b>0 and c>0 and r['scope'] in ['end_to_end','kernel_only']
 metrics.append({**r,'baseline_ms':float(b),'candidate_ms':float(c),'candidate_minus_baseline_ms':float(c-b),'latency_reduction_pct':float((b-c)/b*100),'speedup_baseline_over_candidate':float(b/c),'evidence_kind':'synthetic','input_version':'measurements.csv@v2'})
e=[r for r in metrics if r['scope']=='end_to_end']
b=sum(Decimal(str(r['baseline_ms'])) for r in e);c=sum(Decimal(str(r['candidate_ms'])) for r in e)
results={'input_version':'measurements.csv@v2','input_sha256':sha(INP/'measurements.csv'),'data_kind':'synthetic','formulas':{'speedup':'baseline_ms / candidate_ms','latency_reduction_pct':'100 * (baseline_ms - candidate_ms) / baseline_ms'},'per_workload':metrics,'end_to_end_equal_once_diagnostic':{'assumption':'One invocation of each of small, medium, large; no real workload weights inferred','baseline_total_ms':float(b),'candidate_total_ms':float(c),'speedup':float(b/c),'latency_reduction_pct':float((b-c)/b*100)},'excluded_from_end_to_end_aggregate':['kernel'],'limitations':['No repetitions, variability, correctness checks, runtime configuration, or workload mixture provided','Synthetic fixture arithmetic cannot establish real-model or real-system performance','v1 CSV and figure@v1/background@v1 output bytes absent; no numerical v1-to-v2 delta or historical output revalidation possible']}
dump('results.json',results)
with (OUT/'results.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
refs=['SKILL.md','references/orchestrator.md','references/execution.md','references/task_supervision_workflow.md','references/project_memory_workflow.md','references/agent_communication_workflow.md','references/data_visualization_workflow.md','references/research-data-visualization_execution.md']
dump('loaded_references.json',{'snapshot_root':str(SKILL),'loaded':[{'path':str(SKILL/r),'sha256':sha(SKILL/r),'use':'figure planning only; not an executed visualization role' if 'visualization' in r else 'coordinator execution and handoff recovery planning'} for r in refs],'inputs':[{'path':str(INP/r),'sha256':sha(INP/r)} for r in ['project.json','measurements.csv','concept.txt']]+[{'path':str(BASE/'cases/research-assistant/task.txt'),'sha256':sha(BASE/'cases/research-assistant/task.txt')}],'boundary':'Only frozen snapshot skill and relevant references loaded; no scoring material, repository edits, network, installations, role delegation, or runtime service start'})
log={'python':platform.python_version(),'execution':'CPU standard-library CSV parsing, Decimal arithmetic, output serialization','checks':{'four_unique_workloads':True,'positive_latency_ms':True,'known_scopes':True,'kernel_excluded_from_end_to_end_aggregate':True},'new_experiments':0,'independent_roles_executed':0,'background_services_started':0}
dump('calculation_log.json',log)
print(json.dumps(results,ensure_ascii=False,indent=2))
