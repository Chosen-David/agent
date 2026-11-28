"""Federated discovery over project ResultStore records. Acceptance stays with the producer."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

from .project_docs import document_root
from .result_store import ResultStore


def fingerprint(context):
    """Hash only the scientific context supplied to ResultStore, preserving array order."""
    data = json.dumps(context, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


class ExperimentCatalog:
    def __init__(self, database):
        self.db = sqlite3.connect(database)
        self.db.execute("""CREATE TABLE IF NOT EXISTS runs
            (project TEXT, run TEXT, document_home TEXT, stamp TEXT, digest TEXT, context TEXT, summary TEXT,
            PRIMARY KEY(project, run))""")
        self.db.execute("CREATE INDEX IF NOT EXISTS by_context ON runs(context)")

    def scan(self, project):
        store = ResultStore(project)
        project = str(store.root)
        doc_home = document_root(store.root)
        home = doc_home / "results"
        if not home.is_dir():
            raise ValueError("project result store unavailable")
        seen = set()
        updated = 0
        with self.db:
            for record in home.glob('*/record.json'):
                run = record.parent.name
                seen.add(run)
                stat = record.stat()
                stamp = str((stat.st_dev, stat.st_ino, stat.st_size, stat.st_ctime_ns))
                old = self.db.execute("SELECT stamp,document_home FROM runs WHERE project=? AND run=?",
                                      (project, run)).fetchone()
                if old == (stamp, str(doc_home)):
                    continue
                shown = store.show(run)
                data = shown['record']
                self.db.execute("INSERT OR REPLACE INTO runs VALUES(?,?,?,?,?,?,?)",
                                (project, run, str(doc_home), stamp, shown['record_ref']['sha256'],
                                 fingerprint(data['context']), data['summary']))
                updated += 1
            rows = list(self.db.execute("SELECT run FROM runs WHERE project=?", (project,)))
            self.db.executemany("DELETE FROM runs WHERE project=? AND run=?",
                                ((project, run) for (run,) in rows if run not in seen))
        return dict(project=project, registered=len(seen), refreshed=updated)

    def find(self, context):
        rows = self.db.execute("SELECT project,run,document_home,digest FROM runs WHERE context=? ORDER BY project,run",
                               (fingerprint(context),))
        hits = []
        for project, run, home, digest in rows:
            if str(document_root(project)) != home:
                hits.append(dict(project=project, run_id=run, document_home=home,
                                 decision="verify_delta", reasons=["restore producer document binding"]))
                continue
            store = ResultStore(project)
            decision = store.decide_run(run, context)
            if decision['record_sha256'] != digest:
                raise ValueError("source record changed; refresh catalog")
            hits.append(dict(project=project, **decision))
        return hits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database', type=Path)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('scan').add_argument('project', type=Path)
    sub.add_parser('find').add_argument('context', type=Path)
    args = parser.parse_args()
    catalog = ExperimentCatalog(args.database)
    try:
        result = (catalog.scan(args.project) if args.action == 'scan'
                  else catalog.find(json.loads(args.context.read_text())))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        catalog.db.close()


if __name__ == '__main__':
    main()
