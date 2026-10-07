#!/usr/bin/env python3
"""Minimal 013 corpus adoption; provenance plus bounded development retrieval only."""
import collections
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sqlite3
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
REPORT = ROOT / 'docs/document_architecture_validation/knowledge/upstream-v4'
REMOTE = '013cfa15b72d354ef87ec18eb9698b58f75e3b6d'
PRIOR = '0356e07a42ac0e83a48cc0dabd61caba0f55d490'
AIK = ROOT / 'docs/knowledge_learning/2026-10-07-ai-algorithms'
PLUGIN = ROOT / 'plugins/research-assistant/skills/model-with-knowledge'
V3 = ROOT / 'doc/results/combined-corpus-v3-20261007'
SCOPE = 'Minimal 013-to-integrated-v4 corpus adoption: exact remote corpus and plugin mirror, 80 published plus 2 excluded candidates, four reserved holdout metadata records preserved, ten targeted index tests, and twelve frozen AIK development cases on two backends in default/domain modes. Upstream new-card scientific results are provenance only; raw legacy retrieval scope is eight cases per backend, not 21. No new proofs, research, full catalog, model, production or performance claim.'
COMMANDS = []
def sha(b): return hashlib.sha256(b).hexdigest()
def ref(p):
 p=Path(p);return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def put(p,d):
 Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def blob(tree,p):return subprocess.check_output(['git','show',tree+':'+str(p)],cwd=ROOT)
def paths(tree,p):return subprocess.check_output(['git','ls-tree','-r','--name-only',tree,str(p)],cwd=ROOT,text=True).splitlines()
def hashes(tree,p):return {f:sha(blob(tree,f)) for f in paths(tree,p)}
def disk(p):return {f.relative_to(ROOT).as_posix():sha(f.read_bytes()) for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
def run(cmd,name,allowed=(0,)):
 cp=subprocess.run([str(x) for x in cmd],cwd=ROOT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(OUT)},text=True,capture_output=True)
 (OUT/(name+'.log')).write_text(cp.stdout+cp.stderr)
 COMMANDS.append({'name':name,'command':[str(x) for x in cmd],'exit_code':cp.returncode,'log':ref(OUT/(name+'.log'))})
 assert cp.returncode in allowed,(name,cp.returncode,cp.stdout,cp.stderr)
 return cp

def main():
 assert not (OUT/'manifest.json').exists(),'Frozen result must not be overwritten.'
 started=datetime.now(timezone.utc).isoformat()
 # Metadata is read and checked before scientific card bodies are loaded.
 gate={}
 for p in ('knowledge/evaluation_holdouts.json','plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/evaluation_holdouts.json'):
  b=(ROOT/p).read_bytes();assert b==blob(REMOTE,p)==blob(PRIOR,p)
  gate[p]={'sha256':sha(b),'targets':json.loads(b)['targets']}
 targets=next(iter(gate.values()))['targets'];assert len(targets)==4 and all(t['status']=='reserved' for t in targets)
 assert all(g['targets']==targets for g in gate.values())
 metas={}
 for p in sorted((ROOT/'knowledge/entries').rglob('*.json')):
  d=json.loads(p.read_text());assert d['id'] not in metas;metas[d['id']]=d
  sources=json.dumps(d['sources'],ensure_ascii=False).lower()
  for target in targets:
   for field in ('doi','url'):
    assert field not in target or target[field].lower() not in sources
 counts=collections.Counter(d['status'] for d in metas.values());assert counts=={'published':80,'candidate':2},counts
 put(OUT/'holdout-metadata-gate.json',{'registries':gate,'counts':dict(counts),'exact_registered_source_collisions':[],'metadata_checked_before_card_body_access':True,'reserved_target_content_accessed':False,'SEM_candidate_copy_imported':False})
 corpus=disk(ROOT/'knowledge');assert corpus==hashes(REMOTE,'knowledge')
 mirror=disk(PLUGIN/'assets/knowledge');assert mirror==hashes(REMOTE,'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge')
 assert {p.removeprefix('knowledge/'):h for p,h in corpus.items()}=={p.removeprefix('plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/'):h for p,h in mirror.items()}
 old=hashes(PRIOR,'knowledge/entries');assert all(corpus[p]==h for p,h in old.items())
 added=sorted(p for p in corpus if p.startswith('knowledge/entries/') and p not in old)
 assert added==sorted('knowledge/entries/'+name+ext for name in ('math.centered-covariance-merge','math.dependent-mean-variance') for ext in ('.json','.md'))
 # Bind all actual direct and transitive implementation paths, including standalone plugin dependencies.
 codepaths=['agent_runtime/'+n+'.py' for n in ('__init__','knowledge','knowledge_index','knowledge_reuse','knowledge_ingest','project_docs','core','result_store','result_validation')]
 codepaths+=['plugins/research-assistant/skills/model-with-knowledge/scripts/'+n+'.py' for n in ('knowledge','knowledge_index','knowledge_reuse','knowledge_ingest','project_docs')]
 codepaths+=['tests/test_knowledge_index.py','docs/knowledge_learning/2026-10-07-ai-algorithms/check_domain_recovery.py']
 runtime={}
 for p in codepaths:
  b=(ROOT/p).read_bytes();assert b==blob(PRIOR,p),p
  runtime[p]={'sha256':sha(b),'byte_exact_accepted_v3_tree':True}
 for n in ('knowledge','knowledge_index','knowledge_reuse','knowledge_ingest','project_docs'):
  assert (ROOT/f'agent_runtime/{n}.py').read_bytes()==(PLUGIN/f'scripts/{n}.py').read_bytes()
 evidence={}
 for topic in ('ai-algorithms','matrix-concentration','centering','dependence'):
  for p,h in hashes(REMOTE,'docs/knowledge_learning/2026-10-07-'+topic).items():
   assert sha((ROOT/p).read_bytes())==h,p;evidence[p]=h
 # Preserve every prior native record, manifest, raw row and failure file, not only old pass summaries.
 legacy=hashes(PRIOR,'doc/results')
 for p,h in legacy.items():assert sha((ROOT/p).read_bytes())==h,p
 put(OUT/'identity.json',{'remote_commit':REMOTE,'accepted_v3_tree':PRIOR,'corpus_hashes':corpus,'mirror_hashes':mirror,'corpus_byte_exact_remote':True,'mirrors_byte_exact':True,'prior_entry_files_unchanged':len(old),'added_entry_files':added,'implementation':runtime,'source_evidence_byte_exact_remote':evidence,'legacy_result_files_preserved':legacy,'AIK_publication_receipt_preserved':ref(AIK/'publication.json')})
 plan={'schema_version':'experiment-validation-plan/v1','scope':SCOPE,'criteria':{}}
 criteria={
 'implementation':('Inspect actual evaluator, knowledge/index and all imported guard/ingestion/result modules; compare with accepted v3 source.','Bound implementation is byte-exact v3; exact published SQLite IDs and candidate exclusion hold.'),
 'reference_boundary':('Compare current 48 AIK rows with v3 frozen rows; inspect two holdout registries before card bodies; preserve new-card source results without rederivation.','Fixed cases/targets/budget, all changed ranks and failures explicit; no new scientific applicability claim.'),
 'data_integrity':('Check full corpus/mirror equality with 013, prior entries/evidence immutability and before/after dependency hashes. Recompute actual upstream retrieval denominators.','80 published plus 2 candidates; four reserved records unchanged; eight legacy rows/backend despite 21-case prose; no lost old files.'),
 'numerical_sanity':('Recompute default/domain hit counts from unique backend/case rows and check fulltext and character budget.','Exactly 24 rows/mode and 12 cases/backend; booleans and counts agree; no nonfinite JSON metrics.'),
 'measurement_validity':('Distinguish new bounded development retrieval/index tests from upstream scientific metadata and historical broad-suite results.','No current full-suite/catalog, unseen model, automatic recovery or performance claim; all failures retained.'),
 'reproducibility':('Bind code, protocol, input corpus/cases, old row baselines, raw outputs, commands and environment; independent reviewer inspects and cross-checks.','Dependencies stable throughout this round; native record remains pending until independent verification.')}
 for k,(procedure,acceptance) in criteria.items():plan['criteria'][k]={'procedure':procedure,'acceptance':acceptance,'allow_not_applicable':False}
 put(OUT/'validation-plan.json',plan)
 inputs=[ROOT/p for p in sorted(set(corpus)|set(mirror)|set(evidence))]
 inputs += [V3/n for n in ('record.json','manifest.json','summary.json','aik-default.json','aik-domain.json','index-tests.log')]
 code=[ROOT/p for p in codepaths]+[Path(__file__)]
 deps=sorted(set(inputs+code+[OUT/'validation-plan.json']))
 before={ref(p)['path']:ref(p)['sha256'] for p in deps};put(OUT/'dependencies-before.json',before)
 put(OUT/'environment.json',{'started_at_utc':started,'python':sys.version,'executable':sys.executable,'sqlite_version':sqlite3.sqlite_version,'platform':platform.platform(),'machine':platform.machine(),'network_used':False,'external_model_calls':False,'timing_claims':False,'dependencies':'Python standard library and SQLite FTS5','temporary_files':'Within the result directory; temporary test corpora removed by their owners.'})
 sys.path.insert(0,str(ROOT))
 from agent_runtime.knowledge import KnowledgeStore,KnowledgeError
 from agent_runtime.knowledge_index import build_index,indexed_search
 from agent_runtime.result_store import ResultStore
 from agent_runtime.result_validation import inspect_result
 store=KnowledgeStore(ROOT/'knowledge');assert store.snapshot=='a4fb031c348a33dcfbcf067df3911a56b0db763ffcaf507897e70fd9cb5b2791'
 candidate_ids={k for k,d in metas.items() if d['status']=='candidate'};published_ids=set(metas)-candidate_ids
 exclusion=[]
 with tempfile.TemporaryDirectory(prefix='index-candidate-',dir=OUT) as tmp:
  db=Path(tmp)/'index.sqlite';built=build_index(store,db)
  with sqlite3.connect(db) as con:indexed_ids={r[0] for r in con.execute('SELECT id FROM docs')}
  assert indexed_ids==published_ids
  for kid in sorted(candidate_ids):
   try:store.get(kid)
   except KnowledgeError:blocked=True
   else:blocked=False
   query=kid+' '+metas[kid]['title']
   files={r['id'] for r in store.search(query,limit=20)['results']}
   sql={r['id'] for r in indexed_search(store,db,query,limit=20)['results']}
   assert blocked and kid not in files|sql|indexed_ids
   exclusion.append({'id':kid,'get_blocked':blocked,'absent_from_files_search':True,'absent_from_sqlite_search':True,'absent_from_index':True})
 put(OUT/'candidate-exclusion.json',{'snapshot':store.snapshot,'index_build':built,'published_ids':sorted(published_ids),'indexed_ids':sorted(indexed_ids),'candidates':exclusion})
 cp=run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_knowledge_index.py','-v'],'index-tests')
 assert re.search(r'Ran 10 tests',cp.stderr) and '\nOK\n' in cp.stderr
 aik={};diffs={}
 for mode in ('default','domain'):
  cmd=[sys.executable,'-B',AIK/'check_domain_recovery.py','--repo',ROOT,'--corpus',ROOT/'knowledge','--cases',AIK/'evaluation/frozen_tasks.json','--output',OUT/f'aik-{mode}.json']
  if mode=='default':cmd.append('--unscoped')
  run(cmd,'aik-'+mode,allowed=(0,1))
  data=json.loads((OUT/f'aik-{mode}.json').read_text());prior=json.loads((V3/f'aik-{mode}.json').read_text())
  assert data['snapshot']==store.snapshot and data['cases_sha256']==prior['cases_sha256'] and data['script_sha256']==prior['script_sha256']
  key=lambda r:(r['backend'],r['case'])
  rows=data['rows'];base={key(r):r for r in prior['rows']}
  assert len(rows)==24 and len({key(r) for r in rows})==24 and set(base)=={key(r) for r in rows}
  changes=[]
  for r in rows:
   oldr=base[key(r)];assert (r['query'],r['target'])==(oldr['query'],oldr['target'])
   assert r['fulltext_unchanged'] and r['budget']['used_chars']<=20000
   assert candidate_ids.isdisjoint(r['raw_ids']+r['context_ids'])
   fields=[k for k in ('raw_ids','context_ids','hit','fulltext_unchanged','skipped') if r[k]!=oldr[k]]
   if fields:changes.append({'backend':r['backend'],'case':r['case'],'fields':fields,'prior':{k:oldr[k] for k in fields},'current':{k:r[k] for k in fields}})
  diffs[mode]=changes
  aik[mode]={'rows':24,'context_hits':sum(r['hit'] for r in rows),'raw_top3_hits':sum(r['target'] in r['raw_ids'] for r in rows),'failures':[{'backend':r['backend'],'case':r['case']} for r in rows if not r['hit']],'changed_rows':len(changes),'new_hit_regressions':[{'backend':r['backend'],'case':r['case']} for r in rows if base[key(r)]['hit'] and not r['hit']]}
 put(OUT/'aik-v3-comparison.json',{'baseline_snapshot':prior['snapshot'],'current_snapshot':store.snapshot,'changes':diffs})
 upstream={}
 for topic in ('centering','dependence'):
  folder=ROOT/'docs/knowledge_learning'/('2026-10-07-'+topic)
  scientific=json.loads((folder/'checks.json').read_text());reg=json.loads((folder/'regression.json').read_text());ret=json.loads((folder/'retrieval.json').read_text())
  actual={}
  for backend,d in reg['backends'].items():
   rows=d['queries'];positive=[r for r in rows if r['expected']];assert len(rows)==8 and len(positive)==7
   mean=sum(r['recall_at_3'] for r in positive)/len(positive);context=sum(r['context_recall'] for r in positive)/len(positive)
   assert abs(mean-d['mean_recall_at_3'])<1e-15 and abs(context-d['mean_context_recall'])<1e-15
   actual[backend]={'total':len(rows),'positive':len(positive),'mean_recall_at_3':mean,'mean_context_recall':context,'raw_failures':[{'case':r['case'],'recall_at_3':r['recall_at_3']} for r in positive if r['recall_at_3']<1]}
  newqueries={b:{'count':len(d['queries']),'raw_target_hits':sum(r['recall_at_3']==1 for r in d['queries']),'context_status_counts':dict(collections.Counter(r['context_status'] for r in d['queries']))} for b,d in ret['backends'].items()}
  upstream[topic]={'scientific_checks_reported':scientific.get('count',scientific.get('checks')),'scientific_passed_reported':scientific['passed'],'scientific_scope':scientific['scope'],'scientific_provenance_only':True,'scientific_checks_rerun':False,'raw_regression_snapshot':reg['snapshot'],'regression_scope_is_current_snapshot':reg['snapshot']==store.snapshot,'actual_regression_scope':actual,'prose_claimed_old_cases':21,'inherited_scope_mismatch':True,'upstream_new_development_queries':newqueries,'new_development_queries_rerun':False,'publication':ref(folder/'publication.json')}
 put(OUT/'upstream-provenance-scope.json',upstream)
 after={ref(p)['path']:ref(p)['sha256'] for p in deps};assert before==after,'Dependencies changed during measurement.'
 # Check historical results again as they are not rewritten into this manifest.
 assert all(sha((ROOT/p).read_bytes())==h for p,h in legacy.items())
 put(OUT/'dependencies-after.json',after);put(OUT/'commands.json',COMMANDS)
 put(OUT/'reuse-decisions.json',{'decision':'verify_delta','prior_result_search':ref(OUT/'prior-result-search.json'),'baseline':ref(V3/'summary.json'),'basis':'Current source paths are byte-exact the accepted v3 tree; corpus adds exactly two card pairs and expected metadata. Historical full-suite and v3 results remain scoped to their measured corpora. Current independent reviewer still required.','knowledge_access':{'status':'not_needed','reason':'Task checks corpus identity and deterministic retrieval behavior, not scientific applicability; authored fixed cases are executed unchanged.'},'not_rerun':['full 730-test suite','all legacy catalogs','scientific proofs/experiments/research','old manual recovery'],'upstream_scope':ref(OUT/'upstream-provenance-scope.json'),'excluded_work':'Separate read-only SEM candidate investigation is not imported.'})
 completed=datetime.now(timezone.utc).isoformat()
 summary={'status':'measured-pending-independent-review','scope':SCOPE,'remote_commit':REMOTE,'accepted_v3_tree':PRIOR,'current_snapshot':store.snapshot,'counts':dict(counts),'corpus_files':len(corpus),'corpus_byte_exact_remote':True,'mirrors_byte_exact':True,'prior_entry_files_unchanged':len(old),'added_entry_files':added,'reserved_holdouts_preserved':4,'candidate_exclusion':exclusion,'targeted_index_tests':{'run':10,'passed':10},'AIK':aik,'AIK_differences':ref(OUT/'aik-v3-comparison.json'),'upstream_provenance_scope':ref(OUT/'upstream-provenance-scope.json'),'upstream_legacy_cases_per_backend':8,'source_evidence_files_preserved':len(evidence),'prior_result_files_preserved':len(legacy),'AIK_publication_receipt_preserved':True,'dependencies_stable':True,'completed_at_utc':completed,'limitations':['Native registration remains pending independent review.','Scientific 31/39 check results are upstream provenance, not newly rederived or independently scientifically accepted here.','Upstream reports say 21 legacy queries but each raw regression has eight per backend, seven positive.','Centering retrieval was measured on 79 published + 2 candidates; dependence on current 80 + 2.','Fresh AIK questions are authored development cases; known misses remain failures, not automatic recovery.','No full suite/catalog rerun, new research, unseen model test, GPU, token savings, deployment or performance claim.','Metadata/source-URL collision checks cannot establish absence of all semantic leakage.']}
 put(OUT/'summary.json',summary)
 contract={'result_id':OUT.name,'producer_task_id':'verify-v4-corpus-delta','producer_actor':'v4-corpus-verifier','manifest_path':(OUT/'manifest.json').relative_to(ROOT).as_posix(),'validation_plan':ref(OUT/'validation-plan.json'),'scope':SCOPE}
 raw=[OUT/n for n in ('identity.json','holdout-metadata-gate.json','candidate-exclusion.json','index-tests.log','aik-default.json','aik-default.log','aik-domain.json','aik-domain.log','aik-v3-comparison.json','upstream-provenance-scope.json','dependencies-before.json','dependencies-after.json','commands.json','prior-result-search.json')]
 manifest={**contract,'schema_version':'experiment-result/v1','run_id':OUT.name,'code_revision':REMOTE+' plus unchanged accepted document-governance v3 dependencies; exact bytes bound','execution':{'command':['python -B '+Path(__file__).relative_to(ROOT).as_posix()],'environment_description':'Local deterministic Python standard-library/SQLite FTS5 retrieval and identity checks; no scientific experiment or performance comparison.','seeds':[0],'repeats':1,'started_at':started,'completed_at':completed},'artifacts':{'code':[ref(p) for p in code],'inputs':[ref(p) for p in inputs],'config':[ref(OUT/'validation-plan.json')],'raw_data':[ref(p) for p in raw],'outputs':[ref(OUT/'summary.json'),ref(OUT/'reuse-decisions.json')],'environment':[ref(OUT/'environment.json')]},'metrics':[{'name':k,'value':v,'unit':'count'} for k,v in [('published_entries',80),('candidate_entries_excluded',2),('reserved_holdout_metadata_preserved',4),('targeted_index_tests_passed',10),('aik_default_context_hits',aik['default']['context_hits']),('aik_domain_context_hits',aik['domain']['context_hits']),('aik_rows_per_mode',24),('upstream_legacy_cases_per_backend',8)]]}
 put(OUT/'contract.json',contract);put(OUT/'manifest.json',manifest)
 ResultStore(ROOT).register(contract,measured_at=completed)
 rec=json.loads((OUT/'record.json').read_text());put(OUT/'registration-receipt.json',{'origin':rec['origin'],'status':rec['validation_at_registration']['status'],'manifest':ref(OUT/'manifest.json'),'record':ref(OUT/'record.json')})
 inspection=inspect_result(ROOT,contract);assert inspection['status']=='pending',inspection
 put(OUT/'integrity-no-provider.json',inspection)
 put(REPORT/'summary.json',{'status':summary['status'],'result_summary':ref(OUT/'summary.json'),'contract':ref(OUT/'contract.json'),'manifest':ref(OUT/'manifest.json'),'counts':dict(counts),'index_tests_passed':10,'aik_context_hits':{k:v['context_hits'] for k,v in aik.items()},'aik_pairs_per_mode':24,'upstream_legacy_cases_per_backend':8,'independent_review_required':True})
 print(json.dumps(summary,ensure_ascii=False,indent=2))
 print(json.dumps(json.loads((OUT/'registration-receipt.json').read_text()),indent=2))
if __name__=='__main__':main()
