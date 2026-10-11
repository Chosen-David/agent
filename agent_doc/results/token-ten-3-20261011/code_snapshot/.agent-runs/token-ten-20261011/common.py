import hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2];P=Path(__file__).parent
sys.path.insert(0,str(R))
MODE=int(sys.argv[1]);assert MODE in range(1,11)
REL=f'agent_doc/results/token-ten-{MODE}{"-r4" if MODE==1 else ""}-20261011';B=R/REL
PRIVATE=P/(str(MODE)+("-r4" if MODE==1 else ""));PRIVATE.mkdir(exist_ok=True)
EXE=R/'.agent-runs/engineering-kb/tools/codex.exe'
def dump(path,value):path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path):return {'path':path.relative_to(R).as_posix(),'sha256':sha(path)}
NAMES=('baseline','candidate')
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

def required_source_paths(case):
 import ast,importlib.util
 seeds=list(case.SOURCES)+['agent_runtime/token_usage.py','agent_runtime/result_validation.py','agent_runtime/result_store.py','agent_runtime/project_docs.py','agent_runtime/legacy_result_paths.py']+[str((P/n).relative_to(R).as_posix()) for n in ('common.py','native.py','freeze.py','bind.py','verify.py','independent_checks.py',f'case_{MODE}.py')]
 for name in case.TESTS:
  parts=name.split('.')
  while parts and not (R/('/'.join(parts)+'.py')).is_file():parts.pop()
  assert parts, 'test module source required'
  seeds.append('/'.join(parts)+'.py')
 needed=set(seeds);pending=list(seeds)
 while pending:
  path=pending.pop();tree=ast.parse((R/path).read_bytes())
  parts=Path(path).parts
  for ancestor in Path(path).parents:
   candidate=(ancestor/'__init__.py').as_posix()
   if (R/candidate).is_file() and candidate not in needed:needed.add(candidate);pending.append(candidate)
  if True:
   package='.'.join(parts[:-1]) if parts[0] in ('agent_runtime','scripts','tests') else ''
   for node in ast.walk(tree):
    names=[]
    if isinstance(node,ast.Import):names=[a.name for a in node.names]
    elif isinstance(node,ast.ImportFrom):
     if node.level and not package:continue  # isolated bundle; explicitly listed sibling sources
     name=importlib.util.resolve_name('.'*node.level+(node.module or ''),package) if node.level else (node.module or '')
     names=[name]+[name+'.'+a.name for a in node.names if a.name!='*']
    for name in names:
     if not name.startswith(('agent_runtime.','scripts.','tests.')):continue
     candidate=name.replace('.','/')+'.py'
     if (R/candidate).is_file() and candidate not in needed:needed.add(candidate);pending.append(candidate)
 return sorted(needed)
