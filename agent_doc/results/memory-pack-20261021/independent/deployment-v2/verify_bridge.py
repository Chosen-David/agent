"""Independent deployment-v2 full binding and explicit v1 evidence bridge."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent;OLD_RUN=RUN.parent
SOURCE=ROOT/'agent_doc/results/memory-pack-20261021/deployment-v2';OLD=SOURCE.parent
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def require(cond,reason):
    if not cond:raise AssertionError(reason)
contract=load(SOURCE/'contract.json');manifest,plan,proof=_snapshot(ROOT,contract)
old_proof=load(OLD_RUN/'bindings-v1.json')['proof'];old_manifest=load(OLD/'manifest.json')
require(sha(OLD/'manifest.json')==old_proof['manifest_sha256'],'v1 manifest changed')
require(sha(OLD/'independent/review-v1.json')==sha(OLD_RUN/'review-v1.json'),'original independent review not preserved')
require(sha(OLD/'raw.json')==old_proof['artifact_hashes']['agent_doc/results/memory-pack-20261021/raw.json'],'original raw changed')
old_snapshot=load(OLD/'strict-source-snapshot.json');new_snapshot=load(SOURCE/'strict-source-snapshot.json')
require(set(old_snapshot)==set(new_snapshot),'unexpected snapshot file set change')
changed=[p for p in sorted(old_snapshot) if old_snapshot[p]!=new_snapshot[p]]
require(changed==['agent_runtime/dispatch_context.py','tests/test_dispatch_context.py'],'unexpected snapshot delta')
for p,expected in new_snapshot.items():require(sha(ROOT/p)==expected,'current strict snapshot mismatch '+p)
for p in changed:
    name='old-'+Path(p).name
    require(sha(SOURCE/name)==old_snapshot[p],'archived original bytes mismatch '+p)
unaffected_code=[]
for ref in old_manifest['artifacts']['code']:
    p=ref['path']
    if p=='agent_runtime/dispatch_context.py':continue
    require(sha(ROOT/p)==ref['sha256'],'unaffected v1 code changed '+p);unaffected_code.append(p)
corpus=[ref for ref in old_manifest['artifacts']['inputs'] if ref['path'].startswith('knowledge/')]
for ref in corpus:require(sha(ROOT/ref['path'])==ref['sha256'],'corpus changed '+ref['path'])
old_plan=load(OLD/'validation_plan.json')
for key,criterion in plan['criteria'].items():
    require(criterion['acceptance']==old_plan['criteria'][key]['acceptance'],'threshold changed '+key)
    require(criterion['allow_not_applicable'] is False,'required domain relaxed')
old_env=load(OLD/'environment.json');new_env=load(SOURCE/'environment.json')
for key in ('tiktoken','encoding','ranks_sha256','rank_count','pattern','special_tokens','tokenizer_files'):
    require(old_env[key]==new_env[key],'tokenizer identity changed '+key)
delta=subprocess.check_output(['git','diff','425390428f7ea9dbf5b5a4756c5d6cadcab89be3','d9fdf9b3e9ca4080fd79f3e7cab631b569dfbb89','--',*changed],cwd=ROOT).decode('utf-8')
result={'proof':proof,'artifact_role_counts':{k:len(v) for k,v in manifest['artifacts'].items()},
        'strict_snapshot_files':len(new_snapshot),'strict_snapshot_changed_paths':changed,
        'unaffected_v1_code_files':len(unaffected_code),'unchanged_corpus_files':len(corpus),
        'delta':delta,'bridged_evidence':{
            'producer_52_log_sha256':sha(OLD/'targeted-tests.txt'),
            'independent_properties_sha256':sha(OLD_RUN/'properties-v1.json'),
            'independent_12_log_sha256':sha(OLD_RUN/'regressions-v1.log'),
            'optimized_7_log_sha256':sha(OLD_RUN/'optimized-v1.log')},
        'status':'all new bindings valid; exact v1 bridge isolated to two dispatch files',
        'scope':'conditional historical regression/property reuse, not a claim that original v1 live contract remains valid'}
with (RUN/'bridge.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('artifact_role_counts','strict_snapshot_files','strict_snapshot_changed_paths','unaffected_v1_code_files','unchanged_corpus_files','status')}))
