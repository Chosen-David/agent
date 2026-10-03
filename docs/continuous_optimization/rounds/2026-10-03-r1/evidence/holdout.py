import argparse, copy, hashlib, importlib.util, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'artifacts'
ROOT.mkdir(exist_ok=True)
(ROOT/'audit.txt').write_text('Review performed on synthetic fixture; arithmetic check 7 * 8 = 56.\n')
(ROOT/'bundle.txt').write_text('Synthetic delivery manifest, no external backend executed.\n')
for name in ('cycle',):
    p=ROOT/name
    if not p.is_symlink(): p.symlink_to(name)
ROOT_LOOP=HERE/'root-cycle'
if not ROOT_LOOP.is_symlink(): ROOT_LOOP.symlink_to('root-cycle')

def record():
    return dict(schema_version=1,run_id='isolation-r1',role='handoff-consumer',input_version='sealed-v1',status='completed',limitations=[],artifacts=[dict(id=n,path=p,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for n,p in [('audit','audit.txt'),('bundle','bundle.txt')]],checks=[dict(criterion='synthetic audit saved',status='pass',artifact_ids=['audit'])],tasks=[dict(task_id='inspect',status='done',evidence=['audit']),dict(task_id='deliver',status='done',depends_on=['inspect'],evidence=['bundle'])])

cases=[]
def add(name, expected_valid, change=lambda r:None, root=ROOT, note=''):
    r=record(); change(r); cases.append(dict(name=name,expected_valid=expected_valid,record=r,root=str(root),note=note))
add('two_artifact_handoff',True,note='Valid dependency chain with separate evidence per task.')
add('completed_disconnected_todo',False,lambda r:r['tasks'].append(dict(task_id='unrelated',status='todo')),note='Incomplete task is invalid even outside accepted delivery dependency path.')
add('completed_disconnected_doing',False,lambda r:r['tasks'].append(dict(task_id='transcribe',status='doing')))
add('completed_disconnected_blocked',False,lambda r:r['tasks'].append(dict(task_id='gpu',status='blocked',reason='GPU absent')))
add('completed_nonessential_skip',True,lambda r:r['tasks'].append(dict(task_id='extra',status='skipped',reason='Optional extra excluded from requested deliverable')))
add('completed_skip_with_whitespace_reason',False,lambda r:r['tasks'].append(dict(task_id='extra',status='skipped',reason=' \t\n')))
add('done_truthy_dictionary_evidence',False,lambda r:r['tasks'][0].update(evidence={'audit':'audit'}))
add('done_truthy_string_evidence',False,lambda r:r['tasks'][0].update(evidence='audit'))
add('done_mixed_type_evidence',False,lambda r:r['tasks'][0].update(evidence=['audit',{'id':'bundle'}]))
add('done_existing_and_dangling_evidence',False,lambda r:r['tasks'][0].update(evidence=['audit','inexistent']))
add('done_wrong_namespace_evidence',False,lambda r:r['tasks'][1].update(evidence=['inspect']))
add('optional_evidence_omitted_partial',True,lambda r:(r.update(status='partial',limitations=['Continue optional test']),r['tasks'].append(dict(task_id='later',status='todo'))))
add('partial_todo_dangling_evidence',False,lambda r:(r.update(status='partial',limitations=['Continue test']),r['tasks'].append(dict(task_id='later',status='todo',evidence=['inexistent']))))
add('all_done_on_partial_record',True,lambda r:r.update(status='partial',limitations=['Deliverable awaits external acceptance']),note='Partial record can be internally valid; require-complete still rejects it.')
add('artifact_self_symlink',False,lambda r:r['artifacts'][1].update(path='cycle'),note='Expected diagnostics, never an uncaught RuntimeError.')
add('artifact_embedded_nul',False,lambda r:r['artifacts'][1].update(path='bad\0path'),note='Direct API and CLI must fail diagnostically.')
add('root_self_symlink',False,root=ROOT_LOOP,note='Expected diagnostics, never an uncaught RuntimeError.')
add('no_task_array',True,lambda r:r.pop('tasks'),note='Tasks remain optional for simple saved answers.')
add('internal_relative_path',True,lambda r:r['artifacts'][1].update(path='./bundle.txt'))

p=argparse.ArgumentParser();p.add_argument('validator');p.add_argument('label');p.add_argument('--lock',action='store_true');args=p.parse_args()
manifest=[{k:v for k,v in c.items() if k!='record'} for c in cases]
if args.lock:
    (HERE/'acceptance.json').write_text(json.dumps(manifest,indent=2)+'\n')
else:
    assert manifest==json.loads((HERE/'acceptance.json').read_text()),'Holdout criteria changed'
sp=importlib.util.spec_from_file_location('candidate',args.validator);module=importlib.util.module_from_spec(sp);sp.loader.exec_module(module)
results=[]
for c in cases:
    f=HERE/(c['name']+'.json');f.write_text(json.dumps(c['record'],indent=2))
    try:
        errors=module.validate(copy.deepcopy(c['record']),Path(c['root']))
        api=dict(valid=not errors,errors=errors,exception=None)
    except Exception as ex:
        api=dict(valid=None,errors=None,exception=type(ex).__name__+': '+str(ex))
    proc=subprocess.run([sys.executable,args.validator,str(f),'--root',c['root']],capture_output=True,text=True,timeout=5)
    try: output=json.loads(proc.stdout)
    except Exception: output=None
    cli_ok=output is not None and output.get('integrity_valid')==c['expected_valid'] and proc.returncode==(0 if c['expected_valid'] else 1) and not proc.stderr
    api_ok=api['exception'] is None and api['valid']==c['expected_valid']
    gate=module.validate(c['record'],ROOT,True) if c['name']=='all_done_on_partial_record' else None
    ok=api_ok and cli_ok and (bool(gate) if gate is not None else True)
    results.append(dict(name=c['name'],expected_valid=c['expected_valid'],passed=ok,api=api,cli=dict(returncode=proc.returncode,output=output,stderr=proc.stderr),require_complete_errors=gate))
report=dict(label=args.label,validator=str(Path(args.validator).resolve()),sha256=hashlib.sha256(Path(args.validator).read_bytes()).hexdigest(),cases=len(results),passed=sum(x['passed'] for x in results),results=results,scope='Programmatic local handoff integrity only; no LLM role execution or semantic quality evaluation.')
(HERE/(args.label+'.json')).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
print('Failed:',', '.join(x['name'] for x in results if not x['passed']))
