from pathlib import Path
import json,time
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.handoff_basis import make_token_counter
D=Path(__file__).resolve().parent;s=KnowledgeStore('knowledge');counter=make_token_counter('cl100k_base');start=time.perf_counter();q='相关 高斯 二次 能量 平方 最大 特征值';hits=s.search(q,limit=1);ctx=s.context(hits,max_entries=2,max_chars=20000,include_related=False)
assert ctx['status']=='ready' and 'math.gaussian-quadratic-energy' in [x['id']for x in ctx['entries']];assert s.check_refs(ctx['knowledge_refs'])['valid']
serialize=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'));n=counter(serialize(ctx));alltokens=counter(serialize([s.get(k)for k in sorted(s.records) if s.records[k]['status']=='published']))
(D/'context-cost.json').write_text(json.dumps(dict(encoding=counter.tokenizer_name,version=counter.tokenizer_version,tokens=n,context_ids=[x['id']for x in ctx['entries']],chars=ctx['budget'],all_corpus_naive_reference_tokens=alltokens,seconds=time.perf_counter()-start,scope='serialized JSON and exact tokenizer; no prompt envelope or model billing; naive full corpus not former production baseline'),ensure_ascii=False,indent=2)+'\n')
(D/'knowledge-use.json').write_text(json.dumps(dict(query=q,knowledge_refs=ctx['knowledge_refs'],premises={'n':'fixed in controlled examples','covariance':'known Gaussian separable T and Sigma, not empirical estimates','square':'zero-mean jointly Gaussian only in this example','real_token_model':'unknown, reject transfer'},scope='actual bounded retrieval/reference validation; no live model test'),ensure_ascii=False,indent=2)+'\n');print({'tokens':n,'ids':[x['id']for x in ctx['entries']]})
