import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=Path(__file__).parent
sys.path.insert(0,str(R))
MODE=int(sys.argv[1]);assert MODE==1
REL='agent_doc/results/token-fifty-01-r2-20261012';B=R/REL
PRIVATE=P/'01-r2-private';PRIVATE.mkdir(exist_ok=True)
EXE=Path('C:/Users/WI/Desktop/home_work/AI_LLM/agent/.agent-runs/engineering-kb/tools/codex.exe')
def dump(path,value):path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':path.relative_to(R).as_posix(),'sha256':sha(path)}
NAMES=('baseline','candidate')
ORACLE=read(B/'oracle.json') if (B/'oracle.json').exists() else None
REPORT=read(B/'report.json') if (B/'report.json').exists() else None
