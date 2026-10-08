from pathlib import Path
import subprocess,json,hashlib,tempfile,sys
R=Path.cwd();D=R/'doc/results/combined-integration-v5-20261007';base='013cfa15b72d354ef87ec18eb9698b58f75e3b6d';new='21cb9876084108cb8cb6a92c50279acbcb62648e';tree='5172ad32bf2957e89a9308989a44c326729c2370'
def g(*a):return subprocess.check_output(['git',*a],stderr=subprocess.DEVNULL)
def obj(ref,p):
 v=subprocess.run(['git','show',ref+':'+p],capture_output=True);return v.stdout if v.returncode==0 else None
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
assert g('rev-parse','HEAD').decode().strip()==base;assert g('write-tree').decode().strip()==tree
files=g('ls-files').decode().splitlines();pre={p:sha((R/p).read_bytes()) for p in files if (R/p).is_file()}
details={p.relative_to(R).as_posix():sha(p.read_bytes()) for p in (R/'doc/task/task_details').glob('*.md')};assert len(details)==124
plans={p.relative_to(R).as_posix():sha(p.read_bytes().split(b'## Progress')[0]) for p in (R/'doc/task/task_details').glob('*.md')}
write(D/'pre-integration-identities.json',{'base':base,'accepted_tree':tree,'file_sha256':pre,'detail_sha256':details,'plan_sha256':plans})
paths=g('diff','--name-only',base,new).decode().splitlines();assert len(paths)==68
safe=[];over=[]
for p in paths:
 assert not p.startswith('doc/guide/');w=(R/p).read_bytes() if (R/p).is_file() else None
 (safe if w==obj(base,p) else over).append(p)
assert over==['CODEMAP.md','TASK.md'];assert len(safe)==66
for p in safe:
 b=obj(new,p);assert b is not None;(R/p).parent.mkdir(parents=True,exist_ok=True);(R/p).write_bytes(b)
b=obj(base,'CODEMAP.md');n=obj(new,'CODEMAP.md');assert n.startswith(b);p=R/'CODEMAP.md';p.write_bytes(p.read_bytes()+n[len(b):])
raw=obj(new,'TASK.md');digest=sha(raw);archive=R/f'doc/task/legacy/TASK.{digest}.md';assert not archive.exists();archive.write_bytes(raw)
with tempfile.TemporaryDirectory(prefix='migration-v5-',dir='/tmp') as td:
 t=Path(td);(t/'TASK.md').write_bytes(raw);v=subprocess.run([sys.executable,str(R/'scripts/project_docs.py'),'--root',str(t),'migrate','--date','2026-10-07'],capture_output=True,text=True);assert v.returncode==0,v.stderr;(D/'task-migration-generated.json').write_text(v.stdout)
 added=[]
 for f in sorted((t/'doc/task/task_details').glob('*.md')):
  dst=R/'doc/task/task_details'/f.name
  if not dst.exists():assert f.stem in ['EK-172253-01','EK-172253-02','EK-172253-03'];dst.write_bytes(f.read_bytes());added.append(f.stem)
 assert added==['EK-172253-01','EK-172253-02','EK-172253-03']
 lines=[l for l in (t/'doc/task/TASK.md').read_text().splitlines() if any(f'[{i}]' in l for i in added)]
 p=R/'doc/task/TASK.md';s=p.read_text().replace('## 2026-10-07\n','## 2026-10-07\n\n'+'\n'.join(lines)+'\n',1);p.write_text(s)
assert all(sha((R/p).read_bytes())==h for p,h in details.items())
assert all(sha((R/p).read_bytes().split(b'## Progress')[0])==h for p,h in plans.items())
subprocess.run([sys.executable,'scripts/sync_plugin_references.py'],check=True)
corpus=g('ls-tree','-r','--name-only',new,'knowledge').decode().splitlines();assert all((R/p).read_bytes()==obj(new,p) for p in corpus)
impl={p:h for p,h in pre.items() if p.startswith(('agent_runtime/','scripts/','tests/','apps/paper-reader/','prompts/','workflows/'))};assert all(sha((R/p).read_bytes())==h for p,h in impl.items())
files=g('ls-files').decode().splitlines();h={p:sha((R/p).read_bytes()) for p in files if (R/p).is_file()};idx=g('write-tree');subprocess.run(['git','reset','--soft',new],check=True);assert g('write-tree')==idx and all(sha((R/p).read_bytes())==v for p,v in h.items())
write(D/'integration.json',{'base':base,'upstream':new,'prior_tested_tree':tree,'delta_paths':68,'restored_exact_paths':safe,'merged_paths':over,'canonical_tasks':127,'new_task_ids':added,'archive_path':archive.relative_to(R).as_posix(),'archive_sha256':digest,'prior124_detail_bytes_unchanged_at_migration':True,'prior124_plan_hashes_unchanged':True,'implementation_dependencies_unchanged':impl,'corpus_exact_remote':True,'corpus_files_verified':len(corpus),'published':80,'candidates':3,'guide_files':0,'base_adoption':'Metadata-only reset --soft; index and all tracked worktree bytes unchanged.','excluded_scope':'Separate read-only candidateSEM work from another copy was not read/imported.'})
print('Integrated68paths,127tasks,80published+3candidate; unchanged implementation files:',len(impl))
