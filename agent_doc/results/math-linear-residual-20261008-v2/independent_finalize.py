from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
mp=BASE/'manifest.json';assert sha(mp)=='00e80ea8a8eea909c6d5d1c26ba760a1469a86673d8f4dc6fd817acf51d4b7fe';m=json.loads(mp.read_text());bindings={m['validation_plan']['path']:m['validation_plan']['sha256']}
for refs in m['artifacts'].values():
 for r in refs:
  p=ROOT/r['path'];assert p.is_file() and not p.is_symlink() and sha(p)==r['sha256'],r['path'];assert r['path'] not in bindings or bindings[r['path']]==r['sha256'];bindings[r['path']]=r['sha256']
inv=json.loads((BASE/'corpus_inventory.json').read_text());inventory=[]
for label,dirname,snapshot in [('root','knowledge','snapshot_learning_state.json'),('plugin','plugins/research-assistant/skills/model-with-knowledge/assets/knowledge','snapshot_plugin_learning_state.json')]:
 actual={str(p.relative_to(ROOT)) for p in (ROOT/dirname).rglob('*') if p.is_file()};declared={x['path'] for x in inv[label]};assert declared==actual,(label,declared^actual)
 for r in inv[label]:
  if r['path'].endswith('/learning_state.json'):
   assert r['sha256']==sha(BASE/snapshot)
  else:assert r['path'] in bindings and bindings[r['path']]==r['sha256'] and sha(ROOT/r['path'])==r['sha256'],r['path']
 inventory.append({'root':dirname,'files':len(actual),'all_retrieval_dependencies_bound':True,'learning_state':'historical snapshot, not mutable dependency'})
assert len(bindings)==478
# Source audit is based on actual downloaded primary text; sources.json itself is a frozen manifest input.
source_scope=['Higham definition/block factorization and definite/semidefinite criterion actually read. Statistical predictor and score equations are project derivations.','AttSVD actual arXivv1 HTML methods3.1-3.3 and AppendixB read. Fixed whole query/key logit matrix metric differs from paired risk. AppendixB adds ridge yet writes unregularized norm equality; the card/report correctly warns ridge changes metric. Value mass is a diagonal surrogate for the exact P^TP metric. No experiments reproduced.']
notes='''# Independent result audit_by_gpt

Actual separate verifier context: /root/linear_residual_result_review. This is a local manual host audit; it does not certify Engine/ReviewSession identity. The host must bind the observed delegated start/completion before accepting the receipt.

I read the current producer validate.py, retrieve.py, raw.json, retrieval/config, corpus card proof and two strong prerequisites, source HTML excerpts, frozen report, failure/repair lineage, manifest and validation protocol. All 478 result/protocol bindings match frozen bytes; the entire recursive root and plugin knowledge inventories each contain212 files. Mutable learning metadata is retained as a historical snapshot, not treated as a mutable dependency.

Independent_check.py uses separate dimension-checked indexed arithmetic and explicit scalar/2x2 normal-equation solving, rather than the producer Gauss-Jordan inverse and zip operations. It recalculates every moment, SPD retained matrix, predictor, Schur residual, residual MSE and PSD difference across25 exact records in5 normalized finite laws. Query folding and independently enumerated score risks match. Paired risks reverse reconstruction preference: key losses1,2 versus score losses1/2,0. Nonlinear deterministic b=a² has zero conditional covariance but homogeneous linear residual17/2, so S is not conditional covariance. Noncentral a=1,b=3 and exact zero residual are preserved. Singular retained moments refuse the declared SPD interface; this does not exclude generalized solutions.

Producer helpers do not validate arbitrary ragged input and inv does not independently establish SPD. This is acceptable only because the accepted scope is a fixed well-shaped finite development harness, whose every sample probability/dimension and retained SPD matrix I separately validated; it is not a production covariance API. Numerical production solves, conditioning, ridge and support treatment remain outside acceptance.

The card proof is correct under finite noncentral moments and Caa SPD: residual orthogonality eliminates cross terms; the PSD difference establishes unique homogeneous least squares optimality. Independent query weighting gives a PSD weighted trace difference, with no unique score optimum claimed. Mixed fourth moment integrability is separately required for paired data. Rotation transport explicitly requires Rh(n)B=B Rs(n); I checked the same rotation, opposite rotation with I, and NoPE/RoPE I refusal witnesses. Opposite-frequency anti-linear intertwiners remain possible as explained by the strong prerequisite; these finite witnesses do not reject them generally. Sensor A²/V² units and shifts match.

The actual primary HTML bytes match sources.json. Higham supplies block factorization/PSD background; the statistical derivation is the project's. AttSVD methods and AppendixB concern a fixed complete score-matrix objective. Ridge changes the metric, and per-key mass is a value-output surrogate; no original paper experiments or venue claim is accepted. The v1 serialization failure is explicitly preserved, no v1 raw exists, and v2 changed tuple serialization only. Later evidence-path correction was followed by retrieval/tests/sync reruns with previous outputs preserved.

Independent retrieval reproduced all six top3 lists and the exact three-card strong prerequisite context. Public development queries and manual premise decisions do not constitute model recognition, unseen holdout or refusal evidence. I did not open sealed holdout contents. Independent targeted unit checks report53 tests and pass; sync --check passes. Timings are diagnostics with no comparative performance claim. No model/GPU/token/Lean/e2e or arbitrary-input guarantee is accepted.

Five applicable domains pass. Measurement validity is not applicable because there is no performance/model/accuracy measurement claim; the frozen protocol explicitly allows this status. These results are usable only within the frozen finite mathematical/structural scope after actual host provenance binding. Hashes certify bytes, not truth or identity.
'''
(BASE/'independent_review_by_gpt.md').write_text(notes)
(BASE/'independent_binding_audit.json').write_text(json.dumps({'manifest_sha256':sha(mp),'bindings_checked':len(bindings),'recursive_inventory':inventory,'sources_read_scope':source_scope,'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n')
evidence=[]
for name in ['independent_check.py','independent_checks.json','independent_finalize.py','independent_binding_audit.json','independent_review_by_gpt.md']:
 p=BASE/name;evidence.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
reasons={'implementation':'Read actual code and proof; independently validated all fixed input shapes, normalized probabilities, SPD normal equations and tuple repair. Fixed finite harness only, not arbitrary-input API.','reference_boundary':'Separate scalar/determinant solver and indexed residual enumeration match25records; exact/noncentral/nonlinear/singular/paired/rotation/sensor discrimination passes.','data_integrity':'All478bindings and complete212+212 recursive corpus inventories checked; six public query lists/context independently match; failed v1 has no raw and preserved logs, no sealed contents read.','numerical_sanity':'Fraction recomputation matches moments/PSD/MSE/weighted scores, paired loss reversal and A²/V² sensor units exactly; no finite examples promoted to universal proof.','measurement_validity':'Pre-authorized N/A: no comparative performance, model accuracy, GPU/token/e2e claim. Timings are diagnostics only.','reproducibility':'Independent exact recalculation, actual file/SQLite retrieval,53 targeted unit tests and sync check all reproduced within bounded CPU review.'}
receipt={'schema_version':'experiment-validation/v1','manifest_sha256':sha(mp),'artifact_hashes':bindings,'validation_plan_sha256':m['validation_plan']['sha256'],'scope':m['scope'],'verifier':{'actor':'/root/linear_residual_result_review','independent':True,'source':'actual separate delegated Codex context; local manual host, not Engine authentication','run_id':'math-linear-residual-20261008-v2-independent-1','method':'Actual code/proof/source audit; independently written exact arithmetic recomputation; retrieval/regression reruns; complete frozen dependency audit'},'limitations':['Finite public development harness only; producer helpers are not a dimension-validating production covariance API.','General mathematical derivation reviewed informally, no Lean/formal proof or universal absence of bugs.','No model/GPU/heldout capability/token/e2e/performance claim; source literature experiments not reproduced.','Mutable learning metadata is historical snapshot; host must authenticate observed separate reviewer lifecycle, receipt JSON alone does not.'],'checks':{k:{'verdict':'not_applicable' if k=='measurement_validity' else 'pass','reason':v,'evidence':evidence} for k,v in reasons.items()},'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}
(BASE/'independent_verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
# Recheck the complete frozen bindings after generating independent evidence.
assert sha(mp)==receipt['manifest_sha256']
for p,h in bindings.items():assert sha(ROOT/p)==h,p
print(json.dumps({'receipt_path':str((BASE/'independent_verification.json').relative_to(ROOT)),'receipt_sha256':sha(BASE/'independent_verification.json'),'manifest_sha256':sha(mp),'bindings':len(bindings),'verdict':'five pass, measurement N/A'}))
