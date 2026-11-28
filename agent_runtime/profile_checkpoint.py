"""Run a synchronous Forge profile with job-owned checkpoint output and a registered input."""
import argparse
from contextlib import ExitStack
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid

from .checkpoint_retention import CheckpointRetention


def run(database, directory, argv, *, artifact=None, io=False):
    directory=Path(directory).absolute()
    directory.mkdir(parents=True,exist_ok=True)
    if directory.resolve()!=directory:
        raise ValueError('physical profile directory required')
    store=CheckpointRetention(database)
    with ExitStack() as stack:
        stack.callback(store.db.close)
        lock=stack.enter_context((directory/'profile.lock').open('a+b'))
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state=directory/'profile-owner.json'
        receipt=directory/'profile-result.json'
        def cleanup(record):
            scratch=Path(record['scratch'])
            if scratch.parent!=directory or scratch.resolve()!=scratch or not scratch.name.startswith('io-'):
                raise ValueError('foreign temporary output')
            if scratch.exists():
                s=scratch.stat()
                if [s.st_dev,s.st_ino]!=record['identity']:
                    raise ValueError('temporary output replaced')
                shutil.rmtree(scratch)
            if record['artifact']:
                store.reference(record['artifact'],str(directory),'profile-input',release=True)
            state.unlink()
        if state.exists():
            # The subprocess inherits the flock, including across loss of its parent.
            cleanup(json.loads(state.read_bytes()))
        if receipt.exists():
            if json.loads(receipt.read_bytes())['rc']==0:
                raise FileExistsError('completed profile; use its results')
            receipt.rename(directory/('failed-'+uuid.uuid4().hex+'.json'))
        env=os.environ.copy()
        env.update(FSDP2_SAVE_EVERY_N_STEPS='1' if io else '0',FSDP2_SAVE_ON_END='true' if io else 'false')
        inp=None
        if artifact:
            row=store.db.execute('SELECT physical,dev,ino FROM checkpoint_assets WHERE artifact=?',(artifact,)).fetchone()
            if not row:
                raise ValueError('unknown input checkpoint')
            inp=Path(row[0])
            s=inp.stat()
            if (s.st_dev,s.st_ino)!=row[1:] or directory.is_relative_to(inp):
                raise ValueError('invalid profile/input binding')
            env.update(FSDP2_RESUME_FROM=str(inp),FSDP2_RESUME_STRICT='true',RESUME_MODE='strict')
        scratch=Path(tempfile.mkdtemp(prefix='io-',dir=directory))
        s=scratch.stat()
        record=dict(scratch=str(scratch),identity=[s.st_dev,s.st_ino],artifact=artifact)
        state.write_text(json.dumps(record))
        if artifact:
            store.reference(artifact,str(directory),'profile-input')
        env.update(FSDP2_SAVE_DIR=str(scratch),GENIE_ML_CKPT_OUTPUT_DIR=str(scratch))
        if not io:
            # A timing-only run cannot commit even its first shard.
            scratch.chmod(0o500)
        start=time.time()
        child=subprocess.run(argv,env=env,pass_fds=(lock.fileno(),))
        files=[str(p.relative_to(scratch)) for p in scratch.rglob('*') if p.is_file()]
        result=dict(argv=argv,started=start,ended=time.time(),rc=child.returncode,input_artifact=artifact,
                    input_path=str(inp) if inp else None,io=io,output_files=files,
                    input_manifest_sha256=hashlib.sha256((inp/'manifest.json').read_bytes()).hexdigest() if inp else None,
                    effective_settings={k:env[k] for k in ('FSDP2_SAVE_DIR','FSDP2_SAVE_EVERY_N_STEPS','FSDP2_SAVE_ON_END')})
        receipt.write_text(json.dumps(result,indent=2))
        cleanup(record)
        if files and not io:
            raise RuntimeError('unexpected checkpoint files during timing')
        return child.returncode


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input');p.add_argument('--io',action='store_true')
    p.add_argument('database');p.add_argument('directory');p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args()
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    raise SystemExit(run(a.database,a.directory,command,artifact=a.input,io=a.io))
