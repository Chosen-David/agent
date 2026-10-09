"""One out-of-timing public publish per frozen source; no latency measurement."""
from pathlib import Path
import cProfile, json, sys, tempfile, types
ROOT=Path(__file__).resolve().parents[3]
D=Path(__file__).parent
sys.path.insert(0,str(ROOT))
from scripts.benchmark_communication_candidates_v2 import fixtures, load

def run():
    result={}
    with tempfile.TemporaryDirectory() as tmp:
        for label in ('baseline','strong_baseline','candidate'):
            source=D/(label+'.py')
            box,_,_,event=fixtures(load(source).Mailbox,Path(tmp)/label,100,'single',1000)
            profile=cProfile.Profile();sent=profile.runcall(box.publish,dict(event,event_id='profile-new'))
            stats=[dict(line=e.code.co_firstlineno,name=e.code.co_name,freevars=list(e.code.co_freevars),calls=e.callcount) for e in profile.getstats() if isinstance(e.code,types.CodeType) and e.code.co_filename==str(source) and e.code.co_name=='<genexpr>' and set(e.code.co_freevars)=={'event','r'}]
            result[label]=dict(route_generator_calls=sum(x['calls'] for x in stats),selected_entries=stats,published=sent)
    assert result['baseline']['route_generator_calls']>0
    assert result['strong_baseline']['route_generator_calls']==result['candidate']['route_generator_calls']==0
    assert result['baseline']['published']==result['candidate']['published']==result['strong_baseline']['published']
    return result
if __name__=='__main__':
    (D/'profile_raw.json').write_text(json.dumps(run(),indent=2)+'\n')
