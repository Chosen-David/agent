#!/usr/bin/env python3
"""Restore exact evidence and replay the frozen recorder; never reruns model workers."""
import argparse,hashlib,importlib.util,json,pathlib,shutil,tarfile
p=argparse.ArgumentParser();p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();src=pathlib.Path(__file__).resolve().parent;info=json.loads((src/'archive.json').read_text());archive=src/info['archive'];assert hashlib.sha256(archive.read_bytes()).hexdigest()==info['sha256'];a.out.mkdir(parents=True,exist_ok=False)
with tarfile.open(archive,'r:gz') as t:
 for member in t.getmembers():
  path=pathlib.PurePosixPath(member.name)
  if not member.isfile() or path.is_absolute() or '..' in path.parts:raise ValueError('Unsafe archive member')
  target=a.out/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(t.extractfile(member).read())
index=json.loads((a.out/'archive-files.json').read_text())
for name,expected in index.items():assert hashlib.sha256((a.out/name).read_bytes()).hexdigest()==expected,name
for run in ['run','writer-run']:shutil.copytree(a.out/'snapshot',a.out/run/'snapshot')
spec=importlib.util.spec_from_file_location('frozen_pipeline',a.out/'controller/pipeline.py');pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)
results={run:pipeline.report(a.out/run) for run in ['run','writer-run']}
for run,report in results.items():
 print(json.dumps({'run':run,**{k:v for k,v in report.items() if k!='cases'}},ensure_ascii=False,indent=2))
 if not report['complete']:raise SystemExit(1)
print('Exact files restored, hashes checked, both final reports complete. Historical failures remain in attempt records.')
