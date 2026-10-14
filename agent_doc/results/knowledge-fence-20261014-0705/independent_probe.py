"""Reviewer-owned fixed positions, full outputs and genuine historical cache."""
from pathlib import Path
import importlib.util, json, hashlib, sqlite3, sys, shutil, tempfile
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from agent_runtime import knowledge_index as live
from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
RUN=Path(__file__).parent
spec=importlib.util.spec_from_file_location('agent_runtime.review_historical_index',RUN/'baseline.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

def expected(content, starts):
    lines=content.splitlines(keepends=True)
    nodes=[]; stack=[]
    for i,(start,title,level) in enumerate(starts,1):
        while stack and stack[-1]['level']>=level: stack.pop()
        node=dict(node='s'+str(i),title=title,level=level,start_line=start,parent=stack[-1]['node'] if stack else None)
        nodes.append(node);stack.append(node)
    if not nodes or nodes[0]['start_line']>1:nodes.insert(0,dict(node='intro',title='Holdout',level=0,start_line=1,parent=None))
    for i,node in enumerate(nodes):
        end=nodes[i+1]['start_line']-1 if i+1<len(nodes) else len(lines)
        node.update(end_line=end,text=''.join(lines[node['start_line']-1:end]))
    return nodes
cases=[]
for mark in ['```','~~~~']:
    for suffix in ['language',' # comment','\u2003','\u00a0','\\','`']:
        content='# Root\n'+mark+'lang\n'+mark+suffix+'\n## Hidden\n'+mark+' \t\n## Visible\n'
        starts=[(1,'Root',1),(4,'Hidden',2)] if mark=='```' and suffix=='`' else [(1,'Root',1),(6,'Visible',2)]
        cases.append((mark+repr(suffix),content,starts))
cases += [
 ('invalid_info_then_valid','# Root\n````lang`x\n## Visible\n~~~`good\n# Hidden\n~~~\n# End',[(1,'Root',1),(3,'Visible',2),(7,'End',1)]),
 ('long_info_inside','# Root\n```\n`````lang\n## Hidden\n````\n# End\n',[(1,'Root',1),(6,'End',1)]),
 ('tabs_CR','# Root\r~~~\r~~~ \t\r## Visible\r',[(1,'Root',1),(4,'Visible',2)]),
 ('invalid_at_EOF','```info`bad\n# Visible',[(2,'Visible',1)]),
 ('tilde_mixed_open','~~~````\n# Hidden\n~~~\n# Visible',[(4,'Visible',1)]),
 ('two_mark_control','``lang\n# Visible\n~~\n## Child',[(2,'Visible',1),(4,'Child',2)]),
 ('4space_cannot_close','~~~\n    ~~~\n# Hidden\n~~~\n# Visible',[(5,'Visible',1)]),
 ('empty','',[])]
rows=[]
for name,content,starts in cases:
    record={'title':'Holdout','content':content};want=expected(content,starts);got=live.sections(record)
    rows.append(dict(name=name,input=content,input_sha256=hashlib.sha256(content.encode()).hexdigest(),expected=want,baseline=old.sections(record),actual=got,passed=want==got,source_reassembled=''.join(n['text'] for n in got)==content))
store=KnowledgeStore(ROOT/'knowledge')
corpus=[]
for kid,r in sorted(store.records.items()):
    before=old.sections(r);after=live.sections(r)
    corpus.append(dict(id=kid,sha256=r['sha256'],before=before,after=after,equal=before==after,source_reassembled=''.join(n['text'] for n in after)==r['content']))
with tempfile.TemporaryDirectory(dir=RUN) as tmp:
    corpus_root=Path(tmp)/'knowledge';shutil.copytree(ROOT/'knowledge',corpus_root)
    body=corpus_root/'entries/math.low-rank-svd.md'
    body.write_text(body.read_text()+'\n# CacheRoot\n```lang\n``` misleading\n# CacheHiddenUnique\n```\n# CacheVisibleUnique\n')
    frozen=KnowledgeStore(corpus_root); db=Path(tmp)/'old.sqlite'
    build_old=old.build_index(frozen,db)
    def chunks():
        with sqlite3.connect(db) as con:return [list(x) for x in con.execute('SELECT node,heading,context,body FROM chunks WHERE id=? ORDER BY rowid',('math.low-rank-svd',))]
    before=chunks(); rejected=False;error=None
    try:live.indexed_search(frozen,db,'CacheHiddenUnique')
    except KnowledgeError as e: rejected=True;error=str(e)
    rebuilt=live.build_index(frozen,db);after=chunks();noop=live.build_index(frozen,db)
    cache=dict(old_engine=old.ENGINE_VERSION,new_engine=live.ENGINE_VERSION,old_build=build_old,rejected=rejected,error=error,rebuild=rebuilt,noop=noop,before_chunks=before,after_chunks=after,source_snapshot=frozen.snapshot,old_sections=old.sections(frozen.records['math.low-rank-svd']),new_sections=live.sections(frozen.records['math.low-rank-svd']),passed=rejected and rebuilt['engine_changed'] and rebuilt['updated']==sum(r['status']=='published' for r in frozen.records.values()) and before!=after and any('cachehiddenunique'==x[1] for x in before) and not any('cachehiddenunique'==x[1] for x in after) and not noop['engine_changed'])
files=[ROOT/'agent_runtime/knowledge_index.py',ROOT/'plugins/research-assistant/skills/model-with-knowledge/scripts/knowledge_index.py',RUN/'baseline.py',Path(__file__)]
out=dict(python=sys.version,optimize=sys.flags.optimize,hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},cases=rows,passed=sum(x['passed'] for x in rows),total=len(rows),corpus=corpus,corpus_equal=sum(x['equal'] for x in corpus),corpus_total=len(corpus),cache=cache,all_pass=all(x['passed'] and x['source_reassembled'] for x in rows) and all(x['equal'] and x['source_reassembled'] for x in corpus) and cache['passed'])
print(json.dumps(out,ensure_ascii=False,indent=2))
if not out['all_pass']:sys.exit(1)
