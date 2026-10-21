"""Transparent Linux subject stdout/stderr/exit bridge; no models or shell."""
import base64,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
info=json.loads((out/'linux-fixture.json').read_bytes())
inner="import base64,json,os,subprocess,sys; p=subprocess.run([sys.executable,'-X','utf8',sys.argv[1]+'/scripts/run_role.py','--project',sys.argv[2],'--dry-run',*sys.argv[3:]],cwd=sys.argv[1],env={**os.environ,'PYTHONUTF8':'1','PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.PIPE,stderr=subprocess.PIPE); print(json.dumps({'stdout':base64.b64encode(p.stdout).decode(),'stderr':base64.b64encode(p.stderr).decode(),'exit':p.returncode}))"
p=subprocess.run(['wsl','--exec','python3','-c',inner,info['source'],info['project'],*sys.argv[1:]],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=120)
log=ROOT/'.agent-runs/token10-20261021/wsl09-host.log'
with log.open('ab') as f:f.write(p.stderr)
if p.returncode:
 sys.stdout.buffer.write(p.stdout);sys.stderr.buffer.write(p.stderr);sys.exit(p.returncode)
value=json.loads(p.stdout);assert set(value)=={'stdout','stderr','exit'} and type(value['exit']) is int
sys.stdout.buffer.write(base64.b64decode(value['stdout'],validate=True));sys.stderr.buffer.write(base64.b64decode(value['stderr'],validate=True));sys.exit(value['exit'])
