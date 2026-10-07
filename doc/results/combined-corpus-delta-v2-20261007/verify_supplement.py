#!/usr/bin/env python3
"""Preserve first failures, verify published-only fixture and isolated package."""
import hashlib,json,os,re,shutil,subprocess,sys,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BASE='907890831929a5d200d3fb64c6299449391a1ee8'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
def main():
 assert not (OUT/'supplement.json').exists()
 plugin=ROOT/'plugins/research-assistant/skills/model-with-knowledge'
 paths=[*ROOT.glob('agent_runtime/*.py'),*ROOT.glob('tests/test_knowledge*.py'),ROOT/'tests/test_handoff_basis.py',ROOT/'tests/test_selective_context.py',*ROOT.glob('scripts/*knowledge*.py'),*ROOT.joinpath('knowledge').rglob('*.json'),*ROOT.joinpath('knowledge').rglob('*.md'),*plugin.glob('scripts/*.py'),*plugin.joinpath('assets/knowledge').rglob('*.json'),*plugin.joinpath('assets/knowledge').rglob('*.md'),Path(__file__)]
 before={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}
 commands=[]
 started=datetime.now(timezone.utc).isoformat()
 with tempfile.TemporaryDirectory(prefix='supplement-temp-',dir=OUT) as tmp:
  tmp=Path(tmp);env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':str(tmp)};env.pop('PYTHONPATH',None)
  def run(cmd,name,cwd=ROOT,local_env=None):
   t=time.perf_counter();p=subprocess.run([str(x) for x in cmd],cwd=cwd,env=local_env or env,capture_output=True,text=True)
   (OUT/(name+'.log')).write_text(p.stdout+p.stderr)
   record={'name':name,'command':[str(x) for x in cmd],'cwd':str(cwd),'exit_code':p.returncode,'elapsed_seconds':time.perf_counter()-t}
   commands.append(record)
   return p
  baseline=tmp/'baseline907';baseline.mkdir()
  archive=subprocess.check_output(['git','archive',BASE,'agent_runtime','knowledge','tests/test_knowledge_index.py'],cwd=ROOT)
  subprocess.run(['tar','-x','-C',str(baseline)],input=archive,check=True)
  b=run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_knowledge_index.py','-v'],'baseline907-index-fixture',cwd=baseline)
  assert b.returncode==1 and '75 != 76' in b.stderr and 'failures=4' in b.stderr,b.stdout+b.stderr
  k=run([sys.executable,'-m','unittest','discover','-s','tests','-p','test_knowledge*.py','-v'],'knowledge-tests-after-fixture')
  c=run([sys.executable,'-m','unittest','test_handoff_basis','test_selective_context','-v'],'knowledge-consumer-tests-final',local_env={**env,'PYTHONPATH':str(ROOT/'tests')})
  isolated=tmp/'isolated-package';shutil.copytree(plugin,isolated)
  corpus=isolated/'assets/knowledge';cli=isolated/'scripts/knowledge.py';db=tmp/'isolated-index.sqlite'
  def tool(args,name):
   p=run([sys.executable,'-I','-B',cli,'--root',corpus,*args],name,cwd=Path('/'))
   assert p.returncode==0,p.stderr
   d=json.loads(p.stdout);write(OUT/(name+'.json'),d);return d
  v=tool(['validate'],'isolated-plugin-validate')
  ix=tool(['index','--db',db],'isolated-plugin-index')
  q=tool(['search','推测采样 分布 修正 拒绝 残差','--domain','ai-algorithms','--index',db,'--limit','3'],'isolated-plugin-search')
  p=run([sys.executable,'-I','-B',cli,'--root',corpus,'show','neuro.cephalopod-arm-segmentation'],'isolated-plugin-candidate-get',cwd=Path('/'))
  assert p.returncode==2 and 'not published' in p.stderr,p.stderr
  source_files={str(p.relative_to(ROOT/'knowledge')):sha(p) for p in (ROOT/'knowledge').rglob('*') if p.is_file()}
  package_files={str(p.relative_to(plugin/'assets/knowledge')):sha(p) for p in (plugin/'assets/knowledge').rglob('*') if p.is_file()}
  assert source_files==package_files
  assert v['entries']==78 and ix['indexed']==77
  assert 'ai.speculative-sampling-residual-exactness' in [x['id'] for x in q['results']]
  assert k.returncode==0 and c.returncode==0,(k.stderr,c.stderr)
 after={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}
 assert before==after
 summary={'started_at_utc':started,'completed_at_utc':datetime.now(timezone.utc).isoformat(),'baseline_commit':BASE,'baseline_fixture_failure_inherited':True,'baseline_index_fixture':{'tests':10,'failures':4,'actual_indexed':75,'wrong_total_expected':76},'first_combined_run':{'tests':67,'failures':4,'actual_indexed':77,'wrong_total_expected':78},'fix':'Fixture separately counts all records for ingest and published records for SQLite; runtime unchanged.','fixed_knowledge_tests':67,'consumer_tests':34,'all_postfix_tests_passed':True,'package_isolated':{'python_flags':['-I','-B'],'cwd':'/','PYTHONPATH_unset':True,'metadata_entries':78,'indexed_published':77,'source_mirror_exact':True,'search_target_found':True,'candidate_get_blocked':True},'dependencies_before':before,'dependencies_after':after,'dependencies_stable':True,'commands':commands}
 write(OUT/'supplement.json',summary)
 print(json.dumps({k:v for k,v in summary.items() if not k.startswith('dependencies') and k!='commands'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
