"""Import a local, attributed draft as a candidate, never silently publish it."""
from __future__ import annotations

from datetime import datetime, timezone
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

if __package__:
    from .knowledge import KnowledgeStore, KnowledgeError, _json, _require, MAX_BYTES, _read_utf8_bounded
    from .project_docs import guard_write_path
else:
    from knowledge import KnowledgeStore, KnowledgeError, _json, _require, MAX_BYTES, _read_utf8_bounded
    from project_docs import guard_write_path


def _publish_entry(source, target):
    """Publish the complete pair without replacing any existing target."""
    if sys.platform == 'win32':
        os.rename(source, target)
        return
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        if sys.platform == 'linux':
            rename = libc.renameat2
            rename.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                               ctypes.c_char_p, ctypes.c_uint)
            args = (-100, os.fsencode(source), -100, os.fsencode(target), 1)
        elif sys.platform == 'darwin':
            rename = libc.renamex_np
            rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
            args = (os.fsencode(source), os.fsencode(target), 4)
        else:
            raise AttributeError('unsupported platform')
    except (AttributeError, OSError) as exc:
        raise KnowledgeError('atomic no-replace import publication unavailable') from exc
    rename.restype = ctypes.c_int
    if rename(*args) != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(target))


def ingest(root, metadata_path, body_path):
    guard_write_path(Path(root) / 'entries')
    store=KnowledgeStore(root)
    def read(path):
        path=Path(path)
        _require(path.is_file() and not path.is_symlink(), 'import requires regular local files')
        _require(path.stat().st_size<=MAX_BYTES, 'import exceeds byte budget')
        return _read_utf8_bounded(path, MAX_BYTES, 'import exceeds byte budget')
    raw=read(metadata_path);body=read(body_path)
    d=_json(raw)
    KnowledgeStore._validate(d)
    _require(d['status']=='candidate', 'import drafts as candidate; publication requires review')
    _require(d['id'] not in store.records, 'ID already exists; review and revise its current file')
    _require(bool(body.strip()), 'empty imported body')
    # Validate the combined corpus in isolation before touching canonical entries.
    with tempfile.TemporaryDirectory(prefix='knowledge-ingest-') as tmp:
        stage=Path(tmp)/'knowledge'
        # Only entries participates in KnowledgeStore validation. Root-local
        # indexes, caches and other artifacts are not part of this snapshot.
        shutil.copytree(store.root/'entries',stage/'entries')
        folder=stage/'entries'/d['id']
        _require(not folder.exists(), 'import path collision')
        folder.mkdir()
        # Path.write_text gained newline in 3.10; Path.open also supports 3.9.
        with (folder/'entry.json').open('w', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
        with (folder/'entry.md').open('w', encoding='utf-8', newline='\n') as stream:
            stream.write(body)
        receipt={'schema_version':1,'id':d['id'],'status':'candidate',
                 'imported_at':datetime.now(timezone.utc).isoformat(),
                 'metadata_sha256':hashlib.sha256(raw.encode()).hexdigest(),
                 'body_sha256':hashlib.sha256(body.encode()).hexdigest(),
                 'sources':d['sources'],
                 'scope':'Local attributed draft only; no claim of source verification or correctness.'}
        with (folder/'provenance.txt').open('w', encoding='utf-8', newline='\n') as stream:
            stream.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        candidate=KnowledgeStore(stage)
        destination=guard_write_path(store.root/'entries'/d['id'])
        _require(not destination.exists(), 'import target exists')
        # Staging on destination filesystem makes the directory rename atomic;
        # use an external sibling so readers never see a partial entry pair.
        staging=Path(tempfile.mkdtemp(prefix='.knowledge-import-',dir=store.root.parent))
        try:
            ready=staging/'entry'
            shutil.copytree(folder,ready)
            guard_write_path(destination)
            # No copying remains after this best-effort live corpus check.
            _require(KnowledgeStore(store.root).snapshot==store.snapshot, 'corpus changed during import; retry')
            _publish_entry(ready,destination)
        finally:
            shutil.rmtree(staging)
    return {**receipt,'knowledge_ref':candidate.ref(d['id']),
            'path':destination.relative_to(store.root).as_posix()}
