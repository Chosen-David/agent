from pathlib import Path
import json,hashlib,subprocess,sys,tiktoken
R=Path(__file__).resolve().parents[4];D=R/'doc/results/math-softmax-kl-20261008';I=Path(__file__).parent
read=lambda p:json.loads(p.read_text())
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(D/'manifest.json');old=read(D/'pre-sync/manifest.json')
assert digest(D/'manifest.json')=='6c74f665f6c480648a6ba96bbaa020344ff73436013f694512de09adc127b019'
changed=[];bindings={m['validation_plan']['path']:m['validation_plan']['sha256']}
for role,refs in m['artifacts'].items():
 prior={r['path']:r['sha256'] for r in old['artifacts'][role]}
 for ref in refs:
  assert digest(R/ref['path'])==ref['sha256'];bindings[ref['path']]=ref['sha256']
  if prior.get(ref['path'])!=ref['sha256']:changed.append(ref['path'])
assert set(changed)<={str((D/n).relative_to(R)) for n in ['retrieval-corpus.json','knowledge-usage.json','cost.json']}
assert m['validation_plan']==old['validation_plan'] and m['scope']==old['scope'] and m['metrics']==old['metrics']
corpus=read(D/'retrieval-corpus.json')['files'];oldcorpus=read(D/'pre-sync/retrieval-corpus.json')['files']
actual=sorted(str(p.relative_to(R)) for p in (R/'knowledge/entries').rglob('*') if p.is_file() and p.suffix in ['.json','.md'])
assert actual==sorted(r['path'] for r in corpus) and len(corpus)==188
for ref in corpus:assert digest(R/ref['path'])==ref['sha256']
prior={r['path']:r['sha256'] for r in oldcorpus};current={r['path']:r['sha256'] for r in corpus}
assert all(current[p]==h for p,h in prior.items());added=sorted(set(current)-set(prior));assert len(added)==4
def cli(*args):return json.loads(subprocess.check_output([sys.executable,'-m','agent_runtime.knowledge','--root','knowledge',*args],cwd=R))
idx=I/'search.sqlite';cli('index','--db',str(idx));usage=read(D/'knowledge-usage.json');results=[]
for row in usage['retrieval']:
 result=cli('search',row['input']['query'],'--domain',row['domain'],'--limit','3',*(['--index',str(idx)] if row['backend']=='sqlite' else []))
 assert result==row['result'] and result['results'][0]['id']=='math.softmax-kl-fisher';results.append(result)
assert len(results)==6
show=cli('show','math.softmax-kl-fisher');assert show['knowledge_refs']==usage['knowledge_refs']==read(D/'pre-sync/knowledge-usage.json')['knowledge_refs']
tokens=len(tiktoken.get_encoding('cl100k_base').encode(json.dumps(show,ensure_ascii=False)))
assert tokens==read(D/'cost.json')['body_package_cl100k_base_tokens']==3625
(I/'retrieval-replay-v2.json').write_text(json.dumps(dict(results=results,show=show),ensure_ascii=False,indent=2)+'\n')
(I/'check-delta-result.json').write_text(json.dumps(dict(status='pass',manifest_sha256=digest(D/'manifest.json'),prior_manifest_sha256=digest(D/'pre-sync/manifest.json'),all_bindings=bindings,changed_bound_paths=changed,added_corpus_paths=added,corpus_files=188,prior_corpus_files=184,all_prior_corpus_bytes_unchanged=True,math_code_inputs_raw_environment_config_unchanged=True,retrievals=6,actual_show_encoding_tokens=tokens,encoding='cl100k_base',snapshot=results[0]['snapshot']),indent=2)+'\n')
idx.unlink()
print('targeted delta passed',len(corpus),tokens,digest(D/'manifest.json'))
