"""Schema/hash validation of actual independent evidence; not host authentication."""
import json,hashlib,sys
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review,validate_result_plan
def ref(name):
    f=BASE/name
    return {'path':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
def main():
    dag=json.loads((BASE/'dag.json').read_text());validate_result_plan(dag);contract=dag['tasks'][0]['experiment_result'];manifest,plan,proof=_snapshot(ROOT,contract)
    assert proof['manifest_sha256']=='60602b59ca53ae0407f57c886eaedb134f9538df98834db7dc13ccf053940334'
    def check(verdict,reason,*names):
        return {'verdict':verdict,'reason':reason,'evidence':[ref('independent_report.md')]+[ref(n) for n in names]}
    checks={
      'implementation':check('pass','Actual final code/card/proof boundaries read; fixed supported target lift correct, total-rank caveat explicit, repaired finite-range/decomposition guards directly checked.','independent_verify.py','independent_boundary_recheck.py','independent_sources.json'),
      'reference_boundary':check('pass','72 exact enumerations, 48 direct product-score cases with 17 positive tails, full-space Kronecker least-squares lift, fresh noncentral and misuse witnesses, 11 ordinary plus 10 extreme/injected guard checks pass unchanged tolerances.','independent_observations.json','independent_boundary_observations.json'),
      'data_integrity':check('pass','All 259 role references/257 unique bindings hash-match, all 198 recursive corpus files covered, IDs 72/48/15 unique and complete, independent execution inputs match manifest, retrieval and dependency context match exactly; failed histories retained.','independent_integrity.json','independent_reuse_provenance.json'),
      'numerical_sanity':check('pass','Exact and floated results separated; finite errors far below 1e-9 scaled; MP/support/rank identities checked. Extreme nonfinite outcomes reject; representable tiny nonzero direction passes. Range guards are not numerical accuracy or population-rank certificates. Sensor units and paired/centered/ridge misuse discriminate.','independent_observations.json','independent_boundary_observations.json'),
      'measurement_validity':check('not_applicable','Predeclared allow_not_applicable is true; only diagnostic CPU times and characters/bytes, no fairness/performance/model-accuracy/token savings claim. Public regression inputs cannot count as unseen-model evaluation.','independent_observations.json'),
      'reproducibility':check('pass','Actual independent direct rerun matches final inputs/output/context without overwriting producer raw. Copied full/reader logs byte-verified and runtime/test diff/status versus baseline empty; targeted 52/sync actually rerun in v2. Timing is diagnostic and need not match.','independent_verify.py','independent_observations.json','independent_integrity.json','independent_reuse_provenance.json')}
    receipt={'schema_version':'experiment-validation/v1',**proof,'verifier':{'actor':'independent-math-review','independent':True,'source':'Actual host-provided collaboration context /root/singular_result_review; completion event authenticated separately by parent host','run_id':'math-singular-bilinear-20261008-v2-independent-review-1','method':'Actual source/code inspection plus direct Fraction enumeration, finite-product score checks, full-space Kronecker least-squares lift, range/decomposition rejection reruns and full frozen-hash/runtime-regression-reuse audit'},'checks':checks,'acceptance':'usable-with-scope','limitations':['Finite checks and manual derivation review are not formal proof or universal bug-free assurance.','NumPy decompositions share the installed backend though fixed-lift reference is an independent full-space linear solve.','Supplied supports are not estimated population ranks; finite outputs do not certify arbitrary ill-conditioned accuracy.','No model/token/GPU/real-system/e2e/production gains or protected Engine deployment; only conditional product-law score MSE and public structural retrieval.','Future reserved specification is unexecuted; existing disclosed tests are public regression evidence.','Full 851/reader 3 logs are verified historical unchanged-code observations; only targeted 52/sync and math/retrieval checks reran for v2.','Host must independently authenticate actual reviewer completion SHA; receipt fields and hashes alone are not identity credentials.']}
    statuses,evidence=_review(ROOT,manifest,plan,proof,receipt)
    assert all(s in ('pass','not_applicable') for s in statuses),statuses
    assert _snapshot(ROOT,contract)[2]==proof
    out=BASE/'independent_receipt.json';out.write_text(json.dumps(receipt,indent=2)+'\n');_review(ROOT,manifest,plan,proof,json.loads(out.read_text()))
    print(json.dumps({'receipt_path':str(out.relative_to(ROOT)),'receipt_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'acceptance':'usable-with-scope','manifest_sha256':proof['manifest_sha256'],'schema_check':'passed; host identity authentication separate'}))
if __name__=='__main__':main()
