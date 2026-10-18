"""Frozen paired complete-search benchmark, isolated baseline module globals."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from agent_runtime import knowledge, knowledge_index

BASE = 'a5a13c2aea4165d0d3aebcd6c99ca0135a6efdbb'
QUERIES = ('matrix', '量纲', 'attention', 'zzqxnonexistent', 'attention量纲')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def baseline(name):
    data = subprocess.check_output(['git', 'show', BASE+':agent_runtime/'+name+'.py'], cwd=ROOT)
    ns = {'__name__': 'agent_runtime.baseline_'+name, '__package__': 'agent_runtime', '__file__': str(ROOT/'agent_runtime'/f'{name}.py')}
    exec(compile(data, BASE+':'+name, 'exec'), ns)
    return ns


def run(out):
    assert os.environ.get('PYTHONHASHSEED') == '0'
    out.mkdir(parents=True, exist_ok=False)
    old = baseline('knowledge')
    idx = baseline('knowledge_index')
    idx['_terms'] = old['_terms']
    stores = {'baseline': old['KnowledgeStore'](ROOT/'knowledge'), 'candidate': knowledge.KnowledgeStore(ROOT/'knowledge')}
    inputs = {str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in sorted((ROOT/'knowledge').rglob('*')) if p.is_file()}
    files = ['agent_runtime/knowledge.py','agent_runtime/knowledge_index.py','scripts/benchmark_term_classes.py','tests/test_knowledge_term_classes.py']
    code = {p:sha((ROOT/p).read_bytes()) for p in files}
    (out/'inputs.json').write_text(json.dumps(inputs,sort_keys=True))
    with (out/'raw.jsonl').open('w') as f, tempfile.TemporaryDirectory() as tmp:
        def emit(row):
            line=json.dumps(row,ensure_ascii=False);f.write(line+'\n');f.flush()
        emit({'metadata':{'baseline':BASE,'code':code,'python':sys.version,'platform':platform.platform(),'snapshot':stores['candidate'].snapshot,'plan_sha256':sha((ROOT/'agent_doc/task/task_details/TERMS-CLASS-27.md').read_bytes().split(b'## Progress')[0]),'scope':'full hot-store search; loading/index build excluded','clock':'perf_counter_ns','pairs':11,'warmup_pairs':2,'query_cases':QUERIES,'host_exclusivity':False}})
        db=Path(tmp)/'index.sqlite'
        knowledge_index.build_index(stores['candidate'],db)
        before=sha(db.read_bytes())
        ratios=[]; passes=[]
        for backend in ('lexical','indexed'):
            for qi,q in enumerate(QUERIES):
                for limit in (5,20):
                    def invoke(label):
                        s=stores[label]
                        if backend=='lexical': return s.search(q,limit=limit)
                        fn=idx['indexed_search'] if label=='baseline' else knowledge_index.indexed_search
                        return fn(s,db,q,limit=limit)
                    expected=invoke('baseline')
                    (out/f'{backend}-{qi}-{limit}.json').write_text(json.dumps(expected,ensure_ascii=False,sort_keys=True))
                    samples=[]
                    for pair in range(-2,11):
                        order=['baseline','candidate'] if pair%2==0 else ['candidate','baseline']
                        ns={}
                        for label in order:
                            start=time.perf_counter_ns();actual=invoke(label);ns[label]=time.perf_counter_ns()-start
                            assert actual==expected,(backend,q,limit,label)
                        samples.append({'pair':pair,'order':order,'ns':ns})
                    med={label:statistics.median(s['ns'][label] for s in samples if s['pair']>=0) for label in order}
                    ratio=med['candidate']/med['baseline']
                    ok=med['candidate']<=max(med['baseline']*1.10,med['baseline']+200000)
                    ratios.append(ratio);passes.append(ok)
                    emit({'backend':backend,'query':q,'limit':limit,'samples':samples,'median_ns':med,'ratio':ratio,'parity':True,'nonregression':ok})
        assert sha(db.read_bytes())==before
        for text in ('中'*100000, 'a量纲 '*25000):
            for flags in ({'ascii_words':True,'cjk':False},{'ascii_words':False,'cjk':True},{'ascii_words':True,'cjk':True}):
                peaks={}
                for label in ('baseline','candidate'):
                    tracemalloc.start()
                    result=old['_terms'](text) if label=='baseline' else knowledge._terms(text,**flags)
                    peaks[label]=tracemalloc.get_traced_memory()[1];tracemalloc.stop();del result
                ok=peaks['candidate']<=max(peaks['baseline']*1.5,peaks['baseline']+262144)
                passes.append(ok);emit({'memory':flags,'input_sha256':sha(text.encode()),'peaks':peaks,'pass':ok})
        for p,h in {**inputs,**code}.items(): assert sha((ROOT/p).read_bytes())==h,p
        geo=math.exp(sum(map(math.log,ratios))/len(ratios))
        summary={'summary':True,'geomean_ratio':geo,'accepted':geo<=.90 and all(passes)}
        emit(summary);print(json.dumps(summary))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    run(parser.parse_args().out)
