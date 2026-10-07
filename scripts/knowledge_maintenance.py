#!/usr/bin/env python3
"""Owned tmux interval runner for bounded, resumable knowledge maintenance.

The model command is explicit host configuration, never source material.
No model or paid service is installed by this script.
"""
import argparse
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time

SOCKET = 'agent-knowledge'
SHANGHAI = timezone(timedelta(hours=8))


def interval_seconds(config):
    value = config.get('interval_seconds', 3600)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError('interval_seconds must be a positive integer')
    return value


def next_due(now, interval=3600):
    return now + interval


def advance_due(previous_due, now, interval):
    """Keep the scheduled cadence, skipping elapsed slots after one round."""
    return previous_due + max(1, math.floor((now - previous_due) / interval) + 1) * interval


def load_state(config, now):
    path = Path(config['state_dir'])/'state.json'
    interval = interval_seconds(config)
    try:
        saved = json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError:
        saved = {'rounds': []}
    if saved.get('interval_seconds') != interval:
        if 'next_due' in saved:
            saved.setdefault('schedule_migrations', []).append({
                'at': now, 'previous_due': saved['next_due'],
                'previous_interval_seconds': saved.get('interval_seconds'),
                'interval_seconds': interval})
        saved.update(interval_seconds=interval, next_due=next_due(now, interval))
    # Persist the migration before a heartbeat or a model launch. A guard restart
    # must not reset the new due time or discard historical round receipts.
    atomic(path, saved)
    return saved


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.new')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)


def tmux(*args):
    return subprocess.run(['tmux', '-L', SOCKET, *args], capture_output=True, text=True)


def status(config):
    state = Path(config['state_dir'])
    try:
        live = json.loads((state/'live.json').read_text(encoding='utf-8'))
        os.kill(live['pid'], 0)
        fresh = time.time() - live['heartbeat_at'] < 90
    except (OSError, ValueError, KeyError):
        live, fresh = {}, False
    panes = tmux('list-panes', '-t', '=' + config['session'], '-F', '#{pane_dead}')
    return {'session': config['session'], 'socket': SOCKET,
            'live': fresh and panes.returncode == 0 and '0' in panes.stdout.splitlines(),
            'worker': live, 'interval_seconds': interval_seconds(config),
            'schedule': f'Every {interval_seconds(config)} seconds; missed slots skipped; Asia/Shanghai display',
            'config': str(state/'launch.json')}


def run_round(config):
    repo, state = Path(config['repo']), Path(config['state_dir'])
    dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=repo, capture_output=True, text=True)
    if dirty.returncode or dirty.stdout.strip():
        return {'status':'blocked', 'reason':'repository is dirty or unreadable; no model launched'}
    if not config['runner']:
        return {'status':'blocked', 'reason':'no real model runner configured'}
    run_id = datetime.now(SHANGHAI).strftime('%Y%m%d-%H%M%S')
    run_dir = state/'rounds'/run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    # Single owner across instances. Crash leaves a lock for human reconciliation;
    # never remove an old lock just because a timestamp expired.
    lock = state/'round.lock'
    child = None
    try:
        lock.mkdir()
    except FileExistsError:
        return {'status':'blocked', 'reason':'unreconciled existing maintenance round lock'}
    try:
        prompt = repo/'prompts/engineering_knowledge_continuous_learning.md'
        text = prompt.read_text(encoding='utf-8')
        (run_dir/'prompt.md').write_text(text, encoding='utf-8')
        args = list(config['runner']) + ['--repo', config['windows_repo'] or str(repo),
                '--prompt', str(run_dir/'prompt.md'), '--run-dir', str(run_dir),
                '--timeout', str(config['timeout_seconds'])]
        if config['windows_repo']:
            # Convert only file arguments. Native Windows auth stays on Windows.
            for flag in ('--prompt','--run-dir'):
                i=args.index(flag)+1
                args[i]=subprocess.check_output(['wslpath','-w',args[i]],text=True).strip()
        with (run_dir/'runner.log').open('w', encoding='utf-8') as log:
            child = subprocess.Popen(args, cwd=repo, stdout=log, stderr=subprocess.STDOUT)
            while child.poll() is None:
                atomic(state/'live.json', {'pid':os.getpid(), 'heartbeat_at':time.time(),
                       'session':config['session'], 'active_round':run_id, 'runner_pid':child.pid,
                       'interval_seconds':interval_seconds(config)})
                time.sleep(5)
        result={'status':'runner_succeeded' if child.returncode==0 else 'runner_failed',
                'exit_code':child.returncode,'run_id':run_id,'run_dir':str(run_dir),
                'scope':'Runner exit is not independent scientific acceptance; read final.md and evidence.'}
        atomic(run_dir/'receipt.json',result)
        return result
    finally:
        # A runner may survive a supervisor I/O error. Preserve ownership until
        # an operator reconciles it instead of launching a duplicate model.
        if child is None or child.poll() is not None:
            lock.rmdir()


def serve(config):
    if not os.environ.get('TMUX'):
        raise RuntimeError('serve must be launched by start inside owned tmux')
    state=Path(config['state_dir'])
    saved=load_state(config, time.time())
    while not (state/'stop').exists():
        atomic(state/'live.json', {'pid':os.getpid(),'heartbeat_at':time.time(),
                                 'session':config['session'],'next_due':saved['next_due'],
                                 'interval_seconds':saved['interval_seconds'],
                                 'next_due_shanghai':datetime.fromtimestamp(saved['next_due'],SHANGHAI).isoformat()})
        if time.time() >= saved['next_due']:
            try:
                result=run_round(config)
            except Exception as exc:
                result={'status':'runner_error','reason':f'{type(exc).__name__}: {exc}'}
            saved['rounds'].append(result)
            saved['next_due']=advance_due(saved['next_due'],time.time(),saved['interval_seconds'])
        atomic(state/'state.json',saved)
        time.sleep(20)
    (state/'live.json').unlink(missing_ok=True)


def guard(path, config):
    """Recover a crashed scheduler; never replay an unreconciled model round."""
    state=Path(config['state_dir'])
    while not (state/'stop').exists():
        result=subprocess.run([sys.executable,str(Path(__file__).resolve()),
                               'serve','--config',str(path)],cwd=config['repo'])
        if result.returncode == 0:
            return
        time.sleep(5)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['start','status','stop','serve','guard'])
    p.add_argument('--config',required=True)
    a=p.parse_args(); path=Path(a.config).resolve(); config=json.loads(path.read_text(encoding='utf-8'))
    if a.command=='serve':
        serve(config); return
    if a.command=='guard':
        guard(path,config); return
    if a.command=='start':
        if sys.platform=='win32': raise RuntimeError('start requires Linux/WSL with tmux')
        if not status(config)['live']:
            (Path(config['state_dir'])/'stop').unlink(missing_ok=True)
            if tmux('has-session','-t','='+config['session']).returncode==0:
                raise RuntimeError('existing session has no matching heartbeat; reconcile before restart')
            command=shlex.join([sys.executable,str(Path(__file__).resolve()),'guard','--config',str(path)])
            log=Path(config['state_dir'])/'supervisor.log'
            launched=tmux('new-session','-d','-s',config['session'],'-c',config['repo'],
                          command+' >> '+shlex.quote(str(log))+' 2>&1')
            if launched.returncode: raise RuntimeError(launched.stderr)
            for _ in range(30):
                if status(config)['live']: break
                time.sleep(.2)
        out=status(config)
        atomic(Path(config['state_dir'])/'receipt.json',out)
        print(json.dumps(out,ensure_ascii=False,indent=2))
        if not out['live']: raise RuntimeError('no matching live readback')
    elif a.command=='stop':
        (Path(config['state_dir'])/'stop').touch()
        print(json.dumps({'status':'stop_requested','session':config['session'],
                          'scope':'Current bounded round finishes; owned scheduler then exits.'}))
    else: print(json.dumps(status(config),ensure_ascii=False,indent=2))


if __name__=='__main__': main()
