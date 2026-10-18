import sys,json,hashlib,math,statistics,random,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from scripts import benchmark_term_classes as b
from agent_runtime import knowledge as k,knowledge_index as ki
out=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reviews={}
for label in ['producer','independent']:
 p=out.parent/label
 rows=[json.loads(s) for s in (p/'raw.jsonl').read_text().splitlines()]
 meta=rows[0]['metadata']; inputs=json.loads((p/'inputs.json').read_text())
 assert all(sha(ROOT/f)==v for f,v in {**inputs,**meta['code']}.items())
 assert hashlib.sha256((ROOT/'agent_doc/task/task_details/TERMS-CLASS-27.md').read_bytes().split(b'## Progress')[0]).hexdigest()==meta['plan_sha256']
 cases=[r for r in rows if 'backend' in r];mem=[r for r in rows if 'memory' in r]
 assert len(cases)==20 and len(mem)==6
 for r in cases:
  assert [s['pair'] for s in r['samples']]==list(range(-2,11))
  assert all(s['order']==(['baseline','candidate'] if s['pair']%2==0 else ['candidate','baseline']) for s in r['samples'])
  med={l:statistics.median(s['ns'][l] for s in r['samples'] if s['pair']>=0) for l in ['baseline','candidate']}
  assert med==r['median_ns'] and med['candidate']/med['baseline']==r['ratio']
  assert med['candidate']<=max(med['baseline']*1.1,med['baseline']+200000)
 for r in mem: assert r['peaks']['candidate']<=max(r['peaks']['baseline']*1.5,r['peaks']['baseline']+262144)
 geo=math.exp(sum(math.log(r['ratio']) for r in cases)/20)
 assert geo==rows[-1]['geomean_ratio'] and geo<=.9
 reviews[label]={'geomean_ratio':geo,'nonregression':20,'memory_pass':6,'corpus_files':len(inputs),'worst_ratio':max(r['ratio'] for r in cases),'raw_sha256':sha(p/'raw.jsonl')}
# Full persisted benchmark outputs, not selected fields.
for f in (out.parent/'producer').glob('*.json'):
 assert json.loads(f.read_text())==json.loads((out/f.name).read_text()),f
old=b.baseline('knowledge'); oi=b.baseline('knowledge_index');oi['_terms']=old['_terms']
a=old['KnowledgeStore'](ROOT/'knowledge');c=k.KnowledgeStore(ROOT/'knowledge')
assert oi['indexed_search'].__globals__['_terms'] is old['_terms']
queries=['ＭＡＴＲＩＸ','ＡＴＴＥＮＴＩＯＮ量纲','Kßﬀ','\uf900','\u3400\u9fff','🙂','中-文','a_b a-b a--b','量纲 matrix','１２３','İıſ','注意力','matrix\u200b量纲']
domain=next(d['domains'][0] for d in c.records.values() if d['domains'])
structure=next(d['structures'][0] for d in c.records.values() if d['structures'])
filters=[{}, {'domain':domain},{'structure':structure},{'domain':'absent-domain','structure':'absent-structure'}]
db=out/'extra-index.sqlite';ki.build_index(c,db);dbhash=sha(db)
checked=[]
for q in queries:
 for f in filters:
  for limit in [1,20]:
   for backend in ['lexical','indexed']:
    x=a.search(q,limit=limit,**f) if backend=='lexical' else oi['indexed_search'](a,db,q,limit=limit,**f)
    y=c.search(q,limit=limit,**f) if backend=='lexical' else ki.indexed_search(c,db,q,limit=limit,**f)
    assert x==y,(q,f,limit,backend)
    checked.append({'query':q,'filters':f,'limit':limit,'backend':backend,'output':y})
assert sha(db)==dbhash
rng=random.Random(5727)
alphabet='abXYZ19-_ 中文量纲🙂KßﬀＡＢＣ\uf900\u3400\u9fff\ua000İıſ\u200b'
for i in range(1000):
 text=''.join(rng.choice(alphabet) for _ in range(rng.randrange(300)))
 expected=old['_terms'](text)
 assert k._terms(text)==expected
 for aa,cc in [(False,False),(True,False),(False,True),(True,True)]:
  assert k._terms(text,ascii_words=aa,cjk=cc)=={t for t in expected if (aa and t.isascii()) or (cc and not t.isascii())}
raw_path=ROOT/'.agent-runs/terms-class27/independent-extended-outputs.json'
raw_path.parent.mkdir(parents=True,exist_ok=True)
raw_path.write_text(json.dumps(checked,ensure_ascii=False,sort_keys=True))
manifest={'raw_path':str(raw_path.relative_to(ROOT)),'raw_sha256':sha(raw_path),'output_encoding':'json.dumps(output, ensure_ascii=False, sort_keys=True).encode(utf-8)','cases':[{**{key:value for key,value in row.items() if key!='output'},'output_sha256':hashlib.sha256(json.dumps(row['output'],ensure_ascii=False,sort_keys=True).encode()).hexdigest()} for row in checked]}
(out/'extended-output-hashes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
reviews['extended']={'full_json_searches':len(checked),'unicode_texts':1000,'projection_checks':4000,'seed':5727,'index_unchanged':True}
reviews['verdict']='usable-with-scope'
reviews['scope']='Frozen corpus, hot-store complete search calls, fixed 20-case distribution; no host exclusivity or end-to-end latency claim. Tracemalloc covers Python allocation, not RSS.'
reviews['evidence_hashes']={str(p.relative_to(ROOT)):sha(p) for p in out.glob('*') if p.is_file()}
(out/'review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2))
print(json.dumps(reviews,ensure_ascii=False))
