import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review
B=Path(__file__).resolve().parent
manifest,plan,proof=_snapshot(ROOT,json.loads((B/'contract.json').read_text()))
assert proof==json.loads((B/'independent_snapshot.json').read_text())
def ref(n):
 p=B/n;return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
report='independent_review_by_gpt.md'
checks={
'implementation':('pass','Actual scalar greedy/dual code and general finite coupling, triangle, residual-TV, perturbation and weak-duality proofs reviewed; source/premise distinctions agree',[report,'independent_verify.py']),
'reference_boundary':('pass','Independent grouped-support absolute CDF integral agrees for six transport cases; invalid probability/marginal case and ridge closed form agree; direct checks of all supplied primal/dual constraints',['independent_exact.json',report]),
'data_integrity':('pass','Eight distinct public IDs, six curated Top3 hits, exact complete two-entry prerequisite closure;229 opaque preservation paths unchanged; new JSON/Markdown mirrors equal; all257 native bindings unchanged',['independent_snapshot.json','independent_preservation.json','independent_replay_summary.json']),
'numerical_sanity':('pass','Exact finite Fraction costs/errors/perturbation and primal-dual equality; cancellation and metric mismatch distinguished; force costs and output use N; ridge extra penalty exact',['independent_exact.json',report]),
'measurement_validity':('not_applicable','Validation plan explicitly allows N/A: time/characters/bytes diagnostic only; no model/GPU/performance/token/e2e benefit measured or accepted',[report,'independent_replay_summary.json']),
'reproducibility':('pass','Separate-directory frozen producer replays match non-timing raw and retrieval payloads;34 knowledge/index regressions independently pass; actual before/after native snapshots unchanged',['independent_commands.json','independent_regression.log','independent_replay_summary.json','independent_verify.py'])}
receipt=dict(proof,schema_version='experiment-validation/v1',verifier={
'actor':'/root/transport_result_review','independent':True,'source':'Actual parent-dispatched child result review distinct from root-transport-producer and plan reviewer; parent must observe actual completion and inject trusted adapter; no deployed ReviewSession or cryptographic host authentication claimed','run_id':'math-transport-output-20261009-independent1','method':'Read instructions, frozen contract/criteria/card/code/config/raw and source-limited originals; grouped CDF Fraction reference not producer greedy; direct primal-dual feasibility; separate replay and34 regressions;229 hash-only preservation and new mirror;257 binding before/after native snapshots'},
limitations=[
'Informal finite general proof review and eight public scalar cases; no Lean, general floating-point certificate or universal bug-free implementation guarantee',
'Six exact-alias public file/SQLite Top3 queries and two-card closure establish curated structural behavior only; manual premise decisions are not unseen LLM accuracy/refusal',
'No model/GPU, token savings, production deployment or end-to-end performance evidence; time and characters/bytes diagnostic only',
'Classic selected extracted §2.3/2.5 text and recent AttSVD selected HTML independently read, not full paper/visual review or source experiment reproduction; OTPrune version/author acceptance metadata verified, technical full text not independently reread and formal proceedings not verified',
'229 preservation paths hashed only; holdout contents never parsed or inspected; prior search coverage is not exhaustive absence of reusable results',
'Hash/schema identity does not authenticate reviewer or establish applicability; parent-observed actual completion and trusted host callback required for runtime acceptance'],
checks={k:{'verdict':v,'reason':reason,'evidence':[ref(n) for n in files]} for k,(v,reason,files) in checks.items()})
_review(ROOT,manifest,plan,proof,receipt)
p=B/'independent_receipt.json';p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(hashlib.sha256(p.read_bytes()).hexdigest())
