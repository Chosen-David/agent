#!/usr/bin/env python3
"""Independent pipeline adversarial checks; no paid models; synthetic private rubric."""
import copy, importlib.util, json, pathlib, subprocess, sys, hashlib
ROOT=pathlib.Path(__file__).resolve().parent
LABEL=sys.argv[1] if len(sys.argv)>1 else 'initial'
SOURCE=ROOT.parents[1]/'scripts/agent_eval_pipeline.py'
spec=importlib.util.spec_from_file_location('pipeline_subject',SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def dump(p,v):p.write_text(json.dumps(v),encoding='utf-8')
def load(p):return json.loads(p.read_text())
def cmd(*a):return subprocess.run(a,capture_output=True,text=True,check=True)
work=ROOT/('runs-'+LABEL);work.mkdir(exist_ok=True)
repo=ROOT/'synthetic_repo'
if not repo.exists():
 repo.mkdir();cmd('git','init',str(repo));(repo/'plugins').mkdir();(repo/'plugins/SKILL.md').write_text('Synthetic evaluator test skill.')
 cmd('git','-C',str(repo),'add','.');cmd('git','-C',str(repo),'-c','user.name=Independent Tester','-c','user.email=test@example.invalid','commit','-m','fixture')
sha=cmd('git','-C',str(repo),'rev-parse','HEAD').stdout.strip()
tasks=ROOT/'synthetic_tasks.json';rubric=ROOT/'synthetic_rubric.json';fixtures=ROOT/'synthetic_fixtures';fixtures.mkdir(exist_ok=True);(fixtures/'input.txt').write_text('input-one')
dump(tasks,{'cases':[{'id':'unit-a','role':'synthetic','prompt':'produce answer','skill':'plugins/SKILL.md','fixtures':['input.txt']}]})
dump(rubric,{'criteria':{'unit-a':['synthetic criterion']}})
def receipt(kind):return {'event_id':kind+'-event','kind':kind,'case_id':'unit-a','attempt':1,'actor':'worker-a','adapter':'host',**({'status':'produced'} if kind=='complete' else {})}
def fresh(name,complete=True,adapter='host'):
 run=work/name
 if run.exists():raise RuntimeError('preserve evidence: destination already exists')
 m.prepare_run(repo,sha,run,tasks,rubric,fixtures,{'name':adapter,'model':'synthetic-test-only'})
 s=run/'start-receipt.json';r=receipt('start');r['adapter']=adapter;dump(s,r);d=m.record_start(run,'unit-a','worker-a',s)
 (d/'outputs/answer.txt').write_text('answer')
 if complete:
  c=run/'complete-receipt.json';r=receipt('complete');r['adapter']=adapter;dump(c,r);m.collect(run,'unit-a',1,c)
  g={'grader':'reviewer-b','case_id':'unit-a','attempt':1,'output_hashes':m.hashes(d/'outputs'),'checks':[{'criterion':'synthetic criterion','verdict':'pass','evidence':['answer.txt:1']}]}
  gp=run/'grade-input.json';dump(gp,g);m.grade_attempt(run,'unit-a',1,gp)
 return run,d
results=[]
def check(name,mutate=lambda r,d:None,expected=False,complete=True,adapter='host'):
 run,d=fresh(name,complete,adapter)
 try:
  mutate(run,d);report=m.report(run);accepted=report['complete'];outcome='accepted' if accepted else 'rejected';detail=report
 except Exception as e:accepted=False;outcome='exception';detail={'type':type(e).__name__,'message':str(e)}
 results.append({'name':name,'expected_accept':expected,'accepted':accepted,'ok':accepted==expected,'outcome':outcome,'detail':detail})
def edit(p,fn):data=load(p);fn(data);dump(p,data)
check('legal_control',expected=True)
check('missing_grade',lambda r,d:(d/'grade.json').unlink())
check('not_collected',complete=False)
check('empty_assertions',lambda r,d:edit(d/'grade.json',lambda x:x.update(checks=[])))
check('self_grading',lambda r,d:edit(d/'grade.json',lambda x:x.update(grader='worker-a')))
check('mock_receipts',adapter='mock')
check('input_changed',lambda r,d:(r/'cases/unit-a/inputs/input.txt').write_text('modified'))
check('output_changed',lambda r,d:(d/'outputs/answer.txt').write_text('modified'))
check('manifest_changed_after_start',lambda r,d:edit(r/'manifest.json',lambda x:x.update(revision='0'*40)))
check('wrong_complete_actor',lambda r,d:edit(d/'collection.json',lambda x:x['receipt'].update(actor='other')))
check('wrong_complete_case',lambda r,d:edit(d/'collection.json',lambda x:x['receipt'].update(case_id='another-case')))
check('wrong_complete_attempt',lambda r,d:edit(d/'collection.json',lambda x:x['receipt'].update(attempt=19)))
check('wrong_complete_kind',lambda r,d:edit(d/'collection.json',lambda x:x['receipt'].update(kind='start')))
check('wrong_complete_status',lambda r,d:edit(d/'collection.json',lambda x:x['receipt'].update(status='blocked')))
check('missing_complete_event',lambda r,d:edit(d/'collection.json',lambda x:x['receipt'].pop('event_id')))
check('wrong_start_actor',lambda r,d:edit(d/'start.json',lambda x:x['receipt'].update(actor='other')))
check('malformed_grade_json',lambda r,d:(d/'grade.json').write_text('{'))
check('grade_list_not_object',lambda r,d:dump(d/'grade.json',[]))
check('grade_check_scalar',lambda r,d:edit(d/'grade.json',lambda x:x.update(checks=['pass'])))
check('output_symlink_escape',lambda r,d:((d/'outputs/answer.txt').unlink(),(d/'outputs/answer.txt').symlink_to(fixtures/'input.txt')))
check('fake_evidence_path',lambda r,d:edit(d/'grade.json',lambda x:x['checks'][0].update(evidence=['../../../../nonexistent.txt:1'])))
check('missing_case_directory',lambda r,d:(r/'cases/unit-a').rename(r/'cases/removed'))
# A manifest can be syntactically well formed yet remove expected work before dispatch.
run=work/'empty_manifest_cases';m.prepare_run(repo,sha,run,tasks,rubric,fixtures,{'name':'host'})
edit(run/'manifest.json',lambda x:x.update(expected_cases=[],cases={}))
try:
 rep=m.report(run);acc=rep['complete'];results.append({'name':'empty_manifest_cases','expected_accept':False,'accepted':acc,'ok':not acc,'outcome':'accepted' if acc else 'rejected','detail':rep})
except Exception as e:results.append({'name':'empty_manifest_cases','expected_accept':False,'accepted':False,'ok':True,'outcome':'exception','detail':str(e)})
def escape_attempt(run,directory):
 target=work/(run.name+'-escaped-attempt');directory.rename(target);directory.symlink_to(target,target_is_directory=True)
def escape_case(run,directory):
 case=run/'cases/unit-a';target=work/(run.name+'-escaped-case');case.rename(target);case.symlink_to(target,target_is_directory=True)
check('attempt_directory_symlink_escape',escape_attempt)
check('case_directory_symlink_escape',escape_case)
summary={'scope':'program checks only; synthetic receipts are not genuine model execution','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'total':len(results),'correct_decisions':sum(x['ok'] for x in results),'false_accepts':[x['name'] for x in results if x['accepted'] and not x['expected_accept']],'exceptions':[x['name'] for x in results if x['outcome']=='exception'],'cases':results}
dump(ROOT/('results-'+LABEL+'.json'),summary)
print(json.dumps({k:v for k,v in summary.items() if k!='cases'},indent=2))
