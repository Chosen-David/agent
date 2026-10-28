# USAGE-SHAPE-01 independent fixed-result review

Verdict: **usable-with-scope / accept**. Blocking findings: none within the approved consumed-container repair and frozen offline regression scope. This is fixed-result acceptance, not a third plan review. SYSTEM-99 remains open; native five-job CI and ordinary publication readback remain separate pending evidence.

I reviewed the actual parser/workflow diff, frozen v2 tests and controller, baseline/fixed execution metadata and original raw outputs, and independently checked all fixed-input packet file hashes. I then executed exactly once:

`python -B .agent-runs/usage-shape-0858/capture.py independent`

The controller ran the exact frozen four-module unittest argv and then the single sync-reference check. Original independent stderr reports all **34 methods passing, zero failures/errors/skips**. Both commands exit 0 without timeout. I read the resulting original stderr and metadata, recomputed raw file hashes from disk, and compared every actual recorded source hash to fixed metadata: all match. Empty stdout and empty sync streams are actual zero-byte files. No backend/model/network/old probe/full-suite execution occurred. The inherited prompt-context local CLI fixture is an offline repository test, not a model backend invocation.

## Baseline and result integrity

The baseline original stderr reports 34 methods and 130 failed subcases across two new rejection methods. Independent classification of its actual assertion messages gives 112 uncontrolled AttributeError mismatches, 6 uncontrolled TypeError mismatches and 12 malformed-input acceptances. Both new valid-output controls pass in baseline. These are subcases of a bounded error-handling regression, not 130 independent production defects or an empirical error-rate estimate.

Fixed metadata and raw stderr report 34 passing methods and sync success. Tests have the same frozen SHA before baseline, fixed and independent execution. The actual fixed-input packet SHA-256 is `1102c046f998dbf919d77a2bc72a0918b719be8a9685bc3e8ca06ab72b32f331`; every declared source/raw reference matches its on-disk bytes. Baseline and fixed raw failures/results remain preserved.

## Independent code and oracle review

- `_usage_object` and `_usage_items` have one implementation in token_usage and are reused by turn_usage. Both native parsers guard event, params, turn, item and outer tokenUsage before their consumed object access. Final last/total buckets are guarded before token-field access. Terminal items are a list whose entire membership is checked as objects before semantic item iteration. JSONL item access uses the same object guard.
- Outer tokenUsage containers in earlier native snapshots are validated on arrival, preventing the previously accepted malformed earlier outer snapshot from being hidden by a valid final snapshot. Nested last/total buckets and counter arithmetic are still evaluated on the final snapshot only; acceptance does not certify deep semantic validation of every earlier snapshot.
- The changes do not default malformed containers to zero or empty objects, catch unrelated AttributeError, change counters, sum snapshots, subtract cache, loosen strict integer checks, relax identity/order/no-tool guards or rewrite output dictionaries. Valid zero, cache/reasoning subset bounds, fresh cumulative equality and current inherited-history behavior retain their established semantics.
- New expected dictionaries compare all fields, including exact source/scope strings. Native valid fixtures pass the same retained object later compared for preservation. Malformed JSON-roundtrip fixtures compare the actual parsed input in finally. Existing identity and mutation controls, counter type/arithmetic rejection, tools, order, duplicate terminal and corrupt JSON controls also pass independently.
- Optional omitted terminal items and an unrelated native heartbeat remain accepted. Tuple item sequences are outside the explicitly claimed native JSON-array contract. Object count fields and deeper schemas are outside this container-only change except for preexisting counter validation.
- The actual CI diff adds only one new module invocation to the four-job Linux/Windows matrix and one to the existing macOS job. Actions, existing commands, permissions and timeouts are unchanged. This source inspection establishes intended coverage, not actual native CI execution.

## Bound identities and raw evidence

| Artifact | Actual SHA-256 |
| --- | --- |
| Approved `plan-v2.json` | `05a58706460000ab71b21f380c2609fc392cb99ad134f894b59540d1344a0c95` |
| Approved `capture.py` | `aa072efee5cc79a390572ea28197751b9c2166ca94978fb187f6acad3738d4cb` |
| `agent_runtime/token_usage.py` | `e55a31b5f75328eb39b2b60bbf3e3aa9ecf3cfcee0e54d636df194b595944b7d` |
| `agent_runtime/turn_usage.py` | `a7e6ab3a76fae2f480d700f3705fc4e44a0537309ec09b6bf450c283e6e1dce2` |
| `tests/test_usage_shapes.py` | `452432ce841997893e3c7185513d92e5f68576f6229b6e521ac58bef108b6af0` |
| `.github/workflows/portable-install.yml` | `14f5069b2f3489d140a84351644302cdfeafcfb9f8bf68ca4160549db663d741` |
| `baseline/execution.json` | `10b2559122ec4cbca98fb1ef12e98aee07d428357a4021a240fb55b751aeb9c0` |
| `baseline/unit.stderr` | `382fbe1526fdab7ad8be39206b9891b33c5f30edb19bf839775b12373267e2d3` |
| `fixed/execution.json` | `f412c11c4962a60a573b6c649c5600b7c8e57005a3dcac5190cc7663c41dd19e` |
| `fixed/unit.stderr` | `147f86fc9a29f94473e1ebfcc497767fc464be582a568007f0dbb6cef26ab5ba` |
| `independent/execution.json` | `3fb50ce83a137321dd6396702367aa43c6d07cc9175c511c19b09bba7ad3d84a` |
| `independent/unit.stderr` (5328 bytes) | `386415d4de0c3e746e58eaa9b4ca815f519ced988e86b7f0f9dda4568fa5a412` |
| All three unit stdout files and fixed/independent sync stdout/stderr (each zero bytes) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

Other fixed/independent source identities, all directly matched to actual bytes and each other: AGENTS `97f35fc8fb91097a34380c12a9581936f8a78c6f9c10a05183c84511645738ed`; TASK `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f`; empty GUIDE `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`; guide README `f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261`; test_turn_usage `dd6456ab0bebaf8ae5c70ffa76ad7de997d3e39f5bbae9d0f220d20c56897955`; test_usage_identity `1935a2277f2f2e6dfef26af368bee7cc161843161d848581520af43337af16f9`; test_prompt_context `53e0e26fe1cd9fd21a99ef1b50e66ae07688227792c84e30c9ac633bfac47fcc`. Stable SYSTEM-99 Version54 remains bound by the approved controller's prefix check.

The resulting read budget is plan reviews 2/2 and baseline/fixed/independent each 1/1; publication remains 0/1. Original shared deadline 1793150566.9051683 and consumed older gates remain unchanged. No retry or allowance reset is authorized. This file plus controller-owned independent output/budget are my only writes in this phase.

The acceptance supports controlled rejection and non-regression for these offline fixtures and inspected paths only. It is not provider/ReviewSession certification, runtime adapter deployment, a universal correctness guarantee, token/cost/performance measurement or whole-batch completion.
