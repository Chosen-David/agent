"""Finite public development checks, not a formal proof or model benchmark."""
import json
import math
import pathlib
import sys
import time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
CFG = json.loads((HERE / 'config.json').read_text())

def softmax(s):
    a = np.exp(s - np.max(s))
    return a / a.sum()

def run():
    start = time.perf_counter()
    rng = np.random.default_rng(CFG['seed'])
    rows = []
    def check(name, actual, expected, tol=CFG['tolerance']):
        a, b = np.asarray(actual), np.asarray(expected)
        err = float(np.linalg.norm(a-b))
        scale = 1 + float(np.linalg.norm(b))
        ok = bool(np.isfinite(a).all() and np.isfinite(b).all() and err <= tol*scale)
        rows.append({'id':name,'error':err,'scale':scale,'tolerance':tol,'pass':ok})
    for t in range(CFG['random_cases']):
        n, d, h = int(rng.integers(1, 10)), 4, 3
        V, W = rng.normal(size=(n,d)), rng.normal(size=(h,d))
        Z = V @ W.T
        s, e = rng.normal(size=n), rng.normal(size=n)*rng.choice([.001,.1,1,4])
        p, b = softmax(s), softmax(s+e)
        delta = b-p
        C = Z @ Z.T
        J = np.diag(p)-np.outer(p,p)
        G = J @ C @ J
        dz = Z.T @ delta
        z = Z.T @ p
        lin = Z.T @ J @ e
        D = max(float(np.linalg.norm(x-y)) for x in Z for y in Z)
        osc = float(np.ptp(e))
        check(f'{t}:gram', dz @ dz, delta @ C @ delta)
        shift = rng.normal(size=h)*100
        check(f'{t}:value-shift',(Z-shift).T @ delta,dz)
        check(f'{t}:gauge',G @ np.ones(n),np.zeros(n))
        check(f'{t}:local-gram',lin @ lin,e @ G @ e)
        dt = CFG['fd_step']
        fd = Z.T @ (softmax(s+dt*e)-softmax(s-dt*e))/(2*dt)
        check(f'{t}:derivative',fd,lin,CFG['fd_tolerance'])
        rem = float(np.linalg.norm(dz-lin))
        upper = D*osc**2/8
        rows.append({'id':f'{t}:remainder','remainder':rem,'upper':upper,'pass':rem<=upper+1e-10})
        # Fixed linear readout: sufficient margin check, not e2e evaluation.
        A = rng.normal(size=(3,h))
        bias = rng.normal(size=3)
        score = A @ z + bias
        c = int(np.argmax(score))
        E = float(np.linalg.norm(dz))
        certified = all(score[c]-score[j] > np.linalg.norm(A[c]-A[j])*E for j in range(3) if j!=c)
        retained = int(np.argmax(A @ (z+dz)+bias))==c
        rows.append({'id':f'{t}:margin','certified':certified,'retained':retained,'pass':not certified or retained})
    # Same probability norm, different output errors.
    V = np.array([0.,1.,100.]); a = np.array([-.01,.01,0.]); b=np.array([-.01,0.,.01])
    check('equal-probability-error',np.linalg.norm(a),np.linalg.norm(b))
    check('output-A',V @ a,.01); check('output-B',V @ b,1.)
    # Common values give zero error even if probability vectors differ.
    check('constant-values',np.array([7.,7.,7.]) @ a,0.)
    # Cross-domain: normalized mass mixture -> fixed linear sensor concentration.
    check('concentration-sensor',2*V @ a,.02)
    # Prism stationary-content exact pooling zero and changing-content counterexample.
    B=8; theta=2*math.pi/B; phases=np.exp(1j*np.arange(B)*theta)
    check('pool-zero',abs(phases.mean()),0.)
    check('finite-temperature-cannot-recover',abs(phases.mean()/0.1),0.)
    check('changing-content',abs((np.conjugate(phases)*phases).mean()),1.)
    # Explicit premise decisions, not a model refusal experiment.
    rows.append({'id':'hardmask-local-refused','pass':True,'reason':'-inf logits not finite; exact probability Gram still valid'})
    rows.append({'id':'nonlinear-mixture-refused','pass':True,'reason':'reaction map is not the fixed linear Z operator'})
    return {'cases':rows,'count':len(rows),'passed':sum(x['pass'] for x in rows),'duration_seconds':time.perf_counter()-start,'seed':CFG['seed'],'scope':'CPU finite development checks; premise refusals are explicit author checks, not LLM evaluation'}

if __name__=='__main__':
    out=run()
    target=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'raw.json'
    target.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'}))
    raise SystemExit(0 if out['count']==out['passed'] else 1)
