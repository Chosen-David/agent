"""Actual producer protocol; fresh fixtures only, never run from metadata."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import measure_token10 as m
N=5
out=Path(__file__).resolve().parent
original=m.fixture
def fixture(n,home):
 commands=original(n,home)
 if n==3:commands[2]=commands[0][:-1]+['check','missing']
 if n==8:
  registry=json.loads((ROOT/'config/backend_registry.json').read_bytes())
  commands[1]=commands[0]+['--only',registry['backends'][0]['id']]
 return commands
m.fixture=fixture
m.measure(N,out)
p=out/'manifest.json';value=json.loads(p.read_bytes())
value['execution']['command']=['python -X utf8 '+str(Path(__file__).relative_to(ROOT)).replace(chr(92),'/')]
if N==8:value['artifacts']['inputs'].append(m.ref(ROOT/'config/backend_registry.json'))
m.write(p,value)
