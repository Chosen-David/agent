"""Reference-based retention planning for immutable checkpoint generations.

The producer's ResultStore and live restore adapter retain authority for compatibility.
This catalog never removes payloads. Quarantine requires an explicit adapter-owned
atomic release transaction; without it the result remains a plan.
"""
import json
import os
import shutil
import stat
import uuid
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
            CREATE TABLE IF NOT EXISTS checkpoint_purge_policy(
                artifact TEXT PRIMARY KEY REFERENCES checkpoint_assets);
            CREATE TABLE IF NOT EXISTS checkpoint_refs(
                artifact TEXT REFERENCES checkpoint_assets, consumer TEXT, purpose TEXT,
                PRIMARY KEY(artifact,consumer,purpose));
            CREATE TABLE IF NOT EXISTS checkpoint_history(
                seq INTEGER PRIMARY KEY, artifact TEXT, operation TEXT, detail TEXT);
        """)

    def register(self, artifact, path, *, run, trajectory, family, step, level,
                 origin='historical', auto=False, purge_after_quarantine=False):
        if not all(isinstance(x,str) and x.strip() for x in (artifact,run,trajectory,family)):
            raise ValueError('immutable artifact, run, family and trajectory required')
        if type(step) is not int or step < 0 or level not in {'L0','L1','L2','L3'}:
            raise ValueError('invalid checkpoint level or step')
        if origin not in {'historical','managed'} or type(auto) is not bool or (auto and origin!='managed'):
            raise ValueError('automatic retirement requires producer opt-in at creation')
        if type(purge_after_quarantine) is not bool or (purge_after_quarantine and not auto):
            raise ValueError('permanent retirement requires an explicit managed auto policy')
        physical = Path(path).resolve(strict=True)
        st = physical.stat()
        values = (artifact,str(physical),st.st_dev,st.st_ino,run,trajectory,family,step,level,origin,int(auto))
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM checkpoint_assets WHERE artifact=? OR (dev=? AND ino=?)',
                                  (artifact,st.st_dev,st.st_ino)).fetchone()
            if row:
                if row == values:
                    policy = self.db.execute('SELECT 1 FROM checkpoint_purge_policy WHERE artifact=?',
                                             (artifact,)).fetchone()
                    if bool(policy) != purge_after_quarantine:
                        raise ValueError('retirement authorization is fixed at creation')
                    return artifact
                raise ValueError('asset identity conflict; reference the original artifact ID')
            self.db.execute('INSERT INTO checkpoint_assets VALUES(?,?,?,?,?,?,?,?,?,?,?)',values)
            if purge_after_quarantine:
                self.db.execute('INSERT INTO checkpoint_purge_policy VALUES(?)',(artifact,))
            self._event(artifact,'registered',str(physical))
        return artifact

    def _event(self, artifact, operation, detail):
        self.db.execute('INSERT INTO checkpoint_history(artifact,operation,detail) VALUES(?,?,?)',
                        (artifact,operation,detail))

    def reference(self, artifact, consumer, purpose, *, release=False):
        if not consumer or not purpose:
            raise ValueError('named consumer and purpose required')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            last = self.db.execute("""SELECT operation FROM checkpoint_history
                WHERE artifact=? AND operation LIKE 'quarantin%' ORDER BY seq DESC LIMIT 1""",
                (artifact,)).fetchone()
            if not release and last in {('quarantined',),('quarantine-intent',),('quarantine-purge-intent',),('quarantine-purged',)}:
                raise ValueError('generation is withdrawn or under reconciliation')
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

    def replacement_candidates(self, claim, *, store, verifier):
        """Record an accepted explicit replacement; keep original evidence and all holds."""
        row = self.db.execute('SELECT status,request FROM training_claims WHERE claim=?',(claim,)).fetchone()
        if not row:
            raise ValueError('unknown execution claim')
        req = json.loads(row[1])
        if row[0] != 'awaiting-validation' or req.get('mode') != 'RERUN_REPLACE':
            raise ValueError('completed explicit replacement run required')
        new,old = req['run_id'],req['prior_run']
        if new == old:
            raise ValueError('replacement needs a distinct run')
        checked = store.decide_run(new,req['scientific_context'],verifier=verifier)
        if checked['decision'] != 'reuse' or checked['validation_status'] != 'usable-with-scope':
            raise ValueError('replacement is not accepted for its stated scope')
        candidates=[]
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            for artifact, level in self.db.execute('SELECT artifact,level FROM checkpoint_assets WHERE run=?',(old,)):
                held = self.db.execute('SELECT 1 FROM checkpoint_refs WHERE artifact=? LIMIT 1',(artifact,)).fetchone()
                if level in ('L2','L3') and not held:
                    candidates.append(artifact)
                    self._event(artifact,'replaced-candidate',json.dumps(dict(claim=claim,old=old,new=new,
                        proof=checked['record_sha256'],reason=req['reason'])))
        return dict(action='candidate-for-review',old=old,new=new,artifacts=candidates,
                    reclaimed_bytes=0,scope='producer live holds and unique recovery still require review')

    def quarantine(self, artifact, replacement, *, store, provider, byte_limit):
        """Withdraw a preauthorized, managed generation under a live host-wide release lease.

        The producer adapter must fence all writers and readers (including independent
        launchers) for both assets across review and rename. Quarantine is same-device
        and reversible. An intent is committed before rename for crash reconciliation.
        """
        row = self.db.execute('SELECT physical,origin,auto FROM checkpoint_assets WHERE artifact=?',
                              (artifact,)).fetchone()
        if not row or row[1:] != ('managed',1):
            return dict(status='protected', reason='no creation-time managed retirement policy')
        source = Path(row[0])
        with provider.release_lease(artifact,replacement):
            replacement_row=self.db.execute('SELECT physical FROM checkpoint_assets WHERE artifact=?',(replacement,)).fetchone()
            match=getattr(provider,'generation_matches',None)
            if (not replacement_row or not callable(match) or match(artifact,source) is not True
                    or match(replacement,Path(replacement_row[0])) is not True):
                return dict(status='protected',reason='producer-to-physical generation binding unverified')
            review = self.review(artifact,replacement,store=store,provider=provider,byte_limit=byte_limit)
            if review['status'] != 'candidate-for-review':
                return review
            # Serialize local reference creation with the withdrawal and repeat physical checks.
            target = source.with_name('.quarantine-' + uuid.uuid4().hex)
            detail = json.dumps(dict(source=str(source), target=str(target), replacement=replacement))
            with self.db:
                self._event(artifact,'quarantine-intent',detail)
            with self.db:
                self.db.execute('BEGIN IMMEDIATE')
                holds = self.db.execute('SELECT 1 FROM checkpoint_refs WHERE artifact=? LIMIT 1',
                                        (artifact,)).fetchone()
                expected = self.db.execute('SELECT dev,ino FROM checkpoint_assets WHERE artifact=?',
                                           (artifact,)).fetchone()
                st = source.lstat()
                if holds or (st.st_dev,st.st_ino) != expected or target.exists():
                    self._event(artifact,'quarantine-cancelled',detail)
                    return dict(status='protected',reason='references or identity changed')
                source.rename(target)
                fd = os.open(target.parent,os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
                self._event(artifact,'quarantined',detail)
            return dict(status='quarantined',source=str(source),target=str(target),reclaimed_bytes=0)

    def purge_quarantined(self, artifact, replacement, *, provider):
        """Purge only a separately preauthorized managed generation under a second host fence."""
        approved=self.db.execute('SELECT 1 FROM checkpoint_purge_policy WHERE artifact=?',(artifact,)).fetchone()
        if not approved:
            return dict(status='protected',reason='no creation-time permanent retirement authorization')
        with provider.release_lease(artifact,replacement):
            with self.db:
                self.db.execute('BEGIN IMMEDIATE')
                events=self.db.execute("""SELECT operation,detail FROM checkpoint_history
                    WHERE artifact=? AND operation LIKE 'quarantin%' ORDER BY seq DESC LIMIT 1""",
                    (artifact,)).fetchone()
                if not events or events[0]!='quarantined':
                    return dict(status='protected',reason='requires completed reversible quarantine')
                row=self.db.execute('SELECT physical,dev,ino,origin,auto FROM checkpoint_assets WHERE artifact=?',
                                    (artifact,)).fetchone()
                record=json.loads(events[1])
                target=Path(record['target'])
                if (record.get('replacement')!=replacement or row[3:]!=('managed',1) or target.parent!=Path(row[0]).parent
                        or not target.name.startswith('.quarantine-')):
                    raise ValueError('inconsistent managed quarantine identity')
                st=target.lstat()
                if (st.st_dev,st.st_ino)!=row[1:3] or Path(row[0]).exists():
                    raise ValueError('quarantined identity changed or source is live')
                holds=self.db.execute('SELECT 1 FROM checkpoint_refs WHERE artifact=?',(artifact,)).fetchone()
                facts=provider.purge_facts(artifact,replacement,target)
                required=('restore_verified','lightweight_history_retained','replacement_reachable',
                          'all_references_checked','grace_elapsed','no_unique_scientific_value')
                empty=('active_writes','consumers','recovery_dependencies','retention_holds','leases')
                if (holds or not isinstance(facts,dict) or any(facts.get(k) is not True for k in required)
                        or any(facts.get(k)!=[] for k in empty)):
                    return dict(status='protected',reason='live or unverified research and recovery facts')
                entries=[target]
                if stat.S_ISDIR(st.st_mode):
                    entries.extend(target.rglob('*'))
                allocated=0
                for member in entries:
                    info=member.lstat()
                    if info.st_dev!=st.st_dev or not (stat.S_ISDIR(info.st_mode) or
                            (stat.S_ISREG(info.st_mode) and info.st_nlink==1)):
                        return dict(status='protected',reason='shared, linked or special payload')
                    allocated += info.st_blocks*512
                self._event(artifact,'quarantine-purge-intent',events[1])
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            with self.db:
                self._event(artifact,'quarantine-purged',json.dumps(dict(target=str(target),allocated_bytes=allocated)))
            return dict(status='purged',removed_allocated_bytes=allocated)


def stage_copy(source, destination_parent, *, expected_hashes, provider):
    """Copy under a producer read lease into a fresh, verified, same-destination generation.

    Existing locations and catalog references stay intact; promotion and retirement are
    distinct operations. The provider tests the staged files before publication.
    """
    import hashlib
    source=Path(source).resolve(strict=True)
    parent=Path(destination_parent).resolve(strict=True)
    if not source.is_dir() or not parent.is_dir() or parent.is_relative_to(source):
        raise ValueError('separate source and destination directories required')
    if not expected_hashes or any(not isinstance(d,str) or len(d)!=64 for d in expected_hashes.values()):
        raise ValueError('manifest with content digests required')
    token=uuid.uuid4().hex
    staging=parent/('.copy-'+token)
    final=parent/token
    with provider.copy_lease(source):
        members=list(source.rglob('*'))
        if any(f.is_symlink() or not (f.is_dir() or f.is_file()) for f in members):
            raise ValueError('shared links or special source members require separate reconciliation')
        names={str(f.relative_to(source)) for f in members if f.is_file()}
        if names!=set(expected_hashes):
            raise ValueError('source inventory differs from frozen manifest')
        inventory={}
        for name in expected_hashes:
            rel=Path(name)
            if rel.is_absolute() or '..' in rel.parts or rel.as_posix()!=name:
                raise ValueError('noncanonical manifest member')
            f=source/rel
            if f.resolve(strict=True)!=f or not f.is_file():
                raise ValueError('invalid source member')
            s=f.stat()
            inventory[name]=(s.st_dev,s.st_ino,s.st_size,s.st_ctime_ns)
        if sum(s[2] for s in inventory.values())>shutil.disk_usage(parent).free:
            raise ValueError('insufficient copy staging space')
        staging.mkdir()
        for f in members:
            if f.is_dir():
                (staging/f.relative_to(source)).mkdir(parents=True,exist_ok=True)
        for name,identity in inventory.items():
            inp=source/name
            out=staging/name
            out.parent.mkdir(parents=True,exist_ok=True)
            with inp.open('rb') as src,out.open('xb') as dst:
                shutil.copyfileobj(src,dst,1<<20)
                dst.flush()
                os.fsync(dst.fileno())
            with out.open('rb') as stream:
                if hashlib.file_digest(stream,'sha256').hexdigest()!=expected_hashes[name]:
                    raise ValueError('staged copy digest mismatch: '+name)
            s=inp.stat()
            if (s.st_dev,s.st_ino,s.st_size,s.st_ctime_ns)!=identity:
                raise ValueError('source changed while copying')
        if provider.test_staged(staging) is not True:
            raise ValueError('staged generation failed read or restore test')
        if final.exists():
            raise FileExistsError(final)
        staging.rename(final)
        return dict(source=str(source),verified_copy=str(final),state='staged',reclaimed_bytes=0)
