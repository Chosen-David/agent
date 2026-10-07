"""Import a local, attributed draft as a candidate, never silently publish it."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

if __package__:
    from .knowledge import KnowledgeStore, _json, _require, MAX_BYTES
    from .project_docs import guard_write_path
else:
    from knowledge import KnowledgeStore, _json, _require, MAX_BYTES
    from project_docs import guard_write_path


def ingest(root, metadata_path, body_path):
    guard_write_path(Path(root) / 'entries')
    store=KnowledgeStore(root)
    def read(path):
        path=Path(path)
        _require(path.is_file() and not path.is_symlink(), 'import requires regular local files')
        _require(path.stat().st_size<=MAX_BYTES, 'import exceeds byte budget')
        return path.read_text(encoding='utf-8')
    raw=read(metadata_path);body=read(body_path)
    d=_json(raw)
    KnowledgeStore._validate(d)
    _require(d['status']=='candidate', 'import drafts as candidate; publication requires review')
    _require(d['id'] not in store.records, 'ID already exists; review and revise its current file')
    _require(bool(body.strip()), 'empty imported body')
    # Validate the combined corpus in isolation before touching canonical entries.
    with tempfile.TemporaryDirectory(prefix='knowledge-ingest-') as tmp:
        stage=Path(tmp)/'knowledge'
        shutil.copytree(store.root,stage)
        folder=stage/'entries'/d['id']
        _require(not folder.exists(), 'import path collision')
        folder.mkdir()
        (folder/'entry.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
        (folder/'entry.md').write_text(body)
        receipt={'schema_version':1,'id':d['id'],'status':'candidate',
                 'imported_at':datetime.now(timezone.utc).isoformat(),
                 'metadata_sha256':hashlib.sha256(raw.encode()).hexdigest(),
                 'body_sha256':hashlib.sha256(body.encode()).hexdigest(),
                 'sources':d['sources'],
                 'scope':'Local attributed draft only; no claim of source verification or correctness.'}
        (folder/'provenance.txt').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        candidate=KnowledgeStore(stage)
        destination=guard_write_path(store.root/'entries'/d['id'])
        _require(not destination.exists(), 'import target exists')
        _require(KnowledgeStore(store.root).snapshot==store.snapshot, 'corpus changed during import; retry')
        # Staging on destination filesystem makes the directory rename atomic;
        # use an external sibling so readers never see a partial entry pair.
        staging=Path(tempfile.mkdtemp(prefix='.knowledge-import-',dir=store.root.parent))
        try:
            ready=staging/'entry'
            shutil.copytree(folder,ready)
            guard_write_path(destination)
            os.rename(ready,destination)
        finally:
            shutil.rmtree(staging)
    return {**receipt,'knowledge_ref':candidate.ref(d['id']),
            'path':destination.relative_to(store.root).as_posix()}
