"""Deterministic, payload-only transport accounting; never model/cash accounting."""
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import tiktoken
import test_handoff_basis as fixture
from agent_runtime.handoff_basis import make_token_counter
from agent_runtime.handoff_encoding import (COLUMNS,MEMORY_COLUMNS,
    encode_claims_table,encode_basis_tables,decode_basis_payload)


def dump(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))


def write(path,value):
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode())


def fixtures():
    output={}
    for name,count in [('empty',0),('singleton',1),('short-32',32),('unique-32',32),
                       ('long-8',8),('unicode-8',8)]:
        entries=[];claims=[]
        for i in range(count):
            content=f'Observation {i}: retain unit and limitation.'
            if name=='long-8':content+=' A long unique premise '+str(i)*3+'.'+' original wording.'*256
            if name=='unicode-8':content=f'更正 {i}：单位需核验。\n🧠 "rows" <|endoftext|> \\路径 e\u0301'
            source=f'fixture:source/{i}' if name=='unique-32' else 'fixture:shared-source'
            scope={'task_id':f'T{i}'} if name=='unique-32' else {'task_id':'T1'}
            entries.append(dict(zip(MEMORY_COLUMNS,[f'm{i}','observation',content,source,
                scope,'verified',('active','candidate','superseded','stale')[i%4],
                '2026-10-21T00:00:00Z',None,[f'm{i-1}'] if i else []])))
            claims.append(dict(zip(COLUMNS,[f'c{i}',('supported','candidate','rejected')[i%3],
                [f'c{i-1}'] if i else [],[],[],[f'm{i}'],[]])))
        output[name]={'input_version':'v1','knowledge_refs':[],'memory_refs':[e['id'] for e in entries],
            'evidence_claims':claims,'artifacts':[],'knowledge_entries':[],'memory_entries':entries}
    return output


def measure(output):
    output.mkdir(parents=True,exist_ok=True)
    config=json.loads((Path(__file__).parent/'config.json').read_text(encoding='utf-8'))
    if tiktoken.__version__!=config['tiktoken_version']:raise ValueError('pinned tokenizer required')
    counter=make_token_counter(config['encoding']);encoding=tiktoken.get_encoding(config['encoding'])
    inputs=fixtures()
    if list(inputs)!=config['cases']:raise ValueError('complete configured cases required')
    raw=[]
    for name,payload in inputs.items():
        formats={};before=dump(payload)
        for fmt,encoder in [('json',deepcopy),('claims-table/v1',encode_claims_table),
                            ('basis-tables/v1',encode_basis_tables)]:
            text=dump(encoder(payload))
            if dump(decode_basis_payload(text))!=before:raise ValueError('JSON-value roundtrip mismatch')
            formats[fmt]={'payload':text,'tokens':counter(text),'bytes':len(text.encode()),'chars':len(text)}
        if dump(payload)!=before:raise ValueError('input mutation')
        raw.append({'case':name,'formats':formats})
    # Real entry point, no bypass of Mailbox, dependency hydration or budgets.
    f=fixture.BasisTests();f.setUp()
    try:
        seq=f.send()
        ordinary=f.box.prepare_context('writer',seq,f.request,token_counter=counter,max_chars=200000)
        request={**f.request,'context_format':'basis-tables/v1','context_tokenizer':config['encoding']}
        table=f.box.prepare_context('review',seq,request,token_counter=counter,max_chars=200000)
        if dump(decode_basis_payload(table['payload']))!=dump(json.loads(ordinary['payload'])):
            raise ValueError('Mailbox roundtrip mismatch')
        full=table['usage']['tokens']
        f.box.prepare_context('review',seq,request,token_counter=counter,max_tokens=full,max_chars=200000)
        try:f.box.prepare_context('review',seq,request,token_counter=counter,max_tokens=full-1,max_chars=200000)
        except ValueError:budget_refused=True
        else:raise ValueError('complete token budget bypassed')
        mailbox={'ordinary':ordinary,'table':table,'exact_budget_accepted':True,
                 'one_token_short_refused':budget_refused}
    finally:f.doCleanups()
    ranks=hashlib.sha256()
    for token,rank in sorted(encoding._mergeable_ranks.items(),key=lambda item:item[1]):
        ranks.update(len(token).to_bytes(4,'big'));ranks.update(token);ranks.update(rank.to_bytes(4,'big'))
    env={'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),
         'sqlite':sqlite3.sqlite_version,'tiktoken':tiktoken.__version__,'encoding':encoding.name,
         'ranks_sha256':ranks.hexdigest(),'rank_count':len(encoding._mergeable_ranks),
         'pattern':encoding._pat_str,'special_tokens':encoding._special_tokens,
         'scope':config['measurement'],'repeats':1,'seed':config['seed']}
    package=Path(tiktoken.__file__).parent
    env['tokenizer_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(package.glob('*')) if p.is_file()}
    code=set()
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path:
            path=Path(path).resolve()
            if path.is_relative_to(ROOT) and '.agent-runs' not in path.parts and path.suffix=='.py':
                code.add(path.relative_to(ROOT).as_posix())
    deps={'code':sorted(code),'corpus':[p.relative_to(ROOT).as_posix()
        for p in sorted((ROOT/'knowledge').rglob('*')) if p.is_file() and '__pycache__' not in p.parts]}
    write(output/'inputs.json',inputs);write(output/'raw.json',{'cases':raw,'mailbox':mailbox})
    write(output/'environment.json',env);write(output/'dependencies.json',deps)
    print(json.dumps({'status':'pending-independent-validation','cases':len(raw),'output':str(output)}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    measure(parser.parse_args().output)
