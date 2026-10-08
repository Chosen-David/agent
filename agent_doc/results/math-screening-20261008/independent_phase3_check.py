from pathlib import Path
import json,hashlib,subprocess,sys
import tiktoken
B=Path(__file__).resolve().parent;R=B.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def call(argv):
    assert argv[:5]==['python','-m','agent_runtime.knowledge','--root','knowledge']
    p=subprocess.run([sys.executable,*argv[1:]],cwd=R,capture_output=True,text=True,check=True)
    return json.loads(p.stdout)
contract=json.loads((B/'publication-inputs-v3.json').read_text());bindings={x['path']:sha(R/x['path']) for x in contract['artifacts']}
assert all(bindings[x['path']]==x['sha256'] for x in contract['artifacts'])
mapping=json.loads((B/'relocation.json').read_text());original=json.loads((B/'manifest.json').read_text())
assert len(mapping['files'])==len(original['artifacts'])
for x,y in zip(mapping['files'],original['artifacts']):
    assert x['path']==y['path'] and x['sha256']==y['sha256'] and sha(R/x['relocated_path'])==x['sha256']
old_body=(B/'pre-relocation/knowledge-body.md').read_text();new_body=(R/'knowledge/entries/math.residual-interval-screening.md').read_text()
assert new_body==old_body.replace('doc/results/math-screening-20261008/','agent_doc/results/math-screening-20261008/')
u=json.loads((B/'knowledge-usage.json').read_text());replays=[]
for x in u['retrieval']:
    assert x['domain']=='linear-algebra' and '--domain' in x['argv']
    d=call(x['argv']);ids=[z['id'] for z in d['results']]
    assert ids==x['retrieved_ids'] and d['snapshot']==x['snapshot']
    replays.append({'backend':x['backend'],'argv':x['argv'],'ids':ids,'snapshot':d['snapshot']})
assert sum(x['ids'][0]=='math.residual-interval-screening' for x in replays)==5
assert all('math.residual-interval-screening' in x['ids'] for x in replays)
old=json.loads((B/'baseline-retrieval.json').read_text());reg=json.loads((B/'retrieval-regression.json').read_text())
for x in reg:
    d=call(x['argv']);ids=[z['id'] for z in d['results']]
    assert ids==x['new'] and x['old']==[z['id'] for z in old[x['query']]['results']] and x['old'][0] in ids
show=call(u['show_argv']);count=len(tiktoken.get_encoding('cl100k_base').encode(json.dumps(show,ensure_ascii=False)))
(B/'independent_show_v3.json').write_text(json.dumps(show,ensure_ascii=False,indent=2)+'\n')
cost=json.loads((B/'cost.json').read_text());assert count==cost['complete_show_package_cl100k_base_tokens']==2923
assert abs(sum(x['wall_seconds'] for x in u['retrieval'])-cost['retrieval_wall_seconds'])<1e-15
check=call(['python','-m','agent_runtime.knowledge','--root','knowledge','check-refs',str(B/'knowledge-usage.json')]);assert check['valid']
mirror=R/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge'
files=[p for p in (R/'knowledge').rglob('*') if p.is_file() and p.suffix in ['.md','.json']]
for p in files:assert p.read_bytes()==(mirror/p.relative_to(R/'knowledge')).read_bytes()
hold=R/'knowledge/evaluation_holdouts.json';committed=subprocess.run(['git','show','HEAD:knowledge/evaluation_holdouts.json'],cwd=R,capture_output=True,check=True).stdout
assert hold.read_bytes()==committed
assert {p:sha(R/p) for p in bindings}==bindings
out={'status':'delta-usable-with-scope','publication_inputs_v3_sha256':sha(B/'publication-inputs-v3.json'),'artifact_hashes':bindings,
     'original_manifest_sha256':sha(B/'manifest.json'),'relocation_binding_count':len(mapping['files']),
     'new_body_change':'only doc/results/... to agent_doc/results/... path replacement',
     'new_replays':replays,'old_replays':len(reg),'show_tokens':count,'show_sha256':sha(B/'independent_show_v3.json'),
     'strong_dependency_refs':check,'mirror_checked_files':len(files),'holdout_sha256':sha(hold),'holdout_unchanged_HEAD':True,
     'limits':['All6 new-query successes use explicit linear-algebra domain filter; no unfiltered or automatic semantic-query success claim.',
               '2923 cl100k_base tokens counts json.dumps(full_show,ensure_ascii=False), not bill/savings.',
               'Phase2 failure/pending evidence retained. Phase1 proof/raw acceptance is preserved via relocation hashes, not new data.',
               'No remote publication acceptance, managed ReviewSession, GPU/model or strict floating certificate.']}
(B/'independent_phase3_outputs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['artifact_hashes','new_replays','strong_dependency_refs']},ensure_ascii=False,indent=2))
