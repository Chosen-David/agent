"""Run Linux-only strict boundaries from a byte-verified ext4 snapshot."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[4]
RUN=Path(__file__).resolve().parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


if '--worker' in sys.argv:
    with tempfile.TemporaryDirectory(prefix='memory-pack-strict-') as home:
        root=Path(home)
        with zipfile.ZipFile(sys.argv[-1]) as archive:
            for name in archive.namelist():
                if Path(name).is_absolute() or '..' in Path(name).parts:raise ValueError('snapshot path')
            archive.extractall(root)
        hashes=json.loads((root/'snapshot.json').read_text())
        for name,digest in hashes.items():
            if sha((root/name).read_bytes())!=digest:raise ValueError('source mismatch: '+name)
        print(json.dumps({'verified_files':len(hashes),'snapshot_sha256':sha((root/'snapshot.json').read_bytes()),
                          'python':sys.version,'filesystem':'temporary WSL ext4, exact working source bytes'}),flush=True)
        subprocess.run(['git','init','-q'],cwd=root,check=True)
        subprocess.run(['git','add','.'],cwd=root,check=True,stdout=subprocess.DEVNULL)
        subprocess.run(['git','-c','user.name=Snapshot','-c','user.email=snapshot@example.invalid',
                        'commit','-qm','synthetic test snapshot; not a publication revision'],cwd=root,check=True)
        result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests',
                               '-p','test_external_json_boundaries.py','-v'],cwd=root)
        raise SystemExit(result.returncode)
else:
    names=subprocess.check_output(['git','ls-files','-z','agent_runtime','scripts','knowledge',
                                   'tests','config','templates','prompts','workflows'],cwd=ROOT).decode().split('\0')
    names=[name for name in names if name]
    names+=['tests/test_memory_tables.py']
    hashes={name:sha((ROOT/name).read_bytes()) for name in sorted(names)}
    snapshot=(json.dumps(hashes,sort_keys=True,indent=2)+'\n').encode()
    (RUN/'strict-source-snapshot.json').write_bytes(snapshot)
    target=ROOT/'.agent-runs/memory-pack-20261021/deployment-v2/strict-source.zip'
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(names):archive.writestr(name,(ROOT/name).read_bytes())
        archive.writestr('snapshot.json',snapshot)
    linux='/mnt/c/Users/WI/Desktop/home_work/AI_LLM/agent/'
    command=['wsl','python3',linux+RUN.relative_to(ROOT).as_posix()+'/run_strict_ext4.py',
             '--worker',linux+target.relative_to(ROOT).as_posix()]
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
    (RUN/'strict-boundaries-ext4.txt').write_bytes(result.stdout)
    print('strict-boundaries-ext4 exit',result.returncode)
    raise SystemExit(result.returncode)
