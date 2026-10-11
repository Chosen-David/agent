"""Local synthetic Mailbox replay; no provider/model calls or billing estimates."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import types
import sys
import tempfile
import time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from agent_runtime.communication import Mailbox,canonical
from tests.test_mailbox_pagination import long_fixture


def run(mode):
    try:
        import tiktoken
        encoder=tiktoken.get_encoding('cl100k_base')
        tokenizer={'name':'cl100k_base','version':tiktoken.__version__}
    except (ImportError,ValueError,OSError):
        encoder=None;tokenizer=None
    def size(value):
        text=canonical(value)
        return [len(text.encode()),len(encoder.encode(text,disallowed_special=())) if encoder else None]
    trace=[]
    baseline_revision='3b3c41483a56dbcdcf614f61d44436418c6ee7f9'
    source=(subprocess.check_output(['git','show',baseline_revision+':agent_runtime/communication.py'],cwd=ROOT)
            if mode=='baseline' else (ROOT/'agent_runtime/communication.py').read_bytes())
    module=types.ModuleType('agent_runtime.pagination_replay_source');module.__package__='agent_runtime'
    exec(compile(source,'pagination_replay_source','exec'),module.__dict__)
    def record(op,request,out,elapsed):
        inp=size(request);result=size(out)
        trace.append([f'{mode}-{len(trace)+1:03d}',op,*inp,*result,elapsed,
                      hashlib.sha256(canonical(out).encode()).hexdigest()])
    with tempfile.TemporaryDirectory(prefix='mailbox-replay-') as tmp:
        box,plan,events,deliveries=long_fixture(Path(tmp),mailbox_type=module.Mailbox,
            observe=lambda event,out,elapsed:record(event['sender']+':publish',event,out,elapsed))
        before=box.usage();cursor=0;seen={};received=[]
        def invoke(op,request,fn):
            start=time.perf_counter_ns();out=fn();elapsed=time.perf_counter_ns()-start
            record(op,request,out,elapsed)
            return out
        for i in range(6):
            args={'limit':20}
            if mode=='candidate':args['after_seq']=cursor
            page=invoke('main:index',dict(recipient='main',**args),lambda:box.inbox_index('main',**args))
            received.extend(r['seq'] for r in page['items'])
            seen.update((r['seq'],r) for r in page['items'])
            if mode=='candidate':cursor=page['next_after_seq']
        # One same-call retry is deliberately retained in payload accounting.
        page=invoke('main:index-retry',dict(recipient='main',**args),lambda:box.inbox_index('main',**args))
        received.extend(r['seq'] for r in page['items'])
        for seq,row in seen.items():
            body=invoke('main:read-pending',{'recipient':'main','seq':seq,'body_sha256':row['body_sha256']},lambda:box.read_pending('main',seq,row['body_sha256']))
            assert body['event']==events[seq-1]
        retry=invoke('retrieval:publish-retry',events[0],lambda:box.publish(events[0]))
        assert retry['duplicate'];assert box.usage()==before
        assert all(x['receipt'] is None for x in box.status())
        out={'mode':mode,'source_sha256':hashlib.sha256(source).hexdigest(),
             'environment':{'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'tokenizer':tokenizer},
             'fixture':{'event_count':len(events),'dossier_bytes':(Path(tmp)/'dossier.txt').stat().st_size,
                        'dossier_sha256':hashlib.sha256((Path(tmp)/'dossier.txt').read_bytes()).hexdigest(),
                        'event_ids_sha256':hashlib.sha256(canonical([e['event_id'] for e in events]).encode()).hexdigest()},
             'trace_columns':['local_call_id','operation','input_bytes','input_tokenizer_tokens','output_bytes','output_tokenizer_tokens','elapsed_ns','output_sha256'],
             'trace':trace,'unique_call_ids':len({t[0] for t in trace}),
             'coverage':{'unique_events':len(seen),'expected':120,'index_rows_with_retry':len(received),
                         'repeated_rows':len(received)-len(set(received)),
                         'tail_correction_seen':119 in seen,'acknowledged':0},
             'mailbox_usage':before,
             'edges':[{'sender':s,'recipient':r,'deliveries':40} for s in ('retrieval','review','repair') for r in ('main','independent')],
             'local_payload_totals':{'input_bytes':sum(t[2] for t in trace),'output_bytes':sum(t[4] for t in trace),
                    'input_tokenizer_tokens':sum(t[3] for t in trace) if encoder else None,
                    'output_tokenizer_tokens':sum(t[5] for t in trace) if encoder else None},
             'provider':{'input_tokens':None,'output_tokens':None,'cache_read_tokens':None,'cache_write_tokens':None,
                         'charged_history_tokens':None,'failed_retry_bill':None,'latency':None,'fees':None},
             'setup_publish_calls':120,
             'scope':'Actual local CPU Mailbox calls on synthetic input. Byte/tokenizer proxies include all setup publications, index, body recovery and retries. Coverage differs: no savings ratio or provider-hotspot ranking. Envelope delivery counts exclude repeated reads. No full-chain bill.'}
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['baseline','candidate'],required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.write_text(json.dumps(run(a.mode),ensure_ascii=False,separators=(',',':'))+'\n')
