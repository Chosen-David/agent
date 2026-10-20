"""Freeze this independent manual review; schema checks do not authenticate a host."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from agent_runtime.result_validation import _snapshot, _review

def ref(name):
    path = OUT / name
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
raw = json.loads((OUT / 'raw-native-v3.json').read_text(encoding='utf-8'))
rerun = json.loads((OUT / 'independent-raw-native-v3-final.json').read_text(encoding='utf-8'))
table = '\n'.join(f"| {r['shape']} | {r['read_entries']} | {r['baseline_bytes']} → {r['candidate_bytes']} | {r['baseline_tokens']} → {r['candidate_tokens']} |" for r in raw['observations'])
document = f'''# MEM-INDEX-96 independent result review

Decision: **usable-with-scope** for both final native-v3 contracts. The evidence supports publication of the bounded CLI navigation/storage behavior and the six synthetic UTF-8/native-newline payload comparisons below. It does not support a green whole-repository regression claim or completion of the continuing optimization programme.

Reviewer: `/root/memory_index_verifier`, an independently launched native collaboration context; producer: `/root`. This is the actually executed manual `verify_experiment_result` review, not a deployed ReviewSession, scheduler, or self-authenticating runtime receipt. The parent host must verify this context identity and fixed review bytes before injecting its trusted callback.

## Code and semantic checks

Read the actual `_index_json`, `MemoryLedger.index`, `storage`, inherited `list`, `_read_entry`, `_connect`, `check`/`_walk`, and CLI dispatch; also reviewed the test resource-ownership fix and workflow text. Default list/check/history output remains on the existing path. Index omits only content, preserves metadata, binds the project/filter/full selected entries, refuses changed snapshots, returns complete entries under the full native character budget, and conveys no evidence acceptance. Storage performs observation SQL; it neither initializes a missing ledger nor compacts/deletes evidence.

The independent SQL oracle exercised 180 status/scope/page-limit combinations with deterministic ties, exact filtering and complete hash/metadata comparison, plus body/source/kind/evidence/time/scope/dependency/document changes, legacy schema and a navigation-vs-stale-ancestry trust control. Actual binary subprocess exact-cap checks passed after the native-newline repair. The independently run native focused suite passed 45 tests; optimized Python passed the 11 new tests. These counts are separate runs, not a claim of 56 unique tests.

WAL observations explicitly found SHM bytes changing with a live writer while main DB/WAL contents stayed unchanged in the fixture. The accepted claim is read-only SQL/business state observation, not filesystem immutability or atomic disk accounting. This limitation is reflected in the workflow.

## Frozen data and independent reconstruction

Both final manifests, all declared artifact hashes, configurations, environment files, validation protocol and metric-unit/value mappings were checked with `_snapshot` and direct semantic checks. Implementation SHA256 is `adfb149d706965ad35220b3431b9acf1f0828238ed78cbd787f01e9ac900ea19`; final `project_docs.py` SHA256 is `a2712d093f4012350f6654401a15aa1d22e442d6993482025996b63183477a57`.

From the fixed fixture fields and each recorded literal project root, an independent constructor reproduced all 57 producer response strings, including pretty JSON layout, compact index packets, CRLF and complete body replies. Every recorded SHA256, byte count, character count and token count matched. A separately implemented rank-driven byte-pair-merging reference matched the full compiled tokenizer token sequence for every response. The pinned tokenizer version, rank table, pattern, specials, package files and cache hashes were checked.

The inspected native measurement was independently rerun into `independent-raw-native-v3-final.json` without overwriting producer data. Its 57 captures were again independently reconstructed and fully matched. All byte counts and six scenario sums matched the producer. Token counts can differ between runs because the temporary root's literal text and induced snapshot hashes tokenize differently even at equal path length; each run's exact counts were reconstructed using its own root. This is explained variation, not unexplained measurement disagreement.

| Body shape | Recalled bodies | Full list → index + reads, bytes | Full list → index + reads, o200k tokens |
| --- | ---: | ---: | ---: |
{table}

Every page and every declared required read is included. Short entries and all-body reads cost more; these negative controls remain part of the accepted data. No timing, total model/session tokens, service cached tokens, billing, cash, model quality, TTFT, actual KV-cache or CPU-speed claim follows.

## Regression and environment limits

The producer's full isolated WSL Python 3.14.4 run executed 1357 tests and ended with **6 failures, 1 import error, 12 skipped**. It did not pass. Independent extraction of the Git baseline and execution of `tests.test_result_search_depth` reproduced the same 6 failures among 7 tests in both baseline and current code. The relevant result-store/test/CLI files are unchanged; the independent environment probe demonstrated that this Python build accepts the 10000-level JSON input where those tests expect RecursionError. This is a demonstrated baseline/environment boundary, not evidence of a new ledger regression.

The WSL import error and reader-suite failure were missing `fitz`. In the prepared native Python 3.12/PyMuPDF environment, this reviewer independently reran reader core (2 tests) and app (3 tests) with `PYTHONUTF8=1`; both passed. The earlier default-GBK native core failure is retained. A bounded WSL Python 3.12 environment attempt stopped when downloading uv exceeded 90 seconds; there is no clean full-suite Python 3.12 result. The 12 skipped checks remain unverified.

The final isolated WSL checkout named in the producer receipt is no longer readable. Its execution logs and source-hash receipt are retained, but the missing directory is an archival/replay limitation. Independent targeted checks used the current frozen code and a separately extracted baseline; they do not claim to restore that missing checkout.

These limitations prevent a claim that the whole repository passes. They do not invalidate the directly inspected ledger paths or exactly reconstructed payload data: the scoped semantic tests, independent properties and all applicable measurement/reproduction checks passed, while the observed broad-suite failures were independently isolated outside the changed feature. Publication is acceptable only with this explicit scope and these limitations.

## Retained failures and provenance limits

LF-only v1/v2 data are superseded for the actual native-wire claim. The first actual Windows cap check observed 811 emitted characters against a cap of 810; the implementation now reserves `len(os.linesep)` and exact binary-pipe boundaries pass. Initial test-owned SQLite cleanup/ResourceWarning failures and this reviewer's omitted-commit fixture mistakes remain recorded; the latter were harness errors, not extra implementation bugs.

Earlier v3 draft raw observations were retained, but their original manifest/contract bytes were not completely archived before re-freezing. Their old bindings are stale, no acceptance is inherited, and reconstructed historical manifests would not be original evidence. This acceptance binds only the current final manifests and exact artifact bytes identified by the two JSON reviews.

Evidence is in this run's `independent-*` scripts, oracle/boundary/binding records, subprocess logs and reader checks; the JSON reviews bind the precise evidence hashes. Hash matching identifies files and does not itself prove scientific applicability or authenticate the reviewer. No absolute bug-free, runtime integration or continuing-parent-task completion claim is made.
'''
with (OUT / 'independent-review.md').open('x', encoding='utf-8', newline='\n') as stream:
    stream.write(document)

checks = {
    'implementation': {
        'verdict': 'pass',
        'reason': 'Actual ledger and CLI paths inspected; defaults retained; full selected snapshot binding, complete native-budget entries and observation-only SQL verified. WAL/SHM side effects explicitly scoped.',
        'evidence': [ref('independent-review.md'), ref('independent-boundary-v3-pre-freeze.json'), ref('independent_check.py')]},
    'reference_boundary': {
        'verdict': 'pass',
        'reason': 'Independent direct-SQL oracle passed 180 pagination/filter combinations and mutation/legacy/trust boundaries; actual binary pipe cap exactness and ordinary/optimized focused tests passed.',
        'evidence': [ref('independent-boundary-v3-pre-freeze.json'), ref('independent-tests-v3.json'), ref('independent-tests-v3-0.log'), ref('independent-tests-v3-1.log')]},
    'data_integrity': {
        'verdict': 'pass',
        'reason': 'Current contracts/manifests, all declared artifacts, config/environment and metric mappings bound; all 57 original captures independently reconstructed to identical hashes/counts. Superseded drafts are not reused.',
        'evidence': [ref('independent-bindings-v3-final.json'), ref('independent-oracle-raw-native-v3-final.json'), ref('independent_bindings.py')]},
    'numerical_sanity': {
        'verdict': 'pass',
        'reason': 'Exact nonnegative integer byte/token counts, all sums and signed saving fractions recalculated; all short/full-read regressions retained. Independent BPE reproduced every full token sequence.',
        'evidence': [ref('independent-oracle-raw-native-v3-final.json'), ref('independent_native_oracle.py')]},
    'measurement_validity': {
        'verdict': 'pass',
        'reason': 'Actual binary subprocess stdout preserves UTF-8 and native CRLF; all pages and needed body responses included; tokenizer identity verified. Counts describe response payloads only, with no total-model/latency/quality claim.',
        'evidence': [ref('independent-oracle-raw-native-v3-final.json'), ref('independent-review.md'), ref('independent-pipe-v3-pre-freeze.json')]},
    'reproducibility': {
        'verdict': 'pass',
        'reason': 'Independent native rerun and 57-capture reconstruction passed; byte counts exact, path/digest-dependent token variation fully reconstructed. Focused45/-O11 and independent reader2+app3 passed. Full WSL1357 failed6/error1/skipped12; same depth failures reproduced in baseline, missing fitz handled in native reader checks. No clean whole-suite claim; bounded 3.12 environment retry timed out.',
        'evidence': [ref('independent-raw-native-v3-final.json'), ref('independent-oracle-independent-raw-native-v3-final.json'),
                     ref('independent-tests-v3.json'), ref('independent-reader-checks.json'), ref('independent-reader-0.log'), ref('independent-reader-1.log'),
                     ref('independent-regression-diagnostic.json'), ref('independent-regression-baseline.log'), ref('independent-regression-candidate.log'),
                     ref('independent-regression-environment.log'), ref('final-checks.json'), ref('final-all-wsl.log'), ref('final-reader-wsl.log'), ref('environment-retry.json')]},
}
limitations = [
    'Only final native-v3 synthetic CLI functionality and UTF-8/native-newline response payload bytes/local o200k_base text tokens are usable; no real user-memory workload or whole-repository correctness guarantee.',
    'All short-body and full-read controls can regress; temporary root text and induced snapshot hashes alter token counts even when path length is unchanged.',
    'No total model/session/request/tool/history/reasoning/output accounting, cash, quality, timing, CPU speed, actual KV-cache or serving-model tokenizer claim.',
    'Full WSL Python3.14.4 run failed6/error1/skipped12 among1357 tests. Baseline reproduced the six depth-expectation failures; native UTF8 reader core2/app3 passed after isolated dependency setup. No clean full Python3.12 run; uv download stopped at90seconds. Skips remain unverified.',
    'Storage is read-only SQL/business-state observation; live WAL reader SHM changes were observed and physical disk usage is not an atomic snapshot.',
    'Producer temporary full-regression checkout is no longer readable; retained logs/hash receipt do not restore it. Earlier v3 draft manifest/contract original bytes were incompletely archived; their raw observations and old independent bindings are historical and are not accepted/reused.',
    'This is an actual independent native collaboration review. JSON identity/independent flags do not authenticate a runtime; the parent host must verify context and fixed hashes before trusted injection. No ReviewSession/background deployment or continuing parent-task completion is claimed.',
]
receipts = {}
for suffix in ('bytes', 'tokens'):
    contract = json.loads((OUT / f'contract-native-v3-{suffix}.json').read_text(encoding='utf-8'))
    manifest, plan, proof = _snapshot(ROOT, contract)
    review = {'schema_version': 'experiment-validation/v1', **proof,
              'verifier': {'actor': '/root/memory_index_verifier', 'independent': True,
                           'source': 'Actual independent native collaboration context launched by /root; manual host workflow, not runtime self-authentication',
                           'run_id': 'memory-index96-independent-native-v3-20261020',
                           'method': 'Independent source review, direct-SQL/property oracle, binary pipe/WAL checks, exact wire reconstruction with independent BPE, frozen artifact checks and native measurement/reader reruns; baseline regression isolation'},
              'limitations': limitations, 'checks': checks}
    statuses, evidence = _review(ROOT, manifest, plan, proof, review)
    if statuses != ['pass'] * 6:
        raise AssertionError(statuses)
    if _snapshot(ROOT, contract)[2] != proof:
        raise AssertionError('Frozen inputs changed during review')
    name = f'independent-review-native-v3-{suffix}.json'
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
    receipts[suffix] = ref(name)
print(json.dumps(receipts, indent=2))
