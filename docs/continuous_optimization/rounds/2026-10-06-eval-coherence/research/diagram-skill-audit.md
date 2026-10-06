# Diagram Skill chain audit — 2026-10-06

Scope: T25, read-only audit plus this report; decision `EXECUTE`. Read root `AGENTS.md`, `TASK.md`, and `prompts/decision_review.md`. Root confirmed remote refresh; inspected repository HEAD `e8ee3dca5dc8cd076fc031dd4510dabde214e046`. No Skill/code change, installation, publishing, or real-paper quality claim is made here. Transformer/ResNet/U-Net are evaluation materials, not additional Agent-optimization papers for T20.

## Finding and current chain

**Keep the existing diagram Skills for the first three-paper run.** The suspected omissions—rendered arrow inspection and final-size visual QA—are already explicit. The remaining risk is execution and independent acceptance, not an absent instruction.

| Actual entry / dependency | Confirmed behavior and boundary |
| --- | --- |
| `research-diagrams/SKILL.md` → `references/execution.md`, `workflow.md`, `figure_shared.md` | Source-grounded nodes/edges first; final rendered arrow endpoints, occlusion, and labels must also be inspected. XML/compilation is insufficient. |
| `workflows/diagram_workflow.md`, §§1–4 | Edges carry source, target, direction, kind, label, and source evidence. Groups/invariants are separate. Moving nodes requires endpoint rechecking. Semantic contract comparison precedes final-size and whole-page inspection; failed repairs remain draft. |
| `workflows/figure_shared.md`, §§2–4 | Physical dimensions and evidence are recorded. Semantic/scientific, visual, technical, and reproducibility verdicts are separate. Actual embedded size and grayscale must be viewed; 300 DPI or editor zoom is not evidence. |
| `research-figures/SKILL.md` and `workflows/figure_workflow.md` | Pure topology routes to diagrams; mixed figures have one assembly owner. Final assembled size must be reopened and checked even after individual panels pass. This is a workflow contract, not an automatic router. |
| `paper_exemplar_learning.md`, §7 | Actual original pixels and locations, source hash/read receipt, reader→diagram discussion, visual brief, and brief→plan→implementation mapping; independent scientific and visual verdicts. Staged execution cannot certify independent collaboration. |
| `workflows/figure_tools.md` | Existing verified local capability is sufficient; candidate selection is bounded and upstream dependencies must actually be read. Marker checker availability must not be invented. Installation recipes are not automatic actions. |

Read both role packages, their execution/workflow references, shared QA/tools, and exemplar §7. Byte checks: both roles' shared QA, tools, and workflow copies match their canonical workflows. Exemplar copies differ only by their generated-file notice, not substantive text.

## Upstream source extension, without duplicate counting

The existing source record is `docs/figure_validation.md` §2 (checked 2026-10-03). Reused its exact AGILAB pin rather than registering the same Skill as a new discovery. Rechecked via the GitHub connector on **2026-10-06 UTC**, at commit **`4d9c6af2a3a1d069f374f6fb41624655bc186bba`**. This is a reproducible historical pin, not a claim of latest/default-branch state. Web opening failed; connector retrieval succeeded. No files were installed or upstream scripts executed.

| Actually read at this pin | Git blob SHA | Mechanism / limit |
| --- | --- | --- |
| [scientific-svg-figures/SKILL.md](https://github.com/ThalesGroup/agilab/blob/4d9c6af2a3a1d069f374f6fb41624655bc186bba/.claude/skills/scientific-svg-figures/SKILL.md) | `c3fd36f9418e22ad9c0ea71941e77dc1dbb565f7` | Surface-first layout, editable SVG, geometry before prose, dedicated connector space, physical-size review; quality guidance, not measured model benefit. |
| [figure-classes.md](https://github.com/ThalesGroup/agilab/blob/4d9c6af2a3a1d069f374f6fb41624655bc186bba/.claude/skills/scientific-svg-figures/references/figure-classes.md) | `0450b69117f7fc872f5363d89e7edcdb5de82e50` | Chooses layout from explanatory purpose; diagram classes are heuristics, not scientific structure. |
| [surface-profiles.md](https://github.com/ThalesGroup/agilab/blob/4d9c6af2a3a1d069f374f6fb41624655bc186bba/.claude/skills/scientific-svg-figures/references/surface-profiles.md) | `12891096ae4b8d33c4d0a92ff96b15fed49c62e7` | Browser/slide/report sizes, editable text, export-safe geometry. Its numeric defaults cannot substitute for a paper's actual width/template. |
| [svg-diagrams/SKILL.md](https://github.com/ThalesGroup/agilab/blob/4d9c6af2a3a1d069f374f6fb41624655bc186bba/.claude/skills/svg-diagrams/SKILL.md) | `4c0039bab8c94dfed01277b763e15fe964537010` | Stable marker IDs/units, manual wrapping, endpoint recalculation. Fixed pixel padding is a preset, not universally appropriate. |
| [check_svg_markers.py](https://github.com/ThalesGroup/agilab/blob/4d9c6af2a3a1d069f374f6fb41624655bc186bba/.claude/skills/svg-diagrams/scripts/check_svg_markers.py) | `d9a46e92f86970c71d0b6a841d7964eddb3d097d` | Python standard library only (`argparse`, `re`, `sys`, ElementTree, Path). Checks XML parsing, marker IDs/duplicates, explicit valid marker units, unresolved local marker references in attributes/styles. Does **not** check target geometry, arrow direction, occlusion, line crossings, or paper semantics. |

This extends the old entry-level audit with the actual references and sibling checker. Both chains require semantic arrow targets and embedded-size review; the local chain additionally requires a scientific evidence contract, physical-size records, separate verdicts, and reader handoff. Neither a marker-check pass nor a matching edge list proves that readers see the intended arrows. No need to replace the local Skill or copy upstream instructions.

## Evaluation boundary, actually reproduced

Read `scripts/agent_eval_pipeline.py`, `scripts/paper_exemplar_checks.py`, `evals/tasks.json`, `evals/rubric.json`, and host worker/reviewer instructions. The generic recorder freezes source/input/rubric versions and hashes, requires a different grader identity, binds grades to collected artifacts, and distinguishes blocked/ungradable from semantic failure. It does not inspect pixels. Exemplar checks explicitly describe themselves as structural checks requiring human review.

An in-memory `python -B` call to `validate_grade` accepted one `pass` for criterion `editable SVG, actual render and visual QA` with only a collected `notes.txt` hash and `artifact_refs=['notes.txt']`. No SVG/image existed and no run/grade record was written. Reproduction: call that function with distinct worker/grader strings, matching case/attempt, the one notes hash, and a nonempty evidence string. This confirms its **documented host-review trust boundary**, not an actual false acceptance in the forthcoming figure run. The current default diagram case is only a synthetic six-node/five-edge attention sketch; its previous success cannot certify real-paper diagrams.

## Immediate evaluation and conditional candidate

For the unchanged Transformer and ResNet baseline, then U-Net holdout, apply the already required two views: (1) source/semantic contract against the actual paper, and (2) independent tracing of each important edge in the exported pixels at final paper size. Explicitly record observed source endpoint, target endpoint, arrowhead, legend/type, and any ambiguity. Also inspect full-page embedding, readability, grouping, grayscale, and caption correspondence. A correct checklist paired with a wrong/ambiguous rendered arrow fails semantic acceptance; a scientific pass with unreadable labels fails visual acceptance. Keep original failure renders and repair attempts.

Small future candidate **only if an actual baseline miss occurs**: add an edge-ID→rendered-location trace to the figure-specific reviewer rubric/receipt, requiring direct image references for each identified failure. Do not expand the generic recorder into an inferred geometry oracle, add duplicate Skill prose, or change frozen baseline grading after seeing outcomes. Compare under the same paper input, requested abstraction, size, and budget; develop on Transformer/ResNet and reserve U-Net for transfer. Benefit is presently untested.

Acceptance of this audit: source chain and executable boundary inspected; upstream dependency scope verified; report delivered. T25 remains open pending real generation, independent rendered inspection, and actual figure/text handoff. T20 remains unchanged. Next owner: root coordinates frozen evaluation and records outcomes in root TASK.
