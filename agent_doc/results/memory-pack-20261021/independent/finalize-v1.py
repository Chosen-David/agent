"""Freeze independent six-domain review with future original-byte archive refs."""
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];RUN=Path(__file__).resolve().parent
SOURCE=ROOT/'agent_doc/results/memory-pack-20261021'
DEST='agent_doc/results/memory-pack-20261021/independent/'
sys.path.insert(0,str(ROOT))
from agent_runtime.result_validation import _snapshot,CHECKS
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def ref(name):return {'path':DEST+name,'sha256':hashlib.sha256((RUN/name).read_bytes()).hexdigest()}
contract=load(SOURCE/'contract.json');manifest,plan,proof=_snapshot(ROOT,contract)
if proof['manifest_sha256']!='2f6646f5ac9ef30a45c0db724dbd3d3e74bc0b6aced0b4b31a1cd044c4b50a81':raise AssertionError('manifest changed')
bindings=load(RUN/'bindings-v1.json');properties=load(RUN/'properties-v1.json');payloads=load(RUN/'payload-checks-v1.json')
if bindings['proof']!=proof or any(c['verdict']!='pass' for c in properties['checks']) or payloads['status']!='pass':raise AssertionError('independent evidence inconsistent')
limitations=[
    'Only lossless opt-in transport and six deterministic synthetic compact JSON payload comparisons plus a two-format synthetic actual Mailbox fixture are accepted; no private/user-memory or production workload was tested.',
    'Exact local o200k_base payload tokens and UTF-8 bytes exclude request/tool/model framing, history, reasoning, answers and total session usage; no cash, QA/quality, latency, disk-space or universal bug-free claim.',
    'Empty and singleton packets grow; no aggregate benefit or global-default change is justified. The actual producer Mailbox fixture compares JSON/new only; all three formats were tested in the six fixed cases and the independently built fixture.',
    'The decoder retains its 200000-character and 256-container-depth limits. New wrappers can make an otherwise shallower ordinary object exceed the bound; the new encoder explicitly refuses such packets rather than promising all arbitrary Python objects are encodable.',
    'Relevant native and Linux strict checks were run; full repository suite was not required or executed for this local change. Earlier producer GBK/fcntl and /mnt/c timeout failures remain recorded, with no relaxed threshold.',
    'Actual Mailbox timestamps may differ across independent runs; each current pair must restore exactly and be recounted independently. Six fixed cases did reproduce byte-for-byte.',
    'This review came from actual native collaboration actor /root/memory_index_verifier, not an unavailable preferred external model. Future archive references become valid only after original-byte copying and host identity/hash verification; JSON independent flags do not self-authenticate a provider or deploy ReviewSession.',
]
conclusion={'decision':'usable-with-scope','actor':'/root/memory_index_verifier','run_id':'tok-mem-20261021-independent-v1',
            'result_id':contract['result_id'],'scope':contract['scope'],'manifest_sha256':proof['manifest_sha256'],
            'cases':payloads['cases'],'actual_mailbox_counts':payloads['actual_mailbox_counts'],
            'independent_payload_recounts':43,'random_properties':250,'legacy_differentials':250,
            'invalid_cases':33,'independent_regression_passes':12,'optimized_regression_passes':7,
            'limitations':limitations}
with (RUN/'conclusion-v1.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(conclusion,ensure_ascii=False,indent=2)+'\n')
checks={
 'implementation':{'verdict':'pass','reason':'Read actual new/legacy encoders, strict decoder, immutable Mailbox request flow and basis hydration/budget paths. Complete values remain in payload, exact schemas reject unknown fields, trust gates precede encoding and final budgets follow it. Frozen real dependency bytes matched.',
                   'evidence':[ref('independent-candidate-static-v1.json'),ref('bindings-v1.json'),ref('properties-v1.json')]},
 'reference_boundary':{'verdict':'pass','reason':'Independent constructor and type-sensitive oracle passed 250 randomized payloads/250 legacy differentials, 33 strict/schema refusals, exact 200000-char and 256/257-depth boundaries. Independently built actual Mailbox checks closure, host/consumer caps, immutable requests, artifact changes and correction/reuse refusal.',
                       'evidence':[ref('check_properties.py'),ref('properties-v1.json'),ref('regressions-v1.log'),ref('optimized-v1.log')]},
 'data_integrity':{'verdict':'pass','reason':'All declared artifact hashes and additional 566-file strict snapshot checked. Six independently constructed input cases, all three baselines and the actual two-format Mailbox fixture are present; raw payloads and metric mapping are complete. No synthetic status label is interpreted as scientific evidence.',
                   'evidence':[ref('verify_bindings.py'),ref('bindings-v1.json'),ref('check_payloads.py'),ref('payload-checks-v1.json')]},
 'numerical_sanity':{'verdict':'pass','reason':'All43 payloads recounted to exact nonnegative integer byte/character/token totals and all36 manifest metric values/units checked. Complete independently implemented BPE token sequences match the pinned implementation. Short32 meets both baselines; empty/singleton regressions retained.',
                     'evidence':[ref('check_payloads.py'),ref('payload-checks-v1.json'),ref('conclusion-v1.json')]},
 'measurement_validity':{'verdict':'pass','reason':'Pinned tokenizer version/files, rank digest, pattern and specials verified. Each format restores the identical complete JSON values under declared compact sorted serialization; markers/column overhead included. Counts concern the payload string, not stdout framing/model/session accounting.',
                         'evidence':[ref('payload-checks-v1.json'),ref('rerun-v1/environment.json'),ref('conclusion-v1.json')]},
 'reproducibility':{'verdict':'pass','reason':'Independent subprocess rerun reproduces all six deterministic case records byte-for-byte; actual Mailbox pairs restore exactly and counts are independently verified despite timestamps. Independent necessary regressions12 and optimized7 passed; producer scoped52/strict24 logs and complete source bindings inspected. No full-suite claim.',
                    'evidence':[ref('run_independent.py'),ref('runs-v1.json'),ref('rerun-v1.log'),ref('rerun-v1/inputs.json'),ref('rerun-v1/raw.json'),ref('rerun-v1/environment.json'),ref('regressions-v1.log'),ref('optimized-v1.log'),ref('payload-checks-v1.json')]}}
if set(checks)!=set(CHECKS):raise AssertionError('six domains required')
review={'schema_version':'experiment-validation/v1',**proof,
        'verifier':{'actor':'/root/memory_index_verifier','independent':True,
                    'source':'Actual current native collaboration task dispatched by /root; manual host identity verification required',
                    'run_id':'tok-mem-20261021-independent-v1',
                    'method':'Independent source/hash audit, direct structural and typed randomized oracle, baseline differential, exact strict boundaries, self-built Mailbox gates, pinned tokenizer/independent BPE recount and separate measurement/regression reruns'},
        'limitations':limitations,'checks':checks}
if _snapshot(ROOT,contract)[2]!=proof:raise AssertionError('frozen inputs changed during review')
with (RUN/'review-v1.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
names=['independent-plan-prior-search.json','independent-plan-review.json','independent-candidate-static-v1.json',
       'verify_bindings.py','bindings-v1.json','run_independent.py','runs-v1.json','rerun-v1.log','regressions-v1.log','optimized-v1.log',
       'rerun-v1/inputs.json','rerun-v1/raw.json','rerun-v1/environment.json','rerun-v1/dependencies.json',
       'check_properties.py','properties-v1.json','check_payloads.py','payload-checks-v1.json',
       'conclusion-v1.json','finalize-v1.py','review-v1.json']
archive={'source_root':RUN.relative_to(ROOT).as_posix(),'destination_root':DEST.rstrip('/'),
         'files':[{'relative_path':n,'sha256':ref(n)['sha256']} for n in names],
         'also_copy_this_manifest':'archive-files-v1.json',
         'exclude':'Root-owned strict-source.zip, refresh-paths files, tmp directories and any unlisted file; no recursive-copy assumption'}
with (RUN/'archive-files-v1.json').open('x',encoding='utf-8') as stream:stream.write(json.dumps(archive,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'decision':'usable-with-scope','review_sha256':ref('review-v1.json')['sha256'],
                  'archive_list_sha256':ref('archive-files-v1.json')['sha256'],'files':len(names)+1},indent=2))
