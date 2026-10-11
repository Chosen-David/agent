import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=Path(__file__).parent
sys.path.insert(0,str(R))
MODE=int(sys.argv[1]);assert MODE in range(1,6)
REL=f'agent_doc/results/token-five-{MODE}{"-fixed" if MODE==2 else ""}-20261011';B=R/REL
PRIVATE=P/(str(MODE)+('-fixed' if MODE==2 else ''));PRIVATE.mkdir(exist_ok=True)
EXE=R/'.agent-runs/engineering-kb/tools/codex.exe'
def dump(path,value):path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':path.relative_to(R).as_posix(),'sha256':sha(path)}
NAMES=('baseline1','baseline2','candidate1') if MODE==1 else ('baseline','candidate')
ORACLE=read(B/'oracle.json') if (B/'oracle.json').exists() else None
REPORT=read(B/'report.json') if (B/'report.json').exists() else None
def envelopes(path,expected):
 rows=[];count=0
 for line in path.read_text(encoding='utf-8').splitlines():
  e=json.loads(line);v=e.get('payload',{})
  if e.get('type')=='session_meta':rows.append(('base',json.dumps(v.get('base_instructions'),sort_keys=True,ensure_ascii=False)))
  elif e.get('type')=='response_item' and v.get('type')=='message' and v.get('role') in ('developer','system','user'):
   text=''.join(x.get('text','') for x in v.get('content',[]))
   if text==expected:count+=1
   else:rows.append((v['role'],text))
 assert count==1
 return rows
