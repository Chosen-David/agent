import hashlib,itertools,json,sys,types
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT))
def load(name):
 m=types.ModuleType('agent_runtime._control_'+name);m.__package__='agent_runtime';exec(compile((P/name).read_bytes(),name,'exec'),m.__dict__);o=types.ModuleType('agent_runtime._control_observer');o.__package__='agent_runtime';exec(compile((P/(Path(name).stem+'-observer.py')).read_bytes(),name+'-observer','exec'),o.__dict__);m.read_bound=o.read_bound;return m
baseline=load('baseline.py');candidate=load('candidate.py')
texts=['','x','x\n'*10,'a\r\nERROR\r\nlast','α\u2028ERROR\nβ\r','ERROR\n'*300,'x\n'*1100]
rows=[]
for text,encoding,budget,needles in itertools.product(texts,['lines','chunks','runs'],[700,1000,20000],[[],['ERROR'],['x','ERROR']]):
 (P/'control.log').write_bytes(text.encode());sha=hashlib.sha256(text.encode()).hexdigest()
 def call(module):
  try:return {'ok':module.log_view(P,'control.log',sha,needles=needles,head=2,tail=2,context=1,max_chars=budget,encoding=encoding)}
  except ValueError as e:return {'error':str(e)}
 a,b=call(baseline),call(candidate)
 if a!=b:raise AssertionError((text,encoding,budget,needles,a,b))
 rows.append({'input_sha256':sha,'encoding':encoding,'budget':budget,'needles':needles,'output_sha256':hashlib.sha256(json.dumps(a,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'status':'ok' if 'ok'in a else 'rejected'})
(P/'controls.json').write_text(json.dumps(rows,indent=2)+'\n');print(len(rows),'exact baseline/candidate controls matched')
