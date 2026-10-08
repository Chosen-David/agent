from pathlib import Path
import subprocess, json, hashlib, sys
import tiktoken
BASE=Path(__file__).resolve().parent; ROOT=BASE.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def call(*args):
    r=subprocess.run([sys.executable,'-m','agent_runtime.knowledge','--root','knowledge',*args],cwd=ROOT,capture_output=True,text=True,check=True)
    return json.loads(r.stdout)
contract=json.loads((BASE/'publication-inputs.json').read_text())
bindings={a['path']:sha(ROOT/a['path']) for a in contract['artifacts']}
assert all(bindings[a['path']]==a['sha256'] for a in contract['artifacts'])
original=json.loads((BASE/'manifest.json').read_text())
assert all(sha(ROOT/a['path'])==a['sha256'] for a in original['artifacts'])
usage=json.loads((BASE/'knowledge-usage.json').read_text())
refcheck=call('check-refs',str(BASE/'knowledge-usage.json')); assert refcheck['valid']
index=BASE/'independent_index.sqlite'
call('index','--db',str(index),'--rebuild')
replays=[]
for item in usage['retrieval']:
    args=['search',item['input']['query'],'--limit','3']
    if item['backend']=='sqlite': args+=['--index',str(index)]
    result=call(*args); ids=[x['id'] for x in result['results']]
    assert ids==item['retrieved_ids']
    replays.append({'backend':item['backend'],'query':item['input']['query'],'ids':ids})
assert sum(x['ids'][0]=='math.residual-interval-screening' for x in replays)==5
assert all('math.residual-interval-screening' in x['ids'] for x in replays)
old=json.loads((BASE/'baseline-retrieval.json').read_text())
reg=json.loads((BASE/'retrieval-regression.json').read_text())
old_replays=[]
for item in reg:
    old_ids=[x['id'] for x in old[item['query']]['results']]
    now=[x['id'] for x in call('search',item['query'],'--limit','3')['results']]
    assert old_ids==item['old'] and now==item['new'] and old_ids[0] in now
    old_replays.append({'query':item['query'],'ids':now})
show=call('show','math.residual-interval-screening')
(BASE/'independent_show.json').write_text(json.dumps(show,ensure_ascii=False,indent=2)+'\n')
tokens=len(tiktoken.get_encoding('cl100k_base').encode(json.dumps(show,ensure_ascii=False)))
cost=json.loads((BASE/'cost.json').read_text()); assert tokens==cost['complete_show_package_cl100k_base_tokens']==2920
assert abs(sum(x['wall_seconds'] for x in usage['retrieval'])-cost['retrieval_wall_seconds'])<1e-15
assert cost['retrieval_queries']==6 and cost['host_token_cost'] is None and cost['saving_claim'] is False
mirror=ROOT/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge'
files=[p for p in (ROOT/'knowledge').rglob('*') if p.is_file() and p.suffix in ['.json','.md']]
for p in files: assert (mirror/p.relative_to(ROOT/'knowledge')).read_bytes()==p.read_bytes()
hold=ROOT/'knowledge/evaluation_holdouts.json'
committed=subprocess.run(['git','show','HEAD:knowledge/evaluation_holdouts.json'],cwd=ROOT,capture_output=True,check=True).stdout
assert hold.read_bytes()==committed
holdout=json.loads((BASE/'holdout-protocol.json').read_text()); assert holdout['status']=='not-run'
card=json.loads((ROOT/'knowledge/entries/math.residual-interval-screening.json').read_text())
assert card['status']=='published' and card['verification']['proof']=='derivation-reviewed'
log=(BASE/'regression-published.log').read_text(); assert 'Ran 47 tests' in log and log.rstrip().endswith('OK')
after={p:sha(ROOT/p) for p in bindings}; assert after==bindings
out={'status':'usable-with-scope','publication_inputs_sha256':sha(BASE/'publication-inputs.json'),
     'artifact_hashes':bindings,'replayed_new_queries':replays,'replayed_old_queries':old_replays,
     'reference_check':refcheck,'token_count':tokens,'token_count_serialization':'json.dumps(full_show,ensure_ascii=False), default separators',
     'show_sha256':sha(BASE/'independent_show.json'),'mirror_checked_files':len(files),
     'holdout_sha256':sha(hold),'holdout_equal_HEAD':True,'published_regression_log_sha256':sha(BASE/'regression-published.log'),
     'limitations':['Six public structure queries, not semantic/model refusal evaluation or exhaustive regression.',
                    'Token count is serialized knowledge package size, not API bill or savings comparison.',
                    'One final47 test log readback, no remote publication acceptance. All phase1 numeric limitations persist.',
                    'Source is read v1; no exhaustive latest-version or literature claim.']}
(BASE/'independent_publication_outputs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ['artifact_hashes','reference_check','replayed_new_queries','replayed_old_queries']},ensure_ascii=False,indent=2))
