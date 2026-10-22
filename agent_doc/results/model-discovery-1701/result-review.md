# MODEL-DISCOVERY-02 independent result review

Verdict: **ACCEPT — usable-with-scope**. No blocking findings for the bounded helper and mocked installer consumer change.

## Identity and authorization boundary

Reviewed candidate `/workspace/scratch/6416f20dc59b/agent-model-discovery-1701`, baseline `d8abd23e4626a5d5ee43b9a6cf77388b86da842e`, detail Plan Version 1. Stable prefix before `## Progress` SHA-256 is `a573246cfb18a6c51a9a92d33ce351d08d19646031b689380ead9b99eabb25e3`. Read AGENTS.md, decision review, project document workflow, result-validation lightweight-regression boundary, current task Plan, independent plan review and all four producer logs. Source diff in setup.py is confined to `_auto_discover_inventory`; the new test file contains seven regression tests. TASK/detail changes are task bookkeeping, not additional behavior changes.

This is an independent source and ordinary correctness review with fresh local execution. It is not a performance experiment, authenticated trusted-runtime receipt, publication authorization, live model validation or universal correctness guarantee. No tracked files were modified by this reviewer; output is confined to the assigned run directory.

## Independent execution and source checks

- Loaded baseline source from `git show d8abd23e:setup.py` into an isolated Python module with the actual repository path, then ran the seven candidate regressions against it. Independently reproduced 3 failures and 5 errors across 7 tests: missing first-install output parent, destructive project sentinel removal, uncaught timeout, overlapping-call shared output corruption, and empty inventory consumed by installation. Baseline was not checked out over the candidate.
- Reran `python -m unittest tests.test_model_discovery_setup -v`: 7/7 pass. Reran the same with `python -O`: 7/7 pass; assertions are unittest methods, not optimized-away Python assert statements.
- Reran `python -m unittest tests.test_setup tests.test_model_routing tests.test_install_profiles tests.test_role_process -v`: 40/40 pass. These are repository regression checks, not backend access evidence.
- Independently probed no-gateway behavior with temporary-directory allocation and subprocess execution forbidden: returns None without allocating or invoking discovery and preserves arbitrary original sentinel bytes.
- Independently checked exact discovery command, cwd, capture_output/text/check options and retained `timeout=30`. Missing output, OSError, timeout after partial output, invalid UTF-8, duplicate JSON keys and nonzero exit all return None, remove their exclusive temporary parent, and preserve the project sentinel.
- The seven-test concurrency case overlaps two mock subprocess bodies using a barrier, checks each thread gets its own inventory, requires distinct paths and verifies both temporary parents disappear. Source uses TemporaryDirectory per invocation, so results and cleanup share exclusive ownership; no project `_discovery_tmp.json` path is touched.
- Independently installed into a fresh target (no `.claude`) with an existing CLAUDE.md and mocked native Anthropic inventory. Observed stored inventory, selected research-assistant route, generated agent `model: "claude-opus-5-5"`, retained original user prose, cleaned temporary output and configured `check()` result. Discovery subprocess was mocked; the separate local `git rev-parse` remained real.

The initial additional install-routing probe incorrectly expected the Opus fixture to select research-explore, whose configured candidates do not contain Opus. Its preserved reviewer-boundaries.log records that reviewer-probe failure after all boundary probes passed. Inspection of the actual policy corrected the probe to research-assistant, which does select Opus; reviewer-install-routing.log records the successful consumer check. This is not a candidate defect or a suppressed failure.

## Result interpretation and limits

Accepted: no environment sentinel deletion; per-call temporary ownership; first-install mocked producer output consumption; timeout unavailability fallback with the existing 30-second subprocess setting; failure/malformed JSON cleanup; overlapping helper-call isolation; existing relevant setup/routing regressions. The timeout test raises TimeoutExpired deterministically and inspects timeout=30; it does not wait 30 seconds or measure wall-time enforcement. The concurrency check concerns helper invocations, not transactional concurrency of the entire installer.

The context encloses subprocess execution and load_json, so success and error paths both clean their own directory. The early environment test preserves prior truthiness semantics. Exception handling includes OSError, ValueError (including the loader's ExternalJSONError) and TimeoutExpired. Inventory schema validation still belongs to the existing install consumer; this patch does not broaden that contract.

Explicit `discover(target)`, other doctor behavior, discovery capability assertions, live gateway/authentication, actual model execution and full caller/backend success remain outside acceptance. The suspected pre-existing doctor's local `os` binding issue is a separate pending finding and is neither fixed nor accepted by this patch. No network or model calls were made.

## Evidence hashes

| File | SHA-256 |
| --- | --- |
| `setup.py` | `9ed8af9ff3f0d7665cf30579732aef7d627e441d7cfb01830173622b810963e1` |
| `tests/test_model_discovery_setup.py` | `ff9f50a208fb972b36fc9a4d4c92a118ce571041942ec317c1b238368768cce1` |
| `agent_doc/task/task_details/MODEL-DISCOVERY-02.md` | `f754a44a4ed5516312ab2eac202d3fb5a173ce91ed04d6b65a6415b0688536e9` |
| `.agent-runs/model-discovery-1701/plan-review.md` | `93761c1a41fb5969dc7082ef0026f98f73ec8ed45c32d73a1c948d7ebabd178d` |
| `.agent-runs/model-discovery-1701/baseline.log` | `bf3ade403b94db3c2ea480ad5c3c3215660a0f25e85ecae6823cf6353257b6b4` |
| `.agent-runs/model-discovery-1701/candidate.log` | `bca004149189ec2ec9d3ab737768e0f5cfa08d2e5f630e0e868a5aad90131f10` |
| `.agent-runs/model-discovery-1701/optimized.log` | `3de7d224bfc2edc9d53e4d975c0bf53d2e570eb776aed5899388db942df3ce83` |
| `.agent-runs/model-discovery-1701/integration.log` | `59a9aff700a9c74ea007085f356fe2536413a0a964ab7ad52f0b8f6b728658d9` |
| `.agent-runs/model-discovery-1701/reviewer-baseline.log` | `ac20ab223090ce15396df6ce8bbd773ae1c6e408588236e18bcd34ede1d18ceb` |
| `.agent-runs/model-discovery-1701/reviewer-candidate.log` | `d73bc3c1b51fb0bee148bd9af2de5509ecc1f98734e130e44d5f823c6a885ce2` |
| `.agent-runs/model-discovery-1701/reviewer-optimized.log` | `d73bc3c1b51fb0bee148bd9af2de5509ecc1f98734e130e44d5f823c6a885ce2` |
| `.agent-runs/model-discovery-1701/reviewer-integration.log` | `a93510cca2b532530abdc29e00ab1eca9faceddd81cd358a9a1889d33cb10783` |
| `.agent-runs/model-discovery-1701/reviewer-boundaries.log` | `666b71766db8ba17d77adeeb4f85efbc9dda0bc0080a4362d38b4d8b792fdf56` |
| `.agent-runs/model-discovery-1701/reviewer-install-routing.log` | `a102df156d40bf9dc98e649c49a09a439fb8f4a94e1679379b121a06a9e4ac88` |
