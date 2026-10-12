import json,hashlib
from pathlib import Path
SOURCES=['agent_runtime/text_dictionary.py','scripts/text_dictionary.py','agent_runtime/token_usage.py','tests/test_text_dictionary.py']
TESTS=['tests.test_text_dictionary'];COUNT=16
MECHANISM='Complete exact arbitrary physical-LF-line dictionary and ordered index restoration, including nonconsecutive repeats'
P=Path(__file__).parent
TEXT=(P/'fixture.md').read_bytes().decode('utf8')
QUESTION='Synthetic complete advice meeting. For dictionary encoding reconstruct the text by concatenating dictionary[order[i]] for every index i in order; full encoding uses the whole text. Return all Issue- IDs in source order, their count, status of the last issue, metric_unit, and publish=false because global rule requires current independent verification and blocks publication. Transport does not accept advice or close meetings. JSON only; no tools.\n'
ORACLE_VALUE={'issue_ids':[f'Issue-{i:03}' for i in range(32)],'issue_count':32,'last_status':'pending','unit':'tokens','publish':False}
def build(root):
 from agent_runtime.text_dictionary import text_view,restore_text_view
 from agent_runtime.reference_context import _wire
 root=Path(root).resolve();rel='agent_doc/results/token-fifty-06-20261012/fixture.md';f=root/rel
 if f.exists():assert f.read_bytes()==TEXT.encode()
 else:f.write_bytes(TEXT.encode())
 sha=hashlib.sha256(f.read_bytes()).hexdigest()
 values={'baseline':text_view(root,rel,sha,full=True),'candidate':text_view(root,rel,sha)}
 for v in values.values():assert restore_text_view(root,_wire(v),rel,sha)==TEXT
 assert values['candidate']['encoding']=='dictionary'
 return {'report':{'run_id':'fifty-arbitrary-line-dictionary','complete_issue_count':32,'physical_lf_lines':65,'unique_lines':34,'fixture_origin':{'path':'.agent-runs/token-fifty-06/fixture.md','sha256':sha,'archive_path':rel}},'oracle':ORACLE_VALUE,'prompts':{n:QUESTION+_wire(v) for n,v in values.items()},'packets':values}
def replay(root):
 data=build(root);a=data['packets']['baseline'];b=data['packets']['candidate']
 assert a['source']==b['source'] and a['project_root']==b['project_root']
 assert ''.join(b['dictionary'][i] for i in b['order'])==TEXT
 assert len(data['prompts']['candidate'])<len(data['prompts']['baseline'])
 return {'complete_source_bytes_restored':True,'all32issue_IDs_order_owner_status_and_global_rules_preserved':True,'all65line_indexes_retained':True,'nonconsecutive_repeated_lines_shared':True,'no_omissions_or_authority':True}
