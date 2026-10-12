import json,hashlib,sys,os
from pathlib import Path
SOURCES=['agent_runtime/artifact_context.py','scripts/artifact_context.py','agent_runtime/handoff_basis.py','agent_runtime/token_usage.py','tests/test_artifact_token_selection.py','tests/test_artifact_context.py','tests/test_artifact_identity.py','tests/test_artifact_edits.py']
TESTS=['tests.test_artifact_token_selection','tests.test_artifact_context','tests.test_artifact_identity','tests.test_artifact_edits'];COUNT=33
MECHANISM='Optional explicit-tokenizer whole-complete-packet selection among existing eligible lossless artifact codecs'
GLOBAL='Global rule: current independent verification is required; publication is blocked while status=pending.\nmetric_unit=tokens\n'
BEFORE=GLOBAL+''.join(f'old-{i:03}\n'+('a'*40)+'\n' for i in range(64))
AFTER=GLOBAL+''.join(f'new-{i:03}\n'+('a'*40)+'\n' for i in range(64))
TEXT=json.dumps({'before':BEFORE,'after':AFTER})+'\n'
QUESTION='Synthetic complete artifact pair. The before text is complete in this packet; after may be full text or edits applied in ascending start line order against original before lines, using each delete/insert exactly. Return all ordered new- labels from after, label count, metric_unit and publish=false while the global rule requires current independent verification and status=pending. Existing full/splice/edits representations preserve all text. JSON only; no tools.\n'
ORACLE_VALUE={'labels':[f'new-{i:03}' for i in range(64)],'label_count':64,'unit':'tokens','publish':False}
def counter(root):
 sys.path.insert(0,str(Path(root)/'.agent-runs/token-fifty-tools/tokenizer'))
 os.environ['TIKTOKEN_CACHE_DIR']=str(Path(root)/'.agent-runs/token-fifty-tools/bpe-cache')
 from agent_runtime.handoff_basis import make_token_counter
 return make_token_counter('o200k_base')
def build(root):
 from agent_runtime.artifact_context import compare_artifacts,restore_comparison,_json_text
 root=Path(root).resolve();refs=[]
 for n,text in [('before',BEFORE),('after',AFTER)]:
  rel='agent_doc/results/token-fifty-05-20261012/fixture-'+n+'.txt';f=root/rel
  if f.exists():assert f.read_bytes()==text.encode()
  else:f.write_bytes(text.encode())
  refs.append({'path':rel,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 c=counter(root);values={'baseline':compare_artifacts(root,*refs,multi_edit=True),'candidate':compare_artifacts(root,*refs,multi_edit=True,token_counter=c)}
 for v in values.values():assert restore_comparison(root,v,*refs)==(BEFORE,AFTER)
 assert values['baseline']['after']['representation']=='edits';assert values['candidate']['after']['representation']=='full'
 counts={n:c(_json_text(v)) for n,v in values.items()};assert counts['candidate']<counts['baseline']
 return {'report':{'run_id':'fifty-whole-packet-token-choice','complete_changed_labels':64,'encoding':c.tokenizer_name,'version':c.tokenizer_version,'local_packet_tokens':counts,'model_equivalence_claim':False},'oracle':ORACLE_VALUE,'prompts':{n:QUESTION+_json_text(v) for n,v in values.items()},'packets':values}
def replay(root):
 data=build(root)
 assert data['packets']['baseline']['before']==data['packets']['candidate']['before']
 assert data['packets']['baseline']['after']['ref']==data['packets']['candidate']['after']['ref']
 return {'exact_both_texts_restored':True,'all64labels_order_and_global_pending_rule_preserved':True,'candidate_more_characters_but_fewer_local_tokens':len(data['prompts']['candidate'])>len(data['prompts']['baseline']),'local_encoding_not_provider_mapping':True,'no_omissions_or_recovery_inference':True,'no_scientific_acceptance':True}
