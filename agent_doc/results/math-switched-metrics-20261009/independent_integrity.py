from pathlib import Path
import json, hashlib, subprocess,sys,time
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent;sys.path.insert(0,str(R))
from agent_runtime.result_validation import _snapshot
def digest(b):return hashlib.sha256(b).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'sha256':digest(p.read_bytes())}
c=json.loads((B/'contract.json').read_text());m,p,pf=_snapshot(R,c)
(B/'independent_snapshot.json').write_text(json.dumps(pf,indent=2)+'\n')
earlier=json.loads((B/'pending-v2.json').read_text())
assert all(pf['artifact_hashes'].get(k)==v for k,v in earlier['artifact_hashes'].items())
original=json.loads((B/'raw.json').read_text());replay=json.loads((B/'independent_replay/raw.json').read_text())
original.pop('seconds');replay.pop('seconds');assert original==replay
def no_times(x):
 if isinstance(x,dict):return {k:no_times(v) for k,v in x.items() if not k.endswith('seconds')}
 if isinstance(x,list):return [no_times(v) for v in x]
 return x
retr=json.loads((B/'retrieval.json').read_text());again=json.loads((B/'independent_replay/retrieval.json').read_text());assert no_times(retr)==no_times(again)
assert (B/'retrieval_knowledge_use.json').read_bytes()==(B/'independent_replay/retrieval_knowledge_use.json').read_bytes()
context=retr['context'];assert len(context['entries'])==4 and context['budget']['used_chars']==14961<=18000
assert len(retr['records'])==6 and all(v['hit'] and 'math.switched-quadratic-metrics' in v['actual'][:3] for v in retr['records'])
for e in context['entries']:assert e['content']==(R/'knowledge'/Path(e['path']).with_suffix('.md')).read_text()
mirror=R/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge'
pairs=[]
for pth in (R/'knowledge/entries').rglob('*'):
 if pth.is_file():
  mt=mirror/pth.relative_to(R/'knowledge');assert pth.read_bytes()==mt.read_bytes();pairs.append({'source':ref(pth),'mirror':ref(mt)})
rev='ffe7f9def00ca9275a023c55ad55d916deb5301e'
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',rev,'knowledge/entries'],cwd=R,text=True).splitlines()
candidates=[]
for name in paths:
 if not name.endswith('.json'):continue
 data=subprocess.check_output(['git','show',rev+':'+name],cwd=R)
 if json.loads(data)['status']!='candidate':continue
 for nm in (name,str(Path(name).with_suffix('.md'))):
  past=subprocess.check_output(['git','show',rev+':'+nm],cwd=R)
  assert past==(R/nm).read_bytes();mt=mirror/(R/nm).relative_to(R/'knowledge');assert mt.read_bytes()==past
  candidates.append({'path':nm,'sha256':digest(past),'baseline_revision':rev,'mirror':ref(mt)})
baseline=json.loads((B/'preservation_baseline.json').read_text())
for nm,h in baseline.items():assert digest((R/nm).read_bytes())==h
assert digest(Path('/tmp/switched2026.pdf').read_bytes())==json.loads((B/'research_extraction.json').read_text())['pdf_sha256']
assert digest(Path('/tmp/switched2026.txt').read_bytes())==json.loads((B/'research_extraction.json').read_text())['text_sha256']
for ext in ('json','md'):
 assert (R/f'knowledge/entries/math.switched-quadratic-metrics.{ext}').read_bytes()==(B/f'card_snapshot.{ext}').read_bytes()
out={'verdict':'pass','artifact_count':len(pf['artifact_hashes']),'replay_equal_except_seconds':True,'context_characters':14961,'context_entries':4,'top3_hits':6,'all_knowledge_mirror_pairs':pairs,'candidates_recovered_from_initial_revision':candidates,'holdout_hashes':baseline,'holdout_content_inspected':False,'initial_preservation_guard_limitation':'producer initial glob missed nested candidates; independently reconstructed recursive initial git baseline and checked JSON/MD/mirror bytes','initial_manifest_limitation':'25 binding original omitted full retrieval corpus; expanded245 then249 binding manifests before acceptance; earlier snapshots retained;245artifact subset unchanged'}
(B/'independent_integrity.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('artifact_count','top3_hits','context_characters')}))
print('candidate files:',len(candidates),'mirror pairs:',len(pairs))
