"""Host-level training layout shared by multiple checkouts of one project."""
import argparse
import json
from pathlib import Path
import re
import sqlite3


def identifier(name):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,127}', name):
        raise ValueError('invalid project or run identity')
    return name


class TrainingWorkspace:
    def __init__(self, database):
        self.db=sqlite3.connect(database,timeout=30)
        self.db.execute("""CREATE TABLE IF NOT EXISTS workspace_layouts
            (worktree TEXT PRIMARY KEY, project TEXT, asset_root TEXT, documents TEXT, legacy_output TEXT)""")

    def bind(self, worktree, project, asset_root, documents, legacy_output='outputs'):
        tree=Path(worktree).resolve(strict=True)
        docs=Path(documents).resolve(strict=True)
        assets=Path(asset_root).resolve(strict=True)
        if not all(p.is_dir() for p in (tree,docs,assets)):
            raise ValueError('worktree, document and asset directories must already exist')
        name=identifier(project)
        if assets.is_relative_to(tree) or assets.is_relative_to(docs):
            raise ValueError('large asset root must be outside the worktree and document tree')
        legacy=tree/identifier(legacy_output)
        row=(str(tree),name,str(assets),str(docs),str(legacy))
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            prior=self.db.execute('SELECT * FROM workspace_layouts WHERE worktree=?',(str(tree),)).fetchone()
            peers=self.db.execute('SELECT DISTINCT asset_root,documents FROM workspace_layouts WHERE project=?',(name,)).fetchall()
            if (prior and prior!=row) or any(p!=(str(assets),str(docs)) for p in peers):
                raise ValueError('conflicting layout; reconcile existing references first')
            self.db.execute('INSERT OR IGNORE INTO workspace_layouts VALUES(?,?,?,?,?)',row)
        return self.layout(tree)

    def layout(self, worktree, run_id=None):
        tree=Path(worktree).resolve(strict=True)
        for p in (tree,*tree.parents):
            row=self.db.execute('SELECT * FROM workspace_layouts WHERE worktree=?',(str(p),)).fetchone()
            if row:
                break
        else:
            raise ValueError('no bound worktree for this launch')
        parent=Path(row[2])/'runs'/row[1]
        path=parent/identifier(run_id) if run_id else parent
        if path.resolve()!=path:
            raise ValueError('redirected managed run path')
        legacy=Path(row[4])
        return dict(worktree=row[0],project=row[1],document_root=row[3],
                    configured_legacy_output=str(legacy),physical_legacy_output=str(legacy.resolve()),
                    managed_output=str(path),asset_root=row[2],run_id=run_id)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database',type=Path)
    sub=parser.add_subparsers(dest='command',required=True)
    bind=sub.add_parser('bind')
    bind.add_argument('worktree');bind.add_argument('project')
    bind.add_argument('asset_root');bind.add_argument('documents')
    layout=sub.add_parser('layout')
    layout.add_argument('worktree');layout.add_argument('--run-id')
    layout.add_argument('--path-only',action='store_true')
    args=parser.parse_args()
    tool=TrainingWorkspace(args.database)
    try:
        if args.command=='bind':
            result=tool.bind(args.worktree,args.project,args.asset_root,args.documents)
        else:
            result=tool.layout(args.worktree,args.run_id)
        print(result['managed_output'] if getattr(args,'path_only',False) else json.dumps(result,ensure_ascii=False))
    finally:
        tool.db.close()


if __name__=='__main__':
    main()
