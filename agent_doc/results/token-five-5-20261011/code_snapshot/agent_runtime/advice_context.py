"""Explicit H2-topic navigation for advice, not an assessment cache."""
import hashlib,json,re
from .advice_poll import _root,_path
from .maintenance_observer import read_bound

def advice_view(root,path,headings,expected_sha256,*,max_chars=20000):
    root=_root(root);_path(path)
    if (not isinstance(headings,(list,tuple)) or not headings or len(headings)>128
            or any(type(h) is not str or not h.strip() or len(h)>256 for h in headings)
            or len(set(headings))!=len(headings)):
        raise ValueError('distinct explicit H2 topic titles required')
    if type(expected_sha256) is not str or re.fullmatch('[0-9a-f]{64}',expected_sha256) is None:
        raise ValueError('exact advice source SHA256 required')
    if type(max_chars) is not int or not 1<=max_chars<=1000000:
        raise ValueError('invalid display budget')
    data=read_bound(root,path)
    if hashlib.sha256(data).hexdigest()!=expected_sha256:
        raise ValueError('advice changed; refresh topic selection')
    lines=data.decode('utf-8').splitlines(keepends=True)
    if any('<!--' in line for line in lines):
        raise ValueError('HTML comment layout requires full source; no partial markup')
    topics=[];fence=None
    for i,line in enumerate(lines):
        marker=re.match(r'(`{3,}|~{3,})',line.lstrip())
        if marker:
            token=marker[1]
            if fence is None:fence=token
            elif token[0]==fence[0] and len(token)>=len(fence) and not line.lstrip()[len(token):].strip():fence=None
            continue
        if fence is not None:continue
        if topics and re.match(r'^#\s',line):
            raise ValueError('multiple document-level titles; use full source')
        match=re.match(r'^##[ \t]+(.+?)[ \t]*\r?\n?$',line)
        if match:
            title=re.sub(r'[ \t]+#+[ \t]*$','',match[1]).strip()
            if not title or len(topics)>=128:raise ValueError('invalid/budgeted topic layout')
            topics.append((i,title))
    if fence is not None:raise ValueError('unterminated code fence; use full source')
    titles=[title for _,title in topics]
    if not topics or len(set(titles))!=len(titles) or set(headings)-set(titles):
        raise ValueError('missing or ambiguous topic title; use full source')
    sections=[]
    for n,(start,title) in enumerate(topics):
        end=topics[n+1][0] if n+1<len(topics) else len(lines)
        if title in headings:sections.append({'heading':title,'start_line':start+1,'end_line':end,'text':''.join(lines[start:end])})
    value={'schema_version':'advice-view/v1','project_root':str(root),'source':{'path':path,'sha256':expected_sha256},
           'leading_text':''.join(lines[:topics[0][0]]),'selected_sections':sections,
           'omitted_sections':len(topics)-len(sections),
           'scope':'explicit literal H2 topics outside fences, with all leading text; read full source for dependencies; no assessment, closure or authority'}
    if len(json.dumps(value,ensure_ascii=False))>max_chars:
        raise ValueError('topic view exceeds budget; no partial selected section')
    return value
