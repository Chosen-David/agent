from pathlib import Path
import hashlib,json
from agent_runtime.result_validation import inspect_result
R=Path.cwd();B=R/'agent_doc/results/math-convex-projection-20261009'
c=json.loads((B/'controller_contract.json').read_text());p=inspect_result(R,c)['proof']
def ref(name):
 f=B/name;return {'path':str(f.relative_to(R)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
review={k:p[k] for k in ['manifest_sha256','artifact_hashes','validation_plan_sha256','scope']}
review.update(schema_version='experiment-validation/v1',verifier={'actor':'/root/projection_result_review','independent':True,'source':'Actual parent-dispatched fresh result-review context; distinct from producer and plan reviewer; completion must be observed by parent host','run_id':'math-convex-projection-20261009-independent-result-review-1','method':'Manual implementation/source reading, independent analytical Fraction reference/full certificates, safe frozen-code replay, 53 regression tests, mirror check and before/after runtime hash snapshot'},limitations=['Finite small public rational cases and informal mathematical review; no formal or floating-point numerical certification','Public structural file/SQLite retrieval only, no unseen or model refusal evaluation','No token, GPU, model, online performance or end-to-end benefit claim','Primary-source review limited to Boyd §4.2.3 and WildCat §2.2/2.6 Algorithms2–3; no full paper theorem or experiment replication','Mutating sync replay excluded under assigned write ownership; independent mirror --check confirms final synced state'])
spec={
'implementation':('pass','Actual executed Fraction/face enumeration and retrieval paths read; affine dependence, feasibility, full vertex coverage and source-object distinctions checked',['independent_review_by_gpt.md','independent_verify.py','independent_exact.json']),
'reference_boundary':('pass','Independent closed-form geometry and direct exact reconstruction match ten accepted outputs; negative/empty refusal, duplicate, incomplete max and mapped-kernel boundaries checked',['independent_exact.json','independent_verify.py','independent_review_by_gpt.md']),
'data_integrity':('pass','486 artifact hashes plus protocol, frozen manifest digest, unique P1–P12, six structural records and original source PDF digests verified before/after',['independent_integrity.json','independent_pending_snapshot.json','independent_replay_summary.json']),
'numerical_sanity':('pass','Exact finite rational simplex, residual squares, all vertex scores, full max, nonnegative gap, D<=opt<=P, clipping and gap-zero identities reconstructed',['independent_exact.json','independent_verify.py']),
'measurement_validity':('not_applicable','Validation plan permits N/A: CPU seconds and serialized chars are diagnostics, with no performance, token or model-quality claim',['independent_review_by_gpt.md','independent_replay_summary.json']),
'reproducibility':('pass','Safe output-redirected frozen producer replay matches excluding diagnostic seconds; 53 fixed-module tests and independent mirror check pass; frozen dependencies unchanged',['independent_replay_summary.json','independent_commands.json','independent_command_0.log','independent_command_1.log','independent_integrity.json'])}
review['checks']={k:{'verdict':v,'reason':r,'evidence':[ref(n) for n in fs]} for k,(v,r,fs) in spec.items()}
f=B/'independent_receipt.json';f.write_text(json.dumps(review,indent=2)+'\n')
# Schema/binding verification only; observed identity and acceptance are delivered separately to parent.
from agent_runtime.result_validation import _snapshot,_review
m,pl,pf=_snapshot(R,c);_review(R,m,pl,pf,review)
print(json.dumps({'decision':'usable-with-scope','receipt_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'artifact_hashes':len(pf['artifact_hashes'])}))
