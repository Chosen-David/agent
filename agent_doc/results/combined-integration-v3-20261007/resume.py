from pathlib import Path
import subprocess,json,hashlib,tempfile,sys
R=Path.cwd();D=R/'doc/results/combined-integration-v3-20261007';base='fd9012ca9f953693ad59d30e63d03ac7644c599e';new='f9898dfbd23e9bad7897643b54a419d8c88135bd';tree='a922965b886c38d95dbcb94d2e65f4aee338f6ae'
def g(*a):return subprocess.check_output(['git',*a],stderr=subprocess.DEVNULL)
def obj(ref,p):
 v=subprocess.run(['git','show',ref+':'+p],capture_output=True);return v.stdout if v.returncode==0 else None
def sha(b):return hashlib.sha256(b).hexdigest()
def write(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
prior=json.loads((D/'pre-integration-identities.json').read_text());pre=prior['file_sha256'];details=prior['detail_sha256'];plans=prior['plan_sha256']
assert g('rev-parse','HEAD').decode().strip()==base
paths=g('diff','--name-only',base,new).decode().splitlines();safe=[];same=[];over=[]
for p in paths:
 w=obj(tree,p)
 (safe if obj(base,p)==w else same if obj(new,p)==w else over).append(p)
exact_over=['docs/knowledge_learning/2026-10-07-ai-algorithms/report.md']+[p for p in over if p.startswith('knowledge/') or '/assets/knowledge/' in p]
merged=['prompts/orchestrator.md','prompts/research_orchestrator.md','plugins/research-assistant/skills/model-with-knowledge/SKILL.md']
skill=R/merged[-1]
assert '采样分布校正、算法成本条件' in skill.read_text()
assert skill.read_bytes()==obj(tree,merged[-1])
write(D/'merge-initial-conflict.json',{'path':merged[-1],'operation':'git merge-file -p','returncode':1,'written_conflict_markers':False,'resolution':'Keep accepted candidate description and feature contracts: it already contains both upstream sampling correction and algorithm cost routing phrases, while retaining broader data-structure scope. Only description line conflicted.','upstream_diff_scope':'one description line','preserved_candidate_sha256':sha(skill.read_bytes())})
# Adopt the upstream fixture then retain stronger post-ingestion exact-set controls.
p=R/'tests/test_knowledge_index.py';s=obj(new,p.relative_to(R).as_posix()).decode();needle="        self.assertEqual(build_index(store,self.db)['indexed'],self.published_count)\n"
assert s.count(needle)==1;s=s.replace(needle,needle+"        with sqlite3.connect(self.db) as con:\n            indexed_ids={row[0] for row in con.execute('SELECT id FROM docs')}\n        published_ids={kid for kid,record in store.records.items() if record['status']=='published'}\n        unpublished_ids=set(store.records)-published_ids\n        self.assertEqual(indexed_ids,published_ids)\n        self.assertIn('math.import-example',unpublished_ids)\n        self.assertTrue(indexed_ids.isdisjoint(unpublished_ids))\n",1);p.write_text(s)
# Raw archive and isolated migration preserve all118stable plans.
raw=obj(new,'TASK.md');digest=sha(raw);archive=R/f'doc/task/legacy/TASK.{digest}.md';assert not archive.exists();archive.write_bytes(raw)
with tempfile.TemporaryDirectory(prefix='migration-v3-',dir='/tmp') as td:
 t=Path(td);(t/'TASK.md').write_bytes(raw);v=subprocess.run([sys.executable,str(R/'scripts/project_docs.py'),'--root',str(t),'migrate','--date','2026-10-07'],capture_output=True,text=True);assert v.returncode==0,v.stderr;(D/'task-migration-generated.json').write_text(v.stdout)
 added=[]
 for f in sorted((t/'doc/task/task_details').glob('*.md')):
  dst=R/'doc/task/task_details'/f.name
  if not dst.exists():assert f.stem in ['MATH-17','MATH-18'];dst.write_bytes(f.read_bytes());added.append(f.stem)
 assert added==['MATH-17','MATH-18']
 newlines=[line for line in (t/'doc/task/TASK.md').read_text().splitlines() if any(f'[{i}]' in line for i in added)]
 p=R/'doc/task/TASK.md';s=p.read_text().replace('## 2026-10-07\n','## 2026-10-07\n\n'+'\n'.join(newlines)+'\n',1)
 for id in ['AIK-03','EK-122522-03']:
  assert f'- [ ] [{id}]' in s;s=s.replace(f'- [ ] [{id}]',f'- [x] [{id}]',1)
 p.write_text(s)
for id,receipt,commit in [('AIK-03','docs/knowledge_learning/2026-10-07-ai-algorithms/publication.json','017debae0e490f350ae1364a822ea0d4b2df82cc'),('EK-122522-03','docs/knowledge_learning/2026-10-07-engineering-122522/publication.json','fd9012ca9f953693ad59d30e63d03ac7644c599e')]:
 p=R/f'doc/task/task_details/{id}.md';p.write_text(p.read_text()+f'\n### 已验证上游发布收尾（2026-10-07）\n\n最新main f9898df已包含本任务独立发布与收尾。实现提交 `{commit}`，远端回执 `{receipt}` 按上游字节保留；canonical状态与实际已完成发布同步。原始上下文另存 `{archive.relative_to(R).as_posix()}`。此前本地合并候选中的pending描述仅是旧阶段记录，不再作为当前AIK/本任务未发布主张。DOC/DATA/REUSE/VEX合并发布仍独立待完成，不覆盖上游成功证据。\n')
assert all(sha((R/p).read_bytes().split(b'## Progress')[0])==h for p,h in plans.items())
subprocess.run([sys.executable,'scripts/sync_plugin_references.py'],check=True)
# Entire corpus, not just entry counts, must exactly match latest remote.
corpus=g('ls-tree','-r','--name-only',new,'knowledge').decode().splitlines();assert all((R/p).read_bytes()==obj(new,p) for p in corpus)
# No rollback/cleanup; only base metadata adoption after byte-preserving integration.
tracked=g('ls-files').decode().splitlines();h={p:sha((R/p).read_bytes()) for p in tracked if (R/p).is_file()};index=g('write-tree');subprocess.run(['git','reset','--soft',new],check=True);assert g('write-tree')==index;assert all(sha((R/p).read_bytes())==d for p,d in h.items())
report={'base':base,'upstream':new,'prior_tested_tree':tree,'delta_paths':223,'safe_paths':safe,'already_identical_upstream_paths':same,'overlap_paths':over,'upstream_authoritative_paths':exact_over,'three_way_merged_sources':merged,'canonical_tasks':120,'new_task_ids':added,'completed_by_verified_upstream':['AIK-03','EK-122522-03'],'task_archive':archive.relative_to(R).as_posix(),'task_archive_sha256':digest,'prior118_plan_hashes_unchanged':True,'corpus_exactly_matches_remote':True,'corpus_files_verified':len(corpus),'published':78,'candidates':2,'AIK_republished_or_duplicated':False,'guide_files':0,'base_adoption':'git reset --soft only; index/worktree bytes preserved','scope':'Merge upstream publication and matrix knowledge while preserving tested combined feature runtime and exact historical evidence. No new scientific research or promotion.'}
write(D/'integration.json',report);print(json.dumps({k:v for k,v in report.items() if not isinstance(v,list)},indent=2))
