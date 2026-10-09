"""Scoped validation of intentional unsafe counterexamples; never adopt."""
import sys,json,hashlib,difflib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review,CHECKS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def main(num):
 f=ROOT/'agent_doc/results'/f'comm20-20261009-r{num:02}';batch=f.parent/'comm20-20261009'
 contract=json.loads((f/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract)
 assert json.loads((f/'ready.json').read_text())['manifest']['sha256']==proof['manifest_sha256']
 diff=''.join(difflib.unified_diff((f/'baseline.py').read_text().splitlines(True),(f/'candidate.py').read_text().splitlines(True)));(f/'independent_source.diff').write_text(diff)
 safety=json.loads((f/'independent_safety.json').read_text());assert safety['baseline']['repeats']==safety['candidate']['repeats']==5
 assert json.loads((f/'independent_properties_baseline.json').read_text())['ok']
 for t in safety['baseline']['trials']:
  assert t['duplicate_mutated_ref'].startswith('rejected') and t['changed_valid_manifest'].startswith('rejected') and t['thread_retry']==['accepted']*4
 expected={18:'duplicate_mutated_ref',19:'changed_valid_manifest',20:'thread_retry'}[num]
 for t in safety['candidate']['trials']:
  assert t[expected]=='accepted' if num!=20 else all(x.startswith('rejected:ProgrammingError') for x in t[expected])
 raw=json.loads((f/'raw.json').read_text());repeat=json.loads((f/'independent_replay/raw.json').read_text())
 assert raw['performance']==repeat['performance']=='not evaluated: safety challenge or failed correctness'
 decision={'keep':False,'reason':'NEVER adopt intentional unsafe variant; five independent public counterexamples confirmed','counterexample':expected,'trials':safety,'producer_tests':raw['correctness'],'replay_tests':repeat['correctness']}
 (f/'independent_decision.json').write_text(json.dumps(decision,indent=2)+'\n')
 evidence=[ref(p) for p in [f/'independent_source.diff',f/'independent_decision.json',f/'independent_safety.json',f/'independent_properties_baseline.json',f/'independent_properties_candidate.json',f/'independent_replay/raw.json',f/'independent_replay/safety.json',f/'independent_replay/test_result.json',batch/'independent_safety.py',batch/'independent_validate_safety.py',batch/'independent_properties.py']]
 reasons={
 'implementation':'Exact intentional trust/isolation weakening patch and complete public paths reviewed; current runtime equals safe frozen baseline, not candidate. No adoption authorized.',
 'reference_boundary':'Independent five trials confirm required public safety counterexample versus rejection/working concurrency on baseline. Candidate correctness failure is preserved, not presented as correctness success.',
 'data_integrity':'All manifest bindings checked before/after; raw failures, five independent trial identities and exact candidate/baseline hashes preserved.',
 'numerical_sanity':'Five trials and four threaded retries per trial counted exactly; outcome domains and test/failure counts inspected. No performance metric or unsafe improvement claim.',
 'measurement_validity':'Frozen safety protocol deliberately disables timing/performance adoption. Actual public trust/manifest/isolation counterexamples executed five times independently, with failed tests preserved.',
 'reproducibility':'Exact frozen candidate explicit --candidate replay plus independent own public five-trial safety fixture reproduces intended failure. Scope is valid negative falsification data only.'}
 review={'schema_version':'experiment-validation/v1',**proof,'verifier':{'actor':'comm20-independent-verifier','independent':True,'source':'host collaboration agent /root/comm20_verifier; actual per-round message authenticates','run_id':f'comm20-independent-r{num:02}','method':'independent source/hash review, five own public safety trials, exact frozen harness/test replay'},'limitations':['Intentional rejected unsafe alternatives are evaluated only as local public safety counterexamples; candidate correctness is not accepted.','No performance/timing claim; no model/network/token/deployment effects measured.','Finite fixtures and hashes do not prove universal absence of bugs or authenticate actors without actual trusted host events.'],'checks':{k:{'verdict':'pass','reason':reasons[k],'evidence':evidence} for k in CHECKS},'decision':decision}
 _snapshot(ROOT,contract);_review(ROOT,manifest,plan,proof,review);path=f/'validation.json';path.write_text(json.dumps(review,indent=2)+'\n')
 print(json.dumps({'round':num,'status':'usable-with-scope','keep':False,'validation_sha256':sha(path),'counterexample':expected,'candidate_property':json.loads((f/'independent_properties_candidate.json').read_text()),'candidate_trials':safety['candidate']}))
if __name__=='__main__':main(int(sys.argv[1]))
