"""Actual producer protocol; fresh fixtures only, never run from metadata."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import measure_token10 as m
N=10
out=Path(__file__).resolve().parent
original=m.fixture
def fixture(n,home):
 commands=original(n,home)
 if n==3:commands[2]=commands[0][:-1]+['check','missing']
 if n==8:
  registry=json.loads((ROOT/'config/backend_registry.json').read_bytes())
  commands[1]=commands[0]+['--only',registry['backends'][0]['id']]
 return commands
external=[]
if N==9:
 external=[ROOT/p for p in ['config/role_registry.json','config/role_model_policy.json','prompts/orchestrator.md','prompts/planner_main.md','prompts/review_main.md','workflows/dual_main_workflow.md']]
 external += [ROOT/role['skill'] for role in json.loads((ROOT/'config/role_registry.json').read_bytes())['roles']]
 snapshot={p:p.read_bytes() for p in external}
 import zipfile
 with zipfile.ZipFile(out/'role-inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p,raw in snapshot.items():z.writestr(p.relative_to(ROOT).as_posix(),raw)
m.fixture=fixture
m.measure(N,out)
p=out/'manifest.json';value=json.loads(p.read_bytes())
value['execution']['command']=['python -X utf8 '+str(Path(__file__).relative_to(ROOT)).replace(chr(92),'/')]
if N==8:value['artifacts']['inputs'].append(m.ref(ROOT/'config/backend_registry.json'))
if N==9:
 assert all(p.read_bytes()==raw for p,raw in snapshot.items())
 value['artifacts']['inputs'] += [m.ref(out/'role-inputs.zip')]+[m.ref(p) for p in external]
m.write(p,value)
