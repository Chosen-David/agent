"""New independent namespace-only final validation; original review untouched."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
batch=ROOT/'agent_doc/results/comm20-20261009';old=batch/'final-integration';new=ROOT/'agent_doc/results/comm20-20261009-final-integration'
c=json.loads((new/'contract.json').read_text());m,p,proof=_snapshot(ROOT,c)
assert proof['manifest_sha256']=='945bf3b9298225c22115aede349bb16cc769a7f022fb562112b3ee8732ddd473'
assert new.name==m['run_id']==m['result_id']=='comm20-20261009-final-integration'
namespace=Path('agent_doc/results')/m['run_id']
for path in [c['manifest_path'],*[r['path'] for role in ['raw_data','outputs'] for r in m['artifacts'][role]]]:assert Path(path).is_relative_to(namespace)
assert not (new/'record.json').exists()
oldc=json.loads((old/'contract.json').read_text());oldm,oldp,oldproof=_snapshot(ROOT,oldc);oldv=json.loads((old/'validation.json').read_text());statuses,_=_review(ROOT,oldm,oldp,oldproof,oldv);assert statuses==['pass']*6
assert sha(old/'validation.json')=='6da64b6da90090efdf03740c23433ae100e8caa1e1a6f46964f7c0f6525c10ab'
assert sha(old/'manifest.json')=='efe3af414bf9c2477bfc929d512ee642d289be9143c28dfa1f1bbb1bc3387d9f'
assert m['artifacts']['code']==oldm['artifacts']['code'] and m['scope']==oldm['scope'] and m['execution']==oldm['execution'] and m['metrics']==oldm['metrics']
for file in ['environment.json','tests.log','reader_tests.log','validation_plan.json','summary.json']:assert (new/file).read_bytes()==(old/file).read_bytes()
report_ref=next(r for r in oldm['artifacts']['outputs'] if r['path'].endswith('report.md'));assert report_ref in m['artifacts']['inputs']
rows=[]
for n in range(1,21):
 f=batch.parent/f'comm20-20261009-r{n:02}';contract=json.loads((f/'contract.json').read_text());mm,pp,pr=_snapshot(ROOT,contract);v=json.loads((f/'validation.json').read_text());ss,_=_review(ROOT,mm,pp,pr,v);assert ss==['pass']*6
 rows.append({'round':n,'manifest_sha256':pr['manifest_sha256'],'validation_sha256':sha(f/'validation.json'),'keep':v['decision']['keep']})
assert [r['round'] for r in rows if r['keep']]==[16]
assert (ROOT/'agent_runtime/communication.py').read_bytes()==(batch.parent/'comm20-20261009-r16/candidate.py').read_bytes()
failure=json.loads((old/'registration_failure.json').read_text());assert failure['registration_completed'] is False
review={**oldv,**proof};review['verifier']={**oldv['verifier'],'run_id':'comm20-independent-final-canonical','method':'new namespace-only identity/hash/source revalidation plus all20fresh six-domain audits; unchanged previously passed27tests/61properties preserved'}
audit={'namespace_guard_pass':True,'old_failure_preserved':failure,'same_code_raw_protocol_environment':True,'report_binding_reclassified_to_input':True,'source_sha256':sha(ROOT/'agent_runtime/communication.py'),'rounds':rows,'adopted':[16],'old_review_sha256':sha(old/'validation.json'),'focused_tests_and_properties_reused':'27tests and61properties remain bound to same exact source/report/test bytes; no new timing claim'}
(new/'independent_namespace_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
extra=[ref(new/'independent_namespace_audit.json'),ref(batch/'independent_final_canonical_validate.py'),ref(old/'registration_failure.json'),ref(old/'validation.json')]
for name,check in review['checks'].items():
 check['reason']='Canonical result_id/run_id direct-child namespace and raw/output placement verified; old failed registration preserved; exact original scoped acceptance source/raw/report unchanged. '+check['reason'];check['evidence']=check['evidence']+extra
_snapshot(ROOT,c);_review(ROOT,m,p,proof,review);path=new/'validation.json';path.write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({'status':'usable-with-scope','validation_sha256':sha(path),'manifest_sha256':proof['manifest_sha256'],'namespace':'pass','all20':'pass','oldreview':'unchanged'}))
