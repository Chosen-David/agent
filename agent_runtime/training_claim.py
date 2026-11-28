"""Durable single-flight launch for an explicitly bound training request."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import time
import uuid

from .experiment_catalog import ExperimentCatalog, fingerprint
from .result_store import ResultStore, _context
from .training_artifacts import plan


def execute(database, request, command, *, adapter=None):
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
        hits = catalog.find(context, verifier=getattr(adapter, 'verify', None))
        rerun = mode.startswith('RERUN')
        if hits and not rerun:
            action = 'REUSE_RESULT' if any(h['decision']=='reuse' for h in hits) else 'review_historical_result'
            decision = dict(action=action, hits=hits, purpose=request['purpose'])
            with catalog.db:
                catalog.db.execute("""CREATE TABLE IF NOT EXISTS training_decisions
                    (sequence INTEGER PRIMARY KEY, at REAL, context TEXT, decision TEXT)""")
                catalog.db.execute('INSERT INTO training_decisions(at,context,decision) VALUES(?,?,?)',
                                   (time.time(),fingerprint(context),json.dumps(decision)))
            print(json.dumps(decision),flush=True)
            return 75
        has_assets = catalog.db.execute("""SELECT 1 FROM sqlite_master
            WHERE type='table' AND name='checkpoint_assets'""").fetchone()
        candidates = []
        if has_assets and not rerun:
            candidates = [row[0] for row in catalog.db.execute("""SELECT artifact FROM checkpoint_assets
                WHERE trajectory=? AND family=? AND level='L3' ORDER BY step DESC""",
                (request['trajectory'],request['family']))]
        if candidates or mode=='RESUME':
            if adapter is None or not request.get('producer_project') or not candidates:
                print(json.dumps(dict(action='verify_recovery', candidates=candidates)), flush=True)
                return 75
            recovery = ResultStore(request['producer_project']).longest_recovery(candidates,
                trajectory_id=request['trajectory'],family_sha256=request['family'],
                target_step=request['target_step'],byte_limit=request['hash_budget'],provider=adapter)
            if recovery['action']!='resume':
                print(json.dumps(recovery), flush=True)
                return 75
            command = adapter.resume_command(command,recovery)
            if not isinstance(command,list) or not command or not all(isinstance(v,str) for v in command):
                raise ValueError('trusted adapter must bind the checked restore point to argv')
            request = dict(request, bound_recovery=recovery)
    finally:
        catalog.db.close()
    identity = dict(scientific_fingerprint=fingerprint(context), trajectory=request['trajectory'], goal=request['goal'])
    if mode.startswith('RERUN'):
        identity.update(request_id=request['request_id'])
    key = fingerprint(identity)
    owner = uuid.uuid4().hex
    request = dict(request, run_id=request.get('run_id') or owner)
    db = sqlite3.connect(database, timeout=30)
    try:
        db.execute("""CREATE TABLE IF NOT EXISTS training_claims
        (claim TEXT PRIMARY KEY, owner TEXT, host TEXT, pid INTEGER, child INTEGER,
         heartbeat REAL, status TEXT, request TEXT, rc INTEGER)""")
        db.execute("""CREATE TABLE IF NOT EXISTS training_reservations
            (claim TEXT PRIMARY KEY, device TEXT, bytes INTEGER, pressure TEXT, released INTEGER)""")
        with db:
            db.execute('BEGIN IMMEDIATE')
            changed = db.execute("INSERT OR IGNORE INTO training_claims VALUES(?,?,?,?,?,?,?,?,?)",
                (key,owner,socket.gethostname(),os.getpid(),None,time.time(),'claimed',
                 json.dumps(request,sort_keys=True),None)).rowcount
            if changed and request.get('artifact_plan'):
                supplied = json.loads(Path(request['artifact_plan']).read_text())
                common = dict(output=supplied['physical_output'],run_id=supplied['run_id'],
                    policy=supplied['policy'],steps=supplied['steps'],interval=supplied['interval'],
                    checkpoint_bytes=supplied['checkpoint_bytes'],extra_bytes=supplied['extra_bytes'],
                    reserve_bytes=supplied['reserve_bytes'],quota_free_bytes=supplied.get('quota_free_bytes'),
                    staging_bytes=supplied.get('staging_bytes',0),watermarks=supplied.get('watermarks',(70,80,90,95)),
                    essential=supplied.get('essential',False))
                device = str(plan(**common)['disk_device'])
                reserved = db.execute('SELECT COALESCE(SUM(bytes),0) FROM training_reservations WHERE device=? AND released=0',
                                      (device,)).fetchone()[0]
                last = db.execute('SELECT pressure FROM training_reservations WHERE device=? ORDER BY rowid DESC LIMIT 1',
                                  (device,)).fetchone()
                budget = plan(**common,committed_bytes=reserved+supplied.get('committed_bytes',0),
                              previous_pressure=last[0] if last else None)
                if not budget['fits']:
                    raise ValueError('insufficient launch budget: '+json.dumps(budget))
                db.execute('INSERT INTO training_reservations VALUES(?,?,?,?,0)',
                           (key,device,budget['estimated_bytes'],budget['pressure']))
                print(json.dumps(dict(reservation=budget,claim=key)),flush=True)
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
                db.execute("UPDATE training_reservations SET released=1 WHERE claim=?",(key,))
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
            db.execute("UPDATE training_reservations SET released=1 WHERE claim=?",(key,))
        return rc if rc>=0 else 128-rc
    finally:
        db.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adapter', help='trusted host verifier and native restore adapter')
    parser.add_argument('database')
    parser.add_argument('request',type=Path)
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    command=args.command[1:] if args.command[:1]==['--'] else args.command
    adapter = None
    if args.adapter:
        spec = importlib.util.spec_from_file_location('trusted_training_adapter',args.adapter)
        if spec is None or spec.loader is None:
            raise ValueError('invalid host adapter')
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
    return execute(args.database,json.loads(args.request.read_text()),command,adapter=adapter)


if __name__=='__main__':
    raise SystemExit(main())
