import hashlib, importlib.util, json, pathlib, subprocess, sys
ROOT=pathlib.Path(__file__).resolve().parents[5]; OUT=pathlib.Path(__file__).resolve().parent
script=ROOT/'plugins/research-assistant/skills/research-implement-optimize/scripts/compiler_feedback.py'
spec=importlib.util.spec_from_file_location('target',script);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
checks=[]
def check(name,value):
    checks.append({'name':name,'passed':bool(value)})
raw=("ptxas info : Compiling entry function 'same' for 'sm_90'\r\nptxas info : Function properties for same\r\n 0 bytes stack frame, 4 bytes spill stores, 8 bytes spill loads\r\nptxas info : Used 64 registers, 20 bytes smem\r\nptxas info : Compiling entry function 'same' for 'sm_100a'\r\nptxas info : Used 32 registers\r\nptxas info : Used 33 registers\r\nptxas info : Used 32 registers").encode()
a,b=mod.parse_log(raw)['records']
check('architectures_do_not_merge',(a['target'],b['target'])==('sm_90','sm_100a'))
check('reference_a',a['metrics']==dict(registers_per_thread=64,static_shared_bytes=20,stack_frame_bytes=0,spill_store_bytes=4,spill_load_bytes=8))
check('persistent_conflict',b['metrics']['registers_per_thread'] is None and b['conflicts']==['registers_per_thread'])
check('all_lines',sorted(o['line'] for o in a['observations'])==[3,3,3,4,4])
check('raw_crlf_sha',mod.parse_log(raw)['log_sha256']==hashlib.sha256(raw).hexdigest())
check('max_bytes_accepted',mod.parse_log(b' '*mod.MAX_BYTES)['parse_status']=='no_records')
for name,data in [('max_bytes_rejected',b' '*(mod.MAX_BYTES+1)),('invalid_utf8_rejected',b'\xff'),('record_limit_rejected',(b"ptxas info : Compiling entry function 'a' for 'sm_90'\n"*(mod.MAX_RECORDS+1)))]:
    try:mod.parse_log(data)
    except ValueError:check(name,True)
    else:check(name,False)
check('record_limit_accepted',len(mod.parse_log(b"ptxas info : Compiling entry function 'a' for 'sm_90'\n"*mod.MAX_RECORDS)['records'])==mod.MAX_RECORDS)
metadata=[]
for i in range(1,4):
    relative=f'agent_doc/task/task_details/CONT-20261008-0{i}.md';p=ROOT/relative
    old=subprocess.check_output(['git','show','HEAD:'+relative],cwd=ROOT).decode()
    expected=old.replace('## Plan v1',f'Task-ID: CONT-20261008-0{i}\nDate: 2026-10-08\n\n## Plan\n\nPlan version: v1 (original content retained).',1)
    appended='\n2026-10-08 metadata repair (KERNEL-FEEDBACK-01): canonical Plan heading restored for project document validation. Original plan content/status unchanged; historical snapshots remain historical and no old dispatch is reactivated.\n'
    check('metadata_exact_'+str(i),p.read_text()==expected+appended)
    metadata.append({'path':relative,'before_sha256':hashlib.sha256(old.encode()).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
report={'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'checks':checks,'metadata':metadata}
(OUT/'extra-validation.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))
