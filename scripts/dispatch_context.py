#!/usr/bin/env python3
"""Emit a native dispatch plan, never execute model requests or write guides."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.dispatch_context import prepare_dispatch
from agent_runtime.result_validation import _bytes,_json
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',required=True);p.add_argument('--request',required=True)
    p.add_argument('--force-inherit',action='store_true');p.add_argument('--max-chars',type=int,default=12000);a=p.parse_args(argv)
    try:
        root=Path(a.root)
        if not root.is_absolute():raise ValueError('absolute PROJECT_ROOT required')
        root=root.resolve(strict=True);raw=_bytes(root,a.request)
        if len(raw)>262144:raise ValueError('host request too large')
        result=prepare_dispatch(root,_json(raw),force_inherit=a.force_inherit,max_chars=a.max_chars)
    except (OSError,ValueError,TypeError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));return 1
    print(json.dumps(result,ensure_ascii=False,separators=(',',':')));return 0
if __name__=='__main__':raise SystemExit(main())
