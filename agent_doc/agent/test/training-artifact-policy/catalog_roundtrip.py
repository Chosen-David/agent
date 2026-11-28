"""Actual two-rank DCP producer and restore adapter for ResultStore integration."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from agent_runtime.dcp_generation import DCPGeneration, recovery_record
from agent_runtime.result_store import ResultStore

root=Path(sys.argv[1]).resolve()
family=hashlib.sha256(b'fixed schedule horizon=100').hexdigest()


def worker(mode, generation=None):
    import torch
    import torch.distributed as dist
    dist.init_process_group('gloo')
    rank=dist.get_rank()
    manager=DCPGeneration(root/'checkpoints')
    for step in ([10,20] if mode=='produce' else [json.loads((generation/'generation.json').read_text())['completed_step']]):
        model={'weights':torch.tensor([step],dtype=torch.float32)}
        optimizer={'momentum':torch.tensor([step/2])}
        spec=dict(trajectory='exact',family=family,model=model,optimizer=optimizer)
        if mode=='produce':
            p=manager.save(**spec,step=step,local_state=dict(scheduler=step,rng=torch.get_rng_state(),data=rank+step))
            if not rank:
                (root/f'g{step}.json').write_text(json.dumps(str(p)))
        else:
            model['weights'].zero_()
            optimizer['momentum'].zero_()
            _,local=manager.load(generation,**spec)
            assert model['weights'].item()==step and optimizer['momentum'].item()==step/2
            assert local['scheduler']==step and local['data']==rank+step
            torch.set_rng_state(local['rng'])
    dist.destroy_process_group(manager.io_group)
    dist.destroy_process_group()


def run_workers(mode,*paths):
    subprocess.run([sys.executable,'-m','torch.distributed.run','--standalone','--nproc-per-node=2',
                    __file__,str(root),mode,*map(str,paths)],check=True)


class Adapter:
    def save_completed(self,project,manifest):
        return all((project/r['path']).is_file() for r in manifest['files'])

    def restore(self,project,manifest):
        header=next(x['path'] for x in manifest['files'] if x['path'].endswith('/generation.json'))
        run_workers('restore',(project/header).parent)
        self.restored=manifest['run_id']
        return True

    def verify_training_state(self,project,manifest):
        return self.restored==manifest['run_id']


if len(sys.argv)>2:
    worker(sys.argv[2],Path(sys.argv[3]) if len(sys.argv)>3 else None)
else:
    root.mkdir(parents=True,exist_ok=True)
    run_workers('produce')
    adapter=Adapter()
    store=ResultStore(root)
    for step in (10,20):
        p=Path(json.loads((root/f'g{step}.json').read_text()))
        record=recovery_record(root,p,artifact_id=f's{step}',source_run='cpu-science',producer='two-rank-cpu',
            code_revision='fixture-v1',input_revision='scalar-v1',retention_reason='acceptance')
        m=root/f's{step}.json'
        m.write_text(json.dumps(record))
        store.register_recovery(m.name,byte_limit=1<<22,provider=adapter)
    opts=dict(trajectory_id='exact',family_sha256=family,target_step=30,byte_limit=1<<22,provider=adapter)
    result=store.longest_recovery(['s10','s20'],**opts)
    assert result['step']==20
    (p/'local-0.pt').write_bytes(b'failure injection in disposable fixture')
    fallback=store.longest_recovery(['s10','s20'],**opts)
    assert fallback['step']==10
    print(json.dumps(dict(first=result['step'],after_corruption=fallback['step'],failures=fallback['failed'])))
