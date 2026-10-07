from pathlib import Path
import subprocess,json,hashlib,tempfile,sys
R=Path.cwd();O=R/'doc/results/combined-integration-v2-20261007';base='e7a908aaa2198d740dd4fcfc835b8e2931db16e5';new='907890831929a5d200d3fb64c6299449391a1ee8'
def g(*a):return subprocess.check_output(['git',*a],stderr=subprocess.DEVNULL)
def sha(b):return hashlib.sha256(b).hexdigest()
def obj(ref,p):
 r=subprocess.run(['git','show',ref+':'+p],capture_output=True);return r.stdout if r.returncode==0 else None
assert g('rev-parse','HEAD').decode().strip()==base
assert g('write-tree').decode().strip()=='2ac949bab2c25d7bb51b3cd9f5dc5b0509d377e9'
assert not list((R/'doc/guide').rglob('*'))
existing={p.relative_to(R).as_posix():sha(p.read_bytes()) for p in (R/'doc/task/task_details').glob('*.md')};assert len(existing)==109
plans={p.relative_to(R).as_posix():sha(p.read_bytes().split(b'## Progress')[0]) for p in (R/'doc/task/task_details').glob('*.md')}
files=g('ls-files').decode().splitlines(); hashes={p:sha((R/p).read_bytes()) for p in files if (R/p).is_file()}
(O/'pre-integration-identities.json').write_text(json.dumps({'accepted_tree':'2ac949bab2c25d7bb51b3cd9f5dc5b0509d377e9','base':base,'file_sha256':hashes,'detail_sha256':existing,'plan_sha256':plans},indent=2)+'\n')
paths=g('diff','--name-only',base,new).decode().splitlines();assert len(paths)==124
safe=[];overlap=[]
for p in paths:
 assert not p.startswith('doc/guide/')
 before=obj(base,p);w=(R/p).read_bytes() if (R/p).exists() else None
 (safe if before==w else overlap).append(p)
assert overlap==['CODEMAP.md','TASK.md'],overlap
for p in safe:
 data=obj(new,p);assert data is not None
 (R/p).parent.mkdir(parents=True,exist_ok=True);(R/p).write_bytes(data)
# Both versions add to CODEMAP; append upstream's exact added suffix.
b=obj(base,'CODEMAP.md');n=obj(new,'CODEMAP.md');assert n.startswith(b)
c=R/'CODEMAP.md';c.write_bytes(c.read_bytes()+n[len(b):])
# Generate migration only in isolated root, then preserve all existing detail bytes.
raw=obj(new,'TASK.md');digest=sha(raw);assert digest=='e3467798564183944d564b0fff2648977abd8a8550b87690e0ace82fdcdc24fa'
archive=R/f'doc/task/legacy/TASK.{digest}.md';assert not archive.exists();archive.write_bytes(raw)
with tempfile.TemporaryDirectory(prefix='combined-task-migration-',dir='/tmp') as td:
 t=Path(td);(t/'TASK.md').write_bytes(raw)
 p=subprocess.run([sys.executable,str(R/'scripts/project_docs.py'),'--root',str(t),'migrate','--date','2026-10-07'],capture_output=True,text=True);assert p.returncode==0,p.stderr
 (O/'task-migration-generated.json').write_text(p.stdout)
 additions=[]
 for f in sorted((t/'doc/task/task_details').glob('*.md')):
  dst=R/'doc/task/task_details'/f.name
  if not dst.exists():
   assert f.stem.startswith(('EK-112454-','EK-115246-')),f
   dst.write_bytes(f.read_bytes());additions.append(f.stem)
 assert len(additions)==6,additions
 lines=[s for s in (t/'doc/task/TASK.md').read_text().splitlines() if any(f'[{id}]' in s for id in additions)]
 idx=R/'doc/task/TASK.md';txt=idx.read_text();anchor='## 2026-10-07\n';assert txt.count(anchor)==1
 idx.write_text(txt.replace(anchor,anchor+'\n'+'\n'.join(lines)+'\n',1))
assert all(sha((R/p).read_bytes())==h for p,h in existing.items())
assert len(list((R/'doc/task/task_details').glob('*.md')))==115
assert all((R/p).read_bytes()==obj(new,p) for p in safe)
record={'base':base,'upstream':new,'delta_paths':len(paths),'restored_exactly':safe,'merged_overlaps':overlap,'task_added_ids':additions,'task_archive':archive.relative_to(R).as_posix(),'task_archive_sha256':digest,'existing109_details_byte_identical':True,'existing109_plans_byte_identical':True,'guide_files':0,'scope':'Merge current upstream without changing accepted feature code. Source hashes retain evidence for independent targeted reuse review.'}
(O/'integration.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k!='restored_exactly'},indent=2))
