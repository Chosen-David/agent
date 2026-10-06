# Independent scientific review: held-out U-Net attempt 1

Reviewer: /root/full_paper_controller/scientific_review. Review date2026-10-06. Frozen working-paper rubric; no venue score. PDF SHA2566785f8faa4ff2852aee255ad71efad9ee97a96c48135caaadc9abfff02f15551. Full collection output_hashes copied unchanged in adjacent JSON.

## Held-out ordering and first reading

This case was opened only after the controller’s follow-up released it following the no-writing-prompt-edit freeze at2026-10-06T13:56:24Z (root-no-edit-decision.json). Attention and systems reviews were already delivered. Read complete six-page manuscript text before this case’s blueprint, evidence or companion materials; no prior U-Net manuscript or grader result was read. The shared reproducer/protocol read while reviewing attention contained U-Net functions, but no held-out manuscript or grade; the manuscript/evaluation boundary was preserved. No guidance changes were derived from this review.

The question is whether same-padding replacement alone preserves a four-level U-Net’s spatial contract. That contract includes admissible dimensions, output extent, skip alignment and boundary/context behavior. The paper combines conditional recurrence analysis, an exhaustive finite shape-policy grid, and a separate fixed-positive-weight numerical probe. Strongest evidence is the derived divisible-by16/specific-residue conditions plus a compatible256 same-padding case whose constant-input boundary response differs. The support study distinguishes potential graph paths from measured learned effective receptive fields. It establishes a counterexample to unrestricted drop-in equivalence; it establishes no learned segmentation ranking or original Caffe execution result.

## Acceptance and findings

All eight criteria pass for this bounded working paper, independently assessed after held-out release. No blocking finding or mandatory repair. No inference from the earlier papers’ grades was used. This is not a submission-ready verdict or repository-release action.

### 1. research question and specific gap motivate mechanism — pass

p1 Abstract and Introduction distinguish output extent, skip compatibility, alignment and boundary response, and ask whether changing valid to same alone preserves their joint contract. Introduction paragraph2 explicitly makes the substitution premise hypothetical rather than falsely attributing it to the original authors. p2 pooling/crop recurrences directly address this gap.

### 2. design definitions/conditions sufficient for reconstruction, distinguish existing method from this study — pass

p2 §2 defines square inputs, zero-based indexing, per-convolution zero padding, floor pooling, exact doubling and three crop policies including odd-difference orientation. Eqs1–4 reconstruct the spatial graph and conditional output formulas. p3 §3 states full scalar grid, reduced1–16 channel numerical schedule, normalized positive3x3 kernels, max pooling, transposed-convolution equivalent, asymmetric skips, final identical channels and no softmax. Structural potential support is distinguished from selected argmax gradients. Actual geometry/forward/supports code agrees.

### 3. claims/numbers/citations agree with supplied evidence and negative results, no false novelty, significance, timing or GPU/training claim — pass

Independently replayed actual unet study in a copied source tree. geometry.csv, forward.csv, receptive_fields.csv and layer_traces.json are byte-identical; all48 stored output arrays equal replay arrays and both channels are identical. Recomputed66 cases/39 errors/27 successes; all27 successful extents match Eqs3–4. Same no-crop and symmetric accept only256 in supplied grid; valid symmetric accepts188,252,572; asymmetric accepts all11 in each mode.

p4 §4.2 values match actual arrays/CSV: valid all-ones outputs all1; same256 corner0.11626864920076965 and max1; same188/189/252/253 minimum0.19086768475540394. pp4–5 §4.3 supports/36 threshold agreements and tiny188 corner responses7.171517142302024e-14,2.089348492565811e-12 match. Independent2D reverse graph-support calculation matches all36 recorded Cartesian sets, resolving a possible separability concern.

Original U-Net arXiv v1 pp2–4 confirms Figure1 dimensions/channels, cropped skips, unpadded3x3/ReLU,2x2 pooling, even-prepool requirement and mirrored context. Official project page download passage confirms trained Caffe/tool distribution. Manuscript does not claim execution of original release, trained quality, speed or statistical significance.

### 4. results organized around discriminating questions and interpretation with actual comparative evidence — pass

§4.1/Figure1 distinguish crop failures and extent with every rejection retained, including incompatible even252 and outer257 mismatch. §4.2/Figure2 uses a constant-preserving valid control and same256 case with successful shape compatibility to isolate a remaining boundary distinction. §4.3/Table1 adds shifted/support-size conditions and selected impulse validation. p4 explicitly avoids pixelwise subtraction of differently aligned/extented arrays and attributes the response jointly to the specified graph.

### 5. paragraphs develop scientific argument with precise terminology and natural connective prose, process logs separate, no fabricated polish — pass

p1 progresses from spatial interface to the substitution assumption and a three-part argument. p2 prose explains the equations and why input parity alone is insufficient. p4 paragraph starting Changing the crop policy changes executability connects finite outcomes to Eq3; §4.2 explains the all-ones invariant before discussing measured boundaries. p5 distinguishes support counts from alignment; p6 returns to contract implications. No build/audit log substitutes for the argument, and limitations are attached to relevant inferences.

### 6. full source compiles, every figure/table corresponds to evidence and final PDF all pages are readable — pass

Compiled copied full source with pdflatex exit0. Opened and read all6 original final PDF pages at1.3x, including both figures, table, references and AppendixA; no clipping, unreadable text or equation corruption. Figure1 faithfully displays all66 cases; Figure2 shares0–1 response scale while titles/axes/caption state unequal68x68 versus256x256 extents; Table1 matches exact recorded support intervals/counts. Final PDF SHA2566785f8faa4ff2852aee255ad71efad9ee97a96c48135caaadc9abfff02f15551.

### 7. related-work distinction and limitations are substantive — pass

p2 §2.2 and pp5–6 §5 distinguish original topology/channel counts from reduced-channel fixed-weight probes, original even-prepool and mirror-context rules from floor-pooling/zero-padding stress cases, and scalar572->388 from actual Caffe/training reproduction. p6 §6 limits grid prevalence, feasible-size coverage, numerical channel realism, structural versus effective receptive fields, and missing learned/biomedical/performance/tiling evaluations. These are concrete scope boundaries consistent with the results.

### 8. exemplar-derived blueprint choices implemented with actual locations and appropriate rejections — pass

Five blueprint dimensions implemented: p1–3 problem/geometry/method order; p2 conditional recurrences and p3–5 bounded evidence; p4 full failure grid and p5 shared-scale response/support views; question-resolving topic sentences in §4; p6 rejection of benchmark imitation and limited AppendixA scalar anchor. Checked original EX03 Figure1 p2 and Figure2 p3 pixels plus §2 p4 text, EX10 Figure2 p4 pixels/axis semantics, and already-read EX04 pp4–6/EX06 p2 conditional-claim anchors. Actual blueprint/map locations correspond to manuscript; no exemplar numbers are study measurements.

## Artifact fit, prose and contribution

This manuscript has a complete reader-facing scientific argument without its companions. It first defines what a substitution would need to preserve, then separates a dimension calculation from a numerical construction. The constant-field control on p4 is a mechanism explanation: every stated operation preserves one without inserted zeros, so the altered boundary is interpretable. The paragraph explicitly refusing whole-array pixelwise subtraction is necessary because the output domains differ. The source-reference paragraph on p2 is similarly substantive: violating the original even-prepool condition in a stress test is not evidence that the original architecture was internally inconsistent.

The contribution is elementary and bounded. It neither discovers a new architecture nor shows a previously documented practitioner belief is widespread; p1 openly labels the premise as a potential implementation assumption. That is sufficient for this working-paper task, while its usefulness for a competitive research venue remains unestablished. The repeated negatives are mostly purposeful: trained quality, original implementation fidelity, arbitrary-size coverage, and potential versus effective support are different unsupported inferences. They do not crowd out the positive argument. Figure2 uses equal panel boxes for different output extents, but titles, axes and caption disclose that choice accurately; it is not misleading after reading them.

## Concern checked and rejected

REV-U-C001 (resolved by verification, no manuscript edit): axis-wise support union does not automatically justify a Cartesian-product support after arbitrary skip unions. To avoid trusting this implementation assumption, I wrote an independent reverse-graph2D Boolean dependency calculation that propagates selected output pixels backwards through each convolution, pooling, replicated upsampling and cropped concatenation. For every one of the36 reported structural records, its complete two-dimensional input set equals the claimed Cartesian set and area; zero discrepancies. This validates the reported records, not every possible architecture/input/output. The manuscript already limits empirical impulse coverage accordingly. Supporting files are check_unet_support.py and unet-independent-support-check.json.

## Actual tools, evidence and remaining scope

Reused the frozen research-review/execution/workflow/delivery/exemplar contracts. Read actual geometry/conv/forward/supports/unet code and prospective protocol sectionU. Independently aggregated all66 shape cases; checked successful-formula agreement, all48 numerical arrays and two-channel equality, 36 structural records and36 impulse indicators. Copied paper source under review-owned unet-build; pdflatex succeeds. Replayed the actual U-Net function with single-thread variables and fresh run ID; four principal tabular/trace files are byte-identical and all48 arrays equal supplied data elementwise. This is numerical execution of the declared reduced graph, not training. Files: unet-data-check.json, unet-replay.log, unet-build-check.log, and unet-page-1.png through unet-page-6.png.

Read original arXiv U-Net v1 pp1–4, including actual Figure1/2 pixels, and Group Normalization Figure2 p4 pixels for blueprint axis semantics. Shared FlashAttention/DeepSets/GPipe anchors had already been checked against original passages during earlier cases. On2026-10-06 opened the official Freiburg project page (https://lmb.informatik.uni-freiburg.de/people/ronneber/u-net/), whose Download section explicitly lists the trained network, modified Caffe binaries/source, MATLAB interface and tools; this supports the narrow distribution description. Did not download/run that185MB original release, measure training, or conduct a contemporary U-Net implementation survey. None is claimed by the paper. Ten-exemplar preflight provenance was reused; no claim of independently redoing all182 exemplar pages.

Final six PDF pages were actually viewed at1.3x; all equations and table entries are readable and the full structural AppendixA canonical trace is correct. Separate controller/PDF-reader acceptance remains independent. English-only; parity not applicable. Original-source PDF previews are private source-preview entries with archive:false in review-manifest.json; unet-build is regenerable scratch excluded from public archive. No author output or repository modified. No publication or release performed.
