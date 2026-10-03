"""Scheduler boundary and runnable SQLite foreground backend.

This is NOT an installed daemon. A live serve process is required. Persistence
allows explicit restart on the same disk; it cannot keep a powered-off host alive.
"""
from __future__ import annotations

import time
from typing import Protocol
import uuid

from .core import Engine, Store


class Scheduler(Protocol):
    def capabilities(self) -> dict: ...
    def create(self, run_id: str) -> str: ...
    def read(self, monitor_id: str) -> dict: ...
    def stop(self, monitor_id: str) -> None: ...


def arm(scheduler: Scheduler, run_id: str):
    """Create + readback, never equate module presence or an ID with readiness."""
    capabilities = scheduler.capabilities()
    if not capabilities.get('ready'):
        return {'status': 'blocked', 'reason': capabilities.get('reason', 'scheduler unavailable')}
    try:
        monitor_id = scheduler.create(run_id)
        record = scheduler.read(monitor_id)
        if (not monitor_id or record.get('id') != monitor_id
                or record.get('chain_id') != run_id or record.get('status') != 'active'
                or not record.get('live')):
            return {'status': 'blocked', 'monitor_id': monitor_id,
                    'reason': 'scheduler readback did not confirm live owned monitor; reconcile this ID'}
        return {'status': 'started', 'monitor_id': monitor_id, 'readback': record,
                'durability': capabilities.get('durability')}
    except Exception as exc:
        return {'status': 'blocked', 'reason': f'scheduler operation uncertain: {type(exc).__name__}: {exc}; reconcile by run_id before retry'}


class LocalScheduler:
    def __init__(self, store: Store, clock=time.time):
        self.store, self.clock = store, clock

    def capabilities(self):
        with self.store.transaction() as db:
            live = db.execute('SELECT 1 FROM services WHERE expires>? LIMIT 1', (self.clock(),)).fetchone() is not None
        return {'ready': live, 'backend': 'sqlite-foreground', 'min_seconds': 1,
                'durability': 'same-disk restart only; live host and serve process required',
                'reason': None if live else 'no live local serve process; no daemon installed; host scheduler/cloud adapter not configured'}

    def create(self, run_id):
        monitor_id = 'local:' + run_id
        with self.store.transaction() as db:
            _, state = self.store.load(db, run_id)
            if state['status'] in ('done', 'cancelled', 'failed'):
                raise ValueError('terminal chain cannot be armed')
            if not db.execute('SELECT 1 FROM services WHERE expires>?', (self.clock(),)).fetchone():
                raise RuntimeError('local service offline')
            db.execute('INSERT INTO monitors(id,chain_id,status,due) VALUES (?,?,?,?) ON CONFLICT(chain_id) DO NOTHING',
                       (monitor_id, run_id, 'active', self.clock()))
        return monitor_id

    def read(self, monitor_id):
        with self.store.transaction() as db:
            row = db.execute('SELECT * FROM monitors WHERE id=?', (monitor_id,)).fetchone()
            if not row:
                raise KeyError(monitor_id)
            result = dict(row)
            result['live'] = db.execute('SELECT 1 FROM services WHERE expires>?', (self.clock(),)).fetchone() is not None
            return result

    def stop(self, monitor_id):
        with self.store.transaction() as db:
            db.execute("UPDATE monitors SET status='stopped' WHERE id=?", (monitor_id,))

    def wake(self, run_id, reference):
        """Trusted change notification; coalesce events without bypassing min interval."""
        if not reference:
            raise ValueError('change reference required')
        with self.store.transaction() as db:
            plan, state = self.store.load(db, run_id)
            earliest = max(self.clock(), state.get('last_check_at', 0) + plan['supervision']['min_seconds'])
            db.execute("UPDATE monitors SET due=MIN(due,?),version=version+1 WHERE chain_id=? AND status='active'", (earliest, run_id))
            state['idle_ticks'] = 0
            self.store.save(db, run_id, state)
            self.store.log(db, run_id, self.clock(), 'change_event', reference)

    def heartbeat(self, service_id, ttl=30):
        with self.store.transaction() as db:
            db.execute('INSERT INTO services VALUES (?,?) ON CONFLICT(id) DO UPDATE SET expires=excluded.expires',
                       (service_id, self.clock() + ttl))

    def drain_once(self, engine: Engine):
        """Atomic due reservation prevents duplicate timer delivery across processes."""
        now = self.clock()
        with self.store.transaction() as db:
            row = db.execute("SELECT * FROM monitors WHERE status='active' AND due<=? ORDER BY due LIMIT 1", (now,)).fetchone()
            if not row:
                return False
            plan, state = self.store.load(db, row['chain_id'])
            if state['status'] in ('done', 'cancelled', 'failed'):
                db.execute("UPDATE monitors SET status='stopped' WHERE id=?", (row['id'],))
                return True
            # Reservation is bounded: a crash before tick is retried after this delay.
            delay = state.get('next_check_seconds', plan['supervision']['min_seconds'])
            version = row['version'] + 1
            db.execute('UPDATE monitors SET due=?,version=? WHERE id=?', (now + delay, version, row['id']))
            state['last_check_at'] = now
            self.store.save(db, row['chain_id'], state)
        state = engine.tick(row['chain_id'], 'local-timer:' + uuid.uuid4().hex)
        with self.store.transaction() as db:
            db.execute("UPDATE monitors SET due=? WHERE id=? AND status='active' AND version=?",
                       (self.clock() + state.get('next_check_seconds', plan['supervision']['min_seconds']), row['id'], version))
        return True

    def serve(self, engine, stop_requested=lambda: False, max_seconds=None):
        service_id = uuid.uuid4().hex
        started = time.monotonic()
        try:
            while not stop_requested():
                if max_seconds is not None and time.monotonic() - started >= max_seconds:
                    break
                self.heartbeat(service_id)
                self.drain_once(engine)
                # Fixed service heartbeat cadence; task checks use persisted adaptive due.
                time.sleep(1.0)
        finally:
            with self.store.transaction() as db:
                db.execute('DELETE FROM services WHERE id=?', (service_id,))
