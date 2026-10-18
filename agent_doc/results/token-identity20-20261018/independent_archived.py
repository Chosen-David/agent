import hashlib,json,pathlib,subprocess,sys
sys.path.insert(0,str(pathlib.Path.cwd()))
from agent_runtime.token_usage import short_appserver_usage
from agent_runtime.turn_usage import current_turn_usage
parsers=[]
for path,name,current in [('agent_runtime/token_usage.py','short_appserver_usage',short_appserver_usage),('agent_runtime/turn_usage.py','current_turn_usage',current_turn_usage)]:
    ns={};exec(subprocess.check_output(['git','show','HEAD:'+path]),ns);parsers.append((name,ns[name],current))
results=[]
for variant in ['baseline','candidate']:
    p=pathlib.Path('agent_doc/results/token-fifty-06-20261012')/(variant+'.rpc.jsonl')
    events=[json.loads(line) for line in p.read_text().splitlines()]
    starts=[e['params'] for e in events if e.get('method')=='turn/started']
    assert len(starts)==1
    thread=starts[0]['threadId'];turn=starts[0]['turn']['id']
    for name,old,new in parsers:
        a=old(events,thread,turn);b=new(events,thread,turn);assert a==b
        results.append({'trace':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'parser':name,'complete_output_equal':True,'total_tokens':b['total_tokens']})
print(json.dumps(results,indent=2))
