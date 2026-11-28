"""Exact-generation, post-creation retirement for an exclusive user's local Forge jobs.

The host supplies current launch/queue facts. Kernel write leases on every old
file also fence ordinary open(2) callers that do not use the training registry.
This adapter is scoped to jobs on the local Linux kernel.
"""
from contextlib import contextmanager, ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import time
import uuid


def identity(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(path):
    if not path.is_absolute() or path.resolve(strict=True) != path or not path.is_dir():
        raise ValueError('exact physical directory required')
    manifest = path / 'manifest.json'
    if not stat.S_ISREG(manifest.lstat().st_mode):
        raise ValueError('regular manifest required')
    m = json.loads(manifest.read_bytes())
    names = {'manifest.json', *(f'rank_{i:05}.pt' for i in range(m['rank_count']))}
    if (path.name != f"step_{m['step']}" or m['format'] != 'fsdp2_rank_local_shards'
            or {p.name for p in path.iterdir()} != names or len(m['files']) != m['rank_count']):
        raise ValueError('unexpected generation contents')
    members = {}
    for name in sorted(names):
        p = path / name
        s = p.lstat()
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1:
            raise ValueError('linked or non-regular member')
        members[name] = [*identity(p), s.st_size, s.st_mtime_ns]
    for i, row in enumerate(sorted(m['files'], key=lambda r: r['rank'])):
        if row['rank'] != i or row['path'] != f'rank_{i:05}.pt' or members[row['path']][2] != row['bytes']:
            raise ValueError('rank mapping or length mismatch')
    return dict(path=str(path), directory=identity(path), members=members, manifest=digest(manifest),
                family=m['identity_sha256'], step=m['step'], topology=[m['world_size'],m['ep_size']])


def authorize(store, source, replacement, batch):
    old, new = snapshot(source), snapshot(replacement)
    if (source.parent != replacement.parent or old['step'] >= new['step']
            or old['family'] != new['family'] or old['topology'] != new['topology']):
        raise ValueError('incompatible replacement')
    # A batch cannot silently bind a new generation at a previously authorized path.
    for (entry,) in store.db.execute("SELECT detail FROM checkpoint_history WHERE operation='explicit-retirement'"):
        previous=json.loads(entry)
        if previous['batch']==batch and previous['old']['path']==old['path']:
            if previous['old']!=old or previous['new']!=new:
                raise ValueError('authorization binding changed')
    def register(s):
        key = 'native-' + hashlib.sha256(json.dumps([s['path'],s['directory'],s['manifest']]).encode()).hexdigest()
        return store.register(key, s['path'], run=str(source.parent.parent),trajectory=str(source.parent),
                              family=s['family'],step=s['step'],level='L3')
    key, successor = register(old), register(new)
    prior = store.db.execute("SELECT detail FROM checkpoint_history WHERE artifact=? AND operation='explicit-retirement' ORDER BY seq DESC LIMIT 1",(key,)).fetchone()
    if prior:
        detail=json.loads(prior[0])
        if detail['batch']!=batch or detail['old']!=old or detail['new']!=new:
            raise ValueError('conflicting scope')
        return key
    grant=dict(batch=batch, authorized_at=time.time(), old=old,new=new,successor=successor,
               verification='user accepted native manifest validation only',
               quarantine=str(source.with_name('.quarantine-'+uuid.uuid4().hex)))
    with store.db:
        store._event(key,'explicit-retirement',json.dumps(grant))
    return key


@contextmanager
def file_fence(paths):
    # Nonblocking open avoids deadlock with another owner's lease. Ignore SIGIO
    # only in this synchronous maintenance process; F_GETLEASE detects breaks.
    with ExitStack() as stack:
        old=signal.signal(signal.SIGIO,signal.SIG_IGN)
        stack.callback(signal.signal,signal.SIGIO,old)
        fds=[]
        for path in paths:
            fd=os.open(path,os.O_RDWR|os.O_NONBLOCK|os.O_NOFOLLOW)
            stack.callback(os.close,fd)
            try:
                fcntl.fcntl(fd,fcntl.F_SETLEASE,fcntl.F_WRLCK)
            except OSError as exc:
                raise RuntimeError(f'file lease unavailable: {path}: {exc}') from exc
            fds.append(fd)
        def verify():
            if any(fcntl.fcntl(fd,fcntl.F_GETLEASE)!=fcntl.F_WRLCK for fd in fds):
                raise RuntimeError('concurrent open requested')
        yield verify


def retire(store,key,*,live_check):
    grant=json.loads(store.db.execute("SELECT detail FROM checkpoint_history WHERE artifact=? AND operation='explicit-retirement'",(key,)).fetchone()[0])
    old,new=grant['old'],grant['new']
    source,replacement,target=map(Path,(old['path'],new['path'],grant['quarantine']))
    parent=source.parent
    def event(operation,detail):
        with store.db:
            store._event(key,operation,json.dumps(detail))
    with ExitStack() as stack:
        fd=os.open(parent,os.O_DIRECTORY|os.O_NOFOLLOW)
        stack.callback(os.close,fd)
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if source.parent.resolve()!=parent or target.parent!=parent or snapshot(replacement)!=new:
            raise ValueError('physical binding changed')
        pointer=json.loads((parent/'LATEST').read_bytes())
        if pointer.get('directory')!=replacement.name or pointer.get('manifest_sha256')!=new['manifest']:
            raise ValueError('LATEST changed')
        prior=store.db.execute("SELECT operation,detail FROM checkpoint_history WHERE artifact=? AND operation LIKE 'quarantin%' ORDER BY seq DESC LIMIT 1",(key,)).fetchone()
        if prior and prior[0]=='quarantine-purged':
            return dict(status='already-purged',allocated=0)
        location=target if target.exists() else source
        if location==target and (source.exists() or not prior):
            raise ValueError('unaudited quarantine')
        if not location.exists() and prior and prior[0]=='quarantine-purge-intent':
            event('quarantine-purged',{'reconciled':True})
            return dict(status='purged-before-restart',allocated=0)
        if identity(location)!=old['directory'] or location.resolve()!=location:
            raise ValueError('generation identity changed')
        remaining={p.name for p in location.iterdir()}
        partial=prior and prior[0]=='quarantine-purge-intent' and location==target
        if not remaining<=old['members'].keys() or (not partial and remaining!=old['members'].keys()):
            raise ValueError('generation membership changed')
        for name in remaining:
            p=location/name
            s=p.lstat()
            if [*identity(p),s.st_size,s.st_mtime_ns]!=old['members'][name] or s.st_nlink!=1:
                raise ValueError('member identity changed')
        if 'manifest.json' in remaining and digest(location/'manifest.json')!=old['manifest']:
            raise ValueError('old manifest changed')
        live_check(source,replacement)
        lease_stack=stack.enter_context(ExitStack())
        held=lease_stack.enter_context(file_fence([location/n for n in sorted(remaining)]))
        live_check(source,replacement)
        if snapshot(replacement)!=new or json.loads((parent/'LATEST').read_bytes())!=pointer:
            raise ValueError('replacement or LATEST changed during fencing')
        if identity(location)!=old['directory'] or {p.name for p in location.iterdir()}!=remaining:
            raise ValueError('generation changed during fencing')
        # Check refs in the same transaction that withdraws the asset to other
        # registry clients. Durable intent allows resuming after either rename or unlink.
        with store.db:
            store.db.execute('BEGIN IMMEDIATE')
            if store.db.execute('SELECT 1 FROM checkpoint_refs WHERE artifact=?',(key,)).fetchone():
                raise ValueError('active registry reference')
            if location==source:
                store._event(key,'quarantine-intent',json.dumps({'target':str(target)}))
        held()
        if location==source:
            if target.exists() or identity(source)!=old['directory']:
                raise ValueError('generation identity changed')
            source.rename(target)
            os.fsync(fd)
            event('quarantined',{'target':str(target)})
        held()
        total=sum((target/n).lstat().st_blocks*512 for n in remaining)
        event('quarantine-purge-intent',{'allocated':total,'target':str(target)})
        for name in remaining:
            p=target/name
            if identity(p)!=old['members'][name][:2]:
                raise ValueError('member identity changed in quarantine')
            p.unlink()
        lease_stack.close()
        target.rmdir()
        os.fsync(fd)
        event('quarantine-purged',{'allocated':total})
        return dict(status='purged',allocated=total)
