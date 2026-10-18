"""Independent bounded API checks; no worktree mutation, model calls or timings."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import types

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'agent_runtime/token_usage.py').is_file())
SHA='91d7545b75b090a9eea977af185a6f8d13b5a736'
base_source=subprocess.check_output(['git','show',SHA+':agent_runtime/token_usage.py'],cwd=ROOT)
new_source=(ROOT/'agent_runtime/token_usage.py').read_bytes()
def load(source,name):
    m=types.ModuleType(name)
    exec(compile(source,name,'exec'),m.__dict__)
    return m.short_appserver_usage
before=load(base_source,'baseline_token_usage')
after=load(new_source,'candidate_token_usage')
keys=('inputTokens','cachedInputTokens','outputTokens','totalTokens','reasoningOutputTokens')
def events(i=3,c=1,o=2,r=1):
    counts=dict(zip(keys,(i,c,o,i+o,r)))
    return [{'method':'turn/started','params':{'threadId':'th','turn':{'id':'tu'}}},
      {'method':'thread/tokenUsage/updated','params':{'threadId':'th','turnId':'tu','tokenUsage':{'last':dict(counts),'total':dict(counts)}}},
      {'method':'turn/completed','params':{'threadId':'th','turn':{'id':'tu','status':'completed','items':[]}}}]
def parse(fn,e): return fn(json.loads(json.dumps(e)),'th','tu')
def require(ok,msg):
    if not ok: raise RuntimeError(msg)
def reject(fn,e,label):
    try: parse(fn,e)
    except ValueError: return
    raise RuntimeError('accepted invalid '+label)
reproduced=0
for e0 in (events(0,0,0,0),events(1,1,1,1)):
    for key in keys:
        value=e0[1]['params']['tokenUsage']['total'][key]
        if value in (0,1):
            e=copy.deepcopy(e0);e[1]['params']['tokenUsage']['total'][key]=bool(value)
            require(parse(before,e)==parse(before,e0),'baseline value output changed')
            reject(after,e,'equal bool '+key); reproduced+=1
for key in keys:
    e=events();e[1]['params']['tokenUsage']['total'][key]=float(e[1]['params']['tokenUsage']['total'][key])
    require(parse(before,e)==parse(before,events()),'baseline equal float output changed')
    reject(after,e,'equal float '+key);reproduced+=1
legal=0
for i in (0,1,3,2**54):
  for c in set((0,i)):
    for o in (0,1,4):
      for r in set((0,o)):
        e=events(i,c,o,r)
        expected={'thread_id':'th','turn_id':'tu','input_tokens':i,'cached_input_tokens':c,'output_tokens':o,'total_tokens':i+o,'reasoning_output_tokens':r,'source':'Codex app-server final fresh-turn tokenUsage snapshot','scope':'one no-tool inference turn; cache not subtracted; development/this chat excluded'}
        require(parse(before,e)==expected==parse(after,e),'valid full output mismatch')
        # Final-only semantics deliberately preserved even if earlier total was invalid.
        earlier=copy.deepcopy(e[1]);earlier['params']['tokenUsage']['total']['inputTokens']='bad-early'
        e.insert(1,earlier)
        require(parse(before,e)==expected==parse(after,e),'earlier snapshot policy changed')
        legal+=2
invalid=0
for bucket in ('last','total'):
  for key in keys:
    for bad in (None,'3',[],{},-1,1.25,float('nan'),float('inf'),float('-inf')):
      e=events();e[1]['params']['tokenUsage'][bucket][key]=bad
      reject(before,e,'baseline '+bucket+key+repr(bad))
      reject(after,e,'candidate '+bucket+key+repr(bad));invalid+=1
    e=events();del e[1]['params']['tokenUsage'][bucket][key]
    reject(before,e,'missing '+key);reject(after,e,'missing '+key);invalid+=1
# Existing fresh-total and arithmetic rejection must remain.
for mode in ('history','cached','reasoning','sum','tool','wrongturn','duplicate','failed'):
 e=events()
 if mode=='history':e[1]['params']['tokenUsage']['total']['inputTokens']+=1
 elif mode in ('cached','reasoning','sum'):
  for bucket in ('last','total'):
   e[1]['params']['tokenUsage'][bucket][{'cached':'cachedInputTokens','reasoning':'reasoningOutputTokens','sum':'totalTokens'}[mode]]=99
 elif mode=='tool':e[-1]['params']['turn']['items']=[{'type':'commandExecution'}]
 elif mode=='wrongturn':e[1]['params']['turnId']='other'
 elif mode=='duplicate':e.append(copy.deepcopy(e[-1]))
 elif mode=='failed':e[-1]['params']['turn']['status']='failed'
 reject(before,e,mode);reject(after,e,mode);invalid+=1
print(json.dumps({'baseline_sha':SHA,'baseline_source_sha256':hashlib.sha256(base_source).hexdigest(),'candidate_source_sha256':hashlib.sha256(new_source).hexdigest(),'baseline_accepted_candidate_rejected':reproduced,'legal_complete_output_differential':legal,'existing_invalid_both_rejected':invalid,'note':'NaN/Infinity are additional Python parser robustness cases, not standard JSON provider evidence; no billing/model/performance claim','status':'pass'},indent=2))
