import csv, hashlib, json, statistics, sys
from pathlib import Path
sys.path.insert(0,"/workspace/scratch/c12f3d9f92bd/agent")
from agent_runtime.communication import Mailbox
OUT=Path(__file__).resolve().parent
IN=OUT.parents[2]/"inputs"
ROOT=Path("/workspace/scratch/c12f3d9f92bd/agent/docs/continuous_optimization/rounds/2026-10-07-revision-handoff/evidence/needs-revision")
box=Mailbox("/workspace/scratch/c12f3d9f92bd/revision-w7-private/messages.sqlite",json.loads((ROOT/"communication-plan.json").read_text()),ROOT)
def save(name,x): (OUT/name).write_text(json.dumps(x,indent=2)+"\n")
def digest(b): return hashlib.sha256(b).hexdigest()
inbox=box.inbox("research-review");save("inbox-before.json",inbox)
event=next(x for x in inbox if x["seq"]==3)
verified=[]
for ref in event["event"]["refs"]:
 p=ROOT/ref["path"]; data=p.read_bytes(); got=digest(data); assert got==ref["sha256"]
 local=IN/("manuscript-revised.md" if ref["id"]=="w7-repaired-manuscript" else "response.json")
 assert data==local.read_bytes()
 verified.append(dict(ref,actual_sha256=got,read=True,identical_to_frozen_input=True))
 print("READ VERIFIED",str(p),got); print(data.decode())
save("verified-refs.json",verified)
hashes={p.name:digest(p.read_bytes()) for p in IN.iterdir() if p.is_file()}; save("input-hashes.json",hashes)
f=json.loads((IN/"findings.json").read_text()); assert hashes["manuscript.md"]==f["snapshot"]["id"]
assert hashes["measurements.csv"]==f["snapshot"]["input_sha256"]["measurements.csv"]
old=(IN/"manuscript.md").read_text();new=(IN/"manuscript-revised.md").read_text()
def section(s,name): return s.split("## "+name+"\n",1)[1].split("\n## ",1)[0].strip()
regression={name:section(old,name)==section(new,name) for name in ("Method","Limitations","Background")}; assert all(regression.values())
regression["synthetic_warning_preserved"]=old.splitlines()[2]==new.splitlines()[2]
regression["csv_sha_unchanged"]=True
rows=list(csv.DictReader((IN/"measurements.csv").open())); calculations={}
for w in ("small","large"):
 group=[r for r in rows if r["workload"]==w];b=statistics.mean(float(r["baseline_ms"]) for r in group);c=statistics.mean(float(r["candidate_ms"]) for r in group)
 calculations[w]={"n":len(group),"baseline_mean_ms":b,"candidate_mean_ms":c,"candidate_minus_baseline_ms":c-b,"relative_mean_latency_change_percent":100*(c-b)/b,"paired_difference_ms":[float(r["candidate_ms"])-float(r["baseline_ms"]) for r in group]}
table=[]
for line in new.splitlines():
 fields=[v.strip() for v in line.split("|")[1:-1]]
 if len(fields)==4 and fields[0] in ("small","large"):table.append(dict(zip(("workload","trial","baseline_ms","candidate_ms"),fields)))
regression["six_table_rows_match_csv_exactly"]=table==rows;assert table==rows
save("calculation-results.json",dict(calculations=calculations,regression=regression,inference="Descriptive fixture calculation only; no statistical reliability inference."))
conditions={"REV-F001":["Abstract line 6 states small 30% lower mean latency (100 vs 70 ms), large 20% higher (200 vs 240), baseline mean denominator and fixture-only scope.","Results line 25 states the same computed means and signed relative latency changes; no universal improvement assertion remains."],"REV-F002":["Abstract line 6 explicitly leaves reliability, accuracy equivalence, significance and deployment generalization unevaluated.","Synthetic warning line 3 and no accuracy/statistical measurements line 12 remain; line 25 disclaims reliability/deployment inference. Full manuscript has no new inferential statistics or experimental evidence."],"REV-F003":["Results line 14 labels Table 1 as invented measurements.csv fixtures in milliseconds.","Table body lines 18–23 contains all six original rows exactly; independent CSV/table equality check passed."]}
closure=[]
for item in f["findings"]:
 closure.append(dict(finding_id=item["finding_id"],original_manuscript_sha256=hashes["manuscript.md"],new_manuscript_sha256=hashes["manuscript-revised.md"],original_status=item["status"],status="closed",workflow_status="resolved",owner="original_research_review",original_recheck_conditions=item["recheck_conditions"],evidence=conditions[item["finding_id"]],reason="Both original acceptance conditions satisfied by independently read revised manuscript and unchanged fixture computation, not by response or ACK.",acceptance_results=[dict(condition=c,passed=True,evidence=e) for c,e in zip(item["recheck_conditions"],conditions[item["finding_id"]])]))
save("closure.json",dict(schema_version="1.0",original_role=True,source_seq=3,original_manuscript_sha256=hashes["manuscript.md"],new_manuscript_sha256=hashes["manuscript-revised.md"],csv_sha256=hashes["measurements.csv"],findings=closure,regression=regression,scientific_closure_basis="Actual manuscript and independent calculations; transport consumption is separate",scope="Single bounded recheck; no new experiments, citations, manuscript edits, network, or original finding mutation"))
print(json.dumps(dict(calculations=calculations,regression=regression,closed=[x["finding_id"] for x in closure]),indent=2))
