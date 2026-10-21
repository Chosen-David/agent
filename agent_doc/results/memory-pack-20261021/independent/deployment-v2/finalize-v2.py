"""New scoped review identity and proof after exact, conditional historical bridge."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];RUN=Path(__file__).resolve().parent
SOURCE=ROOT/'agent_doc/results/memory-pack-20261021/deployment-v2';OLD=SOURCE.parent
DEST='agent_doc/results/memory-pack-20261021/independent/deployment-v2/'
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,_bound,CHECKS
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(name):return {'path':DEST+name,'sha256':sha(RUN/name)}
contract=load(SOURCE/'contract.json');manifest,plan,proof=_snapshot(ROOT,contract)
bridge=load(RUN/'bridge.json');payloads=load(RUN/'payload-checks-v2.json')
if proof!=bridge['proof'] or payloads['status']!='pass':raise AssertionError('evidence mismatch')
old_manifest=load(OLD/'manifest.json');old_review=load(OLD/'independent/review-v1.json')
if sha(OLD/'manifest.json')!=old_review['manifest_sha256']:raise AssertionError('historical identity changed')
for criterion in old_review['checks'].values():
    for evidence in criterion['evidence']:_bound(ROOT,evidence)
for item in old_manifest['artifacts']['config']:
    if sha(ROOT/item['path'])!=item['sha256']:raise AssertionError('config bridge changed')
if any(row['exit_code'] for row in load(RUN/'runs.json')['commands']):raise AssertionError('new targeted execution failed')
limitations=[
 'Same bounded lossless opt-in transport and synthetic compact-payload scope as v1; no production/private memory, total model/session usage, cash, quality, latency, disk-space or whole-suite guarantee.',
 'Empty/singleton packets grow. Six fixed cases compare three formats; the producer actual Mailbox fixture compares only ordinary/new. Counts are complete final string bytes/o200k tokens, without model/tool/request/stdout wrappers.',
 'The v1 contract is historical and its wide live binding is stale after the concurrent dispatch update. Reuse is explicitly bridged through unchanged114 code files/config/tokenizer/238 corpus and preserved old two source files; scoped52 and250-property/legacy/invalid observations were not freshly rerun in v2.',
 'Fresh v2 producer dispatch5/strict24 and independent targeted12 passed; independent measurement and40-payload recount passed. No full repository suite was required or run. Existing platform/encoding/timeout failures remain historical; no timeout or threshold was relaxed.',
 'Mailbox timestamps may vary; equality/count checks apply within each current pair. Six deterministic cases matched v1 and both current runs byte-for-byte. Decoder 200000-character/256-container-depth limits and explicit refusal remain.',
 'Actual independent native actor /root/memory_index_verifier uses a new deployment-v2 review run. Future archive refs require original-byte copying and explicit host actor/hash authentication; JSON flags do not authenticate a callback or deploy runtime review.',
]
conclusion={'decision':'usable-with-scope','result_id':contract['result_id'], 'manifest_sha256':proof['manifest_sha256'],
 'run_id':'tok-mem-20261021-independent-deployment-v2','scope':contract['scope'],
 'changed_dependency_paths':bridge['strict_snapshot_changed_paths'],'historical_bridge':'approved and exact; v1 is not current live acceptance',
 'deterministic_case_changes':'none; v1, v2 producer and independent rerun byte-identical',
 'independent_payload_recounts':40,'fresh_independent_regressions':12,
 'cases':payloads['cases'],'actual_mailbox_counts':payloads['actual_mailbox_counts'],'limitations':limitations}
with (RUN/'conclusion-v2.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(conclusion,ensure_ascii=False,indent=2)+'\n')
checks={
 'implementation':{'verdict':'pass','reason':'Independently read new dispatch helper/default scope, path validation, exact two-file diff and production method. Measured Mailbox/basis/encoding/strict/counter code remains unchanged, with no new import-time execution. Complete current dependency bindings and exact historical bridge verified.',
  'evidence':[ref('verify_bridge.py'),ref('bridge.json'),ref('targeted.log')]},
 'reference_boundary':{'verdict':'pass','reason':'The v1 independent250 typed properties/250 legacy differentials/33 invalid and actual Mailbox gates are explicitly bridged only after unchanged relevant source/config/tokenizer/corpus and original evidence hashes. Fresh independent structural/legacy/dispatch12 and current payload reference restoration pass; no boundary criteria relaxed.',
  'evidence':[ref('bridge.json'),ref('targeted.log'),ref('check_payloads.py'),ref('payload-checks-v2.json')]},
 'data_integrity':{'verdict':'pass','reason':'All120 code/241 inputs and other new manifest artifacts matched; full566-file current strict snapshot matched, with only two declared delta paths. Original v1 manifest/raw/review and old two source bytes remain intact. All six cases, all three baselines and actual two-format Mailbox data are complete.',
  'evidence':[ref('bridge.json'),ref('payload-checks-v2.json'),ref('rerun-v2/inputs.json')]},
 'numerical_sanity':{'verdict':'pass','reason':'All40 current complete payloads independently recounted, including full rank-based BPE token sequence equality, byte/character totals, metric units/mappings and required short32 improvement. All deterministic payload/count records exactly match v1; grow controls retained.',
  'evidence':[ref('check_payloads.py'),ref('payload-checks-v2.json'),ref('conclusion-v2.json')]},
 'measurement_validity':{'verdict':'pass','reason':'Same full compact sorted JSON serialization and exact decoded values across pairs. Pinned tokenizer package/rank/pattern/special identity checked again; complete metadata/markers/column overhead counted. No end-to-end model usage or quality inference.',
  'evidence':[ref('payload-checks-v2.json'),ref('rerun-v2/environment.json'),ref('conclusion-v2.json')]},
 'reproducibility':{'verdict':'pass','reason':'Independent v2 measurement rerun reproduced all six deterministic cases byte-for-byte versus current producer and retained v1. Actual Mailbox paired values/counts verified independently. Fresh targeted12 and producer dispatch5/ext4strict24 passed; unchanged scoped v1 regressions/properties bridged with hashes rather than silently reused.',
  'evidence':[ref('run_independent.py'),ref('runs.json'),ref('rerun.log'),ref('targeted.log'),ref('rerun-v2/raw.json'),ref('bridge.json'),ref('payload-checks-v2.json')]}}
if set(checks)!=set(CHECKS) or _snapshot(ROOT,contract)[2]!=proof:raise AssertionError('domains or frozen bytes changed')
review={'schema_version':'experiment-validation/v1',**proof,
 'verifier':{'actor':'/root/memory_index_verifier','independent':True,
   'source':'Actual current native collaboration deployment-v2 verification task dispatched by /root; manual host must authenticate actor and exact bytes',
   'run_id':'tok-mem-20261021-independent-deployment-v2',
   'method':'Independent two-file delta and full hash audit, explicit historical-evidence bridge, new targeted regression/measurement, independent row oracle and full BPE/count reproduction'},
 'limitations':limitations,'checks':checks}
with (RUN/'review-v2.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
names=['verify_bridge.py','bridge.json','run_independent.py','runs.json','rerun.log','targeted.log',
 'prepare_checker.py','checker-preparation-attempt1.json','check_payloads.py','payload-checks-v2.json',
 'rerun-v2/inputs.json','rerun-v2/raw.json','rerun-v2/environment.json','rerun-v2/dependencies.json',
 'conclusion-v2.json','finalize-v2.py','review-v2.json']
archive={'source_root':RUN.relative_to(ROOT).as_posix(),'destination_root':DEST.rstrip('/'),
 'files':[{'relative_path':name,'sha256':ref(name)['sha256']} for name in names],
 'also_copy_this_manifest':'archive-files-v2.json','exclude':'strict-source.zip, tmp directories and all unlisted/root-owned files; do not overwrite v1 archive'}
with (RUN/'archive-files-v2.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(archive,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'decision':'usable-with-scope','review_sha256':ref('review-v2.json')['sha256'],
 'archive_list_sha256':ref('archive-files-v2.json')['sha256'],'files':len(names)+1,'manifest_sha256':proof['manifest_sha256']},indent=2))
