"""Frozen independent tests. Run baseline before candidate; append rather than overwrite history."""
import argparse, copy, datetime, hashlib, itertools, json, math, pathlib, subprocess, sys, tempfile
from fractions import Fraction
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from agent_runtime.knowledge import KnowledgeStore, KnowledgeError, _terms
from agent_runtime.knowledge_index import build_index,indexed_search
OUT=pathlib.Path(__file__).parent
CASES=OUT/'independent_cases.json'
FROZEN='cf894e38f4ea94d3a7865e41007fec491653f615a7dad63f2412c35ff5e2e1ee'
def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def require(v,message):
    if not v: raise AssertionError(message)
def reject(f):
    try:f()
    except KnowledgeError as e:return str(e)
    raise AssertionError('invalid reference accepted')
def fixture(folder,rows):
    root=folder/'micro';(root/'entries').mkdir(parents=True)
    template=json.loads((ROOT/'knowledge/entries/math.low-rank-svd.json').read_text())
    for i,row in enumerate(rows):
        d=copy.deepcopy(template);d.update(id=f'test.independent-{i}',title='隔离节点',summary='局部说明',aliases=[row['alias']],domains=[row.get('domain','probability')],structures=['synthetic-isolation'],assumptions=['Synthetic retrieval only'],status=row.get('status','published'),requires=[],relations=[])
        p=root/'entries'/f"{d['id']}.json";p.write_text(json.dumps(d,ensure_ascii=False));p.with_suffix('.md').write_text(row.get('body','# 条件核查\n这是隔离测试。\n'))
    return KnowledgeStore(root)
def lanes(row):return [m['retriever'] for m in row['matches']]
def run_case(c,real,index,tmp):
    kind=c['kind'];q=c.get('query');detail={}
    if kind in ('synthetic_alias','ambiguous','candidate','domain'):
        rows=[{'alias':q,'body':c.get('body','# 条件核查\n这是隔离测试。\n')}]
        if kind=='ambiguous':rows*=2
        if kind=='candidate':rows.append({'alias':q,'status':'candidate'})
        if kind=='domain':rows=[{'alias':q,'domain':'physics'},{'alias':q,'domain':c['domain']}]
        s=fixture(tmp,rows);db=tmp/'micro.sqlite';build_index(s,db)
        kwargs={'domain':c['domain'],'limit':1} if kind=='domain' else {'limit':3}
        r=indexed_search(s,db,q,**kwargs);f=s.search(q,**kwargs);detail={'sqlite':r,'files':f}
        ids=[x['id'] for x in r['results']];fids=[x['id'] for x in f['results']]
        if kind=='synthetic_alias':
            d=s.records['test.independent-0'];require(not _terms(q)&_terms(d['content']+' '+d['title']+' '+d['summary']),'fixture not alias-only')
            require(ids==['test.independent-0'],'alias target missing')
            require({'document-bm25','section-bm25'}<=set(lanes(r['results'][0])),'alias-only target missing section-bm25 lane')
        elif kind=='ambiguous':require(set(ids)==set(fids)=={'test.independent-0','test.independent-1'},'ambiguity loses eligible target');require(r['applicability']=='unchecked','retrieval claims applicability')
        elif kind=='candidate':require(ids==fids==['test.independent-0'],'candidate exclusion failed')
        elif kind=='domain':require(ids==fids==['test.independent-1'],'domain filtering failed')
    elif kind in ('real_alias','no_hit'):
        r=indexed_search(real,index,q,limit=3);detail={'sqlite':r,'files':real.search(q,limit=3)}
        if kind=='no_hit':require(not r['results'] and not detail['files']['results'],'unexpected no-hit result')
        else:
            d=real.records[c['target']];require(not _terms(q)&_terms(d['content']+' '+d['title']+' '+d['summary']),'real query not alias-only')
            row=next((r for r in r['results'] if r['id']==c['target']),None);require(row is not None,'real target absent top3')
            require('section-bm25' in lanes(row),'real alias-only missing section-bm25 lane')
    elif kind=='refs':
        kid=c['target'];d=real.get(kid);refs=d['knowledge_refs'];detail['valid']=real.check_refs(refs)
        detail['missing_prerequisite']=reject(lambda:real.check_refs([real.ref(kid)]))
        stale=copy.deepcopy(refs);stale[0]['sha256']='0'*64;detail['stale']=reject(lambda:real.check_refs(stale))
        unknown={'id':'math.unregistered-aurora-proof','version':1,'sha256':'a'*64};detail['unknown']=reject(lambda:real.check_refs([unknown]))
        result={'snapshot':real.snapshot,'backend':'independent-seed','results':[real.ref(kid)]};pack=real.context(result,max_entries=1,include_related=False);detail['small_context']=pack;require(not pack['entries'] and pack['skipped'],'partial dependency bundle admitted')
    elif kind=='scientific':
        successes=0;paths=[]
        for signs in itertools.product((-1,1),repeat=7):
            S=Fraction(0);V=Fraction(0);hit=False
            for sign in signs:
                a=Fraction(1) if S<=0 else Fraction(1,4)
                # At each reachable history the two continuations have conditional mean zero.
                require((a+(-a))/2==0,'conditional mean');V+=a*a;S+=a*sign;hit=hit or (S>=2 and V<=3)
            successes+=hit;paths.append({'signs':list(signs),'S':str(S),'V':str(V),'hit':hit})
        probability=Fraction(successes,2**7);bound=math.exp(-4/(2*(3+2/3)))
        detail={'paths':paths,'successes':successes,'total':128,'probability':str(probability),'bound':bound,'decision':'applicable to fixed-budget joint event','assumptions':{'predictable_amplitude':True,'conditional_mean_zero':True,'upper_bound_R':1,'fixed_v':3,'fixed_threshold':2}}
        require(float(probability)<=bound,'finite Freedman check violates bound')
    elif kind=='scientific_refusal':
        mean=(Fraction(1)-Fraction(1,4))/2
        detail={'conditional_mean':str(mean),'decision':'refuse','reason':'a depends on current sign, and X has conditional mean 3/8; observed a squared is not predictable'}
        require(mean==Fraction(3,8) and mean!=0,'refusal derivation incorrect')
    return detail

def main():
    a=argparse.ArgumentParser();a.add_argument('--label',required=True);a.add_argument('--corpus',default=str(ROOT/'knowledge'));args=a.parse_args()
    require(digest(CASES)==FROZEN,'frozen cases modified')
    cases=json.loads(CASES.read_text());real=KnowledgeStore(args.corpus)
    result={'label':args.label,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'cases_sha256':FROZEN,'corpus_root':str(real.root),'snapshot':real.snapshot,'input_hashes':{str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'agent_runtime/knowledge.py',ROOT/'agent_runtime/knowledge_index.py',pathlib.Path(__file__),ROOT/'agent_doc/results/knowledge-freedman-20261008T0915Z/candidate/math.freedman-variance-budget.json',ROOT/'agent_doc/results/knowledge-freedman-20261008T0915Z/candidate/math.freedman-variance-budget.md']},'cases':[]}
    with tempfile.TemporaryDirectory(prefix='independent-alias-') as folder:
        tmp=pathlib.Path(folder);db=tmp/'real.sqlite';result['index']=build_index(real,db)
        for c in cases['cases']:
            child=tmp/c['id'];child.mkdir()
            row={'id':c['id'],'status':'pass'}
            try:row['detail']=run_case(c,real,db,child)
            except Exception as e:
                row.update(status='fail',error=type(e).__name__+': '+str(e))
                # Preserve actual observed retrieval even when assertion failed.
                if c['kind'] in ('real_alias','no_hit'):row['actual']=indexed_search(real,db,c['query'],limit=3)
                elif (child/'micro.sqlite').exists():row['actual']=indexed_search(KnowledgeStore(child/'micro'),child/'micro.sqlite',c['query'],limit=3)
            result['cases'].append(row)
    result['passed']=sum(c['status']=='pass' for c in result['cases']);result['total']=len(result['cases'])
    path=OUT/'independent_results.json';history=json.loads(path.read_text()) if path.exists() else {'schema_version':1,'runs':[]};history['runs'].append(result);path.write_text(json.dumps(history,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'label':args.label,'passed':result['passed'],'total':result['total'],'failures':[{k:r[k] for k in ('id','error')} for r in result['cases'] if r['status']=='fail']},ensure_ascii=False))
if __name__=='__main__':main()
