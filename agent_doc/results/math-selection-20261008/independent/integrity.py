from pathlib import Path
import json,hashlib,subprocess,tiktoken
R=Path(__file__).resolve().parents[4];D=R/'doc/results/math-selection-20261008';O=D/'independent'
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((D/'manifest.json').read_text());refs=[v for a in m['artifacts'].values() for v in a]+[m['validation_plan']]
for v in refs:assert hashfile(R/v['path'])==v['sha256'],v['path']
corpus=json.loads((D/'retrieval-corpus.json').read_text())
for v in corpus['files']:assert hashfile(R/v['path'])==v['sha256']
assert {v['path'] for v in corpus['files']}=={str(p.relative_to(R)) for p in (R/'knowledge/entries').rglob('*') if p.is_file() and p.suffix in ('.json','.md')}
u=json.loads((D/'knowledge-usage.json').read_text());shows=[]
for kid in ['math.finite-menu-selection','math.hoeffding-bounded-mean']:
 shows.append(json.loads(subprocess.check_output(['python','-m','agent_runtime.knowledge','--root','knowledge','show',kid],cwd=R)))
assert shows[0]['knowledge_refs']==u['knowledge_refs']
cost=sum(len(tiktoken.get_encoding('cl100k_base').encode(json.dumps(x,ensure_ascii=False))) for x in shows)
assert cost==json.loads((D/'cost.json').read_text())['body_package_cl100k_base_tokens']
for record in u['retrieval']:
 args=['python','-m','agent_runtime.knowledge','--root','knowledge','search',record['input']['query'],'--domain',record['input']['domain'],'--limit','3']
 if record['backend']=='sqlite':args+=['--index',str(R/'.agent-runs/math-selection-20261008/search.sqlite')]
 found=json.loads(subprocess.check_output(args,cwd=R));assert [(x['id'],x['sha256']) for x in found['results']]==[(x['id'],x['sha256']) for x in record['result']['results']]
result={'status':'pass','manifest_sha256':hashfile(D/'manifest.json'),'manifest_bound_artifacts':len(refs),'corpus_files':len(corpus['files']),'actual_encoding_tokens':cost,'retrieval_records':len(u['retrieval']),'knowledge_refs':u['knowledge_refs']}
(O/'integrity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
