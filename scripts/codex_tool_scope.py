#!/usr/bin/env python3
"""Emit explicit task-scoped app-server overrides; does not edit user settings."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.codex_tool_scope import resolve_tool_scope
from agent_runtime.external_json import ExternalJSONError,load_json

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True,help='absolute current project root')
    p.add_argument('--contract',required=True,help='host-selected requirements JSON under the project')
    a=p.parse_args()
    if not Path(a.root).is_absolute():raise ValueError('absolute project root required')
    root=Path(a.root).resolve(strict=True);path=Path(a.contract)
    path=path if path.is_absolute() else root/path
    for part in (path,*path.parents):
        if part==root:break
        if part.is_symlink():raise ValueError('contract symlink refused')
    if not path.resolve().is_relative_to(root):raise ValueError('contract outside project root')
    contract=load_json(path,max_bytes=8192)
    print(json.dumps(resolve_tool_scope(contract),ensure_ascii=True))

if __name__=='__main__':
    try:main()
    except (ExternalJSONError,OSError,ValueError) as exc:
        print(json.dumps({'error':str(exc)},ensure_ascii=True),file=sys.stderr)
        raise SystemExit(2)
