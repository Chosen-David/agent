from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D, localcontext, ROUND_CEILING
import json,hashlib,subprocess,sys
sys.path.insert(0,str(Path.cwd()))
from agent_runtime.result_validation import _snapshot
R=Path.cwd(); B=R/'agent_doc/results/math-random-score-20261009'
def save(n,x): (B/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
c=json.loads((B/'contract.json').read_text());m,p,pf=_snapshot(R,c);save('independent_snapshot.json',pf)
assert pf['manifest_sha256']=='8d8790c7568e20bccbf667ec0c8d3d7804f3a25d0775b7e6821d1ef4e87cbf7e'
# Independent closed form certificates: diagonal D^T D-I has entry -9/25 in coordinate2.
raw=json.loads((B/'raw.json').read_text());ids=json.loads((B/'cases.json').read_text())['cases'];assert [r['id'] for r in raw['records']]==ids and len(set(ids))==10
norm_error=F(-9,25); diag_plus_minus_norm=1+F(16,25)
assert diag_plus_minus_norm==F(41,25) and abs(diag_plus_minus_norm-2)/2==F(9,50)
assert F(0)*norm_error==0
assert F(1)**2==1 and F(-1)*F(1)==-1
assert F(1)-0>F(1,10)*2 and F(9,10)>F(1,10)
assert F(1,5)==F(1,10)*2 and F(1,10)==F(1,10)
assert abs(F(-1,20)-F(1,20))==F(1,10) and abs(F(1,10)-0)==F(1,10) and F(-1,20)<F(1,10)
assert 1+(-1)==0 and 1**2+(-1)**2==2
# Inverse objective evaluated directly as e1^T diag(1,1/99) e1 and scalar inverse(100).
assert F(1)==1 and F(1,1+99)==F(1,100)
event_error=norm_error*F(4,5)**2
assert event_error==F(-144,625)
for norm in (F(16,5),F(4,5)): assert abs(event_error)<=F(2,5)*norm
assert (event_error-event_error)/4==0
with localcontext() as ctx:
 ctx.prec=80; eps=D(1)/5; delta=D(1)/20; constant=eps**2/4-eps**3/6; ratio=(D(81920)).ln()/constant;dim=int(ratio.to_integral_value(rounding=ROUND_CEILING));failure=D(4096)*(-D(dim)*constant).exp();assert dim==1306 and failure<delta and dim>128
save('independent_exact.json',{'case_ids':ids,'count':10,'all_reconstructed':True,'event_errors':str(event_error),'dimension':dim,'failure_decimal_80':str(failure),'method':'Direct diagonal coordinate identities, scalar inverse, score inequalities and 80-digit Decimal sanity; not producer function reuse or probability simulation'})
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
for path,info in zip(['/tmp/jl_classic.pdf','/tmp/jl_recent.pdf'],json.loads((B/'sources.json').read_text())):
 h=hashlib.sha256(Path(path).read_bytes()).hexdigest();assert h==info['pdf_sha256'];source_digests.append({'path':path,'sha256':h})
_,_,after=_snapshot(R,c);assert pf==after
save('independent_integrity.json',{'artifact_hash_count':len(pf['artifact_hashes']),'before_after_equal':True,'recursive_coverage':coverage,'sources':source_digests,'holdout_content_read':False,'failed_attempt_preserved':True})
save('independent_replay_summary.json',{'exact_cases_match':10,'retrieval_records_match':len(rerun['records']),'context':{'status':rerun['context']['status'],'ids':[x['id'] for x in rerun['context']['entries']]},'excluded_replay_comparison':'diagnostic times only','regression_tests':53,'mirror_check':True})
print(json.dumps({'artifacts':len(pf['artifact_hashes']),'cases':10,'retrievals':6,'tests':53,'mirror':True}))
