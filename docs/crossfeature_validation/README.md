# Cross-feature development evaluation

This is an explicit development evaluation, not a runtime service. Ordinary user tasks do not run it. See [plan](plan.md), [primary-source research and adoption](research.md), and [independent engineering review](reviews/engineering-review.md).

The registry's existing 14-role task catalog and host pipeline are reused. This bounded round targets visualization, architecture reading, paper-delivery acceptance, coordination, code organization and supervisor runtime. Noise/reviewer/experiment evaluation belongs to parallel task `01a10049`; its results are not silently counted here. No SGLang or private paper data is included.

## Interpretation

- Program tests really create files/SQLite state/figures/PDFs, execute code and read artifacts. Their control receipts are synthetic. They are not host role execution evidence.
- Host cases use real separate collaboration workers, frozen commit/input/output hashes, recorded turn summaries, and independent worker-context acceptance. Model identity/seed/token usage/monetary cost are not exposed and remain unknown. Receipts are trusted controller observations, not cryptographic attestation. Isolation is by instruction on a shared filesystem, not a security sandbox.
- The figure audit reads instrumented artists and compares actual PDF raster bytes to a controlled pre-export reference. This is not an arbitrary-image detector. Holdouts are distinct parameters/combinations, not novel mechanisms. The audit was repaired after review; the fixture family is no longer a pristine blind development holdout.
- Paper controls demonstrate a bounded research narrative versus audit/copied prose and incomplete learning declarations. The generated manuscript PDFs are text-only and refer to a separately supplied SVG; exemplar PDFs describe figures/tables in text. They do **not** certify a fully illustrated submission-ready paper or ten genuinely published/read papers. Real published-exemplar acquisition, genuine multi-role paper production and final full-paper visual delivery remain untested in this round.
- One trial per host batch provides no reliability/variance estimate or pass^k. Adaptive repairs are retained, never treated as independent repeated trials. Claims remain limited to these synthetic samples.

## Reproduce program checks

From repository root, explicitly as development work:

```sh
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
python scripts/sync_plugin_references.py --check
python evals/crossfeature/runtime_execute.py --out /tmp/runtime-results.json
python evals/crossfeature/architecture_cases.py --out /tmp/architecture-results.json
python evals/crossfeature/paper_cases.py --out /tmp/paper-controls
MPLCONFIGDIR=/tmp/mpl-crossfeature XDG_CACHE_HOME=/tmp/cache-crossfeature python evals/crossfeature/viz_suite.py --output /tmp/viz-controls
```

Visualization requires NumPy, Matplotlib, Pillow, PyMuPDF and Noto Sans CJK. Missing stack/font is explicitly skipped by unit tests and blocks that capability; it must not become a model pass. Do not install paid/external services to satisfy these commands.

## Reproduce host preparation / replay

Prepare a new run with the applicable catalog and isolated inputs, e.g.:

```sh
python scripts/agent_eval_pipeline.py prepare --dev-eval --revision HEAD --out /tmp/new-architecture-role --tasks evals/crossfeature/architecture_tasks.json --rubric evals/crossfeature/architecture_rubric.json --fixture-root evals/crossfeature/architecture_inputs
```

Preparation does not run a model. Follow the actual dispatch, collect and independent grade steps in [pipeline documentation](../agent_eval_pipeline.md). Paper's generic builder creates `/tmp/paper-controls/blind`; use that as its fixture root. Visualization uses `viz_tasks.json`, `viz_host_rubric.json`, `viz_host_inputs/`. Organization reuses registry inputs. Never pass outcome/oracle/rubric files to workers.

The evidence archive preserves complete pinned runs and two exact recorder implementations: three cases began before the development gate/dependency repair, two afterwards. Implementation hashes select the matching original recorder when replaying. No manifest hash was edited to hide a change. Archive replay verifies records and hashes, **not** new model execution or the semantic truth of grader prose. Independent reviews and actual outputs must also be read.

## Actual results and remaining gaps

| Feature | Executed program controls | Actual host / independent acceptance |
|---|---|---|
| Visualization | 12 generated/rendered cases; final instrumented FP=0/FN=0 after documented repairs; 7 adversarial/render tests | 12/12 decisions correct, 5/5 rubric criteria; 2 additional supported uncertainty observations retained separately from mutation labels |
| Architecture | 7/7 default/optional/error/shape/float32/full-consumer controls | 7 actual inputs executed; 5/5 criteria with anchored code evidence |
| Paper delivery | 10 declaration controls: 2 accepted good controls, 5 correctly rejected bad controls, **3 semantic false negatives** | 4 manuscript +3 learning +2 receipt judgments: FP=0/FN=0; 5/5 criteria for bounded material acceptance only |
| Supervisor runtime | 37 existing/new executed fault cases pass, including 4 new boundaries | No model benchmark needed for deterministic core; coordination role separately rejects unsupported monitor/completion/permission claims |
| Coordination | **1 semantic false negative**: integrity-only validator accepts producer v1 while consumer requires v2 | Actual role rejects inappropriate consumption, missing render and unproven live monitor; 5/5 criteria |
| Code organization | Real unchanged input/output hashes and retained historical mapping | 3/3 criteria; actual role writes bounded docs/proposal, preserves active/protected files and avoids redundant commentary |
| Development-only routing | 4 executed CLI/runtime boundary tests pass; real ordinary artifact task succeeds without reading eval inputs | Prompt boundary is additionally documented, not claimed universally enforced by Python |
| Noise/reviewer/experiment (other task) | Integrated from `e6711ad785f8d931c426041773ed64cb40357c54`; all hooks preserved | [Owner's 12-case, 48-criterion results](../measurement_evidence/holdout-summary.json), not rerun or relabeled as this round's results |

Five host batches pass their 23 frozen criteria, with original first attempts retained. [Host reports](host-reports.json), [artifact manifest](artifact-manifest.json), [individual acceptance records](reviews/review.md), [paper per-item outcomes](reviews/paper-items.json) and [figure per-case outcomes](reviews/viz-case-outcomes.json) support those narrow claims. Replay:

```sh
python evals/crossfeature/replay_host.py docs/crossfeature_validation/host-evidence.tar.gz
```

The three paper validator misses are disguised audit content, copied manuscript body and queued dispatch masquerading as role-start evidence. The production validators explicitly check declarations/integrity, not these semantics; actual role judgment detected the supplied counterexamples. A figure declaration validator likewise accepts falsely asserted render checks; a host or trusted render oracle remains necessary. These gaps were not “fixed” by weakening the rubric or calling a declaration pass semantic success.

Review repaired live versus removed-artist observation, stale PDF caching, extractable-but-invisible PDF text, uncounted unexpected report outcomes, a missing paper-validator snapshot dependency, and outdated prepare instructions. The initial defects and subsequent independent reproductions remain in [review](reviews/review.md) and [engineering review](reviews/engineering-review.md). The figure rubric changed during harness repair and is explicitly versioned; its parameter holdouts cannot support an untouched-heldout/generalization claim.

Release validation after integrating concurrent main: **257 repository tests +3 reader tests passed**, no skips, offline plugin references synchronized, diff whitespace check clean. Logs are local evidence here. Frozen host skill results remain tied to `15e633e`, not silently attributed to new concurrent noise skills. Interfaces used by these tasks were preserved; no rerun of unrelated role domains is claimed.

Further untested boundaries: long real research projects/full manuscript generation, genuine published-exemplar learning, unseen plotting systems/fonts/error conventions, successful third-party extension code, real tensor frameworks/GPU, real filesystem archive moves, multi-host runtime/NFS/clock jumps/database loss, arbitrary external cancellation, terminal artifact mutation, malicious shared-filesystem workers, measured repeat-run reliability and cost. Normal task QA remains active; only synthetic development evaluation is gated.
