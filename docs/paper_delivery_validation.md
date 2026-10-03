# Paper delivery repair — 2026-10-03

## Evidence and responsibility

Baseline inspected: `4439900` (including code-reading work), then integrate remote `18ed6bc` before release. No SGLang files or branches touched. No private manuscript or raw research data included.

The reported incident is execution evidence supplied by the task owner, not independently recovered manuscript history: writing began before the actual repository writing/reader/reviewer instructions were loaded; an audit narrative replaced a requested submission; layout and technical checks were treated as sufficient; messaging a finished reviewer was mistaken for a new review run. These are execution failures, not all repository bugs.

Repository evidence: `config/role_registry.json` names `research-write`, not a `paper-writing` skill. `workflows/paper_writing_workflow.md` §§4.1, 4.3–5 already require argument structure, no fabrication, separate scientific/visual review, and incomplete status for missing evidence. The previous `scripts/validate_handoff.py` validates paths/hashes and caller-supplied checks, without paper-specific artifact or content criteria. It intentionally does not certify semantics. The repair supplies that missing domain contract instead of pretending the old workflow asked for audits.

## Change and activation

Read `plugins/research-assistant/skills/research-assistant/SKILL.md`, then the actual `research-write/SKILL.md`, each role's `references/execution.md` and relevant `references/workflow.md` (`orchestrator.md` for coordinator), plus the locally bundled `references/paper_delivery_contract.md`. These paths share prefix `plugins/research-assistant/skills/`.

Sequence: coordinator binds user artifact/venue/languages/constraints and frozen skill version → writer loads instructions before work, builds argument and honest evidence ledger → freeze each language's final manuscript/PDF → independently start `research-review` and `research-read-pdf` with their actual instructions → obtain actual start/result receipts → resolve issues → rebuild/review new hashes → coordinator compares all required checks with original target.

`workflows/paper_delivery_contract.md` is canonical; `scripts/sync_plugin_references.py` bundles it into all four roles. `scripts/validate_paper_delivery.py RECORD --root RUN_DIR` checks declarations in addition to the existing generic handoff validator. There is no automatic host hook: the coordinator must explicitly run it, or record manual contract review in a scriptless plugin environment. It does not prove receipts authentic, role files read, experiments real, or semantic judgments correct. Host evidence and actual content review remain necessary.

Audit/source manifests remain private companions. Scientific limitations, relevant implementation assumptions and reproducibility details stay in the paper. Missing results yield a working manuscript and claim-specific blockers/recovery tasks, never invented measurements or a substituted audit report.

## Upstream inspection

Read systems-paper-writing SKILL.md from Orchestra-Research/AI-Research-SKILLs and academic-paper-review SKILL.md from ChanMeng666/academic-paper-review-skill, plus both MIT licenses. Exact commits, URLs and hashes are in `paper_delivery_sources.lock.json`. Borrowed principles: problem/choice/evidence argument, audience-specific artifact, separate verification notes. No source templates/text or runtime copied; fixed page counts, fixed contribution counts and review-report templates were not imported as paper rules. Initial guessed raw URLs returned 404; actual paths were discovered from shallow clones and read.

## Independent review and finite evidence

Independent agent `/root/independent_review` read changes without editing and identified staged completion, shared reviewer/reader, honest partial receipts, missing schema fields and stale scientific-review hash gaps. Fixes add explicit pending role states, completion-only independence, documented fields and scientific snapshot binding. Receipt checks remain file-integrity checks; dispatch is not proof of execution.

The independent reviewer assessed two invented excerpts, not private manuscripts:

- A: Abstract inventories available source; introduction lists paths; evaluation reports discrepancies without measurements; conclusion completes audit. Requested submission + passed layout still fails artifact_fit/contribution/evidence: removing audit activities leaves no scientific argument. Remedy is a research question, contribution and evidence plan, with useful audit details kept separately.
- B: Queue splitting, a two-class model with an explicit service-time condition, single-server synthetic comparison, memory tradeoff, untested generalization and unverified closest-work citations. artifact_fit passes for the excerpt; method/contribution/evidence/related_work remain unresolved. This is an honest limited-evidence working draft, not submission-ready. Verify derivation, fair baseline, statistics and primary citations before deciding whether bounded claims satisfy the target.

These manual cases are not a live paper rewrite benchmark or proof of quality improvement. The tests consume declared findings; they do not classify prose by keywords. User inspection of a real rewritten EN/ZH manuscript is still required.

## Reproduce

```bash
python scripts/sync_plugin_references.py --check
python -m unittest discover -s tests -p test_paper_delivery.py -v
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
```

Focused regression: 15 tests (artifact substitution; audit findings despite headings/layout; layout-only acceptance; unloaded role; missing result receipt; partial/stale reading; unsupported result finding; limited-evidence draft; language coverage; independent role separation; stale scientific review; honest not-run reviewer; malformed declarations). These test integrity/rejection behavior, not model compliance. Final merged suite counts are recorded in the release handoff.
