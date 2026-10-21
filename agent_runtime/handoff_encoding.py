"""Opt-in, lossless claim-table context. Not evidence acceptance or compression of prose."""
from copy import deepcopy

from .external_json import strict_json

FORMAT='claims-table/v1'
COLUMNS=('id','status','depends_on','artifact_ids','knowledge_ids','memory_ids','assumptions')

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

def decode_basis_payload(text):
    """Restore exact JSON values. Caller still must revalidate source/freshness/authority."""
    if not isinstance(text,str) or len(text)>200000:
        raise ValueError('bounded serialized context required')
    data=strict_json(text.encode('utf-8'))
    if not isinstance(data,dict):raise ValueError('basis object required')
    if 'context_format' not in data:return data
    if data.pop('context_format')!=FORMAT:raise ValueError('unsupported context format')
    table=data.get('evidence_claims')
    if (not isinstance(table,dict) or set(table)!={'columns','rows'} or
            table['columns']!=list(COLUMNS) or not isinstance(table['rows'],list)):
        raise ValueError('exact claim table schema required')
    claims=[]
    for row in table['rows']:
        if not isinstance(row,list) or len(row)!=len(COLUMNS):raise ValueError('truncated/extended claim row')
        claims.append(dict(zip(COLUMNS,row)))
    data['evidence_claims']=claims
    return data
