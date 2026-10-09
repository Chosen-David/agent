#!/usr/bin/env python3
"""Emit bounded explicit skill exclusions for a new thread; never write settings."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.codex_skill_scope import resolve_skill_scope
from agent_runtime.result_validation import _bytes,_json

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True)
    p.add_argument('--request',required=True,help='project-relative trusted host request JSON')
    a=p.parse_args(argv)
    try:
        root=Path(a.root)
        if not root.is_absolute():raise ValueError('absolute PROJECT_ROOT required')
        root=root.resolve(strict=True)
        data=_bytes(root,a.request)
        if len(data)>262144:raise ValueError('skill request budget exceeded')
        request=_json(data)
        if not isinstance(request,dict) or set(request)!={'project_root','contract','catalog','current_skills_config'}:
            raise ValueError('explicit host request fields required')
        if Path(request['project_root']).resolve(strict=True)!=root or Path(request['catalog']['cwd']).resolve(strict=True)!=root:
            raise ValueError('skill scope belongs to a different project')
        result=resolve_skill_scope(request['contract'],request['catalog'],request['current_skills_config'])
    except (KeyError,TypeError,OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=False));return 1
    print(json.dumps(result,ensure_ascii=False,separators=(',',':')));return 0

if __name__=='__main__':raise SystemExit(main())
