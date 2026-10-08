from pathlib import Path
import subprocess,json,hashlib,tempfile,sys
R=Path.cwd();D=R/'doc/results/final-delta-v6-20261007';base='21cb9876084108cb8cb6a92c50279acbcb62648e';new='a52e95eb916ecf04f18f6f5716fa290dc1da6a9a';tree='ca6ad9049b362c124062ca47c6d039ab9e834d79'
def g(*a):return subprocess.check_output(['git',*a],stderr=subprocess.DEVNULL)
def obj(ref,p):
 v=subprocess.run(['git','show',ref+':'+p],capture_output=True);return v.stdout if v.returncode==0 else None
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
assert g('rev-parse','HEAD').decode().strip()==base
plans={p.relative_to(R).as_posix():sha(p.read_bytes().split(b'## Progress')[0]) for p in (R/'doc/task/task_details').glob('*.md')};assert len(plans)==127
paths=g('diff','--name-only',base,new).decode().splitlines();over=['CODEMAP.md','TASK.md'];safe=[p for p in paths if p not in over]
assert len(paths)==28 and all((R/p).read_bytes()==obj(new,p) for p in safe)
raw=obj(new,'TASK.md');digest=sha(raw);archive=R/f'doc/task/legacy/TASK.{digest}.md';assert archive.read_bytes()==raw
write(D/'bounded-migration-stop.json',{'reason':'Initial migration explicitly stopped when an additional upstream INDEX-04 task appeared; no task detail or index was written by that failed step.','resolution':'Preserve all three actual new upstream IDs: INDEX-04, MATH-23, MATH-24. INDEX-04 records already completed upstream design delivery; no new design or SEM work is executed.','scope':'Task-record preservation only, not scope expansion.'})
with tempfile.TemporaryDirectory(prefix='migration-v6-',dir='/tmp') as td:
 t=Path(td);(t/'TASK.md').write_bytes(raw);v=subprocess.run([sys.executable,str(R/'scripts/project_docs.py'),'--root',str(t),'migrate','--date','2026-10-07'],capture_output=True,text=True);assert v.returncode==0,v.stderr
 added=[]
 for f in sorted((t/'doc/task/task_details').glob('*.md')):
  dst=R/'doc/task/task_details'/f.name
  if not dst.exists():assert f.stem in ['INDEX-04','MATH-23','MATH-24'];dst.write_bytes(f.read_bytes());added.append(f.stem)
 assert len(added)==3
 lines=[l for l in (t/'doc/task/TASK.md').read_text().splitlines() if any(f'[{i}]' in l for i in added)]
 p=R/'doc/task/TASK.md';p.write_text(p.read_text().replace('## 2026-10-07\n','## 2026-10-07\n\n'+'\n'.join(lines)+'\n',1))
assert all(sha((R/p).read_bytes().split(b'## Progress')[0])==h for p,h in plans.items())
subprocess.run([sys.executable,'scripts/sync_plugin_references.py'],check=True)
corpus=g('ls-tree','-r','--name-only',new,'knowledge').decode().splitlines();assert len(corpus)==176;assert all((R/p).read_bytes()==obj(new,p) for p in corpus)
impl=g('ls-tree','-r','--name-only',tree,'agent_runtime','scripts','tests','apps/paper-reader','prompts','workflows').decode().splitlines();assert all((R/p).read_bytes()==obj(tree,p) for p in impl)
tracked=g('ls-files').decode().splitlines();pre={p:sha((R/p).read_bytes()) for p in tracked if (R/p).is_file()};idx=g('write-tree');subprocess.run(['git','reset','--soft',new],check=True);assert g('write-tree')==idx and all(sha((R/p).read_bytes())==h for p,h in pre.items())
write(D/'delta.json',{'base':base,'upstream':new,'prior_tested_tree':tree,'prior_acceptance':{'path':'docs/document_architecture_validation/independent/upstream-v5-review.json','sha256':sha((R/'docs/document_architecture_validation/independent/upstream-v5-review.json').read_bytes())},'upstream_paths':[{ 'path':p,'blob':g('rev-parse',new+':'+p).decode().strip(),'sha256':sha(obj(new,p)),'mode':'merged-navigation' if p in over else 'exact-upstream'} for p in paths],'task_archive':archive.relative_to(R).as_posix(),'task_archive_sha256':digest,'new_task_ids':added,'canonical_tasks':130,'prior_plan_count':127,'prior_plan_map_sha256':sha(json.dumps(plans,sort_keys=True).encode()),'all_prior_plans_unchanged':True,'implementation_files_unchanged':len(impl),'corpus_exact_remote_files':176,'guide_files':0,'base_adoption':'soft reset only; tracked bytes and index unchanged','scope':'Only actual upstream28path delta; prior accepted Git tree and report referenced, no copied whole inventory. SEM excluded.'})
print('Integrated28paths;130tasks; all127Plans and142implementation files preserved')
