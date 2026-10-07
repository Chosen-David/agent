#!/usr/bin/env python3
"""Cross-check metrics, bind final phases, and register native pending evidence."""
import hashlib,json,math,statistics,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
REPORT=ROOT/'docs/document_architecture_validation/knowledge/upstream-v2'
BASE='907890831929a5d200d3fb64c6299449391a1ee8'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def gitjson(path):return json.loads(subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT))

def main():
 assert not (OUT/'manifest.json').exists()
 initial=json.loads((OUT/'summary.json').read_text());supp=json.loads((OUT/'supplement.json').read_text())
 comp=json.loads((OUT/'catalog-comparison.json').read_text());pres=json.loads((OUT/'preservation.json').read_text())
 checks=[]
 for p in sorted(OUT.glob('*.json')):
  j=json.loads(p.read_text())
  if not isinstance(j,dict) or 'backends' not in j:continue
  for backend,b in j['backends'].items():
   rows=b['queries'];rec=[];ctx=[];rr=[]
   for r in rows:
    expected=r['expected'];actual=r['actual'];context=r['context_ids']
    if expected:
     hit=[x for x in expected if x in actual]
     v=len(hit)/len(expected); c=sum(x in context for x in expected)/len(expected);rank=1/min(actual.index(x)+1 for x in hit) if hit else 0
     assert r['recall_at_3']==v and r['context_recall']==c and r['reciprocal_rank']==rank
     rec.append(v);ctx.append(c);rr.append(rank)
    else:assert r['no_hit_correct']==(not actual)
   assert statistics.mean(rec)==b['mean_recall_at_3']
   assert statistics.mean(ctx)==b['mean_context_recall']
   assert statistics.mean(rr)==b['mean_reciprocal_rank']
   checks.append({'file':p.name,'backend':backend,'rows':len(rows),'mean_recall_at_3':statistics.mean(rec),'mean_context_recall':statistics.mean(ctx),'mean_reciprocal_rank':statistics.mean(rr)})
 # Independently audit additive metadata, rather than allow any change by filename.
 coverage=gitjson('knowledge/coverage.json'); current=json.loads((ROOT/'knowledge/coverage.json').read_text())
 ai={'ai.speculative-sampling-residual-exactness','ai.speculative-decoding-cost-bound'}
 def remove_ai(obj):
  if isinstance(obj,list):return [remove_ai(x) for x in obj if not(isinstance(x,str) and x in ai)]
  if isinstance(obj,dict):return {k:remove_ai(v) for k,v in obj.items()}
  return obj
 assert remove_ai(current)==coverage
 base_state=gitjson('knowledge/learning_state.json');state=json.loads((ROOT/'knowledge/learning_state.json').read_text());removed=[]
 def remove_history(obj):
  if isinstance(obj,list):
   out=[]
   for x in obj:
    if isinstance(x,dict) and x.get('round')=='2026-10-07-ai-algorithms-combined-release':removed.append(x)
    else:out.append(remove_history(x))
   return out
  if isinstance(obj,dict):return {k:remove_history(v) for k,v in obj.items()}
  return obj
 assert remove_history(state)==base_state and len(removed)==1
 metrics={'metric_recomputation_passed':True,'catalog_outputs_checked':len(checks)//2,'backend_outputs_checked':len(checks),'query_backend_rows_checked':sum(x['rows'] for x in checks),'checks':checks,'coverage_only_two_added_ids':True,'learning_state_only_one_added_history':True,'upstream_cursors_priorities_history_preserved':True,'new_history':removed[0]}
 write(OUT/'metric-and-metadata-audit.json',metrics)
 # Binding verifies original retrieval semantics remain identical after test-only correction.
 deps=json.loads((OUT/'dependencies-before.json').read_text());changes={p:{'before':h,'after':sha(ROOT/p)} for p,h in deps.items() if sha(ROOT/p)!=h}
 assert set(changes)=={'tests/test_knowledge_index.py'},changes
 fixedtest=supp['dependencies_before']['tests/test_knowledge_index.py'];assert fixedtest==sha(ROOT/'tests/test_knowledge_index.py')
 final={'schema_version':1,'status':'measured-pending-independent-release-review','base_commit':BASE,'task_refs':['AIK-03','DOC-04'],
  'snapshots':initial['snapshots'],'published_counts':initial['published_counts'],'candidate_counts':initial['unpublished_candidate_counts'],
  'old_entry_files_unchanged':152,'default_catalog_queries':58,'default_query_backend_pairs':116,'additional_context8_pairs':42,
  'no_new_per_query_regressions':True,'aik_default_context_hits':21,'aik_domain_context_hits':23,'aik_backend_cases':24,
  'manual_recovery_cases':3,'manual_recovery_max_used_chars':max(r['context']['budget']['used_chars'] for r in json.loads((OUT/'manual-recovery.json').read_text())['rows']),
  'known_failures':{'default_aik':['files:A12','sqlite:A03','sqlite:A12'],'domain_aik':['sqlite:A12'],'default_original_context':[6/7,6/7],'default_round2_context':[0.75,0.875],'context8_round2_context':[0.875,0.75],'default_morphology_context':[0,0.75],'context8_morphology_context':[0,1]},
  'fixture_correction':{'initial_failures':4,'actual907_reproduction_failures':4,'classification':'Inherited test expectation counted candidate as indexed; corrected published-only count and exact-ID exclusion; no runtime change.','changed_dependency':changes},
  'fresh_tests':{'knowledge':67,'handoff_basis_and_selective_context':34,'total':101,'passed':True},'isolated_plugin':supp['package_isolated'],
  'metric_recomputation_passed':True,'source_files_stable_except_documented_test_correction':True,'upstream_metadata_preserved':True,
  'limitations':initial['limitations'],'independent_review_required':True,'completed_at_utc':supp['completed_at_utc']}
 write(OUT/'final-summary.json',final);write(REPORT/'final-summary.json',final)
 scope=json.loads((OUT/'validation-plan.json').read_text())['scope']
 contract={'result_id':'combined-corpus-delta-v2-20261007','producer_task_id':'verify-corpus-delta','producer_actor':'corpus-delta-verifier','manifest_path':str((OUT/'manifest.json').relative_to(ROOT)),'validation_plan':ref(OUT/'validation-plan.json'),'scope':scope}
 # All generated raw data and derived results are centralized; references do not relocate history.
 allfiles=[p for p in sorted(OUT.glob('*')) if p.is_file()]
 exclude={'artifact-manifest.json','final-summary.json','metric-and-metadata-audit.json','validation-plan.json'}
 raw=[p for p in allfiles if p.suffix in ('.json','.log') and p.name not in exclude]
 codepaths=[*ROOT.glob('agent_runtime/*.py'),ROOT/'scripts/eval_knowledge.py',ROOT/'docs/knowledge_learning/2026-10-07-ai-algorithms/check_domain_recovery.py',ROOT/'docs/document_architecture_validation/knowledge/verify_manual_recovery.py',*ROOT.glob('tests/test_knowledge*.py'),ROOT/'tests/test_handoff_basis.py',ROOT/'tests/test_selective_context.py',*ROOT.glob('plugins/research-assistant/skills/model-with-knowledge/scripts/*.py'),*OUT.glob('*.py')]
 inputs=[*ROOT.glob('knowledge/**/*.json'),*ROOT.glob('knowledge/**/*.md'),*ROOT.glob('evals/knowledge/*.json'),ROOT/'docs/knowledge_learning/2026-10-07-ai-algorithms/evaluation/frozen_tasks.json',*ROOT.glob('plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/**/*.json'),*ROOT.glob('plugins/research-assistant/skills/model-with-knowledge/assets/knowledge/**/*.md')]
 manifest={**contract,'schema_version':'experiment-result/v1','run_id':OUT.name,'code_revision':'actual907-plus-staged-integration; hashes bound in artifacts',
  'execution':{'command':['python doc/results/combined-corpus-delta-v2-20261007/verify_delta.py','python doc/results/combined-corpus-delta-v2-20261007/verify_supplement.py','python doc/results/combined-corpus-delta-v2-20261007/finalize_evidence.py'],'environment_description':'Python standard library, CPU lexical and SQLite FTS5 retrieval. Separate baseline907 runtime subprocesses. Original failures retained; fixed fixture and isolated package measured separately. No performance claim.','repeats':1,'seeds':[0],'started_at':initial['started_at_utc'],'completed_at':supp['completed_at_utc']},
  'artifacts':{'code':[ref(p) for p in sorted(set(codepaths))],'inputs':[ref(p) for p in sorted(set(inputs))],'config':[ref(OUT/'validation-plan.json')],'raw_data':[ref(p) for p in raw],'outputs':[ref(OUT/'final-summary.json'),ref(OUT/'metric-and-metadata-audit.json')],'environment':[ref(OUT/'environment.json')]},
  'metrics':[{'name':n,'value':v,'unit':'count'} for n,v in [('default_backend_cases',116),('context8_backend_cases',42),('new_regressions',0),('aik_default_context_hits',21),('aik_domain_context_hits',23),('aik_backend_cases',24),('manual_recovery_cases',3),('fresh_test_passes',101),('preserved_initial_fixture_failures',4)]]}
 write(OUT/'contract.json',contract);write(OUT/'manifest.json',manifest)
 sys.path.insert(0,str(ROOT))
 from agent_runtime.result_store import ResultStore
 record=ResultStore(ROOT).register(contract,measured_at=supp['completed_at_utc'])
 write(OUT/'registration-receipt.json',{'record_ref':ref(OUT/'record.json'),'origin':record['origin'],'status':record['validation_at_registration']['status'],'manifest_ref':ref(OUT/'manifest.json'),'contract_ref':ref(OUT/'contract.json')})
 print(json.dumps({'status':record['validation_at_registration']['status'],'origin':record['origin'],'manifest':ref(OUT/'manifest.json'),'final_summary':ref(OUT/'final-summary.json'),'record':ref(OUT/'record.json')},indent=2))
if __name__=='__main__':main()
