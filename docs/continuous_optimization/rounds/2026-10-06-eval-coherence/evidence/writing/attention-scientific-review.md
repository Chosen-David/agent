# Independent scientific review: attention attempt 1

Reviewer: /root/full_paper_controller/scientific_review. Review date: 2026-10-06. Criterion: frozen eight-item working-paper rubric, not venue readiness. Manuscript PDF SHA256: 322b63a0b43550840626b95c46405dbf3a057ae440b09c0d189bf555d8403e74. All collection hashes are bound verbatim in the adjacent JSON.

## First-pass understanding before companions

Read complete six-page paper.txt before data/blueprint/companions, then all six final rendered pages. The question is whether stable tiled evaluation preserves the same masked attention target under extreme scores and how this differs from local masking. The mechanism is an online maximum with denominator and value numerator expressed in a common exponential scale. Strongest evidence is the real-arithmetic invariant plus a defined 648-case forward sweep against a separately organized dense float64 reference; the exact far-key construction is decisive against universal equality of local and global operators. It establishes neither a new algorithm nor universal floating-point stability, GPU performance, linear total-memory use or downstream quality.

## Acceptance and findings

All eight criteria pass for a bounded working paper. There is no confirmed blocker or mandatory revision. This is an acceptance of the actual scientific argument and supplied evidence, not of a venue submission or repository release.

### 1. research question and specific gap motivate mechanism — pass

p1 Abstract and Introduction paragraphs 1–3 ask whether tiling preserves a global masked target under extreme scores and whether locality does the same. The motivating gap is the independent small implementation and separation of mechanisms, explicitly not a new stable merge. p2 supplies the recurrence that answers this question.

### 2. design definitions/conditions sufficient for reconstruction, distinguish existing method from this study — pass

p2 §2.1 defines Q,K,V, arbitrary Boolean allowed sets, finite scores, nonempty rows and the target. §2.2 gives m/l/a invariant, rescaling induction, complete disjoint visitation and empty-tile guard. p3 Table1 and §3 specify all sweep factors, seed formula, quantization-before-reference, reference precision and error criterion. Actual dense/blockwise code agrees.

### 3. claims/numbers/citations agree with supplied evidence and negative results, no false novelty, significance, timing or GPU/training claim — pass

Independently aggregated all 648 accuracy CSV rows: four dtype/scale groups each have 162 observations; maxima are 1.2212453270876722e-15, 3.532729664357248e-13, 5.339567372697474e-7, 2.988110650203879e-5; zeros 0,129,0,105. All finite and within stated thresholds. Naive CSV has 0/108 scale1 and 108/108 scale100 nonfinite cases. Independent replay returned byte-identical accuracy.csv, naive_failures.csv, counterexample.json, masked_row_contract.json.

p5 §4.3 counterexample outputs 0 through query12 then 3.2,4,16/3, versus global1; maximum discrepancy13/3 is correct. Source review of FlashAttention §3.1/Algorithm1/Theorem1 and §3.3, Transformer §3.2, and pinned interface confirms attribution. p5 shape ratio16 is exact accounting, not a speed/memory measurement; p6 excludes CUDA/training claims.

### 4. results organized around discriminating questions and interpretation with actual comparative evidence — pass

p3–4 §4.1 answers numerical fidelity using stable dense comparison; p4 §4.2 exposes overflow through the intentionally weak unstabilized comparator and distinguishes it from the baseline; pp4–5 §4.3 supplies an exact semantic counterexample. The p4 paragraph about concentrated distributions explicitly treats this as unmeasured possible explanation.

### 5. paragraphs develop scientific argument with precise terminology and natural connective prose, process logs separate, no fabricated polish — pass

p1 starts from the scientific distinction, not artifact checks. p2 paragraph after Eq3 explains why rescaling retains relative masses; the correctness paragraph establishes the invariant. p4 results paragraph reconciles exact-zero cases with larger maxima, and p5 §5 opens by separating computational fidelity from model suitability. Commands/logs remain companions. Definitions and connective prose form a complete argument.

### 6. full source compiles, every figure/table corresponds to evidence and final PDF all pages are readable — pass

Successfully compiled a copied full paper source with pdflatex (exit0) inside review-owned attention-build; no author outputs changed. Opened and read all six final PDF page PNGs at 1.3x: equations, both tables, both figures, captions and references readable, no clipping/overlap. Table2 and Figure1 match recomputed CSV groups; Figure2 matches naive counts and full counterexample vector. PDF SHA256 322b63a0b43550840626b95c46405dbf3a057ae440b09c0d189bf555d8403e74.

### 7. related-work distinction and limitations are substantive — pass

pp5–6 §5 locates the inherited merge relative to FlashAttention and scaled operator relative to Vaswani, and distinguishes the generic NumPy probe from the pinned CUDA interface. Its concrete limits include N<=128, three seeds, quantized-input float64 reference, missing score-gap/value-magnitude stress, no arbitrary precision/gradient/dropout/GPU/timing/quality results, and quadratic mask allocation. Source passages confirm these distinctions.

### 8. exemplar-derived blueprint choices implemented with actual locations and appropriate rejections — pass

All five blueprint dimensions are implemented: organization (p1 contrast -> p2 mechanism -> p3 design -> pp3–5 contrasts); claim/evidence (p2 conditional induction versus p3–4 finite evidence); figures (pp4–5 errors/zeros/tolerances and distinct failure panels); rhetoric (p2 alpha explanation and p4 qualified concentration hypothesis); content rejection (pp5–6 omit broad CUDA/training benchmarks). Checked actual original anchors EX04 pp4–6 and pixel page5, EX01 p4, EX05 §§2.2/3 pp3–4 and pixel Figure2 p3, EX06 p2 theorem conditions, EX09 p2 algorithm. Preflight contains ten distinct selected works and per-page records; this reviewer did not re-perform all 182 exemplar pages. These transfers are writing decisions, never this study measurements.

## Specific artifact, argument and prose assessment

The paper survives removal of its audit companions: its operator definitions, invariant, sweep design, comparisons and semantic example form a standalone explanation. It does not merely count tests. The modest increment is a bounded independent reproduction that keeps stabilization, tiling and mask changes conceptually distinct. The paragraph beginning “The high-scale group simultaneously...” (p4) is especially useful because it identifies an alternative explanation without falsely claiming a measured concentration mechanism. The source-interface paragraph (p6) is relevant scope rather than a process log: it prevents the mathematical value dimension and arbitrary mask from being mistaken for supported upstream kernel inputs. There are repeated scope statements in the abstract/introduction/discussion, but they control different inferential boundaries and are not a paragraph-level defect. The counterexample is elementary; that limits research novelty but does not invalidate this working-paper assignment.

An optional future numerical experiment could stratify by score gap/value magnitude and measure concentration, as already suggested on p6. It is not a condition of this acceptance because neither causal attribution of zero error nor a universal error bound is asserted. A richer contemporary efficient-attention survey would be needed for a new-algorithm/SOTA paper, not this explicitly historical mechanism reproduction.

## Actual checks and limits

Loaded frozen research-review SKILL/execution/workflow and delivery/exemplar contracts. Used shell/Python, PyMuPDF, image viewing, NumPy replay and pdflatex. Read supplied protocol section A and actual dense/blockwise/attention functions; independently grouped raw CSV rows and checked JSON and interface source. Re-ran only attention into a copied artifact under the review directory. The replay principal outputs are byte-identical; compilation succeeds. Review-owned supporting files: attention-data-check.json, attention-replay.log, attention-build-check.log, attention-page-1.png through attention-page-6.png, original-source anchor PNGs.

Read original source text from official FlashAttention selected PDF pp4–6, Transformer p4, GPipe pp3–4, Deep Sets p2 and Adam p2; opened FlashAttention Algorithm1 page5 and GPipe Figure2 page3 pixels. These are actual source passages, not only companion claims. Official FlashAttention exemplar is 35 pages while the paper cites its disclosed 34-page arXiv version; I checked the shared mechanism against the official source but did not establish byte identity of those two editions. The related mechanism and scope statements agree. On 2026-10-06 a bounded web check surfaced primary records for FlashAttention-2 (arXiv:2307.08691) and FlashAttention-3 (arXiv:2407.08608); these are later GPU optimization routes, and no exhaustive 2026 novelty search or superiority claim is made here. The manuscript already disclaims new mechanism/SOTA claims.

All ten exemplar identities and records are available, but I checked the blueprint-relevant source anchors rather than claiming a second full 182-page corpus read. English is the only requested/delivered language, so language parity is not applicable. Controller/independent all-page role owns separate acceptance; this review does not release or publish anything. No author output or repository file was changed, and no held-out manuscript or grade was read.
