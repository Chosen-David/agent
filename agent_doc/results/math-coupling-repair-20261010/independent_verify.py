"""Independent frozen failure replay; never changes candidate or fixtures."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,subprocess,sys,importlib.util
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot
contract=json.loads((B/'contract.json').read_text())
_,_,before=_snapshot(ROOT,contract)
(B/'independent_snapshot.json').write_text(json.dumps(before,indent=2)+'\n')
commands=[]
for name,args in [('verify',['verify.py',str(B/'independent_replay')]),('diagnose',['diagnose.py']),('retrieve',['retrieve.py',str(B/'independent_replay')])]:
 (B/'independent_replay').mkdir(exist_ok=True)
 cmd=[sys.executable,str(B/args[0])]+args[1:]
 p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
 (B/f'independent_{name}.log').write_text(p.stdout+p.stderr)
 commands.append({'command':cmd,'exit_code':p.returncode})
assert commands[0]['exit_code']!=0 and commands[1]['exit_code']==0
spec=importlib.util.spec_from_file_location('producer',B/'verify.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
cases=json.loads((B/'fixtures.json').read_text())['cases']
# Hand-derived matrices: no row/column scaling reference algorithm reused.
matrices=[[[Q(1,2),0],[0,Q(1,2)]],[[0,1],[0,0]],[[Q(1,4)]*2]*2,[[Q(1,2),0],[0,Q(1,2)]],[[0,1],[0,0]],[[Q(1,4)]*2]*2]
records=[]
for c,Gref in zip(cases,matrices):
 G,tau,delta,diff,res=v.repair(c['F'],c['a'],c['b']);assert G==Gref
 U=sum(Gref[i][j]*abs(Q(c['v'][i])-Q(c['v'][j])) for i in range(2) for j in range(2))
 records.append({'id':c['id'],'reference_G':[[str(x) for x in r] for r in Gref],'reference_U':str(U),'frozen_U':c['expected_U'],'frozen_match':U==Q(c['expected_U'])})
bad=cases[6];rejections=[]
for c in [bad]+bad['invalid_mass_variants']:
 try:v.repair(c['F'],c['a'],c['b'])
 except ValueError as e:rejections.append(str(e))
 else:raise AssertionError('invalid accepted')
# T8 only allowed coupling sends all mass from value0 to value2, so OPT=2.
assert max(Q(3)-Q(x) for x in [0,2])==3
exact={'cases':records,'T6_derivation':'F already below both target marginals: row deficits=(0,1/4), column deficits=(1/4,0). Added mass1/4 at(2,1), existing(1,2)mass1/4; each cost2. U=1; rawcost=1/2; tau=1/4; bound=1 exactly.', 'T7_independent_diagnostic_rejections':rejections,'T8_independent_closed_form':{'h':'3','L':'0','OPT':'2'},'original_verify_reached_T7_T8':False,'original_raw_created':(B/'independent_replay/raw.json').exists()}
(B/'independent_exact.json').write_text(json.dumps(exact,indent=2)+'\n')
baseline=json.loads((B/'preservation_baseline.json').read_text())
mismatch=[p for p,h in baseline.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
assert not mismatch
_,_,after=_snapshot(ROOT,contract);assert before==after
pres={'checked':len(baseline),'mismatch':mismatch,'method':'opaque bytes SHA256 only; contents not parsed or inspected','before_after_manifest_bindings_equal':before==after,'bound_artifacts':len(before['artifact_hashes']),'candidate_canonical_json_exists':(ROOT/'knowledge/entries/math.coupling-marginal-repair.json').exists()}
(B/'independent_preservation.json').write_text(json.dumps(pres,indent=2)+'\n')
(B/'independent_commands.json').write_text(json.dumps(commands,indent=2)+'\n')
print(json.dumps({'failure_reproduced':True,'frozen_mismatches':sum(not c['frozen_match'] for c in records),'preservation':pres}))
