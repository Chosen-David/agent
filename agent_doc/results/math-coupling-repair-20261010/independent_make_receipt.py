import json,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review
manifest,plan,proof=_snapshot(ROOT,json.loads((B/'contract.json').read_text()))
assert proof==json.loads((B/'independent_snapshot.json').read_text())
def ref(n):
 p=B/n;return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
report='independent_review_by_gpt.md'
checks={
 'implementation':('pass','Exact clipping/completion and zero branch match limited informal proof; no float/sparse/API guarantee',[report,'independent_verify.py']),
 'reference_boundary':('fail','Independent hand-derived T6 matrix has cost1 versus frozen1/2; unchanged verify aborts beforeT7/T8',['independent_exact.json','independent_verify.log',report]),
 'data_integrity':('fail','231 opaque paths and257 bindings intact; required current candidate/closure absent, historical draft retrieval and inaccurate candidate eight-case statement do not satisfy frozen acceptance',['independent_preservation.json','independent_retrieve.log',report]),
 'numerical_sanity':('pass','Supplemental exact matrices/conservation/cost and T7 diagnostic refusal/T8 direct dual arithmetic agree; original eight-case acceptance not inferred',['independent_exact.json',report]),
 'measurement_validity':('not_applicable','Protocol permits N/A; diagnostic seconds/characters are not performance/token/model metrics',[report]),
 'reproducibility':('fail','Unchanged negative verify/diagnose reproduced; original full eight-case/current retrieval/34-test acceptance not reproduced from frozen current corpus',['independent_commands.json','independent_verify.log','independent_diagnose.log','independent_retrieve.log',report])}
receipt=dict(proof,schema_version='experiment-validation/v1',verifier={'actor':'/root/repair_result_review','independent':True,'source':'Actual parent-dispatched independent child different from producer and plan reviewer; parent must observe completion and supply trusted adapter; no cryptographic identity or deployed ReviewSession claimed','run_id':'math-coupling-repair-20261010-independent1','method':'Code and limited source review; hand-derived matrix cost reference; unchanged failure/diagnose/current retrieval replay; opaque preservation and native binding before/after checks'},limitations=['Original scope invalid, candidate unpublished; no scientific downstream acceptance','All2x2 public rational cases and informal finite proof only; no float/GPU/model/Lean/universal correctness certification','Sources selectively read at reported sections; no full proof review, source experiments reproduction or formal recent-preprint acceptance verification','Historical temporary draft retrieval and34-test regression not current replay; diagnostic characters/seconds are not tokens/performance','231 preserved paths hashed only; holdout contents never inspected','Parent-observed independent completion and trusted host callback required; hashes alone cannot authenticate reviewer'],checks={k:{'verdict':v,'reason':reason,'evidence':[ref(n) for n in files]} for k,(v,reason,files) in checks.items()})
statuses,_=_review(ROOT,manifest,plan,proof,receipt);assert 'fail' in statuses
p=B/'independent_receipt.json';p.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(hashlib.sha256(p.read_bytes()).hexdigest())
