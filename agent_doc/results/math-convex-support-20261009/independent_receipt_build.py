import json,hashlib
from pathlib import Path
from agent_runtime.result_validation import inspect_result
root=Path.cwd();d=root/'agent_doc/results/math-convex-support-20261009';c=json.loads((d/'controller_contract.json').read_text());p=inspect_result(root,c)['proof']
def ref(name):
 q=d/name;return {'path':str(q.relative_to(root)),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
evidence=[ref(x) for x in ['independent_check.py','independent_exact.json','independent_replay_comparison.json','independent_bindings.json','independent_commands.json','independent_command_0.log','independent_command_1.log','independent_review_by_gpt.md']]
reasons={
 'implementation':'Read exact RREF null-direction reducer and retrieval path; independently audited finite-termination proof and all trace invariants. BASE-only redirection preserves executed producer code and original corpus.',
 'reference_boundary':'Independent determinant minors, direct vector sums and simplex equations verify rank/output/support/tightness, nonconvex refusal and wrong-original-weight counterexample; no producer reducer used as reference.',
 'data_integrity':'All 482 manifest artifacts and validation plan (483 proof bindings) match before/after; all eight case IDs and six retrieval records match; raw originals retained with first failed mirror regression.',
 'numerical_sanity':'Exact Fraction checks verify every nonnegative coefficient, unit mass, output, augmented rank and decreasing active support; no floating tolerance used.',
 'measurement_validity':'Predeclared N/A: no performance/model/token measurements; elapsed diagnostics excluded from semantic replay comparison.',
 'reproducibility':'Independent safe producer reruns match exact/retrieval semantics; frozen five-module command runs all 53 tests successfully and mirror --check exits zero.'}
r={k:p[k] for k in ['manifest_sha256','artifact_hashes','validation_plan_sha256','scope']};r.update(schema_version='experiment-validation/v1',verifier={'actor':'/root/convex_support_result_review','independent':True,'source':'actual distinct collaboration actor context dispatched by /root; post-data tools executed in this context','run_id':'math-convex-support-20261009-independent-review-1','method':'Read actual frozen code/card/proof/source definitions and independently recompute exact outputs/rank by determinant minors; safe reruns and frozen regressions'},limitations=['Informal general proof; no Lean certificate; finite public fixtures only.','No model/GPU/actual token/unseen holdout/real Indexer trace/end-to-end/performance measurements.','Only source definitions and author caveat screened; no full-paper proof or experiment replication.','Same filesystem and host permissions; distinct review actor is an observed collaboration context, not Engine authentication; JSON alone never authorization.'],checks={k:{'verdict':'not_applicable' if k=='measurement_validity' else 'pass','reason':v,'evidence':evidence} for k,v in reasons.items()})
(d/'independent_receipt.json').write_text(json.dumps(r,indent=2)+'\n');accepted=inspect_result(root,c,lambda *_:r);assert accepted['status']=='usable-with-scope',accepted
(d/'independent_gate_check.json').write_text(json.dumps(accepted,indent=2)+'\n');print('Decision',accepted['status']);print('Receipt SHA256',hashlib.sha256((d/'independent_receipt.json').read_bytes()).hexdigest())
