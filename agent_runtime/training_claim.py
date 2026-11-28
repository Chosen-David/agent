"""Durable single-flight launch for an explicitly bound training request."""
import argparse
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import time
import uuid

from .experiment_catalog import ExperimentCatalog, fingerprint
from .result_store import _context


def execute(database, request, command):
    if not command or not isinstance(request, dict):
        raise ValueError('bound request and command required')
    for field in ('family', 'trajectory', 'purpose', 'goal', 'mode'):
        if not isinstance(request.get(field), str) or not request[field].strip():
            raise ValueError('missing request field ' + field)
    mode = request['mode']
    if mode not in ('NEW_TRAIN','RESUME','RERUN_REPLICATE','RERUN_REPLACE','DIAGNOSTIC_ONLY'):
        raise ValueError('unsupported launch mode')
    if mode.startswith('RERUN') and not all(request.get(k) for k in ('reason','prior_run','request_id')):
        raise ValueError('explicit rerun needs reason, prior run and stable request ID')
    context = request.get('scientific_context')
    _context(context)
    if not context or not isinstance(request.get('evidence_gap'), str) or not request['evidence_gap'].strip():
        raise ValueError('scientific conditions and an explicit evidence gap required')
    catalog = ExperimentCatalog(database)
    try:
        hits = catalog.find(context)
    finally:
        catalog.db.close()
    if hits and not mode.startswith('RERUN'):
        print(json.dumps(dict(action='review_historical_result', hits=hits)), flush=True)
        return 75
    identity = {k:request[k] for k in ('family','trajectory','goal')}
    if mode.startswith('RERUN'):
        identity.update(request_id=request['request_id'])
    key = fingerprint(identity)
    owner = uuid.uuid4().hex
    db = sqlite3.connect(database, timeout=30)
    try:
        db.execute("""CREATE TABLE IF NOT EXISTS training_claims
        (claim TEXT PRIMARY KEY, owner TEXT, host TEXT, pid INTEGER, child INTEGER,
         heartbeat REAL, status TEXT, request TEXT, rc INTEGER)""")
        with db:
            changed = db.execute("INSERT OR IGNORE INTO training_claims VALUES(?,?,?,?,?,?,?,?,?)",
                (key,owner,socket.gethostname(),os.getpid(),None,time.time(),'claimed',
                 json.dumps(request,sort_keys=True),None)).rowcount
        if not changed:
            row = db.execute('SELECT status,host,pid,child FROM training_claims WHERE claim=?',(key,)).fetchone()
            print(json.dumps(dict(claim=key, existing=row, action='inspect_existing')),flush=True)
            return 75
        print(json.dumps(dict(claim=key,owner=owner,request=request)),flush=True)
        try:
            child = subprocess.Popen(command)
        except OSError:
            with db:
                db.execute("UPDATE training_claims SET status='launch-failed' WHERE claim=?",(key,))
            raise
        while True:
            with db:
                db.execute("UPDATE training_claims SET child=?,heartbeat=?,status='running' WHERE claim=? AND owner=?",
                           (child.pid,time.time(),key,owner))
            try:
                rc = child.wait(timeout=30)
                break
            except subprocess.TimeoutExpired:
                continue
        with db:
            db.execute('UPDATE training_claims SET heartbeat=?,status=?,rc=? WHERE claim=? AND owner=?',
                       (time.time(),'awaiting-validation' if rc==0 else 'failed',rc,key,owner))
        return rc if rc>=0 else 128-rc
    finally:
        db.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('database')
    parser.add_argument('request',type=Path)
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    command=args.command[1:] if args.command[:1]==['--'] else args.command
    return execute(args.database,json.loads(args.request.read_text()),command)


if __name__=='__main__':
    raise SystemExit(main())
