"""Optional named-tokenizer payload accounting; not billing/model quality."""
import json, time
from pathlib import Path
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.handoff_basis import make_token_counter

start=time.perf_counter();store=KnowledgeStore('knowledge');count=make_token_counter('cl100k_base')
query='线性方程算出来的残差很小，解的分量还可能排反吗？'
hits=store.search(query,limit=1)
selected=store.context(hits,max_entries=1,max_chars=12000,include_related=False)
assert [r['id'] for r in selected['entries']]==['math.linear-solve-backward-error']
dump=lambda x:json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
# Deliberately naive all-corpus baseline, not previous production behavior.
full=[store.get(k) for k in sorted(store.records)]
out=dict(schema_version=1,encoding=count.tokenizer_name,tokenizer_version=count.tokenizer_version,selected_context_tokens=count(dump(selected)),all_corpus_tokens=count(dump(full)),selected_ids=[r['id'] for r in selected['entries']],status=selected['status'],seconds=time.perf_counter()-start,scope='Serialized JSON payload under explicit cl100k_base; all-corpus is a naive reference, not previous production. No billing, prompt envelope or model A/B.',knowledge_refs=selected['knowledge_refs'])
assert out['selected_context_tokens']<out['all_corpus_tokens']
Path(__file__).with_name('context-cost.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
Path(__file__).with_name('knowledge-use.json').write_text(json.dumps(dict(knowledge_root='knowledge',knowledge_refs=selected['knowledge_refs'],scope='Finite verification and manually audited mapping; semantic applicability not certified by identity checks.'),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
