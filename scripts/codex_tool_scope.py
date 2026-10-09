#!/usr/bin/env python3
"""Emit explicit task-scoped app-server overrides; does not edit user settings."""
import argparse
import json
from pathlib import Path
import stat
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from agent_runtime.codex_tool_scope import resolve_tool_scope

def unique_keys(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate contract key')
        result[key]=value
    return result

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
    if not stat.S_ISREG(path.stat().st_mode) or path.stat().st_size>8192:
        raise ValueError('bounded regular contract file required')
    data=path.read_bytes()
    if len(data)>8192:raise ValueError('contract grew beyond bound')
    print(json.dumps(resolve_tool_scope(json.loads(data,object_pairs_hook=unique_keys)),ensure_ascii=True))

if __name__=='__main__':main()
