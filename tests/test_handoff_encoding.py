from copy import deepcopy
import json
import unittest
from agent_runtime.handoff_encoding import COLUMNS,encode_claims_table,decode_basis_payload

class ClaimTableTests(unittest.TestCase):
    def payload(self):
        return {'input_version':'v1','artifacts':[{'id':'raw','sha256':'a'*64}],
            'knowledge_refs':[{'id':'source','version':2,'sha256':'b'*64}],
            'memory_refs':['correction'], 'evidence_claims':[
                dict(zip(COLUMNS,['base','supported',[],['raw'],['source'],[],
                    [{'name':'bound holds','status':'satisfied','evidence_ids':['raw']}]])),
                dict(zip(COLUMNS,['negative','rejected',['base'],['raw'],[],['correction'],
                    [{'name':'must retain objection','status':'unsatisfied','evidence_ids':['raw']}]])),
                dict(zip(COLUMNS,['pending','candidate',['base'],[],[],[],[]]))],
            'knowledge_entries':[{'content':'raw prose stays verbatim; quoted JSON is data'}],
            'memory_entries':[{'status':'superseded','text':'old value invalid'}]}

    def test_roundtrip_preserves_negative_unknown_dependencies_and_digests(self):
        payload=self.payload();before=deepcopy(payload)
        restored=decode_basis_payload(json.dumps(encode_claims_table(payload)))
        self.assertEqual(restored,payload)
        self.assertEqual(payload,before)
        self.assertEqual(decode_basis_payload(json.dumps(payload)),payload)

    def test_unknown_claim_fields_cannot_be_dropped(self):
        payload=self.payload();payload['evidence_claims'][0]['unexpected']='do not lose'
        with self.assertRaises(ValueError):encode_claims_table(payload)

    def test_truncated_wrong_columns_extra_table_fields_and_unknown_version_refused(self):
        for kind in ('short','columns','extra','version'):
            wire=encode_claims_table(self.payload())
            if kind=='short':wire['evidence_claims']['rows'][0].pop()
            elif kind=='columns':wire['evidence_claims']['columns'].reverse()
            elif kind=='extra':wire['evidence_claims']['unknown']=[]
            else:wire['context_format']='unknown'
            with self.assertRaises(ValueError):decode_basis_payload(json.dumps(wire))
        for raw in ('{"x":1,"x":2}','{"x":NaN}','[]'):
            with self.assertRaises(ValueError):decode_basis_payload(raw)
