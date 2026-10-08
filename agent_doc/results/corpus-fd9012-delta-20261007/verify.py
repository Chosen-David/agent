#!/usr/bin/env python3
"""Minimal candidate-only fd9012 delta; not a new full-corpus acceptance run."""
import hashlib,json,os,shutil,sqlite3,subprocess,sys,tempfile
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
OLD=ROOT/'doc/results/combined-corpus-delta-v2-20261007'
REPORT=ROOT/'docs/document_architecture_validation/knowledge/fd9012-supplement'
NEW='neuro.salamander-cell-type-homology'; BASE='fd9012ca9f953693ad59d30e63d03ac7644c599e'
sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore,KnowledgeError
from agent_runtime.knowledge_index import build_index,indexed_search
from agent_runtime.result_store import ResultStore

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def main():
 assert not (OUT/'manifest.json').exists()
 start=datetime.now(timezone.utc).isoformat()
 pres=json.loads((OLD/'preservation.json').read_text())
 previous=json.loads((OLD/'final-summary.json').read_text())
 old_entry_hashes={p:h for p,h in pres['candidate_file_hashes'].items() if p.startswith('entries/')}
 assert len(old_entry_hashes)==156
 assert all(sha(ROOT/'knowledge'/p)==h for p,h in old_entry_hashes.items())
 deps=[*ROOT.glob('agent_runtime/*.py'),ROOT/'tests/test_knowledge_index.py',*ROOT.joinpath('knowledge').rglob('*.json'),*ROOT.joinpath('knowledge').rglob('*.md'),*ROOT.joinpath('plugins/research-assistant/skills/model-with-knowledge/assets/knowledge').rglob('*.json'),*ROOT.joinpath('plugins/research-assistant/skills/model-with-knowledge/assets/knowledge').rglob('*.md'),Path(__file__)]
 before={str(p.relative_to(ROOT)):sha(p) for p in deps}
 oldcode=json.loads((OLD/'supplement.json').read_text())['dependencies_after']
 for p,h in oldcode.items():
  if p.startswith('agent_runtime/') or p=='tests/test_knowledge_index.py':assert sha(ROOT/p)==h,(p,h)
 registry=ROOT/'knowledge/evaluation_holdouts.json'
 assert sha(registry)==pres['holdout_registry_sha256']
 holdouts=json.loads(registry.read_text());metas={}
 for p in sorted((ROOT/'knowledge/entries').rglob('*.json')):
  d=json.loads(p.read_text());metas[d['id']]=d
  for target in holdouts['targets']:
   for key in ('doi','url'):
    assert key not in target or target[key].lower() not in json.dumps(d['sources'],ensure_ascii=False).lower()
 assert Counter(d['status'] for d in metas.values())=={'published':77,'candidate':2}
 assert metas[NEW]['status']=='candidate'
 entryfiles={str(p.relative_to(ROOT/'knowledge')) for p in (ROOT/'knowledge/entries').rglob('*') if p.is_file()}
 added=entryfiles-set(old_entry_hashes)
 assert added=={'entries/neuroscience/'+NEW+ext for ext in ('.json','.md')}
 assert len([p for p in old_entry_hashes if p.endswith('.json') and metas[json.loads((ROOT/'knowledge'/p).read_text())['id']]['status']=='published'])==77
 plugin=ROOT/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge'
 assert {str(p.relative_to(ROOT/'knowledge')):sha(p) for p in (ROOT/'knowledge').rglob('*') if p.is_file()}=={str(p.relative_to(plugin)):sha(p) for p in plugin.rglob('*') if p.is_file()}
 # Three representative cases only. Full catalog measurement remains the907 run.
 bee=json.loads((ROOT/'evals/knowledge/bee-learning-queries.json').read_text())['cases'][0]
 aik=json.loads((ROOT/'docs/knowledge_learning/2026-10-07-ai-algorithms/evaluation/frozen_tasks.json').read_text())['cases'][-1]
 examples=[{'id':'bee-natural','query':bee['query']},{'id':'aik-A12','query':aik['query']},{'id':'nohit','query':'quasar photosynthesis chloroplast'}]
 rows=[];exclusion=[]
 with tempfile.TemporaryDirectory(prefix='candidate-delta-',dir=OUT) as temp:
  temp=Path(temp);corpus=temp/'knowledge';shutil.copytree(ROOT/'knowledge',corpus)
  for ext in ('.json','.md'):(corpus/'entries/neuroscience'/(NEW+ext)).unlink()
  old=KnowledgeStore(corpus);assert old.snapshot==previous['snapshots']['candidate']
  db=temp/'index.sqlite';oldindex=build_index(old,db)
  pre={}
  for case in examples:
   for b in ('files','sqlite'):
    found=old.search(case['query'],limit=3) if b=='files' else indexed_search(old,db,case['query'],limit=3)
    context=old.context(found)
    pre[(case['id'],b)]=(found,context)
  for ext in ('.json','.md'):shutil.copy2(ROOT/'knowledge/entries/neuroscience'/(NEW+ext),corpus/'entries/neuroscience'/(NEW+ext))
  new=KnowledgeStore(corpus)
  stale=False
  try:indexed_search(new,db,examples[0]['query'],limit=3)
  except KnowledgeError as exc:stale='stale' in str(exc)
  assert stale
  newindex=build_index(new,db)
  assert newindex['indexed']==77 and newindex['updated']==0 and newindex['removed']==0 and newindex['unchanged']==77
  for case in examples:
   for b in ('files','sqlite'):
    found=new.search(case['query'],limit=3) if b=='files' else indexed_search(new,db,case['query'],limit=3)
    ctx=new.context(found);oldfound,oldctx=pre[(case['id'],b)]
    assert found['results']==oldfound['results']
    assert [x['id'] for x in ctx['entries']]==[x['id'] for x in oldctx['entries']]
    rows.append({'case':case['id'],'query':case['query'],'backend':b,'old_results':oldfound['results'],'new_results':found['results'],'context_ids':[x['id'] for x in ctx['entries']],'raw_ranking_equal':True,'context_ids_equal':True})
  ids={x[0] for x in sqlite3.connect(db).execute('SELECT id FROM entries')}
  published={kid for kid,d in metas.items() if d['status']=='published'};candidates=set(metas)-published
  assert ids==published and ids.isdisjoint(candidates)
  for kid in sorted(candidates):
   blocked=False
   try:new.get(kid)
   except KnowledgeError:blocked=True
   query=metas[kid]['aliases'][0]
   fr=new.search(query,limit=20);sr=indexed_search(new,db,query,limit=20)
   assert blocked and kid not in [x['id'] for x in fr['results']+sr['results']]
   exclusion.append({'id':kid,'status':metas[kid]['status'],'get_blocked':blocked,'absent_from_files':True,'absent_from_sqlite_search':True,'absent_from_index':kid not in ids})
  cmd=[sys.executable,'-m','unittest','discover','-s','tests','-p','test_knowledge_index.py','-v']
  env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(temp)}
  p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  (OUT/'index-tests.log').write_text(p.stdout)
  assert p.returncode==0 and 'Ran 10 tests' in p.stdout
 current=KnowledgeStore(ROOT/'knowledge');assert current.snapshot==new.snapshot
 after={str(p.relative_to(ROOT)):sha(p) for p in deps};assert before==after
 raw={'started_at_utc':start,'completed_at_utc':datetime.now(timezone.utc).isoformat(),'base_commit':BASE,'prior_staged_tree':'a0e5731ee615a84db9041c1e5187e233f055de16','before_snapshot':old.snapshot,'after_snapshot':current.snapshot,'prior_entry_files_unchanged':156,'published_entry_files_unchanged':154,'published_count':77,'candidate_count':2,'added_entry_files':sorted(added),'published_runtime_source_unchanged':True,'holdout_registry_unchanged':True,'holdout_metadata_collisions':[],'metadata_checked_before_loading_bodies':True,'holdout_target_contents_read':False,'candidate_exclusion':exclusion,'stale_index_rejected':stale,'index_refresh':newindex,'representative_queries':rows,'focused_index_tests':{'command':cmd,'exit_code':p.returncode,'tests':10,'passed':True},'mirrored_corpus_exact':True,'dependencies_before':before,'dependencies_after':after,'dependencies_stable':True,'scope':'Candidate-only integration identity/exclusion and unchanged-published ranking semantics;3representative queries per backend and10index tests, not a new full-catalog evaluation.'}
 write(OUT/'raw-checks.json',raw)
 summary={k:raw[k] for k in ('base_commit','prior_staged_tree','before_snapshot','after_snapshot','prior_entry_files_unchanged','published_entry_files_unchanged','published_count','candidate_count','added_entry_files','published_runtime_source_unchanged','holdout_registry_unchanged','candidate_exclusion','stale_index_rejected','index_refresh','focused_index_tests','mirrored_corpus_exact','dependencies_stable','scope')}
 summary.update({'status':'measured-pending-independent-review','representative_query_backend_pairs':6,'all_representative_rankings_and_context_ids_unchanged':True,'prior_retrieval_reuse_scope':'Published metadata/body bytes, ranking source and published graph are unchanged; both search backends and related/context exclude candidate records. Prior default/domain/known-gap outcomes remain applicable under those unchanged semantics, supported by6representative checks, not remeasured full catalogs.','limitations':['No scientific review or promotion of salamander/cephalopod candidates.','Candidate-only changes alter whole-corpus snapshot and require stale SQLite metadata refresh;77published documents unchanged.','Original907native result stays immutable. Current old-manifest validation may be stale for changed metadata; prior staged Git tree preserves original bound bytes.','No full catalog or full730 cycle repeated; release reviewer owns scoped acceptance.']})
 write(OUT/'summary.json',summary);write(REPORT/'summary.json',summary)
 write(OUT/'environment.json',{'python':sys.version,'sqlite':sqlite3.sqlite_version,'network_used':False,'dependencies':'Python standard library and SQLite FTS5','timing_claim':False})
 scope=raw['scope'];criteria={}
 for name,proc in {'implementation':'Confirm all previous77published pairs and runtime code hashes unchanged; inspect candidate exclusion before scoring/indexing.','reference_boundary':'Compare pre-addition snapshot reconstruction with original snapshot; prove both candidates excluded and oldindex stale until refresh.','data_integrity':'Bind original native result and raw identities, current corpus, source, catalog selections and actual log; preserve907records.','numerical_sanity':'Check counts79total=77published+2candidate;77index IDs exactly published;6representative backend comparisons equal.','measurement_validity':'Restrict claims to unchanged semantics and representative spot checks; no full-catalog remeasurement or performance claims.','reproducibility':'Record exact10-test command and source hashes before/after; independent reviewer verifies scoped evidence.'}.items():criteria[name]={'procedure':proc,'acceptance':'The stated check must hold; no missing/inconsistent dependencies or candidate scientific promotion.','allow_not_applicable':False}
 write(OUT/'validation-plan.json',{'schema_version':'experiment-validation-plan/v1','scope':scope,'criteria':criteria})
 contract={'result_id':OUT.name,'producer_task_id':'verify-fd9012-candidate-delta','producer_actor':'corpus-delta-verifier','manifest_path':str((OUT/'manifest.json').relative_to(ROOT)),'validation_plan':ref(OUT/'validation-plan.json'),'scope':scope}
 inputs=[*ROOT.joinpath('knowledge').rglob('*.json'),*ROOT.joinpath('knowledge').rglob('*.md'),OLD/'manifest.json',OLD/'record.json',OLD/'final-summary.json',OLD/'preservation.json',OLD/'catalog-comparison.json',OLD/'supplement.json',ROOT/'evals/knowledge/bee-learning-queries.json',ROOT/'docs/knowledge_learning/2026-10-07-ai-algorithms/evaluation/frozen_tasks.json']
 manifest={**contract,'schema_version':'experiment-result/v1','run_id':OUT.name,'code_revision':BASE+' plus approved stagedAIK/runtime; actual hashes bound','execution':{'command':['python '+str(Path(__file__).relative_to(ROOT))],'environment_description':'Local Python/SQLite; minimum candidate-only delta; representative checks only.','repeats':1,'seeds':[0],'started_at':start,'completed_at':raw['completed_at_utc']},'artifacts':{'code':[ref(p) for p in [Path(__file__),*ROOT.glob('agent_runtime/*.py'),ROOT/'tests/test_knowledge_index.py']],'inputs':[ref(p) for p in inputs],'config':[ref(OUT/'validation-plan.json')],'raw_data':[ref(OUT/'raw-checks.json'),ref(OUT/'index-tests.log')],'outputs':[ref(OUT/'summary.json')],'environment':[ref(OUT/'environment.json')]},'metrics':[{'name':n,'value':v,'unit':'count'} for n,v in [('published_entries',77),('candidate_entries',2),('unchanged_prior_entry_files',156),('representative_backend_pairs',6),('focused_index_tests_passed',10)]]}
 write(OUT/'contract.json',contract);write(OUT/'manifest.json',manifest)
 ResultStore(ROOT).register(contract,measured_at=raw['completed_at_utc'])
 saved=json.loads((OUT/'record.json').read_text());write(OUT/'registration-receipt.json',{'origin':saved['origin'],'status':saved['validation_at_registration']['status'],'manifest':ref(OUT/'manifest.json'),'record':ref(OUT/'record.json'),'summary':ref(OUT/'summary.json')})
 print(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(json.loads((OUT/'registration-receipt.json').read_text()),indent=2))
if __name__=='__main__':main()
