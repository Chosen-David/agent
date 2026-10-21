"""Deterministic minimum complete encoding; no scalar/authority shortcuts."""
from copy import deepcopy
import json
import unittest
from agent_runtime.handoff_encoding import (COLUMNS,MEMORY_COLUMNS,choose_basis_payload,
    encode_claims_table,encode_basis_tables,decode_basis_payload)


def payload(count):
    return {'evidence_claims':[dict(zip(COLUMNS,[str(i),'rejected',[],[],[],[],[]])) for i in range(count)],
            'memory_entries':[dict(zip(MEMORY_COLUMNS,[str(i),'observation','保留 🧠\n<|endoftext|>',
                'fixture',{'types':[True,1,1.0,None]},'verified','active','fixed',None,[]])) for i in range(count)]}


class AutoFormatTests(unittest.TestCase):
    def test_exhaustive_feasible_minimum_types_and_input_unchanged(self):
        for size in (0,1,2,32):
            value=payload(size);before=deepcopy(value)
            candidates=[json.dumps(f(value),ensure_ascii=False,sort_keys=True,separators=(',',':'))
                        for f in (deepcopy,encode_claims_table,encode_basis_tables)]
            for counter in (len,lambda s:7):
                expected=min(enumerate(candidates),key=lambda p:(counter(p[1]),len(p[1]),p[0]))[1]
                text,tokens=choose_basis_payload(value,counter)
                self.assertEqual(text,expected);self.assertEqual(tokens,counter(text))
                self.assertEqual(json.dumps(decode_basis_payload(text),sort_keys=True),json.dumps(value,sort_keys=True))
            self.assertEqual(value,before)

    def test_caps_filter_before_selection_and_counter_is_strict(self):
        value=payload(8)
        text,n=choose_basis_payload(value,len)
        self.assertEqual(choose_basis_payload(value,len,max_chars=len(text),max_tokens=n),(text,n))
        with self.assertRaises(ValueError):choose_basis_payload(value,len,max_chars=1)
        for counter in (None,lambda s:True,lambda s:-1,lambda s:1.5):
            with self.assertRaises(ValueError):choose_basis_payload(value,counter)

    def test_unknown_fields_fall_back_complete_not_truncated(self):
        value=payload(4);value['memory_entries'][0]['future']='keep every field'
        text,_=choose_basis_payload(value,len)
        self.assertEqual(decode_basis_payload(text),value)
        value['evidence_claims'][0]['future']={'x':True}
        text,_=choose_basis_payload(value,len)
        self.assertEqual(json.loads(text),value)
