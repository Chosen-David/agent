"""Render or restore a complete SHA-bound project text with exact line sharing."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.text_dictionary import text_view,restore_text_view
from agent_runtime.maintenance_observer import read_bound
from agent_runtime.context_serialization import render_context

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True);p.add_argument('--path',required=True)
    p.add_argument('--sha256',required=True);p.add_argument('--full',action='store_true')
    p.add_argument('--max-chars',type=int,default=1000000);p.add_argument('--compact',action='store_true')
    p.add_argument('--restore',help='project-relative frame file; independently supplied source binding still required')
    a=p.parse_args(argv)
    try:
        if a.restore:
            if a.full:raise ValueError('full and restore are mutually exclusive')
            value={'text':restore_text_view(a.root,read_bound(a.root,a.restore,max_bytes=4*1024*1024),a.path,a.sha256,max_chars=a.max_chars)}
        else:value=text_view(a.root,a.path,a.sha256,full=a.full,max_chars=a.max_chars)
        print(render_context(value,compact=a.compact));return 0
    except (OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));return 1

if __name__=='__main__':raise SystemExit(main())
