"""Opt-in lossless basis tables; no evidence acceptance or prose summarization."""
from copy import deepcopy
import json

from .external_json import strict_json

FORMAT='claims-table/v1'
COLUMNS=('id','status','depends_on','artifact_ids','knowledge_ids','memory_ids','assumptions')
BASIS_TABLE_FORMAT='basis-tables/v1'
AUTO_FORMAT='auto-lossless/v1'
MEMORY_COLUMNS=('id','kind','content','source','scope','evidence','status','created_at','document_refs','deps')

def encode_claims_table(payload):
    if not isinstance(payload,dict) or 'context_format' in payload:
        raise ValueError('unencoded basis object required')
    claims=payload.get('evidence_claims')
    if not isinstance(claims,list) or any(not isinstance(c,dict) or set(c)!=set(COLUMNS) for c in claims):
        raise ValueError('complete claim objects required; never drop unknown fields')
    result=deepcopy(payload)
    result['context_format']=FORMAT
    result['evidence_claims']={'columns':list(COLUMNS),'rows':[[deepcopy(c[k]) for k in COLUMNS] for c in claims]}
    return result

def encode_basis_tables(payload):
    """Share claim/memory column names, retaining every original JSON value."""
    result=encode_claims_table(payload)
    entries=payload.get('memory_entries')
    if not isinstance(entries,list) or any(not isinstance(e,dict) or set(e)!=set(MEMORY_COLUMNS) for e in entries):
        raise ValueError('complete memory objects required; never drop unknown fields')
    result['context_format']=BASIS_TABLE_FORMAT
    result['memory_entries']={'columns':list(MEMORY_COLUMNS),
                              'rows':[[deepcopy(e[k]) for k in MEMORY_COLUMNS] for e in entries]}
    # Table wrappers add nesting. Reject packets our bounded strict decoder
    # cannot restore, rather than returning a successful unusable handoff.
    decode_basis_payload(json.dumps(result,ensure_ascii=False,sort_keys=True,separators=(',',':')))
    return result

def _decode_table(table, columns, label):
    if (not isinstance(table,dict) or set(table)!={'columns','rows'} or
            table['columns']!=list(columns) or not isinstance(table['rows'],list)):
        raise ValueError('exact '+label+' table schema required')
    entries=[]
    for row in table['rows']:
        if not isinstance(row,list) or len(row)!=len(columns):
            raise ValueError('truncated/extended '+label+' row')
        entries.append(dict(zip(columns,row)))
    return entries

def choose_basis_payload(payload, token_counter, *, max_chars=200000, max_tokens=None):
    """Opt-in to all three v1 wire formats; minimize (tokens, chars, order).

    Incompatible table schemas fall back to complete JSON. No field is dropped.
    All candidates include their headers, must decode, and must fit both caps.
    """
    if not callable(token_counter):raise ValueError('auto format requires actual token_counter')
    candidates=[]
    for order,encoder in enumerate((deepcopy,encode_claims_table,encode_basis_tables)):
        try:
            text=json.dumps(encoder(payload),ensure_ascii=False,sort_keys=True,separators=(',',':'))
            decode_basis_payload(text)
        except ValueError:
            continue
        tokens=token_counter(text)
        if type(tokens) is not int or tokens<0:
            raise ValueError('token_counter must return nonnegative integer')
        if len(text)<=max_chars and (max_tokens is None or tokens<=max_tokens):
            candidates.append((tokens,len(text),order,text))
    if not candidates:raise ValueError('no complete supported basis fits character/token budget')
    tokens,_,_,text=min(candidates)
    return text,tokens

def decode_basis_payload(text):
    """Restore exact JSON values. Caller still must revalidate source/freshness/authority."""
    if not isinstance(text,str) or len(text)>200000:
        raise ValueError('bounded serialized context required')
    data=strict_json(text.encode('utf-8'))
    if not isinstance(data,dict):raise ValueError('basis object required')
    if 'context_format' not in data:return data
    context_format=data.pop('context_format')
    if context_format not in (FORMAT,BASIS_TABLE_FORMAT):raise ValueError('unsupported context format')
    data['evidence_claims']=_decode_table(data.get('evidence_claims'),COLUMNS,'claim')
    if context_format==BASIS_TABLE_FORMAT:
        data['memory_entries']=_decode_table(data.get('memory_entries'),MEMORY_COLUMNS,'memory')
    return data
