"""One owned WSL tmux timer; actual worker is fresh native Windows Python."""
import fcntl,json,os,subprocess,time
from pathlib import Path
R=Path(__file__).resolve().parents[2];S=R/'.agent-runs/token-optimizer-hourly';S.mkdir(exist_ok=True)
ROOT_WINDOWS='C:/Users/WI/Desktop/home_work/AI_LLM/agent'
STATE_WINDOWS=ROOT_WINDOWS+'/.agent-runs/token-optimizer-hourly'
lock=(S/'timer.lock').open('a+b')
fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
def heartbeat(phase,child=None):
 value={'project_root':ROOT_WINDOWS,'pid':os.getpid(),'child_pid':child,'interval_seconds':3600,'phase':phase,'heartbeat_at':time.time()}
 tmp=S/'heartbeat.json.new';tmp.write_text(json.dumps(value)+'\n');tmp.replace(S/'heartbeat.json')
def state():
 value=json.loads((S/'state.json').read_text())
 if value['project_root'].replace('\\','/')!=ROOT_WINDOWS or value['interval_seconds']!=3600:raise ValueError('foreign timer state')
 return value
with (S/'timer.private.log').open('a',buffering=1) as log:
 while True:
  heartbeat('waiting')
  due=state()['next_due']
  if time.time()<due:
   time.sleep(min(30,max(1,due-time.time())));continue
  command=['/mnt/c/Python312/python.exe','-X','utf8',ROOT_WINDOWS+'/scripts/token_optimizer.py',
           '--root',ROOT_WINDOWS,'--state-dir',STATE_WINDOWS,'--codex',ROOT_WINDOWS+'/.agent-runs/engineering-kb/tools/codex.exe']
  child=subprocess.Popen(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
  while child.poll() is None:
   heartbeat('worker',child.pid);time.sleep(5)
  log.write(json.dumps({'finished_at':time.time(),'exit_code':child.returncode})+'\n')
  # A failure before tick advances the slot is not an excuse for an immediate retry storm.
  if state()['next_due']<=time.time():
   heartbeat('host-failure-cooldown');time.sleep(60)
