# GATEWAY-CONTRACT-01 final independent result review

Verdict: ACCEPT — usable-with-scope. The candidate-1 redaction finding is repaired and independently revalidated. This is an actual native separate-context source/result review, not an authenticated ReviewSession receipt or publication authorization.

## Scope, history and implementation

Reviewed approved Plan v1, plan-review.md, actual scripts/discover_models.py, setup install/check/doctor paths, model_routing.validate_inventory/resolve, run_role.py consumer, docs/role_models.md and both test files. Base: 44110e54e82f66b3bff24450e026e4aea46934f9. Plan stable-prefix SHA256: `1e9da3a515780d9944020bfaefe16633154723b51799404a890aa848fb5d1b68`. GUIDE.md is empty and was not written. No production/test/TASK files were changed by the reviewer.

New ID-only discoveries remain inactive (`available:false`, empty capabilities). A gateway listing therefore cannot establish same-interface authentication, tools or vision; native is only an inactive schema placeholder. Explicit host inventories are validated without overriding availability, capabilities or transport. Name classifications are clearly preview hints and do not influence routing. Both unchanged resolver and installed consumer preserve default fallback for unknown entries and select the original exact policy candidate for explicit host declarations.

The response read is bounded at 1 MiB+1 before strict_json; malformed UTF8, duplicate/nonfinite JSON, bad envelope or nonstring/empty IDs are rejected rather than silently filtered. Direct build_inventory malformed IDs cannot reach string methods. Controlled CLI failures do not produce traceback for covered inputs. Tmux retains its exact source-file command, five seconds and no retry; missing executable, timeout and nonzero status enter warnings, not fixes, while preserving the remaining health report. Only success claims Applied. Existing needs_restart semantics are deliberately unchanged.

Candidate-1 REVISE is preserved in result-review-v1.md and reviewer-invalid-url.log. It independently exposed a synthetic password echo from Request-construction ValueError before the catch block. The repaired candidate moves Request construction/add_header into the protected block and converts ValueError/HTTPException to a generic RuntimeError without raw URL/header/exception text. Original failure evidence was retained; the old acceptance was not carried over to this changed function body. The earlier source-only adjustment removed misleading comments and corrected _classify's return annotation; final execution below is on the ultimate hash including the actual redaction repair.

## Independently executed final checks

- `python -m unittest discover -s tests -p test_gateway_contract.py -v`: 15/15 pass, reviewer-v2-normal.log.
- Same command under `python -O`: 15/15 pass, reviewer-v2-optimized.log. unittest assertions remain active with optimization.
- Combined discovery of test_setup.py, test_setup_portable.py, test_model_discovery_setup.py, test_setup_doctor.py, test_install_recovery.py, test_model_routing.py, test_install_profiles.py and test_role_process.py: 73/73 pass, reviewer-v2-integration.log.
- Independently loaded git-show baseline setup.py with the actual unchanged resource root, loaded old discover_models.py and used that actual old script for CLI cases. Final 15 tests reproduce failures=17/errors=12, reviewer-v2-baseline.log. The earlier 13-case baseline had 17 failures/9 errors. The three added old-source errors are unhandled URL/header validation exceptions; they differ from failure counts on intermediate candidate 1, whose main caught and printed some ValueErrors. Subtest counts are not distinct production defect counts.
- reviewer_v2_probe.py reruns original actual discovery.main -> HTTP fixture -> written inventory -> actual setup.install -> actual run_role.py --dry-run. Unknown listing selects default fallback; explicit host inventory selects the original opus model with no explicit inventory supplied to the consumer. No model executes. Ordinary reinstall retains the explicitly provided native host snapshot.
- The actual doctor CLI against an owned fake tmux executable exiting 7 returns configured JSON, a warning and empty fixes while preserving a healthy installation. No tmux server is started.
- The actual discovery CLI with a schemeless synthetic credential-bearing URL returns controlled nonzero with no password/whole URL/traceback. Additional in-process main probes exercise real stdlib formatting for bad port, URL control characters and authorization-header newline, with socket/connect forbidden: each rejects before connection and emits a generic diagnostic without the synthetic sentinels. HTTPError/URLError/TimeoutError fixtures likewise do not echo synthetic auth token, URL userinfo password or raw server reason.
- Exactly 1 MiB of valid padded JSON is accepted; +1 byte is rejected. Direct malformed-ID inputs produce ValueError. Full additional probe output: reviewer-v2-probes.log.
- Source/task `git diff --check` passes at review time. Source hashes below match the final reviewed objects.

The existing doctor test correction is appropriate: the nonzero branch now checks warnings, success checks fixes_applied, and the opposite list must be empty. Exact subprocess arguments and timeout assertions remain. No failure assertion was merely removed to obtain a pass.

## Evidence integrity and boundaries

I reread the complete final independent normal/optimized/integration logs after execution: 2467/2467/11165 bytes, with 15/15/73-test summaries and OK. Producer original failure logs and candidate logs were inspected; independent complete records support the final count. The earlier unrelated partial-log observation is not assumed resolved or reused as evidence. Initial REVISE, raw synthetic leakage probe, initial baseline and all later records remain intact.

No live gateway/model/authentication/tmux server, native Windows, throughput, task quality, provider cost, automatic remediation of all older guessed inventories or SYSTEM99 completion is accepted. `available:false` means unverified/inactive here, not experimentally disproven access. Existing stored snapshot provenance remains unknown and is not mass-rewritten; ordinary preservation and explicit host refresh are the tested paths, while existing doctor refresh behavior remains its own operation. Per-role capabilities and model availability still need actual host verification. Existing needs_restart semantics, multi-file installer failure/concurrency handling and other declared SYSTEM99 gaps remain open. Publication still needs the main agent's fresh fetch, exact-file/nonforce update and remote SHA/tree/content readback.

## Final source hashes

| File | SHA256 |
| --- | --- |
| setup.py | 236746f8a816921ee841a3a1017a78dd4992ebcd16c1ee6a8a04094bc084eb77 |
| scripts/discover_models.py | e5845b0a14392d9045edc6ddf5a9f527c362c679e1c9d503107216516dd84b98 |
| tests/test_gateway_contract.py | dc42d025864508acdeba907b9bf2b2bb96182bcb140a4e5cb1b49f3d564d7bc8 |
| tests/test_setup_doctor.py | ae16ed1328e5092a1d59c8696710bcc750bbcf62d02e13519000c253274339c6 |
| docs/role_models.md | 792caaa79c1bc03516cfea0329a3688a2db684a335276c8442a945a03c3c7085 |

## Final raw-log hashes

- reviewer-v2-normal.log: `d07873d12f98261e90916143885660879fa94104801eeafea2f963765757b2b1`
- reviewer-v2-optimized.log: `89a9200d7c239100a4f96961b3400d7313342c8d98921182a67fdaae773dd2b0`
- reviewer-v2-integration.log: `f203f3a407d02e1f273c6849d6b5630483af8f64aa5ce9fb340d51b62114c717`
- reviewer-v2-baseline.log: `8165c65ae698abdd478e52c02bffa66d1506c0944e1ec37d5bba4a522678d44c`
- reviewer-v2-probes.log: `d1117165a5b251f31cdc16131abaa1492af68c14fab1c21d1e7b215aa9294f7a`
