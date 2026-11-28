"""Reference-based retention planning for immutable checkpoint generations.

The producer's ResultStore and live restore adapter retain authority for compatibility.
This catalog never removes payloads. Quarantine requires an explicit adapter-owned
atomic release transaction; without it the result remains a plan.
"""
import json
import sqlite3
from pathlib import Path


class CheckpointRetention:
    def __init__(self, database):
        self.db = sqlite3.connect(database, timeout=30)
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS checkpoint_assets(
                artifact TEXT PRIMARY KEY, physical TEXT NOT NULL, dev INTEGER, ino INTEGER,
                run TEXT NOT NULL, trajectory TEXT NOT NULL, family TEXT NOT NULL, step INTEGER,
                level TEXT NOT NULL, origin TEXT NOT NULL, auto INTEGER NOT NULL,
                UNIQUE(dev,ino));
            CREATE TABLE IF NOT EXISTS checkpoint_refs(
                artifact TEXT REFERENCES checkpoint_assets, consumer TEXT, purpose TEXT,
                PRIMARY KEY(artifact,consumer,purpose));
            CREATE TABLE IF NOT EXISTS checkpoint_history(
                seq INTEGER PRIMARY KEY, artifact TEXT, operation TEXT, detail TEXT);
        """)

    def register(self, artifact, path, *, run, trajectory, family, step, level,
                 origin='historical', auto=False):
        if not all(isinstance(x,str) and x.strip() for x in (artifact,run,trajectory,family)):
            raise ValueError('immutable artifact, run, family and trajectory required')
        if type(step) is not int or step < 0 or level not in {'L0','L1','L2','L3'}:
            raise ValueError('invalid checkpoint level or step')
        if origin not in {'historical','managed'} or type(auto) is not bool or (auto and origin!='managed'):
            raise ValueError('automatic retirement requires producer opt-in at creation')
        physical = Path(path).resolve(strict=True)
        st = physical.stat()
        values = (artifact,str(physical),st.st_dev,st.st_ino,run,trajectory,family,step,level,origin,int(auto))
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM checkpoint_assets WHERE artifact=? OR (dev=? AND ino=?)',
                                  (artifact,st.st_dev,st.st_ino)).fetchone()
            if row:
                if row == values:
                    return artifact
                raise ValueError('asset identity conflict; reference the original artifact ID')
            self.db.execute('INSERT INTO checkpoint_assets VALUES(?,?,?,?,?,?,?,?,?,?,?)',values)
            self._event(artifact,'registered',str(physical))
        return artifact

    def _event(self, artifact, operation, detail):
        self.db.execute('INSERT INTO checkpoint_history(artifact,operation,detail) VALUES(?,?,?)',
                        (artifact,operation,detail))

    def reference(self, artifact, consumer, purpose, *, release=False):
        if not consumer or not purpose:
            raise ValueError('named consumer and purpose required')
        with self.db:
            if release:
                count = self.db.execute('DELETE FROM checkpoint_refs WHERE artifact=? AND consumer=? AND purpose=?',
                                        (artifact,consumer,purpose)).rowcount
            else:
                count = self.db.execute('INSERT OR IGNORE INTO checkpoint_refs VALUES(?,?,?)',
                                        (artifact,consumer,purpose)).rowcount
            if count:
                self._event(artifact,'released' if release else 'referenced',json.dumps([consumer,purpose]))

    def review(self, artifact, replacement, *, store, provider, byte_limit):
        # Both sets of facts are necessary: local references and producer-side
        # reachability, locks, live readers, integrity and actual restore.
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            rows = []
            for key in (artifact,replacement):
                row = self.db.execute('SELECT * FROM checkpoint_assets WHERE artifact=?',(key,)).fetchone()
                if not row:
                    raise ValueError('unknown checkpoint ' + key)
                rows.append(row)
            old,new = rows
            reasons = []
            if old[5:7] != new[5:7] or new[7] <= old[7] or old[8] != 'L3' or new[8] != 'L3':
                reasons.append('distinct compatible later full recovery point required')
            for row in rows:
                try:
                    st=Path(row[1]).stat()
                    if (st.st_dev,st.st_ino)!=row[2:4]:
                        reasons.append('physical identity changed')
                except OSError as exc:
                    reasons.append(str(exc))
            holds = self.db.execute('SELECT consumer,purpose FROM checkpoint_refs WHERE artifact=?',
                                    (artifact,)).fetchall()
            if holds:
                reasons.append('active retention references')
            if not reasons:
                verified = store.review_recovery(artifact,replacement,byte_limit=byte_limit,provider=provider)
                reasons += verified['reasons']
                if verified['action']!='candidate-for-review' and not reasons:
                    reasons.append('producer did not accept replacement')
            status = 'protected' if reasons else 'candidate-for-review'
            result=dict(artifact=artifact,replacement=replacement,status=status,reasons=reasons,
                        references=holds,preauthorized=bool(old[10]), origin=old[9], reclaimed_bytes=0)
            self._event(artifact,'retention-review',json.dumps(result))
        return result
