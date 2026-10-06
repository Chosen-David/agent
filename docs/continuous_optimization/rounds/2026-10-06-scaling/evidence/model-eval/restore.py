#!/usr/bin/env python3
"""Restore hash-bound role records; replay records, never models. Standard library only."""
import argparse,pathlib,json,hashlib,tarfile,shutil,importlib.util,sys

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',type=pathlib.Path,required=True);args=ap.parse_args();src=pathlib.Path(__file__).resolve().parent;out=args.out
 if out.exists() or out.is_symlink():raise SystemExit('Refusing existing output destination')
 info=json.loads((src/'archive.json').read_text());archive=src/info['archive']
 if digest(archive)!=info['sha256']:raise SystemExit('Archive hash mismatch')
 with tarfile.open(archive,'r:gz') as tar:
  members=tar.getmembers();names=set()
  for m in members:
   p=pathlib.PurePosixPath(m.name)
   if not m.isfile() or p.is_absolute() or '..' in p.parts or m.name in names:raise SystemExit('Unsafe archive member')
   names.add(m.name)
  out.mkdir(parents=True)
  for m in members:
   dst=out/m.name;dst.parent.mkdir(parents=True,exist_ok=True)
   with tar.extractfile(m) as inp,dst.open('xb') as f:shutil.copyfileobj(inp,f)
 index=json.loads((out/'archive-files.json').read_text())
 for name,sha in index.items():
  if digest(out/name)!=sha:raise SystemExit('Payload hash mismatch: '+name)
 for recipe in json.loads((out/'large-fixture-recipes.json').read_text()):
  path=pathlib.PurePosixPath(recipe['path'])
  if path.is_absolute() or '..' in path.parts or not recipe['path'].endswith('/inputs/large-evidence.bin'):raise SystemExit('Unsafe generated-fixture path')
  if recipe['bytes']!=12582912 or recipe['fill_byte']!=120:raise SystemExit('Unsupported fixture recipe')
  target=out/recipe['path'];target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f:
   for _ in range(12):f.write(b'x'*1048576)
  if digest(target)!=recipe['sha256']:raise SystemExit('Generated fixture hash mismatch')
 labels=['run','writer-run','writer-corrected-run','baseline-run']
 for label in labels:shutil.copytree(out/'snapshot',out/label/'snapshot')
 for f in (out/'baseline-overlay').rglob('*'):
  if f.is_file():shutil.copyfile(f,out/'baseline-run/snapshot'/f.relative_to(out/'baseline-overlay'))
 sys.dont_write_bytecode=True
 spec=importlib.util.spec_from_file_location('frozen_pipeline',out/'controller/pipeline.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
 reports={label:p.report(out/label) for label in labels}
 for label,r in reports.items():
  if r['integrity_errors']:raise SystemExit('Replay integrity failed: '+label)
  if label!='writer-run' and not r['complete']:raise SystemExit('Expected complete run failed: '+label)
 if reports['writer-run']['complete'] or reports['writer-run']['cases'][0]['attempts'][0]['semantic_verdict'] is not None:raise SystemExit('Historical ungradable case lost')
 result={label:{k:r[k] for k in ['expected','passed','first_pass','complete','integrity_errors','correct_to_wrong','wrong_to_correct']} for label,r in reports.items()}
 (out/'replay-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));print('Records restored and replayed; no models rerun, no semantic reviews recreated.')
if __name__=='__main__':main()
