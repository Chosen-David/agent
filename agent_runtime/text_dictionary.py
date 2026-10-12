"""Complete exact text line sharing, including nonconsecutive repeats."""
import hashlib
import re
from .advice_poll import _root
from .maintenance_observer import read_bound
from .reference_context import _budget, _json, _wire

SCHEMA='text-dictionary/v1'
SCOPE='complete exact text/order/terminators; restore before current evidence gates; no omission, assessment or meeting closure'
MAX_LINES=50000
MAX_BYTES=2*1024*1024

def _lines(text):
    # Only physical LF separates lines; standalone CR and Unicode separators
    # are data. Preserve CRLF and the final unterminated fragment exactly.
    parts=text.split('\n')
    return [p+'\n' for p in parts[:-1]]+([parts[-1]] if parts[-1] else [])

def _source(root,path,sha,max_chars):
    root=_root(root);_budget(max_chars)
    if type(sha) is not str or re.fullmatch('[0-9a-f]{64}',sha) is None:
        raise ValueError('source SHA256 required')
    raw=read_bound(root,path,max_bytes=MAX_BYTES)
    if hashlib.sha256(raw).hexdigest()!=sha:
        raise ValueError('source changed; refresh text binding')
    text=raw.decode('utf-8')
    if len(text)>max_chars:raise ValueError('expanded text exceeds character budget')
    lines=_lines(text)
    if len(lines)>MAX_LINES:raise ValueError('source line count exceeds budget')
    return root,raw,text,lines

def text_view(root,path,expected_sha256,*,full=False,max_chars=1000000):
    if type(full) is not bool:raise ValueError('full must be boolean')
    root,raw,text,lines=_source(root,path,expected_sha256,max_chars)
    common={'schema_version':SCHEMA,'project_root':str(root),
            'source':{'path':path,'sha256':expected_sha256},'scope':SCOPE}
    value={**common,'encoding':'full','text':text}
    if not full and lines:
        table=[];lookup={};order=[]
        for line in lines:
            if line not in lookup:lookup[line]=len(table);table.append(line)
            order.append(lookup[line])
        candidate={**common,'encoding':'dictionary','dictionary':table,'order':order}
        if len(_wire(candidate))<len(_wire(value)):value=candidate
    if len(_wire(value))>max_chars:raise ValueError('text view exceeds display budget')
    return value

def restore_text_view(root,serialized,path,expected_sha256,*,max_chars=1000000):
    """Authenticate complete text against a fresh independently bound source."""
    root,raw,original,source_lines=_source(root,path,expected_sha256,max_chars)
    if type(serialized) is bytes:
        if len(serialized)>4*max_chars:raise ValueError('frame exceeds byte budget')
        serialized=serialized.decode('utf-8')
    if type(serialized) is not str or len(serialized)>max_chars:
        raise ValueError('bounded serialized text frame required')
    value=_json(serialized)
    common={'schema_version':SCHEMA,'project_root':str(root),
            'source':{'path':path,'sha256':expected_sha256},'scope':SCOPE}
    if type(value) is not dict or any(value.get(k)!=v for k,v in common.items()):
        raise ValueError('text frame binding/version/scope mismatch')
    if value.get('encoding')=='full':
        if set(value)!=set(common)|{'encoding','text'} or type(value['text']) is not str:
            raise ValueError('invalid full text frame')
        text=value['text']
        if len(text)>max_chars or len(text.encode('utf-8'))>MAX_BYTES:
            raise ValueError('expanded text exceeds budget')
    elif value.get('encoding')=='dictionary':
        if set(value)!=set(common)|{'encoding','dictionary','order'}:
            raise ValueError('invalid dictionary frame fields')
        table=value['dictionary'];order=value['order']
        if (type(table) is not list or type(order) is not list or
                not 1<=len(table)<=MAX_LINES or not 1<=len(order)<=MAX_LINES or
                len(order)!=len(source_lines)):
            raise ValueError('invalid dictionary/index counts')
        if any(type(line) is not str or not line or _lines(line)!=[line] for line in table):
            raise ValueError('dictionary must contain complete physical LF lines')
        if len(set(table))!=len(table):raise ValueError('duplicate dictionary entries')
        lengths=[len(line) for line in table]
        sizes=[len(line.encode('utf-8')) for line in table]
        chars=bytes_used=0;used=set();first_seen=[]
        for position,index in enumerate(order):
            if type(index) is not int or not 0<=index<len(table):
                raise ValueError('invalid dictionary index')
            if position!=len(order)-1 and not table[index].endswith('\n'):
                raise ValueError('unterminated line only at EOF')
            chars+=lengths[index];bytes_used+=sizes[index]
            if chars>max_chars or bytes_used>MAX_BYTES:
                raise ValueError('expanded text exceeds budget before allocation')
            if index not in used:used.add(index);first_seen.append(index)
        if first_seen!=list(range(len(table))):
            raise ValueError('all unique dictionary entries required in first-occurrence order')
        text=''.join(table[index] for index in order)
    else:raise ValueError('unknown text encoding')
    if text.encode('utf-8')!=raw:raise ValueError('restored text differs from current source')
    return text
