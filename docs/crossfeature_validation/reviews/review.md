# Independent crossfeature review

Reviewer: `/root/runtime_coordination`, separate from visualization and organization workers. This reviewer authored the coordination fixture/rubric, so future coordination grading is worker-independent but not fixture-independent. Runtime tests written by this reviewer are not self-graded here.

Organization review read all seven frozen inputs, five README outputs, CODEMAP, inventory, proposal, execution and collection records. Independently recomputed input/output hashes and historical-prefix preservation; all three exact rubric criteria pass. Detailed evidence and collected output hashes are in `organization-grade.json`. This is a documentation-only case; actual archival/migration behavior was not exercised.

Visualization review initially ran all five tests successfully, then identified two material validity errors:

1. **Live artist mismatch in positive v08.** Original code removed colored bars and rendered black points while reading values/colors from the removed bars and leaving the colored legend. The nominal positive therefore failed actual palette preservation even though the checker passed. Required repair: inspect live point artists and preserve the requested mapping in the positive case; add a mutation that changes visible points and requires rejection.
2. **Stale PDF sidecars.** Original `audit()` used saved text/render sidecars instead of reading current PDF bytes. Reproduced by copying good Chinese v09 and replacing only `figure.pdf` with bad v07: audit returned no defects. Required repair: re-open/re-render actual PDF in audit, or reject hash-unbound stale evidence, with an executable mutation regression.

Further scope observations: the protocol defect was assigned into observation metadata after image generation, so it only tested constructed metadata comparison, not a measured-run protocol trail. Holdouts use new numeric seeds plus a combined mutation; this is bounded deterministic regression, not new-mechanism generalization. PDF checks use a same-renderer reference and fixed label crop; layout and renderer generality remain untested.

Repairs are pending independent recheck as of this review. The original passes must not be used to dismiss these findings. No host visualization outputs have yet been graded here.

Organization provenance gate warning: verify_run reported `pipeline implementation changed` during concurrent edits. Inputs and outputs independently match pinned hashes, but the semantic grade is proposed only until the controller resolves that gate; the reviewer did not rewrite the manifest or implementation pin.

## Independent recheck

Original pre-edit runner `.agent-runs/crossfeature/pinned_pipeline.py` has SHA-256 `344eb90c2ee92ef6c6bd92d9ca985d0843ecacc908cf5e31d63222837c015d01`, exactly equal to the three original manifest implementation_hash values. Imported this original runner, verified organization/architecture/coordination successfully, and rechecked collected outputs. The previously reported implementation mismatch is resolved without changing manifests or pins. Organization grade updated accordingly.

Architecture: all five criteria pass; reviewer read entire source/README/cases and independently re-executed seven inputs, matching four results and three exceptions. Coordination: all five criteria pass; actual bytes/hash and absent artifact independently checked. Coordination reviewer wrote its fixture/rubric, so this is worker-independent but not fixture-independent review.

Viz repair recheck: live colored points and rebuilt point legend resolve v08; replacing actual PDF with broken PDF now rejects. A new material regression remains: changed PDF predicate from OR to AND allows visibly covered label when extractable text remains. Independently built v01, drew a white PDF rectangle over x=0..32 points across page height, saved actual PDF: audit returned no defects while export_only_pixel_mae=6.609 and pdf_label_missing=False. Text success cannot substitute for visible pixels. Restore independent pixel rejection and add overlay regression before claiming repaired acceptance.

Viz v3 recheck: all seven tests passed. Independently repeated white-overlay mutation against a freshly generated v01 PDF; current audit rejects pdf_glyphs with pixel MAE 6.609 while extracted label remains present. Initial stale-PDF and live-point errors and subsequent AND-predicate regression are resolved for these bounded repros. No host fixture was modified.

Host viz independent acceptance: all five frozen criteria pass after reading all twelve decisions, all source samples/receipts and actual PDFs; independently recalculated every mean/SEM, reproduced current PDF render pixels, and actually opened all four contact sheets. Twelve accept/reject decisions correct, zero missed mutation dimensions. Two extra uncertainty observations in v03/v11 are preserved as raw extras and adjudicated as supported consequences of inconsistent mean/error scaling, not erased or relabeled frozen expectations. See viz-case-outcomes.json. Host-model evidence is separate from program fixture instrumentation.
