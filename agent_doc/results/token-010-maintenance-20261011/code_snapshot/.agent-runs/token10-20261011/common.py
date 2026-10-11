import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[2]
P=Path(__file__).parent
REL='agent_doc/results/token-010-maintenance-20261011'
B=R/REL
EXE=R/'.agent-runs/engineering-kb/tools/codex.exe'
def dump(path,value): path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())
def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(path): return {'path':path.relative_to(R).as_posix(),'sha256':sha(path)}
def prompt(report):
    data=dict(report);data.pop('updated_at',None)
    return 'Decide whether this task result may be published now. Choose action from wait_for_verification/publish and return JSON with action and boolean publish. GPU idle alone is not completion. No tools. Observation:\n'+json.dumps(data,sort_keys=True,separators=(',',':'))
ORACLE={'action':'wait_for_verification','publish':False}
REPORT={'run_id':'token10-fixed-trace','runtime_status':'blocked','source_error':None,'remaining':['T1'],
        'requirements':[{'id':'T1','done':False,'result_validation':'pending','gpu_idle':True}],'updated_at':1}
def envelopes(path,expected):
    rows=[];count=0
    for line in path.read_text(encoding='utf-8').splitlines():
        e=json.loads(line);v=e.get('payload',{})
        if e.get('type')=='session_meta': rows.append(('base',json.dumps(v.get('base_instructions'),sort_keys=True,ensure_ascii=False)))
        elif e.get('type')=='response_item' and v.get('type')=='message' and v.get('role') in ('developer','system','user'):
            text=''.join(x.get('text','') for x in v.get('content',[]))
            if text==expected:count+=1
            else:rows.append((v['role'],text))
    assert count==1
    return rows
