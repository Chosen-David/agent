# Independent plan review — COMMUNICATION-UTF8-01 v1

Decision: approve for the bounded local regression branch described below. No test, probe, model, benchmark or candidate execution was performed in this review. This is the independent agent's actual review record, not a fabricated protected-runtime authentication receipt or user permission.

## Frozen object

Project: `/workspace/scratch/6416f20dc59b/agent-run-1303`; actual HEAD `a4ce7568e5801584330f4446982c5fd6d9cea6a6`.

| Object | SHA-256 |
|---|---|
| `.agent-runs/communication-utf8-0703/plan.md` | `2563788e16d9ac81d0bbeef9d67bde5380b5138f5c2114d597fe44f97876f853` |
| proposed test | `d071609898540a32edc3885e3a479933988d3f6715e31cb2fa5d65964469fd74` |
| frozen runner | `1e495e0077f2e68c3807266878845c67f774e05338986be54bb3fa85f50f5160` |
| proposed communication source | `6ba4e5b12e92e3fb70c7ad21a105d9fc33b6083e47ecf3eb957a0eea5e6afd59` |
| current communication source | `6150b7bf94e72bb450ce05efc936cd71ade776f2492f812323190100b460f02f` |
| serializer | `2606666cf723af13cb2b8a4a0934848f233ffb16c50728fc4a43da01ff26453d` |
| reused fixture | `232f4bad46429e8408c902ff486bb8023fde7b0715f9b233cb3a522b1293f442` |
| current native CI | `804dfec5af0adf236c3b175f84070a60ad02b2024f55294e191643cb1223cbd4` |
| current SYSTEM-99 detail | `615918c9bac298c235074328c7cfc0ffd9c0140fb9e700d51fcec08c87e9cc57` |

Read AGENTS, review-main, dual-main, project-document, result-validation, result-reuse and knowledge-access guidance; canonical TASK and relevant SYSTEM-99 stable sections/progress; guide contents; actual communication/serializer/fixture, proposed test/runner/source, CI, prior-results JSON, token10-final/02 configs and final replay's explicit UTF-8 environment. GUIDE.md is empty (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`); README describes the human-only boundary. No guide content was changed. No external/theoretical knowledge is necessary for this narrowly local Python/SQLite contract review; project source and workflow evidence supply the applicable facts.

## Full review

**Intent — pass.** The current module is a distinct native entry point from the five context-wire and two validation CLI repairs recorded in SYSTEM-99. It emits non-ASCII JSON without calling the existing output configurator. The proposed production diff is exactly the import extension and one call at main entry; it preserves argument parsing, all command dispatch, exception/exit protocol, serializers, SQLite behavior and schema. This is a plausible static defect candidate, not yet a runtime reproduction. Version46 is to be written only after this review. The same SYSTEM-99 batch remains open; this review grants no new paper credit or completion claim.

**Guide — pass.** Empty GUIDE.md adds no substantive task constraints; the human-only directory protection remains binding. Parent reports current user authorization for in-place work and ordinary main push. No proposal writes guide, foreign zip, old evidence or SGLang. The owner/path split and SYSTEM-99 single-writer rule are retained. This review authorizes neither new resources nor a different goal.

**Assumptions — pass.** Actual CLI subprocesses inherit forced `PYTHONUTF8=0` and `PYTHONIOENCODING=cp936/ascii`; bytes are captured and decoded as UTF-8 only in the oracle. The existing helper reconfigures stdout and stderr once, matching this entry's use of text streams. Unicode exists in an event identifier, summary/action, receipt reason, artifact path and manifest criterion. The reused fixture's artifact reference is shared with the record, so changing its path precedes re-saving/re-hashing the manifest; its source artifact bytes remain valid. Reviewer ACK and writer pending delivery remain distinct. The test's source-location cwd resolves the repository root only when the test is installed at `tests/test_communication_output.py`, as planned. The runner explicitly prepends real `root/tests` and root to PYTHONPATH and names the installed test module; it does not run the private proposal copy. CI unittest discovery also imports the fixture from real tests.

**Prior results — pass.** Actual search JSON contains 299 scanned, partial=true and 25 errors; it is not exhaustive absence evidence. Five candidate metadata records do not establish the new forced-legacy-stream behavior or consumer-state invariant. token10-final replay explicitly forces UTF-8, and token10-02 config concerns communication compact/token accounting. No empirical result is reused or promoted. The plan's final paragraph accurately preserves these limits.

**Acceptance — pass.** Three new test methods exercise 28 native CLI subprocesses: 16 read/index cases, eight consume/context cases and four Unicode-error cases across two encodings and two layouts. Success requires exit0, empty stderr, UTF-8-decodable complete JSON; inbox/read-pending compare complete fixture-derived envelopes, status preserves both receipts, and inbox-index is an ASCII metadata control. Before/after logical SQLite dumps and source-JSON hashes fence read side effects. Consume compares the complete manifest; context compares its complete parsed basis payload with literal expected fields, while checking the no-token/no-selection defaults. Both check persisted record/request before decoding stdout, unchanged source JSON and all receipt states. Thus a rendering failure after basis persistence is retained rather than hidden. Context wrapper metadata is not a new complete byte-for-byte oracle; existing handoff regressions cover the surrounding API, and this acceptance is restricted to the tested transport/payload and state invariants. Unicode duplicate-key errors require the original error object, exit1 and empty stderr, with unchanged DB/files. JSON equality deliberately permits native newline/layout differences; the plan does not claim exact LF bytes or new budgets. Baseline failures must be retained and attributable to encoding; fixture/other failures cannot be called accepted reproduction.

The exact eleven-module runner is a suitable bounded regression set for this two-line production fix. A baseline pass would disprove the claimed reproduced failure under that environment; preserve it and report honestly. A fixed pass plus independently reviewed raw logs/source and the later independent fixed invocation is required before claiming this branch accepted. Four native CI jobs remain separately pending until actually read back. No global, model-quality, performance, deployment or completed-round conclusion follows.

**Risk — pass.** Low-impact reversible change; no schema, budgets, ACK semantics, token counters, dependencies or duplicate serializer added. The test isolates roots/DBs and checks persisted mutation separately from receipts. Existing rejected/exhausted full-suite, context-wire, PID, alias, role and model gates remain unchanged. Any discovered fixture defect requires preserved failure and versioned review inside the original branch budget, rather than silent oracle relaxation or another label.

**Resources — pass.** One producer baseline, one producer fixed invocation and one independent fixed invocation, each label once; each runner invocation <=120 seconds, each new CLI child <=15 seconds, one shared 600-second elapsed branch budget beginning at the baseline. No tests have consumed that budget during this review. Runner logs/metas are exclusive-label outputs, preserve combined raw output and source/test/CI hashes, and compare pre/post content. Human supervision must preserve budget.json/logs rather than delete/reseed them. No retries, full-suite reruns, paid models, GPU, services or extra monitors are authorized here. Existing native CI matrix is Ubuntu/Windows × Python3.10/3.12; exactly one new test-discovery step is the reviewed intended CI change, with source/CI diff to be checked again during result review.

## Compact verdict

```json
{
  "decision": "approve",
  "summary": "Approve the frozen distinct communication CLI UTF-8 regression branch, pending actual baseline, fixed execution, independent code/raw-result review and the separately requested independent fixed run; existing exhausted gates stay closed.",
  "checks": {
    "intent": "pass",
    "guide": "pass",
    "assumptions": "pass",
    "prior_results": "pass",
    "acceptance": "pass",
    "risk": "pass",
    "resources": "pass"
  },
  "findings": []
}
```
