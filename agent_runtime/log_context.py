"""Literal, recoverable log excerpts. An omitted line is not a clean result."""
import hashlib,json,re
from .advice_poll import _root
from .maintenance_observer import read_bound


def log_view(root, path, expected_sha256, *, needles=(), head=2, tail=2, context=1, max_chars=20000, encoding='lines'):
    root=_root(root)
    if encoding not in ('lines','chunks','runs'):
        raise ValueError('unknown log encoding')
    if type(expected_sha256) is not str or re.fullmatch('[0-9a-f]{64}',expected_sha256) is None:
        raise ValueError('source SHA256 required')
    if (not isinstance(needles,(list,tuple)) or len(needles)>16 or
            any(type(n) is not str or not 1<=len(n)<=100 for n in needles) or len(set(needles))!=len(needles)):
        raise ValueError('distinct bounded literal needles required')
    if any(type(n) is not int or not 0<=n<=1000 for n in (head,tail,context)):
        raise ValueError('invalid line selection bounds')
    if type(max_chars) is not int or not 1<=max_chars<=1000000:
        raise ValueError('invalid display budget')
    data=read_bound(root,path,max_bytes=32*1024*1024)
    if hashlib.sha256(data).hexdigest()!=expected_sha256:
        raise ValueError('source changed; refresh selection')
    lines=data.decode('utf-8').splitlines(keepends=True)
    keep=set(range(min(head,len(lines))))|set(range(max(0,len(lines)-tail),len(lines)))
    counts={n:0 for n in needles}
    for i,line in enumerate(lines):
        for needle in needles:
            if needle in line:
                counts[needle]+=1
                keep.update(range(max(0,i-context),min(len(lines),i+context+1)))
    # Preserve every requested literal match; never hide excess matches at LIMIT.
    value={'schema_version':'log-view/v1','project_root':str(root),'source':{'path':path,'sha256':expected_sha256},
           'selection':{'head':head,'tail':tail,'context':context,'needles':list(needles)},
           'literal_match_line_counts':counts,'total_lines':len(lines),'omitted_lines':len(lines)-len(keep),
           'lines':[{'line':i+1,'text':lines[i]} for i in sorted(keep)],
           'scope':'partial display only; retrieve omitted lines from exact source; no proof of success or absence of errors'}
    if encoding in ('chunks','runs'):
        if sum(len(row['text']) for row in value['lines'])>max_chars:
            raise ValueError('selected log exceeds budget; no silent truncation')
    if encoding=='runs':
        runs=[];last=0
        for row in value.pop('lines'):
            if runs and row['line']==last+1 and row['text']==runs[-1]['text']:
                runs[-1]['count']+=1
            else:runs.append({'start':row['line'],'count':1,'text':row['text']})
            last=row['line']
        value.update(encoding='runs',runs=runs)
    elif encoding=='chunks':
        chunks=[];parts=[];end=0;start=0
        for row in value.pop('lines'):
            if parts and row['line']!=end+1:
                chunks.append({'start':start,'text':''.join(parts)});parts=[]
            if not parts:start=row['line']
            parts.append(row['text'])
            end=row['line']
        if parts:chunks.append({'start':start,'text':''.join(parts)})
        value.update(encoding='chunks',chunks=chunks)
    if len(json.dumps(value,ensure_ascii=False))>max_chars:
        raise ValueError('selected log exceeds budget; no silent truncation')
    return value


def restore_log_lines(value, *, max_chars=1000000):
    """Decode selected lines, without claiming source authenticity or success."""
    if type(max_chars) is not int or not 1<=max_chars<=1000000:
        raise ValueError('invalid restoration budget')
    if type(value) is not dict or value.get('schema_version')!='log-view/v1':
        raise ValueError('invalid log view')
    total=value.get('total_lines');omitted=value.get('omitted_lines')
    if any(type(n) is not int or n<0 for n in (total,omitted)) or omitted>total:
        raise ValueError('invalid line counts')
    if value.get('encoding','lines')=='lines':
        if 'chunks' in value or 'runs' in value:raise ValueError('ambiguous line encoding')
        rows=value.get('lines')
    elif value.get('encoding')=='chunks':
        if 'lines' in value or 'runs' in value or type(value.get('chunks')) is not list:
            raise ValueError('ambiguous chunk encoding')
        rows=[];last=0;used=0
        for chunk in value['chunks']:
            if type(chunk) is not dict or set(chunk)!={'start','text'}:
                raise ValueError('invalid chunk')
            start=chunk['start'];text=chunk['text']
            if type(start) is not int or start<=last or type(text) is not str or not text:
                raise ValueError('invalid chunk start/text')
            used+=len(text)
            if used>max_chars:raise ValueError('restored log exceeds budget')
            for offset,line in enumerate(text.splitlines(keepends=True)):
                rows.append({'line':start+offset,'text':line})
                if len(rows)>total-omitted:raise ValueError('too many restored lines')
            last=rows[-1]['line']
    elif value.get('encoding')=='runs':
        if 'lines' in value or 'chunks' in value or type(value.get('runs')) is not list:
            raise ValueError('ambiguous run encoding')
        rows=[];last=0;used=0
        for run in value['runs']:
            if type(run) is not dict or set(run)!={'start','count','text'}:
                raise ValueError('invalid run')
            start,count,text=run['start'],run['count'],run['text']
            if type(start) is not int or type(count) is not int or not last<start<=total or not 1<=count<=total-start+1 or count>total-omitted-len(rows):
                raise ValueError('invalid run range')
            if type(text) is not str or not text:
                raise ValueError('run must contain one exact line')
            used+=count*len(text)
            if used>max_chars:raise ValueError('restored log exceeds budget')
            if text.splitlines(keepends=True)!=[text]:
                raise ValueError('run must contain one exact line')
            if count>1 and text[-1] not in '\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029':
                raise ValueError('repeated line must retain terminator')
            rows.extend({'line':start+i,'text':text} for i in range(count))
            last=start+count-1
    else:raise ValueError('unknown log encoding')
    if type(rows) is not list or len(rows)!=total-omitted:
        raise ValueError('selected line count mismatch')
    last=0;used=0
    for row in rows:
        if type(row) is not dict or set(row)!={'line','text'}:
            raise ValueError('invalid selected line')
        position=row['line'];text=row['text']
        if type(position) is not int or not last<position<=total or type(text) is not str or not text or text.splitlines(keepends=True)!=[text]:
            raise ValueError('invalid selected line boundary')
        used+=len(text)
        if used>max_chars:raise ValueError('restored log exceeds budget')
        last=position
    return [dict(row) for row in rows]
