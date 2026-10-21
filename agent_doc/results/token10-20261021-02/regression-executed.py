import hashlib,json,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
out=ROOT/'agent_doc/results/token10-20261021-02'
paths=[ROOT/p for p in subprocess.check_output(['git','ls-files','agent_runtime','scripts'],cwd=ROOT).decode().splitlines() if p.endswith('.py')]+[ROOT/'tests/test_context_serialization.py',ROOT/'tests/test_communication_usage.py',ROOT/'agent_doc/results/communication-ledger-20261009/baseline_communication.py']
with zipfile.ZipFile(out/'regression-source.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in paths:z.write(p,p.relative_to(ROOT).as_posix())
source='/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent/agent_doc/results/token10-20261021-02/regression-source.zip'
code="import hashlib,json,pathlib,subprocess,sys,tempfile,zipfile; z=zipfile.ZipFile('"+source+"'); root=pathlib.Path(tempfile.mkdtemp(prefix='token10-02-')); z.extractall(root); assert all(hashlib.sha256((root/i.filename).read_bytes()).digest()==hashlib.sha256(z.read(i)).digest() for i in z.infolist()); print('Exact archive bytes verified on ext4',flush=True); p=subprocess.run([sys.executable,'-m','unittest','tests.test_context_serialization','tests.test_communication_usage'],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT); sys.stdout.buffer.write(p.stdout); sys.exit(p.returncode)"
p=subprocess.run(['wsl','--exec','python3','-c',code],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(out/'regression-wsl-retry.txt').write_bytes(p.stdout)
(out/'regression-wsl-host-stderr.bin').write_bytes(p.stderr)
print(p.stdout.decode('utf-8'));p.check_returncode()
m=json.loads((out/'manifest.json').read_bytes())
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
m['artifacts']['inputs'].append(ref(out/'regression-source.zip'))
m['artifacts']['raw_data'] += [ref(out/'regression-wsl.txt'),ref(out/'regression-wsl-retry.txt'),ref(out/'regression-wsl-host-stderr.bin')]
m['artifacts']['code'] += [ref(p) for p in paths if p.relative_to(ROOT).as_posix() not in {r['path'] for r in m['artifacts']['code']}]
(out/'manifest.json').write_bytes((json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode())
