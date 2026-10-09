"""Independent final gate, all20 frozen result proofs and final source/report."""
import json,sys,hashlib,re,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_review,CHECKS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
f=ROOT/'agent_doc/results/comm20-20261009/final-integration';batch=f.parent
contract=json.loads((f/'contract.json').read_text());manifest,plan,proof=_snapshot(ROOT,contract)
assert proof['manifest_sha256']=='efe3af414bf9c2477bfc929d512ee642d289be9143c28dfa1f1bbb1bc3387d9f'
rows=[]
for n in range(1,21):
 d=batch.parent/f'comm20-20261009-r{n:02}';c=json.loads((d/'contract.json').read_text());m,p,pr=_snapshot(ROOT,c);v=json.loads((d/'validation.json').read_text());statuses,e=_review(ROOT,m,p,pr,v);assert statuses==['pass']*6
 rows.append({'round':n,'manifest_sha256':pr['manifest_sha256'],'validation_sha256':sha(d/'validation.json'),'evidence_count':len(e),'keep':v['decision']['keep'],'six_domains':'pass'})
assert [r['round'] for r in rows if r['keep']]==[16]
assert (ROOT/'agent_runtime/communication.py').read_bytes()==(batch.parent/'comm20-20261009-r16/candidate.py').read_bytes()
log=(f/'tests.log').read_text();reader=(f/'reader_tests.log').read_text();own=(f/'independent_tests.log').read_text()
assert 'Ran 887 tests' in log and log.rstrip().endswith('OK (skipped=8)') and len(re.findall(r'\.\.\. skipped',log))==8
assert 'Ran 3 tests' in reader and reader.rstrip().endswith('OK')
assert 'Ran 27 tests' in own and own.rstrip().endswith('OK')
assert json.loads((f/'independent_properties.json').read_text())['count']==61
report=(batch/'report.md').read_text();numbers=[]
for name,file,repeats in [('producer','raw.json',11),('independent','independent_replay/raw.json',5)]:
 raw=json.loads((batch.parent/'comm20-20261009-r16'/file).read_text());case=next(c for c in raw['cases'] if c['total']==20000 and c['layout']=='single');assert len(case['raw'])==repeats
 med={n:statistics.median(p[n] for p in case['raw']) for n in ['baseline','candidate']};assert med==case['median_ms'];ratio=med['baseline']/med['candidate']
 assert f"{med['baseline']:.6f}" in report and f"{med['candidate']:.6f}" in report and f"{ratio:.6f}" in report
 numbers.append({'role':name,'median_ms':med,'ratio':ratio,'saving_ms':med['baseline']-med['candidate'],'repeats':repeats})
summary=json.loads((f/'summary.json').read_text());assert summary['rounds']==20 and summary['adopted']==[16] and summary['tests']=={'run':887,'pass':879,'skip':8,'fail':0,'reader_pass':3}
audit={'rounds':rows,'evaluated':20,'adopted':[16],'runtime_sha256':sha(ROOT/'agent_runtime/communication.py'),'source_matches_adopted16':True,'producer_tests':summary['tests'],'independent_focused_tests':27,'own_properties':61,'recalculated_measurements':numbers,'report':'Exact gains, negative outcomes, noise/trust/limited synthetic scope preserved; no fresh performance/live-service claim.'}
(f/'independent_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
evidence=[ref(p) for p in [f/'independent_audit.json',f/'independent_tests.log',f/'independent_properties.json',batch/'independent_final_validate.py',batch/'independent_properties.py',ROOT/'tests/test_communication_regressions.py',batch/'report.md']]
reasons={
'implementation':'Live runtime equals exactly accepted16 projection; complete source/diff reviewed, both new public regressions meaningful. All rejected query/constructor/safety variants excluded.',
'reference_boundary':'Independent27 communication/usage/newregression tests and61 own list/bytes/root/hash/receipt/atomicbudget/migration/concurrency properties passed. Earlier safety and constructor counterexamples remain rejected.',
'data_integrity':'Freshly rehashed20 frozen manifests/artifacts/protocols and six-domain independent evidence, final manifest/report/test/source before/after. Only adopted decision16.',
'numerical_sanity':'Recomputed16 eleven/five pair medians, ratios and savings against report;20evaluated/oneadopted;887tests879pass8skip,reader3,independent27 match complete logs.',
'measurement_validity':'No new integration performance claim. Complete887/3logs and skip scope inspected. Earlier16 sharedCPU/warmcache synthetic usage gain close to thresholds retained with noise limits; no deployment/model/token/network extrapolation.',
'reproducibility':'Exact adopted-source identity confirmed; independent27focused tests and61properties rerun. All20 prior repeats/counterexamples hash-valid; numeric-key reopen and mutated-reference new regressions pass.'}
review={'schema_version':'experiment-validation/v1',**proof,'verifier':{'actor':'comm20-independent-verifier','independent':True,'source':'host collaboration context /root/comm20_verifier; actual final message authenticates','run_id':'comm20-independent-final-integration','method':'fresh20recursivehash/sixdomain audit, source/report review, independent27tests/61properties'},'limitations':['Performance support only from accepted16 synthetic public usage case on sharedCPU/warmcache; no new integration timing.','Full887suite has8explicit skips; finite27focused tests/61properties do not prove universal bug freedom or external deployment.','Research screening is background; no paper replication, new scientific algorithm, model/token/network quality or persistent supervisor deployment certified.'],'checks':{k:{'verdict':'pass','reason':reasons[k],'evidence':evidence} for k in CHECKS}}
_snapshot(ROOT,contract);_review(ROOT,manifest,plan,proof,review);path=f/'validation.json';path.write_text(json.dumps(review,indent=2)+'\n')
print(json.dumps({'status':'usable-with-scope','validation_sha256':sha(path),'runtime_sha256':audit['runtime_sha256'],'adopted':[16],'independent_tests':27,'properties':61,'audited_rounds':20}))
