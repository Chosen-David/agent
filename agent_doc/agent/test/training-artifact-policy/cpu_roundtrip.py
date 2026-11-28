"""Run with torchrun --nproc-per-node=2 and a disposable shared directory."""
import sys
from pathlib import Path

import torch
import torch.distributed as dist

from agent_runtime.dcp_generation import DCPGeneration


dist.init_process_group('gloo')
rank = dist.get_rank()
writer = DCPGeneration(sys.argv[1])
model = {'weight': torch.tensor([1., 2.])}
optimizer = {'momentum': torch.tensor([3., 4.])}
local = dict(data=20 + rank, rng=torch.get_rng_state(), scheduler={'last_epoch': 20})
options = dict(trajectory='cpu-roundtrip', family='schedule100', model=model)
path = writer.save(**options, step=20, optimizer=optimizer, local_state=local, asynchronous=True)
assert not path.exists()
writer.wait()
model['weight'].zero_()
optimizer['momentum'].zero_()
restored, progress = writer.load(path, **options, optimizer=optimizer)
assert model['weight'].tolist() == [1., 2.]
assert optimizer['momentum'].tolist() == [3., 4.]
assert progress['data'] == 20 + rank and torch.equal(progress['rng'], local['rng'])
assert progress['scheduler'] == local['scheduler']
weights = writer.save(**options, step=21)
try:
    writer.load(weights, **options, optimizer=optimizer)
except RuntimeError as exc:
    assert 'incompatible' in str(exc)
else:
    raise AssertionError('L2 accepted as L3')
if rank == 0:
    (path/'local-0.pt').write_bytes(b'injected-corruption')
dist.barrier()
try:
    writer.load(path, **options, optimizer=optimizer)
except RuntimeError as exc:
    assert 'integrity mismatch' in str(exc)
else:
    raise AssertionError('corruption accepted')
writer.load(weights, **options)
print(f'rank={rank} full recovery, per-rank state, L2 restriction and corruption isolation passed', flush=True)
dist.destroy_process_group(writer.io_group)
dist.destroy_process_group()
