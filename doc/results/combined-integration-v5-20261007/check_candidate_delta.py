from pathlib import Path
import sys,subprocess,tempfile,shutil,json,hashlib,sqlite3
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R))
from agent_runtime.knowledge import KnowledgeStore,KnowledgeError
from agent_runtime.knowledge_index import build_index,indexed_search
D=Path(__file__).resolve().parent;OLD='5172ad32bf2957e89a9308989a44c326729c2370';NEW='21cb9876084108cb8cb6a92c50279acbcb62648e'
def g(*args):return subprocess.check_output(['git','-C',str(R),*args])
def sha(b):return hashlib.sha256(b).hexdigest()
current=KnowledgeStore(R/'knowledge');pub={k:v for k,v in current.records.items() if v['status']=='published'};candidates={k for k,v in current.records.items() if v['status']=='candidate'}
assert len(pub)==80 and len(candidates)==3
files=g('ls-tree','-r','--name-only',NEW,'knowledge').decode().splitlines();assert len(files)==174
assert all((R/p).read_bytes()==g('show',NEW+':'+p) for p in files)
mirror=R/'plugins/research-assistant/skills/model-with-knowledge/assets/knowledge';assert all((mirror/Path(p).relative_to('knowledge')).read_bytes()==(R/p).read_bytes() for p in files)
prior_entry_files=g('ls-tree','-r','--name-only',OLD,'knowledge/entries').decode().splitlines();assert len(prior_entry_files)==164
assert all((R/p).read_bytes()==g('show',OLD+':'+p) for p in prior_entry_files)
queries=['speculative sampling residual exactness','dependent mean variance','matrix covariance'];comparisons=[];blocks=[]
with tempfile.TemporaryDirectory(prefix='v5-corpus-',dir='/tmp') as td:
 t=Path(td);oldroot=t/'knowledge'
 for p in g('ls-tree','-r','--name-only',OLD,'knowledge').decode().splitlines():
  dest=t/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(g('show',OLD+':'+p))
 old=KnowledgeStore(oldroot);db=t/'index.sqlite';old_index=build_index(old,db)
 initial={q:{'files':[v['id'] for v in old.search(q,limit=8)['results']],'sqlite':[v['id'] for v in indexed_search(old,db,q,limit=8)['results']]} for q in queries}
 shutil.copytree(R/'knowledge',oldroot,dirs_exist_ok=True);fresh=KnowledgeStore(oldroot)
 try:indexed_search(fresh,db,queries[0]);raise AssertionError('stale index accepted')
 except KnowledgeError as e:stale_error=str(e)
 refreshed=build_index(fresh,db);assert refreshed['updated']==0 and refreshed['removed']==0
 with sqlite3.connect(db) as con:indexed={row[0] for row in con.execute('SELECT id FROM docs')}
 assert indexed==set(pub) and indexed.isdisjoint(candidates)
 for kid in sorted(candidates):
  try:fresh.get(kid);raise AssertionError('candidate returned by default get')
  except KnowledgeError as e:blocks.append({'id':kid,'get_blocked':True,'error':str(e)})
  assert kid not in [v['id'] for v in fresh.search(kid,limit=20)['results']]
  assert kid not in [v['id'] for v in indexed_search(fresh,db,kid,limit=20)['results']]
 for q in queries:
  after={'files':[v['id'] for v in fresh.search(q,limit=8)['results']],'sqlite':[v['id'] for v in indexed_search(fresh,db,q,limit=8)['results']]}
  assert after==initial[q];comparisons.append({'query':q,'before':initial[q],'after':after,'same':True})
 result={'scope':'Candidate-only delta: published bytes and search implementation unchanged.6representative rankings plus exact80ID index/candidate guards; no broadcatalog or scientific experiment.','previous_tree':OLD,'base_commit':NEW,'prior_snapshot':old.snapshot,'current_snapshot':current.snapshot,'published':80,'candidates':3,'corpus_files_exact_remote':174,'mirror_exact':True,'prior_entry_files_preserved':164,'holdouts_unchanged':(R/'knowledge/evaluation_holdouts.json').read_bytes()==g('show',OLD+':knowledge/evaluation_holdouts.json'),'candidate_blocks':blocks,'rankings':comparisons,'old_index':old_index,'refreshed_index':refreshed,'stale_index_error':stale_error,'indexed_ids_exactly_published':True,'limits':['Unchanged representative rankings are not a fresh entire-catalog score.','Candidate evidence is not promoted or scientifically certified.','Prior AIK21/24default23/24domain results are reused for unchanged published inputs, not rerun here.']}
 (D/'candidate-only-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['published','candidates','corpus_files_exact_remote','prior_entry_files_preserved','indexed_ids_exactly_published']},indent=2))
