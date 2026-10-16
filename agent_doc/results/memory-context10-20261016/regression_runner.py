import sys,io,json,hashlib,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))

def main():
    source=ROOT/'agent_runtime/project_memory.py'
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    records=[]
    for directory in ('tests','apps/paper-reader/tests'):
        t=time.monotonic()
        suite=unittest.defaultTestLoader.discover(str(ROOT/directory),pattern='test*.py',top_level_dir=str(ROOT/directory))
        result=unittest.TextTestRunner(stream=io.StringIO(),verbosity=1).run(suite)
        records.append({'directory':directory,'run':result.testsRun,'skipped':len(result.skipped),'errors':[(str(test),err) for test,err in result.errors],'failures':[(str(test),err) for test,err in result.failures],'successful':result.wasSuccessful(),'wall_seconds':time.monotonic()-t})
    after=hashlib.sha256(source.read_bytes()).hexdigest()
    Path(__file__).with_name('final-regression.json').write_text(json.dumps({'source_sha256_before':before,'source_sha256_after':after,'results':records},indent=2))
    return 0 if before==after and all(r['successful'] for r in records) else 1

if __name__=='__main__':
    raise SystemExit(main())
