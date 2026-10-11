"""Literal, recoverable log excerpts. An omitted line is not a clean result."""
import hashlib,json,re
from .advice_poll import _root
from .maintenance_observer import read_bound


def log_view(root, path, expected_sha256, *, needles=(), head=2, tail=2, context=1, max_chars=20000):
    root=_root(root)
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
    if len(json.dumps(value,ensure_ascii=False))>max_chars:
        raise ValueError('selected log exceeds budget; no silent truncation')
    return value
