from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np
D=Path(__file__).resolve().parent; R=D.parents[3]; original=D.parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((original/'manifest.json').read_text()); hashes={}
for group,items in manifest['artifacts'].items():
 for item in items:
  p=R/item['path']; assert h(p)==item['sha256'],item['path']; hashes[item['path']]=h(p)
assert json.loads((original/'raw.json').read_text())==json.loads((D/'rerun/raw.json').read_text())
# Enumerate a nonzero-mean unequal-probability rectangular product law without producer atom-generation.
Q=np.array([[1.,2.],[-2.,1.],[3.,-1.]]); pq=np.array([.2,.3,.5])
K=np.array([[2.,1.,0.],[0.,1.,3.],[1.,-2.,1.],[2.,2.,2.]]); pk=np.array([.1,.2,.3,.4])
Sq=Q.T@np.diag(pq)@Q; Sk=K.T@np.diag(pk)@K; H=np.array([[1.,-2.,.3],[.7,.2,-1.]])
# Cholesky whitening instead of producer symmetric eigensquare root.
L=np.linalg.cholesky(Sq); T=np.linalg.cholesky(Sk); C=L.T@H@T
u,s,v=np.linalg.svd(C,full_matrices=False); cases=[]
for r in range(3):
 Z=(u[:,:r]*s[:r])@v[:r]; M=np.linalg.solve(L.T,Z)@np.linalg.solve(T,np.eye(3)); E=H-M
 risk=sum(pq[i]*pk[j]*(Q[i]@E@K[j])**2 for i in range(3) for j in range(4))
 trace=np.trace(E@Sk@E.T@Sq); tail=sum(s[r:]**2)
 assert np.allclose([risk,trace],[tail,tail],atol=1e-10)
 cases.append({'shape':[2,3],'rank':r,'risk':risk,'trace':float(trace),'tail':float(tail)})
retrieval=[]
idx=D/'knowledge.sqlite'
def cli(args):
 p=subprocess.run([sys.executable,'-m','agent_runtime.knowledge','--root','knowledge',*args],cwd=R,capture_output=True,text=True); assert p.returncode==0,p.stderr; return json.loads(p.stdout)
cli(['index','--db',str(idx)])
usage=json.loads((original/'knowledge-usage.json').read_text())
for x in usage['retrieval']:
 args=['search',x['query'],'--limit','3']
 if x['backend']=='sqlite': args+=['--index',str(idx)]
 out=cli(args); ids=[z['id'] for z in out['results']]; assert ids==x['ids']; retrieval.append({**x,'actual_ids':ids})
refs=cli(['check-refs',str(original/'knowledge-usage.json')]);assert refs['valid']
show=cli(['show','math.weighted-bilinear-low-rank']); assert {x['id'] for x in show['knowledge_refs']}=={'math.low-rank-svd','math.weighted-bilinear-low-rank'}
import tiktoken
encoded=json.dumps(show,ensure_ascii=False); tokens=len(tiktoken.get_encoding('cl100k_base').encode(encoded)); assert tokens==2914
record={'manifest_sha256':h(original/'manifest.json'),'artifact_hashes':hashes,'raw_byte_identical':h(original/'raw.json')==h(D/'rerun/raw.json'),'rectangular_nonzero_mean_reference':cases,'retrieval':retrieval,'refs':refs,'encoded_tokens':tokens,'encoder':'cl100k_base','limitations':['local encoding only; no host cost or model A/B','public CPU fixtures only','no production input validation or extreme ill-conditioning certification']}
(D/'cross-check.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n'); print(json.dumps({'hashes':len(hashes),'raw_identical':record['raw_byte_identical'],'retrieval_checks':len(retrieval),'additional_reference_cases':len(cases),'tokens':tokens}))
