"""Explicit-tokenizer payload accounting, not model billing or quality."""
from pathlib import Path
import json,time
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.handoff_basis import make_token_counter
s=KnowledgeStore('knowledge');counter=make_token_counter('cl100k_base');D=Path(__file__).resolve().parent
cur=json.loads((D/'curriculum.json').read_text());start=time.perf_counter();rows=[];refs={};dump=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
for t in cur['topics']:
 h=s.search(t['public_query'],domain='algebra',limit=1)
 ctx=s.context(h,max_entries=1,max_chars=16000,include_related=False)
 assert [x['id'] for x in ctx['entries']]==[t['id']] and ctx['status']=='ready'
 n=counter(dump(ctx));assert n<4500,(t['id'],n)
 rows.append(dict(id=t['id'],tokens=n,status=ctx['status'],chars=ctx['budget'],scope='structural query, domain fixed to algebra; full one-entry package, no optional relations'))
 for r in ctx['knowledge_refs']:refs[r['id']]=r
alltokens=counter(dump([s.get(k) for k in sorted(s.records)]))
physics_query='单位 周期 长度 重力 变量';physics=s.search(physics_query,domain='physics',limit=3)
assert 'physics.dimensionless' in [x['id'] for x in physics['results']]
out=dict(schema_version=1,encoding=counter.tokenizer_name,tokenizer_version=counter.tokenizer_version,entries=len(s.records),rows=rows,max_selected_context_tokens=max(x['tokens'] for x in rows),all_corpus_tokens=alltokens,seconds=time.perf_counter()-start,domain_scoped_physics_ids=[x['id'] for x in physics['results']],scope='cl100k_base serialized JSON; no prompt envelope, real billed tokens, model A/B or production improvement. All-corpus is naive reference, not former production.')
(D/'context-cost.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');(D/'knowledge-use.json').write_text(json.dumps(dict(knowledge_root='knowledge',knowledge_refs=list(refs.values()),scope='Public finite derivations; not semantic/model quality proof'),ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='rows'},ensure_ascii=False))
