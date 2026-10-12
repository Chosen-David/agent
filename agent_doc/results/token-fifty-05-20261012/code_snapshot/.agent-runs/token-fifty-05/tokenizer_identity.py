from pathlib import Path
import hashlib,json,sys,os,importlib.metadata
R=Path(__file__).resolve().parents[2];P=Path(__file__).parent
V=R/'.agent-runs/token-fifty-tools/tokenizer';C=R/'.agent-runs/token-fifty-tools/bpe-cache'
sys.path.insert(0,str(V));os.environ['TIKTOKEN_CACHE_DIR']=str(C)
import tiktoken
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def capture():
 enc=tiktoken.get_encoding('o200k_base')
 files=[{'path':f.relative_to(R).as_posix(),'sha256':digest(f),'bytes':f.stat().st_size} for f in sorted(V.rglob('*')) if f.is_file() and '__pycache__' not in f.parts and f.suffix!='.pyc']
 caches=[{'path':f.relative_to(R).as_posix(),'sha256':digest(f),'bytes':f.stat().st_size} for f in sorted(C.glob('*')) if f.is_file()]
 versions={d.metadata['Name']:d.version for d in importlib.metadata.distributions(path=[str(V)])}
 return {'schema_version':'external-tokenizer-identity/v1','encoding':enc.name,'versions':versions,'files':files,'cache_files':caches,'package_root':str(V),'cache_root':str(C),'source':'https://github.com/openai/tiktoken/tree/0.12.0','scope':'Explicit local packet tokenizer only; no model mapping/full-request or billing equivalence. Files kept in task-private installation; public hashes permit independent binding/reinstall validation. Python bytecode excluded; actual source/binary/data files bound.','reproduce':'Python3.12 Windows amd64: pip install --target TASK_PRIVATE_DIR tiktoken==0.12.0 with all versions pinned as recorded; set TIKTOKEN_CACHE_DIR to task-private cache; get_encoding(o200k_base). Compare hashes; changed dependency wheel/data requires new validation.'}
def verify(report):
 for row in report['files']+report['cache_files']:assert digest(R/row['path'])==row['sha256'],row['path']
 assert capture()==report
 return True
if __name__=='__main__':
 report=capture();out=R/'agent_doc/results/token-fifty-05-20261012/tokenizer-identity.json'
 assert not out.exists();out.write_bytes((json.dumps(report,indent=2)+'\n').encode())
 print(json.dumps({'files':len(report['files']),'cache_files':len(report['cache_files']),'identity_sha256':digest(out)}))
