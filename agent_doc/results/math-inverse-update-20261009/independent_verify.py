from pathlib import Path
from fractions import Fraction as F
import json,hashlib,subprocess,sys
sys.path.insert(0,str(Path.cwd()))
from agent_runtime.result_validation import _snapshot
R=Path.cwd();B=R/'agent_doc/results/math-inverse-update-20261009'
def save(n,x): (B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
c=json.loads((B/'contract.json').read_text());m,p,pf=_snapshot(R,c);save('independent_snapshot.json',pf)
assert pf['manifest_sha256']=='3dd17e6e2a7908b0f17bba5efa4cf04bef9fef30b86c2a52202f74edd1fd8b3b'
raw=json.loads((B/'raw.json').read_text());ids=json.loads((B/'cases.json').read_text())['cases'];assert [r['id'] for r in raw['records']]==ids and len(set(ids))==10
# Independent determinant/adjugate 2x2 direct inverse and coordinate multiply, no producer elimination or update reuse.
def direct(a,b,c,d):
 det=F(a)*d-F(b)*c
 if not det:raise ValueError('singular')
 return [[F(d)/det,-F(b)/det],[-F(c)/det,F(a)/det]]
def encode(x):
 if isinstance(x,list):return [encode(v) for v in x]
 if isinstance(x,F):return str(x)
 return x
records={r['id']:r['values'] for r in raw['records']};checks=[]
def check(id,key,v):assert records[id][key]==encode(v),(id,key,records[id][key],encode(v));checks.append([id,key])
check('rankone-general','B',[[F(4),F(0)],[F(4),F(1)]]);check('rankone-general','S',[[F(2,3)]])
I=direct(4,0,4,1);check('rankone-general','solution',[[I[0][0]*3+I[0][1]*4],[I[1][0]*3+I[1][1]*4]])
check('zero-update','inverse',direct(2,1,0,3));check('zero-update','S',[[F(1)]])
check('rankdeficient-factors','inverse',direct(3,0,0,1));check('rankdeficient-factors','S',[[F(2),F(1)],[F(1),F(2)]])
assert direct(1,0,0,1)==[[1,0],[0,1]]
try:direct(0,0,0,1)
except ValueError:pass
else:raise AssertionError('singular reference accepted')
assert records['singular-base']=={'B_invertible':True,'decision':'reject A inverse formula'};checks.append(['singular-base','all'])
check('zero-capacitance','B',[[F(0),F(0)],[F(0),F(1)]]);assert records['zero-capacitance']['beta']=='0'
check('spd-add','B',[[F(3),F(0)],[F(0),F(3)]]);check('spd-add','beta',F(3,2))
check('spd-downdate','B',[[F(1),F(0)],[F(0),F(3)]]);check('spd-downdate','a',F(1,2));check('spd-downdate','beta',F(1,2))
check('indefinite-invertible','B',[[F(-3),F(0)],[F(0),F(1)]]);check('indefinite-invertible','a',F(4));assert direct(-3,0,0,1)==[[F(-1,3),0],[0,1]]
check('ridge-stream','C_new',[[F(3),F(2)],[F(2),F(7)]]);check('ridge-stream','h_new',[[F(3)],[F(5)]]);I=direct(3,2,2,7);check('ridge-stream','solution',[[I[0][0]*3+I[0][1]*5],[I[1][0]*3+I[1][1]*5]]);check('ridge-stream','beta',F(17,6))
u=float(2**54); beta=1+u;theta=1/beta;xhat=1-u*theta;true=F(1,2**54+1);r=1-F(2**54+1)*F.from_float(xhat);eta=abs(r)/(F(2**54+1)*abs(F.from_float(xhat))+1)
assert sys.float_info.radix==2 and sys.float_info.mant_dig==53 and xhat==0 and eta==1
for key,val in [('beta_float_hex',beta.hex()),('theta_hex',theta.hex()),('xhat_hex',xhat.hex()),('exact_solution',true),('actual_residual_exact',r),('normalized_residual',eta),('forward_relative_error',abs(F.from_float(xhat)-true)/true),('direct_on_rounded_B_hex',(1/beta).hex())]:check('binary64-cancellation',key,val)
assert F(1)*F(1)==1 and F(2**54+1)*F(1,2**54+1)==1
save('independent_exact.json',{'case_ids':ids,'count':10,'all_reconstructed':True,'checks':checks,'binary64':{'xhat':xhat,'eta':str(eta),'condition_A':'1','condition_true_B':'1'},'method':'Independent 2x2 determinant/adjugate direct inverses, coordinate solves, diagonal SPD signs and scalar exact/binary64 operations; no producer update or elimination reuse'})
# All writes replayed under original __file__ (reads unchanged), filenames replaced only at write sites.
for source,target,repls in [('validate.py','independent_replay_raw.json',[("(B/'raw.json').write_text","(B/'independent_replay_raw.json').write_text")]),('retrieve.py','independent_replay_retrieval.json',[("(BASE/'retrieval.json').write_text","(BASE/'independent_replay_retrieval.json').write_text"),("(BASE/'retrieval_knowledge_use.json').write_text","(BASE/'independent_replay_knowledge_use.json').write_text")])]:
 code=(B/source).read_text()
 for a,b in repls: assert code.count(a)==1;code=code.replace(a,b)
 (B/('independent_redirected_'+source)).write_text(code)
 exec(compile(code,str(B/source),'exec'),{'__file__':str(B/source),'__name__':'__main__'})
replay=json.loads((B/'independent_replay_raw.json').read_text());assert {k:v for k,v in replay.items() if k!='elapsed_seconds'}=={k:v for k,v in raw.items() if k!='elapsed_seconds'}
original=json.loads((B/'retrieval.json').read_text()); rerun=json.loads((B/'independent_replay_retrieval.json').read_text())
def clean(x):
 if isinstance(x,dict): return {k:clean(v) for k,v in x.items() if k not in ('seconds','load_seconds','index_build_seconds')}
 if isinstance(x,list): return [clean(v) for v in x]
 return x
assert clean(original)==clean(rerun)
commands=[['python','-m','unittest','tests.test_knowledge','tests.test_knowledge_index','tests.test_knowledge_math','tests.test_knowledge_handoff','tests.test_knowledge_reuse','-v'],['python','scripts/sync_plugin_references.py','--check']];runs=[]
for i,cmd in enumerate(commands):
 z=subprocess.run(cmd,capture_output=True,text=True);(B/f'independent_command_{i}.log').write_text(z.stdout+z.stderr);runs.append({'command':cmd,'returncode':z.returncode});assert z.returncode==0
assert 'Ran 53 tests' in (B/'independent_command_0.log').read_text();save('independent_commands.json',runs)
# Verify recursive corpus binding without inspecting any holdout content.
bound=set(pf['artifact_hashes']);coverage={}
for corpus in ['knowledge','plugins/research-assistant/skills/model-with-knowledge/assets/knowledge']:
 files={str(x.relative_to(R)) for x in (R/corpus).rglob('*') if x.is_file() and x.name!='learning_state.json'};missing=sorted(files-bound);assert not missing,missing;coverage[corpus]={'files':len(files),'missing':missing,'excluded_live_state':'learning_state.json'}
source_digests=[]
for path,info,key in zip(['/tmp/sm_classic.html','/tmp/sm_recent.pdf'],json.loads((B/'sources.json').read_text()),['html_sha256','pdf_sha256']):
 h=hashlib.sha256(Path(path).read_bytes()).hexdigest();assert h==info[key];source_digests.append({'path':path,'sha256':h})
_,_,after=_snapshot(R,c);assert pf==after
save('independent_integrity.json',{'artifact_hash_count':len(pf['artifact_hashes']),'before_after_equal':True,'recursive_coverage':coverage,'sources':source_digests,'holdout_content_read':False,'failed_attempt_preserved':True})
save('independent_replay_summary.json',{'exact_cases_match':10,'retrieval_records_match':len(rerun['records']),'context':{'status':rerun['context']['status'],'ids':[x['id'] for x in rerun['context']['entries']]},'excluded_replay_comparison':'diagnostic times only','regression_tests':53,'mirror_check':True})
print(json.dumps({'artifacts':len(pf['artifact_hashes']),'cases':10,'retrievals':6,'tests':53,'mirror':True}))
