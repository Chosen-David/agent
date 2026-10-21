"""Exact JSON-value transport and real consumer gates for opt-in basis tables."""
from copy import deepcopy
import json
import os
import subprocess
import sys
import unittest

import test_handoff_basis as fixture
from agent_runtime.handoff_basis import basis_context
from agent_runtime.handoff_encoding import (BASIS_TABLE_FORMAT, COLUMNS, MEMORY_COLUMNS,
    encode_basis_tables, decode_basis_payload)


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


class MemoryTableTests(unittest.TestCase):
    def payload(self):
        return {'evidence_claims':[dict(zip(COLUMNS,['c','rejected',[],[],[],['m'],[]]))],
                'memory_entries':[dict(zip(MEMORY_COLUMNS,['m','correction',
                    '保留\n正文 <|endoftext|> "columns" 🧠','human:source',
                    {'x':[True,1,1.0,None,False,0]},'unverified','superseded',
                    '2026-10-21T00:00:00Z',{'sha256':'b'*64},['ancestor']]))],
                'memory_refs':['m'],'extra':{'keep':'unknown top-level values'}}

    def test_exact_values_types_input_and_empty_lists(self):
        for size in (0,1,8):
            value=self.payload();value['memory_entries']*=size
            before=deepcopy(value)
            wire=encode_basis_tables(value)
            # Canonical JSON distinguishes True/1, integer/float and null.
            self.assertEqual(canonical(decode_basis_payload(canonical(wire))),canonical(value))
            self.assertEqual(canonical(value),canonical(before))
            self.assertEqual(wire['context_format'],BASIS_TABLE_FORMAT)

    def test_unknown_missing_fields_and_preencoded_input_refused(self):
        for collection in ('evidence_claims','memory_entries'):
            for change in ('extra','missing','not-object'):
                value=self.payload()
                if change=='extra':value[collection][0]['unknown']='must not disappear'
                elif change=='missing':value[collection][0].pop('id')
                else:value[collection][0]=[]
                with self.assertRaises(ValueError):encode_basis_tables(value)
        with self.assertRaises(ValueError):encode_basis_tables(encode_basis_tables(self.payload()))

    def test_malformed_tables_and_strict_json_refused(self):
        for collection in ('evidence_claims','memory_entries'):
            for change in ('short','long','columns','extra','rows','row','missing'):
                value=encode_basis_tables(self.payload());table=value[collection]
                if change=='short':table['rows'][0].pop()
                elif change=='long':table['rows'][0].append('extra')
                elif change=='columns':table['columns'].reverse()
                elif change=='extra':table['unknown']=True
                elif change=='rows':table['rows']={}
                elif change=='row':table['rows'][0]={}
                else:value.pop(collection)
                with self.assertRaises(ValueError):decode_basis_payload(canonical(value))
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":1e400}',
                     '{"context_format":"basis-tables/v2"}', '[]'):
            with self.assertRaises(ValueError):decode_basis_payload(text)

    def test_encoder_refuses_packets_outside_decoder_bounds(self):
        value=self.payload();value['memory_entries'][0]['content']='x'*200000
        with self.assertRaises(ValueError):encode_basis_tables(value)
        for depth in (245,260):
            value=self.payload();nested=0
            for _ in range(depth):nested=[nested]
            value['memory_entries'][0]['scope']=nested
            if depth==245:
                self.assertEqual(canonical(decode_basis_payload(canonical(encode_basis_tables(value)))),
                                 canonical(value))
            else:
                with self.assertRaises(ValueError):encode_basis_tables(value)


class MemoryTableMailboxTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.BasisTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.request={**self.f.request,'context_format':BASIS_TABLE_FORMAT}

    def test_actual_mailbox_closure_budget_and_immutable_consumption(self):
        f=self.f;seq=f.send()
        plain=f.box.prepare_context('writer',seq,f.request)
        table=f.box.prepare_context('review',seq,self.request)
        restored=decode_basis_payload(table['payload'])
        self.assertEqual(canonical(restored),canonical(json.loads(plain['payload'])))
        self.assertEqual({e['id'] for e in restored['memory_entries']},{'input-v1','derived-v1'})
        count=len(table['payload'])
        f.box.prepare_context('review',seq,self.request,max_chars=count,token_counter=len,max_tokens=count)
        for kwargs in ({'max_chars':count-1},{'token_counter':len,'max_tokens':count-1}):
            with self.assertRaises(ValueError):f.box.prepare_context('review',seq,self.request,**kwargs)
        with self.assertRaises(ValueError):f.box.prepare_context('review',seq,f.request)

    def test_correction_and_reuse_do_not_bypass_freshness(self):
        f=self.f;seq=f.send();f.box.prepare_context('review',seq,self.request)
        known=['input-v1','derived-v1']
        pack=basis_context(f.root,f.record,self.request,known_memory_ids=known)
        self.assertEqual(decode_basis_payload(pack['payload'])['memory_entries'],[])
        f.memory.correct('input-v1','input-v2','corrected units','human:correction','unit error')
        with self.assertRaises(ValueError):f.box.prepare_context('review',seq,self.request)
        with self.assertRaises(ValueError):basis_context(f.root,f.record,self.request,known_memory_ids=known)

    def test_artifact_mutation_rejected(self):
        f=self.f;seq=f.send();f.box.prepare_context('review',seq,self.request)
        (f.root/'result.json').write_text('changed')
        with self.assertRaises(ValueError):f.box.prepare_context('review',seq,self.request)

    def test_cli_uses_the_same_format_and_roundtrip(self):
        f=self.f;seq=f.send()
        for name,value in [('plan',f.plan),('request',self.request)]:
            (f.root/(name+'.json')).write_text(canonical(value),encoding='utf-8')
        command=[sys.executable,'-m','agent_runtime.communication','--db',str(f.box.path),
            '--plan',str(f.root/'plan.json'),'--root',str(f.root),'context','review',str(seq),
            '--request',str(f.root/'request.json')]
        output=subprocess.run(command,capture_output=True,encoding='utf-8',
                              env={**os.environ,'PYTHONUTF8':'1'},timeout=60)
        self.assertEqual(output.returncode,0,output.stdout+output.stderr)
        actual=json.loads(output.stdout)
        plain=f.box.prepare_context('writer',seq,f.request)
        self.assertEqual(canonical(decode_basis_payload(actual['payload'])),
                         canonical(json.loads(plain['payload'])))
