import json, math, pathlib, subprocess
base=pathlib.Path('/tmp/knowledge-forward-b')
skill=base/'skill'
log=[]
def run(args):
    cmd=['python','scripts/knowledge.py','--root','assets/knowledge']+args
    p=subprocess.run(cmd,cwd=skill,text=True,capture_output=True)
    log.extend(['$ '+' '.join(cmd),'cwd='+str(skill),p.stdout,p.stderr,'exit='+str(p.returncode)])
    if p.returncode: raise RuntimeError(p.stderr)
    return json.loads(p.stdout)
run(['search','worker relabeling permutation equal queues optimization symmetry dynamic transition state merging','--limit','5'])
run(['search','period length gravity units dimensional analysis dimensionless amplitude oscillator','--limit','5'])
entries=[run(['show',k]) for k in ['math.symmetry-quotient','physics.dimensionless']]
refs={r['id']:r for entry in entries for r in entry['knowledge_refs']}
payload={'task_id':'knowledge-forward-b','task_refs':['/tmp/knowledge-forward-b/report.md','/tmp/knowledge-forward-b/evidence.txt'],'knowledge_root':'skill/assets/knowledge','knowledge_refs':list(refs.values())}
(base/'refs.json').write_text(json.dumps(payload,indent=2)+'\n')
run(['check-refs',str(base/'refs.json')])
# Independent task examples; no repository test or rubric loaded.
speeds=[2,1,1]
static_good=max(2/speeds[0],1/speeds[2])
static_bad=max(2/speeds[1],1/speeds[2])
dynamic_a=max(4/speeds[0],1/speeds[1],1/speeds[2])
dynamic_b=max(1/speeds[0],4/speeds[1],1/speeds[2])
assert (static_good,static_bad,dynamic_a,dynamic_b)==(1,2,2,4)
# Simpson integration of the finite-amplitude pendulum integral.
def elliptic_k(k,n=10000):
    h=(math.pi/2)/n
    f=lambda u: 1/math.sqrt(1-k*k*math.sin(u)**2)
    return h/3*(f(0)+f(math.pi/2)+sum((4 if j%2 else 2)*f(j*h) for j in range(1,n)))
l=1; gravity=9.81; theta=math.pi/3
small=2*math.pi*math.sqrt(l/gravity)
finite=4*math.sqrt(l/gravity)*elliptic_k(math.sin(theta/2))
finite_half=4*math.sqrt(l/gravity)*elliptic_k(math.sin(theta/2),5000)
assert abs(finite-finite_half)<1e-10
D=[[0,1,1],[1,0,-2]]; v=[1,-.5,.5]
assert [sum(a*b for a,b in zip(row,v)) for row in D]==[0,0]
checks={'static_makespans_seconds':[static_good,static_bad],'dynamic_makespans_seconds':[dynamic_a,dynamic_b],'dimension_matrix':D,'null_vector':v,'l_over_g_seconds_squared':l/gravity,'sqrt_l_over_g_seconds':math.sqrt(l/gravity),'small_amplitude_period_seconds':small,'sixty_degree_period_seconds':finite,'sixty_degree_relative_increase':finite/small-1,'integration_resolution_difference_seconds':abs(finite-finite_half),'time_unit_change_seconds_to_milliseconds':{'l_over_g_numeric_original':1/9.81,'l_over_g_numeric_new':1/(9.81/1000000),'expected_period_numeric_factor':1000,'actual_l_over_g_numeric_factor':1000000}}
log.extend(['Independent calculations (Python standard library):',json.dumps(checks,indent=2),'Assertions: PASS. Numerical convergence is an empirical check, not a rigorous quadrature error bound.'])
(base/'evidence.txt').write_text('\n'.join(log)+'\n')
(base/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
