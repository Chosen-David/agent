"""Durable experiment-review handoff for a trusted, single-host research supervisor.

Trusted adapters own evidence verification, authenticated human decisions and
idempotent downstream dispatch. Worker input never selects executable callbacks.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
from pathlib import Path
import sqlite3
import time


class ResearchHandoff:
    def __init__(self,database,clock=time.time):
        self.path=Path(database).resolve()
        self.db=sqlite3.connect(self.path,timeout=30)
        self.db.row_factory=sqlite3.Row
        self.clock=clock
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS research_reviews(
          task TEXT PRIMARY KEY, spec TEXT NOT NULL, state TEXT NOT NULL,
          created REAL, deadline REAL, receipt TEXT, reason TEXT);
        CREATE TABLE IF NOT EXISTS research_events(
          seq INTEGER PRIMARY KEY, task TEXT, at REAL, state TEXT, reason TEXT);
        CREATE TABLE IF NOT EXISTS research_services(
          pool TEXT PRIMARY KEY, heartbeat REAL, available INTEGER, reason TEXT);
        """)

    def service(self,pool,available,reason):
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO research_services VALUES(?,?,?,?)',
                            (pool,self.clock(),int(available),reason))

    def preflight(self,pool,max_age=90):
        row=self.db.execute('SELECT * FROM research_services WHERE pool=?',(pool,)).fetchone()
        if not row or not row['available'] or self.clock()-row['heartbeat']>max_age:
            raise RuntimeError('review backend unavailable: '+(row['reason'] if row else 'no live consumer'))

    @staticmethod
    def validate(spec):
        for name in ('task','experiment','cycle','producer','pool','evidence','contract','on_pass','on_reject','authorization'):
            if not isinstance(spec.get(name),str) or not spec[name].strip():
                raise ValueError('missing handoff field '+name)
        if type(spec.get('takeover')) is not bool or not isinstance(spec.get('dependencies'),list):
            raise ValueError('explicit takeover policy and dependencies required')
        if spec['task'] in spec['dependencies'] or not all(isinstance(d,str) and d for d in spec['dependencies']):
            raise ValueError('invalid review dependency')

    @staticmethod
    def insert(db,spec,now):
        ResearchHandoff.validate(spec)
        packed=json.dumps(spec,sort_keys=True)
        prior=db.execute('SELECT spec FROM research_reviews WHERE task=?',(spec['task'],)).fetchone()
        if prior:
            if prior[0]!=packed:raise ValueError('task binding changed; version review')
            return
        db.execute('INSERT INTO research_reviews VALUES(?,?,?,?,?,NULL,NULL)',
                   (spec['task'],packed,'waiting-human',now,now+600))
        db.execute('INSERT INTO research_events(task,at,state,reason) VALUES(?,?,?,?)',
                   (spec['task'],now,'waiting-human','audit window open'))

    def submit(self,spec,*,created=None):
        now=self.clock() if created is None else created
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            self.insert(self.db,spec,now)

    def tick(self,host,tasks,*,idle,independent):
        # Run admitted independent work even when another task lacks a reviewer.
        actions={}
        if idle():
            for action in independent:
                try:outcome=action()
                except Exception as exc:outcome='blocked: '+str(exc)
                actions[action.__name__]=outcome
                if outcome=='launched':break
        for task in tasks:
            try:actions[task]=self.advance(task,host)
            except Exception as exc:
                self._set(task,'blocked-backend',str(exc))
                actions[task]='blocked-backend'
        return actions

    def _event(self,task,state,reason):
        self.db.execute('INSERT INTO research_events(task,at,state,reason) VALUES(?,?,?,?)',
                        (task,self.clock(),state,reason))

    def _set(self,task,state,reason,receipt=None):
        with self.db:
            self.db.execute('UPDATE research_reviews SET state=?,reason=?,receipt=coalesce(?,receipt) WHERE task=?',
                (state,reason,json.dumps(receipt) if receipt is not None else None,task))
            self._event(task,state,reason)

    @contextmanager
    def lock(self,task):
        key=hashlib.sha256(task.encode()).hexdigest()
        path=self.path.with_name(self.path.name+'.review-'+key+'.lock')
        with path.open('a+b') as f:
            try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:
                yield False
            else:yield True

    def advance(self,task,host,*,human=None):
        with self.lock(task) as owned:
            if not owned:return 'busy'
            row=self.db.execute('SELECT * FROM research_reviews WHERE task=?',(task,)).fetchone()
            if not row:raise KeyError(task)
            spec=json.loads(row['spec'])
            state=row['state']
            if state in ('rejected','repair'):
                handler=getattr(host,'remediate',None)
                if handler:handler(spec,json.loads(row['receipt']))
                return state
            if state in ('completed','blocked-human','blocked-ambiguous'):return state
            if any(not self.db.execute("SELECT 1 FROM research_reviews WHERE task=? AND state='completed'",(dep,)).fetchone()
                   for dep in spec['dependencies']):return 'waiting-dependencies'
            if state in ('passed','resuming'):
                try:
                    receipt=json.loads(row['receipt'])
                    if not host.valid(spec,receipt):raise ValueError('stale or unverified receipt')
                    self._set(task,'resuming','reconcile downstream by cycle and task ID')
                    done=host.resume(spec,receipt)
                    if done:self._set(task,'completed','downstream launch independently observed')
                    return 'completed' if done else 'resuming'
                except Exception as exc:
                    self._set(task,'resuming',str(exc));return 'resuming'
            if human is not None:
                if state!='waiting-human' or self.clock()>=row['deadline']:raise ValueError('late human response')
                receipt=host.human(spec,human)
            else:
                if self.clock()<row['deadline']:return 'waiting-human'
                if not spec['takeover']:
                    self._set(task,'blocked-human','human authorization required');return 'blocked-human'
                try:self.preflight(spec['pool'])
                except RuntimeError as exc:
                    self._set(task,'blocked-backend',str(exc));return 'blocked-backend'
                try:
                    self._set(task,'running','independent consumer claimed review')
                    if state=='running':
                        recover=getattr(host,'recover',None)
                        receipt=recover(spec) if recover else None
                        if not receipt:
                            self._set(task,'blocked-ambiguous','reconcile previous reviewer invocation before retry')
                            return 'blocked-ambiguous'
                    else:receipt=host.review(spec)
                except Exception as exc:
                    self._set(task,'blocked-ambiguous',str(exc));return 'blocked-ambiguous'
            if not host.valid(spec,receipt):
                self._set(task,'blocked-backend','receipt failed current binding');return 'blocked-backend'
            verdict=receipt['decision']
            if verdict not in ('passed','rejected','repair'):raise ValueError('unknown review outcome')
            self._set(task,verdict,receipt['reason'],receipt)
            if verdict in ('rejected','repair'):
                handler=getattr(host,'remediate',None)
                if handler:handler(spec,receipt)
            return verdict
