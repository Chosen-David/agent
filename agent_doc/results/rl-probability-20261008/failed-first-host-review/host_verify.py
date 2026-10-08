"""Controller-selected deterministic reviewer; not an independent AI model.

Run explicitly in a separate host process. Checks raw denominators, fresh
retrieval/decision replay and exact dependency hashes before result acceptance.
"""
import hashlib
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from agent_runtime.knowledge import KnowledgeStore
from agent_runtime.knowledge_index import build_index, indexed_search
from agent_runtime.knowledge_reuse import decision_support
import tempfile

REL='doc/results/rl-probability-20261008'


def ref(root,path):
    return {'path':path,'sha256':hashlib.sha256((root/path).read_bytes()).hexdigest()}


def verify(root,manifest,plan):
    root=Path(root);base=root/REL
    inventory=json.loads((base/'source-inventory.json').read_text())
    for item in inventory['files']:
        data=(root/item['path']).read_bytes()
        if item['normalization']=='utf8-lf':
            data=data.decode('utf-8').replace('\r\n','\n').encode('utf-8')
        assert hashlib.sha256(data).hexdigest()==item['sha256'],item['path']
    raw=json.loads((base/'retrieval.json').read_text())
    assert len(raw['baseline'])==len(raw['current'])>0
    assert len({(x['backend'],x['case']) for x in raw['current']})==len(raw['current'])
    for old,new in zip(raw['baseline'],raw['current']):
        assert all(old[k]==new[k] for k in ('backend','case','query','expected'))
        if old['recall'] is not None:
            assert new['recall']==sum(x in new['actual'] for x in new['expected'])/len(new['expected'])
            assert new['recall']>=old['recall']
        if old['no_hit_correct'] is True: assert new['no_hit_correct'] is True
    store=KnowledgeStore(root/'knowledge')
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'replay.sqlite';build_index(store,db)
        for row in raw['new']:
            hits=store.search(row['query'],limit=3) if row['backend']=='files' else indexed_search(store,db,row['query'],limit=3)
            actual=[x['id'] for x in hits['results']]
            assert actual==row['actual'] and all(x in actual for x in row['expected'])
    assert len(raw['new'])==4 and len(raw['decisions'])==8
    for row in raw['decisions']:
        record=store.get(row['id'])
        assert record['status']=='published' and record['reuse']['paper']['local_reproduction']=='not-run'
        query=next(x['query'] for x in raw['new'] if row['id'] in x['expected'])
        replay=decision_support(store,query,row['context'],explicit_reproduction=row['case']=='explicit-reproduction',limit=20)
        hit=next(x for x in replay['results'] if x['id']==row['id'])
        assert row['actual']==row['expected']==hit['disposition'] and hit['automatic_skip_authorized'] is False
        store.check_refs(row['knowledge_refs'])
    counts=[]
    for name in ('repository','reader'):
        text=(base/(name+'.log')).read_text()
        match=re.search(r'Ran (\d+) tests?',text);assert match and re.search(r'^OK(?: \(skipped=\d+\))?$',text,re.M)
        assert not re.search(r'^(FAIL|ERROR):',text,re.M)
        counts.append(int(match[1]))
        # Reuse the already reviewed verbose-log accounting helper; do not
        # accept only a pasted OK summary as evidence of test denominators.
        import importlib.util
        spec=importlib.util.spec_from_file_location('prior_host_accounting',root/'doc/results/codex-pull-sync-20261007/host_verify.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        assert module.counts(base/(name+'.log'))[0]==int(match[1])
    checks=json.loads((base/'checks.json').read_text())
    assert len(checks)==5 and all(c['exit_code']==0 for c in checks)
    prompt=(root/'prompts/engineering_knowledge_continuous_learning.md').read_text(encoding='utf-8')
    assert 'priority.next_domain' in prompt and '只有缺失游标时' in prompt
    assert '先补新增神经科学缺口' not in prompt
    bindings={manifest['validation_plan']['path']:manifest['validation_plan']['sha256']}
    for group in manifest['artifacts'].values():
        for item in group:
            assert ref(root,item['path'])==item
            bindings[item['path']]=item['sha256']
    observations=[ref(root,REL+'/'+p) for p in ('retrieval.json','checks.json','host-process.json','repository.log','reader.log')]
    reasons={
      'implementation':'Read actual search/reuse paths and independently replay both backends and refusal dispositions; inspect saved cursor instruction.',
      'reference_boundary':'Matching, omitted context, changed setting and explicit reproduction checked; no automatic skip authorized.',
      'data_integrity':f'Unique old query IDs and exact case/input comparison; {len(raw["current"])} old rows, 4 new rows, 8 decisions; unittest totals {counts}. Hashes bind dependencies.',
      'numerical_sanity':'Recompute recall from IDs, require nonregression; finite unitless denominators; no numeric paper data used as local measurement.',
      'measurement_validity':'Public authored development queries and unit tests only; no blind model, paper reproduction, performance or continuous-CS claim.',
      'reproducibility':'Fresh separate-process replay against current exact hash-bound corpus and runtime; full unit checks read from frozen Linux checkout.'}
    host=json.loads((base/'host-process.json').read_text())
    assert host['pid']>0 and host['actor']=='host-retrieval-reviewer'
    return {'schema_version':'experiment-validation/v1','manifest_sha256':hashlib.sha256((base/'manifest.json').read_bytes()).hexdigest(),
            'artifact_hashes':bindings,'validation_plan_sha256':manifest['validation_plan']['sha256'],'scope':plan['scope'],
            'verifier':{'actor':'host-retrieval-reviewer','independent':True,'source':'explicit controller-injected deterministic separate-process checker', 'run_id':host['run_id'],'method':'raw accounting, source inspection, reference reconstruction and actual fresh replay'},
            'limitations':['Deterministic host review is not a second independent AI/scientific review.','Public authored queries do not measure model reasoning, unseen retrieval, GPU performance or paper reproduction.','Prompt cursor instruction does not prove model compliance; grid-CS approximation and episode discrepancy remain unresolved.'],
            'checks':{key:{'verdict':'not_applicable' if key=='measurement_validity' else 'pass','reason':reason,'evidence':observations} for key,reason in reasons.items()}}
