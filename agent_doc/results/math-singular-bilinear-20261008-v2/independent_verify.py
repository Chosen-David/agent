"""Independent public finite checks; canonical producer files are read only."""
import json, itertools, time, importlib.util, tempfile, hashlib, sys
from pathlib import Path
from fractions import Fraction as F
import numpy as np
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT))

def risk(qs,qp,ks,kp,E):
    return sum((pq*pk*sum((qi*E[i][j]*kj for i,qi in enumerate(q) for j,kj in enumerate(k)),F())**2 for q,pq in zip(qs,qp) for k,pk in zip(ks,kp)),F())
def second(vs,ps):
    return [[sum((p*v[i]*v[j] for v,p in zip(vs,ps)),F()) for j in range(len(vs[0]))] for i in range(len(vs[0]))]
def rank(A):
    A=[[F(x) for x in row] for row in A];h=0
    for j in range(len(A[0])):
        pivot=next((i for i in range(h,len(A)) if A[i][j]),None)
        if pivot is None:continue
        A[h],A[pivot]=A[pivot],A[h];v=A[h][j];A[h]=[x/v for x in A[h]]
        for i in range(len(A)):
            if i!=h:
                c=A[i][j];A[i]=[x-c*y for x,y in zip(A[i],A[h])]
        h+=1
        if h==len(A):break
    return h
def states(am):return [tuple(F(a)*s for a,s in zip(am,z)) for z in itertools.product([-1,1],repeat=len(am))]
def fracmat(A):return [[F(x) for x in row] for row in A]
def main():
    t=time.perf_counter();raw=json.loads((BASE/'raw.json').read_text());res={'scope':'public development checks only','errors':{},'exact':[],'float':[]}
    spec=importlib.util.spec_from_file_location('producer_readonly',BASE/'validate.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
    # Independently recompute every exact output from its recorded inputs.
    for c in raw['exact_cases']:
        qs,ks=states(c['q_amplitudes']),states(c['k_amplitudes']);qp=[F(1,len(qs))]*len(qs);kp=[F(1,len(ks))]*len(ks)
        H,M=fracmat(c['H']),fracmat(c['M']);E=[[h-m for h,m in zip(hr,mr)] for hr,mr in zip(H,M)]
        v=risk(qs,qp,ks,kp,E);S,T=second(qs,qp),second(ks,kp)
        tr=sum((E[i][j]*E[a][b]*S[i][a]*T[j][b] for i,a,j,b in itertools.product(range(3),repeat=4)),F())
        weights=sorted((F(c['q_amplitudes'][i]**2*c['k_amplitudes'][i]**2)*H[i][i]**2 for i in range(3)),reverse=True)
        target=sum(weights[c['r']:],F());assert v==tr==target==F(c['exact_risk'])==F(c['tail_target']);assert rank(M)<=c['r']
        trial=[[H[i][j]-F([1,-2,3][i]*[2,1,-1][j]) for j in range(3)] for i in range(3)]
        trialv=risk(qs,qp,ks,kp,trial);assert trialv==F(c['trial_risk'])
        res['exact'].append({'id':c['id'],'enumerated_risk':str(v),'trace':str(tr),'tail':str(target),'rank':rank(M),'trial':str(trialv)})
    maxima={k:0. for k in ['risk_tail_scaled','lift_scaled','least_squares_lift_scaled','full_tail_scaled','norm_decomposition_scaled','solver_reproduction_scaled','support_scaled','mp_scaled']}
    for c in raw['float_cases']:
        U,a,V,b,H,M,Cr,N=[np.array(c[x],float) for x in ['U','a','V','b','H','M','Cr','N']];m,n=H.shape
        # JSON loses zero-column matrix shape; restore from recorded ambient dimensions.
        U=U.reshape(m,len(a));V=V.reshape(n,len(b));Cr=Cr.reshape(len(a),len(b))
        L=(U*a)@U.T;R=(V*b)@V.T;P=U@U.T;Q=V@V.T;fullC=L@H@R;fullCr=U@Cr@V.T
        qs=np.array([U@(a*np.array(z)) for z in itertools.product([-1,1],repeat=len(a))]);ks=np.array([V@(b*np.array(z)) for z in itertools.product([-1,1],repeat=len(b))]);direct=float(np.mean((qs@(H-M)@ks.T)**2))
        tail=float(np.sum(np.linalg.svd(fullC,compute_uv=False)[c['r']:]**2))
        # General linear operator least-squares reference, not the producer's support division path.
        op=np.kron(R.T,L);ls=np.linalg.lstsq(op,fullCr.reshape(-1,order='F'),rcond=1e-14)[0].reshape((m,n),order='F')
        out=p.solve(U,a,V,b,H,c['r']);Li=np.linalg.pinv(L);Ri=np.linalg.pinv(R)
        vals={'risk_tail_scaled':abs(direct-c['tail'])/max(1.,c['tail']),'lift_scaled':np.linalg.norm(L@M@R-fullCr)/max(1.,np.linalg.norm(fullC)),'least_squares_lift_scaled':np.linalg.norm(ls-M)/max(1.,np.linalg.norm(M)),'full_tail_scaled':abs(tail-c['tail'])/max(1.,c['tail']),'norm_decomposition_scaled':abs(np.linalg.norm(M+N)**2-np.linalg.norm(M)**2-np.linalg.norm(N)**2)/max(1.,np.linalg.norm(M)**2+np.linalg.norm(N)**2),'solver_reproduction_scaled':np.linalg.norm(out['M']-M)/max(1.,np.linalg.norm(M)),'support_scaled':np.linalg.norm(P@M@Q-M)/max(1.,np.linalg.norm(M)),'mp_scaled':max(np.linalg.norm(L@Li@L-L),np.linalg.norm(Li@L@Li-Li),np.linalg.norm((L@Li).T-L@Li),np.linalg.norm((Li@L).T-Li@L),np.linalg.norm(R@Ri@R-R),np.linalg.norm(Ri@R@Ri-Ri),np.linalg.norm((R@Ri).T-R@Ri),np.linalg.norm((Ri@R).T-Ri@R))/max(1.,np.linalg.norm(L),np.linalg.norm(R),np.linalg.norm(Li),np.linalg.norm(Ri))}
        for k,v in vals.items():assert np.isfinite(v) and v<=1e-9,(c['id'],k,v);maxima[k]=max(maxima[k],float(v))
        rr=int(np.linalg.matrix_rank(M,tol=1e-9));assert rr<=c['r'];res['float'].append({'id':c['id'],'direct_product_risk':direct,'rank':rr,'errors':{k:float(v) for k,v in vals.items()}})
    res['errors']=maxima
    # A noncentral, asymmetric, non-coordinate, nonuniform rational distribution.
    qs=[(F(1),F(2),F(0)),(F(3),F(-1),F(0)),(F(0),F(4),F(0))];qp=[F(1,2),F(1,3),F(1,6)]
    ks=[(F(2),F(0)),(F(-1),F(3))];kp=[F(2,5),F(3,5)];E=[[F(2),F(-1)],[F(3),F(4)],[F(-2),F(1)]]
    v=risk(qs,qp,ks,kp,E);S,T=second(qs,qp),second(ks,kp);tr=sum((E[i][j]*E[h][l]*S[i][h]*T[j][l] for i,h in itertools.product(range(3),repeat=2) for j,l in itertools.product(range(2),repeat=2)),F());assert v==tr
    res['noncentral_fresh']={'q':[[str(x) for x in q] for q in qs],'q_p':[str(x) for x in qp],'k':[[str(x) for x in k] for k in ks],'k_p':[str(x) for x in kp],'E':[[str(x) for x in row] for row in E],'risk':str(v),'trace':str(tr)}
    # Recompute misuse values from actual distributions, including scalar correlated joint law.
    paired=sum((pr*x**4 for x,pr in zip([F(-1),F(0),F(1)],[F(1,4),F(1,2),F(1,4)])),F());proxy=sum((pr*x*x for x,pr in zip([F(-1),F(0),F(1)],[F(1,4),F(1,2),F(1,4)])),F())**2
    centered=risk([(F(2),)],[F(1)],[(F(3),)],[F(1)],[[F(1)]]);tiny=risk([(F(0),F(1,10**6)),(F(0),F(-1,10**6))],[F(1,2)]*2,[(F(1),F(0)),(F(-1),F(0))],[F(1,2)]*2,[[F(0),F(0)],[F(10**6),F(0)]])
    assert (paired,proxy,centered,tiny)==(F(1,2),F(1,4),F(36),F(1));ce=raw['counterexamples'];assert paired==F(ce['paired_true']) and proxy==F(ce['independent_proxy']) and centered==F(ce['noncentral_true']) and tiny==F(ce['tiny_eigenvalue_discarded_true_risk'])
    sensor=raw['sensor'];sv=risk([tuple(F(x) for x in q) for q in sensor['q']],[F(1,2)]*2,[tuple(F(x) for x in k) for k in sensor['k']],[F(1,2)]*2,[[F(h)-F(m) for h,m in zip(hr,mr)] for hr,mr in zip(sensor['H'],sensor['M'])]);assert sv==0
    assert sum((F(x)**2 for row in sensor['M'] for x in row),F())==F(2,25);assert sum((F(x)**2 for row in sensor['M_plus_N'] for x in row),F())==F(1252,25)
    # Invisible addition is not automatically feasible; tied targets can have unequal lift norms.
    L=np.diag([1.,0.]);R=L.copy();M=np.diag([1.,0.]);N=np.diag([0.,1.]);assert np.linalg.norm(L@N@R)==0 and np.linalg.matrix_rank(M+N)==2
    Lt=np.diag([1.,2.]);Rt=np.eye(2);Ht=np.diag([1.,.5]);C1=np.diag([1.,0.]);C2=np.diag([0.,1.]);T1=np.linalg.inv(Lt)@C1;T2=np.linalg.inv(Lt)@C2;assert np.linalg.norm(Lt@Ht-C1)**2==np.linalg.norm(Lt@Ht-C2)**2==1 and np.linalg.norm(T1)**2==1 and np.linalg.norm(T2)**2==.25
    ridge=p.solve(np.eye(2),[2**.5,1],np.eye(2),[2**.5,1],np.diag([1.,10.]),1)['M'];original=float(np.linalg.norm(np.diag([1.,0.])@(np.diag([1.,10.])-ridge)@np.diag([1.,0.]))**2);assert original==1
    res['counterexamples']={'paired':str(paired),'product_proxy':str(proxy),'centered_true':str(centered),'tiny_true':str(tiny),'ridge_original_risk':original,'invisible_addition_rank':2,'rank_budget':1,'tied_targets_risks':[1.,1.],'tied_lift_norm_squared':[1.,.25],'sensor_risk':str(sv),'sensor_norm_squared':['2/25','1252/25']}
    args=[np.eye(2),[1,1],np.eye(2),[1,1],np.eye(2),1];guards=[]
    tests=[('negative-rank',5,-1),('fractional-rank',5,.5),('bool-rank',5,True),('excess-rank',5,3),('negative-scale',1,[1,-1]),('zero-scale',1,[1,0]),('nonorthogonal',0,np.ones((2,2))),('nonfinite',4,np.array([[np.inf,0],[0,1]])),('shape',1,[1]),('complex',4,np.eye(2,dtype=complex)),('vector-H',4,[1,2])]
    for name,idx,val in tests:
        case=args.copy();case[idx]=val
        try:p.solve(*case)
        except ValueError as e:guards.append({'id':name,'exception':str(e)})
        else:raise AssertionError(name)
    res['guards']=guards
    from agent_runtime.knowledge import KnowledgeStore
    from agent_runtime.knowledge_index import build_index,indexed_search
    s=KnowledgeStore(ROOT/'knowledge');cfg=json.loads((BASE/'retrieval_protocol.json').read_text());obs=json.loads((BASE/'retrieval.json').read_text());assert s.snapshot==obs['snapshot'];s.check_refs(json.loads((BASE/'knowledge_use.json').read_text())['knowledge_refs']);records=[]
    with tempfile.TemporaryDirectory() as td:
        db=Path(td)/'independent.sqlite';build_index(s,db)
        for backend in cfg['required_backends']:
            for i,q in enumerate(cfg['queries']):
                out=s.search(q,domain=cfg['domain'],limit=cfg['cutoff']) if backend=='files-lexical-v1' else indexed_search(s,db,q,domain=cfg['domain'],limit=cfg['cutoff']);ids=[x['id'] for x in out['results']];record=next(x for x in obs['records'] if x['backend']==backend and x['case']=='R'+str(i+1));assert ids==record['actual'] and cfg['expected_id'] in ids;records.append({'backend':backend,'case':'R'+str(i+1),'ids':ids})
    context=s.context(s.search(cfg['queries'][0],domain=cfg['domain'],limit=1),**cfg['context']);assert context==obs['context'];res['retrieval']={'snapshot':s.snapshot,'records':records,'context_status':context['status'],'context_ids':[e['id'] for e in context['entries']],'used_chars':context['budget']['used_chars']}
    res['diagnostic_seconds']=time.perf_counter()-t;res['input_hashes']={x:hashlib.sha256((BASE/x).read_bytes()).hexdigest() for x in ['validate.py','raw.json','retrieve.py','retrieval.json','retrieval_protocol.json','knowledge_use.json']}
    (BASE/'independent_observations.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'exact':len(res['exact']),'float':len(res['float']),'guards':len(guards),'queries':len(records),'errors':maxima,'diagnostic_seconds':res['diagnostic_seconds']}))
if __name__=='__main__':main()
