import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

repo = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo))
from agent_runtime.knowledge import KnowledgeStore, KnowledgeError
from agent_runtime.knowledge_ingest import ingest

outcomes = []
with tempfile.TemporaryDirectory(prefix='independent-ingest-') as temporary:
    base = Path(temporary)
    isolated = base / 'isolated-skill'
    shutil.copytree(repo / 'plugins/research-assistant/skills/model-with-knowledge', isolated)
    for mode in ('module', 'isolated'):
        corpus = base / ('corpus-' + mode)
        shutil.copytree(repo / 'knowledge', corpus)
        before = KnowledgeStore(corpus)
        baseline_files = {p.relative_to(corpus).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in corpus.rglob('*') if p.is_file()}
        metadata = json.loads((corpus/'entries/math.cauchy-schwarz.json').read_text(encoding='utf-8'))
        identity = 'math.independent-compat-' + mode
        metadata.update(id=identity, status='candidate', requires=[], relations=[])
        meta, body = base / (mode + '.json'), base / (mode + '.md')
        raw_meta = json.dumps(metadata, ensure_ascii=False, indent=2).replace('\n', '\r\n')
        raw_body = '# Unicode draft 中文\r\nCR\rLF\nLS:\u2028No final newline'
        meta.write_bytes(raw_meta.encode('utf-8'))
        body.write_bytes(raw_body.encode('utf-8'))
        expected_meta = raw_meta.replace('\r\n','\n').replace('\r','\n')
        expected_body = raw_body.replace('\r\n','\n').replace('\r','\n')
        if mode == 'module':
            receipt = ingest(corpus, meta, body)
        else:
            command = [sys.executable, '-I', str(isolated/'scripts/knowledge.py'), '--root', str(corpus), 'ingest', str(meta), str(body)]
            completed = subprocess.run(command, cwd=base, capture_output=True, text=True)
            assert completed.returncode == 0, completed.stderr
            receipt = json.loads(completed.stdout)
        assert receipt['status'] == 'candidate'
        assert receipt['metadata_sha256'] == hashlib.sha256(expected_meta.encode()).hexdigest()
        assert receipt['body_sha256'] == hashlib.sha256(expected_body.encode()).hexdigest()
        folder = corpus / receipt['path']
        assert (folder/'entry.md').read_bytes() == expected_body.encode('utf-8')
        assert (folder/'entry.json').read_bytes() == (json.dumps(metadata, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
        assert (folder/'provenance.txt').read_bytes().endswith(b'\n')
        assert b'\r' not in (folder/'provenance.txt').read_bytes()
        after = KnowledgeStore(corpus)
        assert after.records.keys() == before.records.keys() | {identity}
        assert all(after.records[k] == v for k, v in before.records.items())
        for relative, digest in baseline_files.items():
            assert hashlib.sha256((corpus/relative).read_bytes()).hexdigest() == digest
        assert after.ref(identity) == receipt['knowledge_ref']
        saved = {p.name:p.read_bytes() for p in folder.iterdir()}
        try:
            ingest(corpus, meta, body)
        except KnowledgeError:
            pass
        else:
            raise AssertionError('duplicate import accepted')
        assert saved == {p.name:p.read_bytes() for p in folder.iterdir()}
        outcomes.append({'mode': mode, 'candidate': identity, 'checks': 'exact UTF8/LF bytes, normalized-source receipt hashes, candidate refs, baseline bytes/records unchanged, duplicate rejected'})
print(json.dumps({'python':sys.version.split()[0], 'outcomes':outcomes}, ensure_ascii=False))
