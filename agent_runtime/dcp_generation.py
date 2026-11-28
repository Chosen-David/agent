"""Optional Torch DCP writer. Call save/wait/load collectively on the same ranks."""
import hashlib
import json
import os
from pathlib import Path
import uuid


class DCPGeneration:
    """One in-flight save. Publish immutable generations on a shared POSIX filesystem."""
    def __init__(self, root):
        import torch.distributed as dist
        self.dist = dist
        self.root = Path(root).resolve()
        self.rank = dist.get_rank()
        self.world = dist.get_world_size()
        self.io_group = dist.new_group(backend="gloo")
        self.pending = None

    def _check_all(self, error):
        errors = [None] * self.world
        self.dist.all_gather_object(errors, error)
        if any(errors):
            raise RuntimeError(str(errors))

    def _file_digests(self, path):
        files = sorted(f for f in path.rglob('*') if f.is_file() and f.name != 'generation.json')
        local = {}
        error = None
        try:
            for f in files[self.rank::self.world]:
                with f.open('rb') as stream:
                    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
                local[str(f.relative_to(path))] = digest
        except OSError as exc:
            error = str(exc)
        self._check_all(error)
        parts = [None] * self.world
        self.dist.all_gather_object(parts, local)
        return {k:v for part in parts for k,v in part.items()}

    def save(self, *, trajectory, family, step, model, optimizer=None, local_state=None,
             asynchronous=False):
        import torch
        import torch.distributed.checkpoint as dcp
        self.wait()
        level = 'L2' if optimizer is None else 'L3'
        error = None
        if not trajectory or not family or type(step) is not int or step < 0:
            error = 'invalid trajectory, family or step'
        if level == 'L3' and (not isinstance(local_state, dict) or
                not {'scheduler','data','rng'} <= local_state.keys() or
                any(local_state[k] is None for k in ('scheduler','data','rng'))):
            error = 'rank-local scheduler, data and RNG state required'
        self._check_all(error)
        identity = dict(trajectory_id=trajectory, family_sha256=family, completed_step=step,
                        asset_level=level, world_size=self.world)
        identities = [None] * self.world
        self.dist.all_gather_object(identities, identity)
        if any(i != identity for i in identities):
            raise ValueError('rank checkpoint identities disagree')
        token = [uuid.uuid4().hex if self.rank == 0 else None]
        self.dist.broadcast_object_list(token)
        temp = self.root / ('.partial-' + token[0])
        final = self.root / token[0]
        error = None
        if self.rank == 0:
            try:
                temp.mkdir(parents=True, exist_ok=False)
            except OSError as exc:
                error = str(exc)
        self._check_all(error)
        state = dict(model=model)
        if level == 'L3':
            state['optimizer'] = optimizer
            error = None
            try:
                with (temp / f'local-{self.rank}.pt').open('xb') as f:
                    torch.save(local_state, f)
                    f.flush()
                    os.fsync(f.fileno())
            except Exception as exc:
                error = str(exc)
            self._check_all(error)
        future = None
        error = None
        try:
            if asynchronous:
                future = dcp.async_save(state, checkpoint_id=temp/'dcp', process_group=self.io_group)
                staged = getattr(future, 'staging_completion', None)
                if staged is not None:
                    staged.result()
            else:
                dcp.save(state, checkpoint_id=temp/'dcp', process_group=self.io_group)
        except BaseException as exc:
            error = repr(exc)
        self._check_all(error)
        self.pending = temp, final, identity, future
        if not asynchronous:
            self.wait()
        return final

    def wait(self):
        if self.pending is None:
            return
        temp, final, metadata, future = self.pending
        self.pending = None
        error = None
        try:
            if future is not None:
                getattr(future, 'upload_completion', future).result()
        except BaseException as exc:
            error = repr(exc)
        self._check_all(error)
        error = None
        metadata['files'] = self._file_digests(temp)
        if self.rank == 0:
            try:
                if not (temp/'dcp'/'.metadata').is_file():
                    raise ValueError('DCP completion metadata missing')
                with (temp/'generation.json').open('x') as f:
                    json.dump(metadata, f, sort_keys=True)
                    f.flush()
                    os.fsync(f.fileno())
                temp.rename(final)
                fd = os.open(self.root, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            except (OSError, ValueError) as exc:
                error = str(exc)
        self._check_all(error)

    def load(self, path, *, trajectory, family, model, optimizer=None):
        """Load a trusted self-produced generation; each rank gets its own local state."""
        import torch
        import torch.distributed.checkpoint as dcp
        error = None
        m = {}
        try:
            path = Path(path).resolve(strict=True)
            if path.parent != self.root or path.name.startswith('.'):
                raise ValueError('generation outside committed root')
            m = json.loads((path/'generation.json').read_text())
            level = 'L2' if optimizer is None else 'L3'
            if (trajectory, family, self.world, level) != (
                    m['trajectory_id'], m['family_sha256'], m['world_size'], m['asset_level']):
                raise ValueError('incompatible trajectory, family, topology or asset level')
        except (OSError, KeyError, ValueError) as exc:
            error = repr(exc)
        self._check_all(error)
        paths = [None] * self.world
        self.dist.all_gather_object(paths, str(path))
        if len(set(paths)) != 1:
            raise ValueError('ranks selected different checkpoint generations')
        digests = self._file_digests(path)
        self._check_all(None if digests == m.get('files') else 'checkpoint integrity mismatch')
        state = dict(model=model)
        local = None
        error = None
        if optimizer is not None:
            state['optimizer'] = optimizer
            try:
                local = torch.load(path/f'local-{self.rank}.pt', map_location='cpu', weights_only=False)
                if not {'scheduler','data','rng'} <= local.keys():
                    raise ValueError('incomplete local state')
            except Exception as exc:
                error = repr(exc)
        self._check_all(error)
        dcp.load(state, checkpoint_id=path/'dcp', process_group=self.io_group)
        return state, local


def recovery_record(project, generation, *, artifact_id, source_run, producer, code_revision,
                    input_revision, retention_reason, consumers=(), dependencies=()):
    """Translate an immutable DCP generation to the existing ResultStore contract."""
    root = Path(project).resolve(strict=True)
    path = Path(generation).resolve(strict=True)
    path.relative_to(root)
    if path.name.startswith('.'):
        raise ValueError('partial or withdrawn generation')
    header = path/'generation.json'
    raw = header.read_bytes()
    metadata = json.loads(raw)
    if metadata['asset_level'] != 'L3':
        raise ValueError('only full training state can enter the recovery store')
    files=[]
    for name,digest in {**metadata['files'],'generation.json':hashlib.sha256(raw).hexdigest()}.items():
        source = (path/name).resolve(strict=True)
        if source != path/name or not source.is_relative_to(path):
            raise ValueError('noncanonical generation member')
        item=dict(path=str(source.relative_to(root)),sha256=digest,expected_size_bytes=source.stat().st_size,
                  type='metadata')
        if name.startswith('local-') and name.endswith('.pt'):
            item.update(type='rank',rank=int(name[6:-3]))
        files.append(item)
    return dict(schema_version='recovery-manifest/v1', run_id=artifact_id, source_run=source_run,
                producer=producer,code_revision=code_revision,input_revision=input_revision,
                retention_reason=retention_reason,consumers=list(consumers),dependencies=list(dependencies),
                save_state='complete',files=files, world_size=metadata['world_size'],
                trajectory_id=metadata['trajectory_id'],family_sha256=metadata['family_sha256'],
                completed_step=metadata['completed_step'],asset_level='L3')
