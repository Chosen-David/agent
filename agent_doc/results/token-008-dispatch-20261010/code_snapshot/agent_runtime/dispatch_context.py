"""Host-selected fresh subtask context; unknown needs keep inherited history."""
import copy,json
from pathlib import Path
from .result_validation import _bound

SCHEMA='dispatch-context/v1'
def prepare_dispatch(root,request,*,force_inherit=False,max_chars=12000):
    root=Path(root)
    if not root.is_absolute():raise ValueError('absolute PROJECT_ROOT required')
    root=root.resolve(strict=True)
    fields={'schema_version','project_root','task_id','parent','settings_complete','needs_complete','history_required','guide_verified_human','required_refs','context_refs','instruction'}
    if not isinstance(request,dict) or set(request)!=fields or request['schema_version']!=SCHEMA:
        raise ValueError('explicit host dispatch contract required')
    if not isinstance(request['project_root'],str) or Path(request['project_root']).resolve(strict=True)!=root:
        raise ValueError('wrong project binding')
    if type(request['needs_complete']) is not bool or request['history_required'] not in (None,False,True) or (request['history_required'] is not None and type(request['history_required']) is not bool):
        raise ValueError('explicit completeness/history requirements required')
    if type(request['settings_complete']) is not bool or type(request['guide_verified_human']) is not bool or type(force_inherit) is not bool or type(max_chars) is not int or not 1<=max_chars<=100000:
        raise ValueError('invalid host flags/budget')
    for k in ('task_id','instruction'):
        if not isinstance(request[k],str) or not request[k].strip() or len(request[k])>4000:raise ValueError('bounded task/instruction required')
    parent=request['parent'];keys={'thread_id','last_turn_id','cwd','model','reasoning_effort','approval_policy','sandbox','config'}
    if not isinstance(parent,dict) or set(parent)!=keys:raise ValueError('native parent settings required')
    for k in keys-{'config'}:
        if not isinstance(parent[k],str) or not parent[k].strip() or len(parent[k])>4096:raise ValueError('bounded native parent metadata required')
    if Path(parent['cwd']).resolve(strict=True)!=root:raise ValueError('cross-project parent forbidden; rebind target project separately')
    if not isinstance(parent['config'],dict):raise ValueError('host-resolved parent config required')
    refs=request['context_refs'];required=request['required_refs']
    if not isinstance(refs,list) or not isinstance(required,list) or max(len(refs),len(required))>64:
        raise ValueError('bounded context/reference lists required')
    def key(ref):
        if not isinstance(ref,dict) or set(ref)!={'path','sha256'}:raise ValueError('exact context reference fields required')
        if not isinstance(ref['path'],str) or not isinstance(ref['sha256'],str):raise ValueError('invalid reference types')
        return (ref['path'],ref['sha256'])
    supplied=[key(r) for r in refs];needed=[key(r) for r in required]
    if len(set(supplied))!=len(supplied) or len(set(needed))!=len(needed) or not set(needed)<=set(supplied):
        raise ValueError('missing or duplicate required dependencies')
    docs=[]
    for ref in refs:
        raw=_bound(root,ref)
        if len(raw)>max_chars*4:raise ValueError('context document exceeds whole budget')
        text=raw.decode('utf-8')
        if len(text)>max_chars:raise ValueError('context document exceeds whole budget')
        docs.append({**ref,'text':text})
    fresh=not force_inherit and request['settings_complete'] and request['needs_complete'] and request['history_required'] is False
    if fresh:
        guides=[d for d in docs if d['path']=='agent_doc/guide/GUIDE.md']
        if len(guides)!=1 or key({k:guides[0][k] for k in ('path','sha256')}) not in needed:
            raise ValueError('current project guide is a mandatory fresh-context dependency')
        if guides[0]['text'].strip() and not request['guide_verified_human']:
            raise ValueError('nonempty guide human provenance not verified')
    packet={'schema_version':'subtask-context/v1','project_root':str(root),'task_id':request['task_id'],
        'instruction':request['instruction'],'guide_verified_human':request['guide_verified_human'],'documents':docs}
    text=json.dumps(packet,ensure_ascii=False,separators=(',',':'))
    if len(text)>max_chars:raise ValueError('complete subtask context exceeds budget; no truncation')
    params={'cwd':str(root),'model':parent['model'],'approvalPolicy':parent['approval_policy'],
        'sandbox':parent['sandbox'],'ephemeral':False,'config':copy.deepcopy(parent['config'])}
    params['config']['model_reasoning_effort']=parent['reasoning_effort']
    if not fresh:
        if not request['settings_complete']:params={}
        params.update(threadId=parent['thread_id'],lastTurnId=parent['last_turn_id'],excludeTurns=True)
    return {'schema_version':'dispatch-plan/v1','method':'thread/start' if fresh else 'thread/fork','params':params,
        'input_text':text,'scope':'host-declared dependency-complete closed task' if fresh else 'inherit history; unknown or required history retained',
        'authorization':'unchanged native parent settings; contract is not authorization',
        'source_dependencies':copy.deepcopy(refs)}
