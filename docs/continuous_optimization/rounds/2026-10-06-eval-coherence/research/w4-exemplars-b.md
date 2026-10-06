# T24 / W4 writing exemplars B

Completed actual reading: **3 papers, 83 physical pages, 69 figures/tables**. Reader: `/root/exemplar_read_b`. No manuscript writing occurred in this context. This is extra writing study, not a second count of the already completed agent-research corpus.

Original full PDFs and pixels remain outside the repository. JSON records individual page/pixel SHA256 receipts, source versions and all observations. These receipts establish traceability, not independent scientific correctness or reproduction. Root still owns the ten-paper preflight, template verification, synthesis and manuscript evidence binding.

## EX04 — FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness (NeurIPS 2022)

Publication: https://proceedings.neurips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html
Identity: `NeurIPS2022:67d57c32e20fd0a7a302cb81d36e40d5; DOI10.52202/068431-1189`
Selection: Direct exact/approximate attention argument; separates arithmetic, IO, kernel and end-to-end claims.
Quality judgment: Published main-conference paper with mathematical contract, mechanistic ablations, tunedbaseline comparison and disclosed practicallimits; venue alone not qualityproof.

### Frozen sources

- official extended full PDF including main pp1–16 and appendicespp17–35: 35 physical pages; `6b0fcf9037095c8a10453267cd48d125652deb171b64d3ec9397a563ff5d93ca`; https://proceedings.neurips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Supplemental-Conference.pdf

### Page-by-page actual reading

| Document / physical page | Printed page | Concrete observation |
| --- | --- | --- |
| flash / 1 | 1 | Abstract moves from long-context cost through IO-aware exact computation to measured training and quality outcomes. Introduction argues FLOP reductions can fail to improve wall-clock time; conference footer verifies NeurIPS 2022. |
| flash / 2 | 2 | Figure1 combines hierarchy capacities/bandwidth, tiled data movement, and attention-only timing. Introduction names tiling and recomputation as established techniques and separates IO analysis from block-sparse extension. |
| flash / 3 | 3 | Three outcome bullets anticipate training, quality, and attention benchmarks. Background defines GPU memory hierarchy, compute versus memory bounds, kernel fusion, and Q/K/V dimensions. |
| flash / 4 | 4 | Algorithm0 makes intermediate HBM materialization visible. Section3.1 derives numerically stable block softmax merging and explains why recomputation can save memory traffic. |
| flash / 5 | 5 | Algorithm1 specifies block sizes and persistent row statistics. Theorem1 gives exact output/FLOPs/extra space; Theorem2 states the SRAM range before its IO bound and gives a proof sketch. |
| flash / 6 | 6 | Figure2 contrasts FLOPs with HBM traffic/runtime and varies block size/sparsity. Proposition3 only denies asymptotic improvement for all SRAM sizes; the paper explicitly leaves a stronger parameterized lower bound open. |
| flash / 7 | 7 | Experimental overview separates training speed, quality, and kernel benchmarking. Tables1–2 specify endpoint/hardware or perplexity alongside time; footnote notes LRA tuning sensitivity. |
| flash / 8 | 8 | Tables3–6 cover LRA, changed context length, document classification, and Path tasks. Longer context changes the model setting. Table4 caption says 0.7 while displayed 18.2 to17.2 is1.0: retain as a source inconsistency, not our result. |
| flash / 9 | 9 | Figure3 exposes runtime crossover and memory growth. Section5 explicitly acknowledges CUDA engineering and portability costs; single-GPU result is separated from future multi-GPU work. |
| flash / 10 | 10 | Concludes multi-GPU direction and societal impacts; credits Apex implementation provenance and funding. References begin with IO theory, structured models, and domain datasets. |
| flash / 11 | 11 | References7–23 continue legal tasks, KeOps, gradient checkpointing, compilers, sparse attention and working-set origins. Mixed algorithm/system/application sources support different argument roles. |
| flash / 12 | 12 | References24–44 include BERT, vision Transformers, optimizer-independent checkpointing, datasets, structured state spaces, memory hierarchy and hardware lottery. |
| flash / 13 | 13 | References45–62 include data-movement studies, GPU microarchitecture, medical dataset, accelerator architecture, approximation baselines, MLPerf and online softmax. |
| flash / 14 | 14 | References63–82 include dated MLPerf and NVIDIA architecture sources, framework/compilation, Rabe–Staats, language models and sparse/long-context methods. |
| flash / 15 | 15 | References83–98 close with LRA, Roofline/data locality, Transformers software, lower-bound literature and efficient attention. Bibliography is part of selected PDF coverage. |
| flash / 16 | 16 | Checklist points claims and limitations to main sections, proofs toC, experimental details/assets toE. Checklist declarations are author assertions, not independent reproduction. |
| flash / 17 | 17 | AppendixA groups related work by IO, structured matrices, sparse training and efficient Transformers. AppendixB starts by distinguishing reduced peak memory from reduced memory accesses. |
| flash / 18 | 18 | B.1–B.2 derive forward normalization and backward gradients; D_i=dO_i dot O_i avoids retaining a full softmax-gradient row. Max-shifting is omitted only in simplified derivation. |
| flash / 19 | 19 | Completes dQ/dK scalar sums and gives Algorithm2 with scaling, masking, dropout and saved RNG state; these assumptions are absent from the simplified main algorithm on purpose. |
| flash / 20 | 20 | Algorithm3 states standard backward baseline. B.4 explains RNG regeneration and row-dot simplification; B.5 compares the mechanism with Rabe–Staats rather than only ranking speed. |
| flash / 21 | 21 | Algorithm4 specifies block backward updates and saved inputs. Comparison distinguishes incremental single-output accumulation from per-block temporary outputs; proof section begins FLOP count. |
| flash / 22 | 22 | Inductive proof tracks m, l and O after each block and establishes exact attention. IO proof counts standard materialized matrices then passes over Q/O. |
| flash / 23 | 23 | Block-memory constraints imply block dimensions and IO bound. Proposition3 proof uses M=Theta(Nd), a limited quantifier; backward proof mirrors forward pass counting. |
| flash / 24 | 24 | Algorithm5 adds the nonzero-block predicate. Sparse IO proof retains mandatory Nd output term; multi-GPU discussion is explicitly a potential extension. |
| flash / 25 | 25 | D.2 discusses sparse MLP and kernel methods as possibilities. E.1/E.2 give BERT/GPT optimizer, precision, effective batch, shared validation split and hardware. Table7 adds a weaker baseline without replacing MLPerf. |
| flash / 26 | 26 | Figure4 compares validation curves over steps; Table8 varies GPU count while fixing global batch. LRA details disclose precision exceptions and geometric mean speedup; Path transfer procedure begins. |
| flash / 27 | 27 | Path continuation mentions overfitting after additional fine-tuning. Tables9–11 show ViT end-to-end versus per-step settings and compiler/fusion baselines; E.6 introduces Apex comparison. |
| flash / 28 | 28 | Table12 reports FlashAttention slightly slower than FMHA at sequence128 overall and faster at256/512. Figure5 Roofline shows remaining performance headroom; hardware sensitivity section starts. |
| flash / 29 | 29 | Figures6–7 vary sequence length, masking/dropout and head dimension on A100. Text connects larger head dimension to smaller feasible blocks and notes causal-mask benefit. |
| flash / 30 | 30 | Figures8–9 compare RTX3090 and T4, with separate T4 forward-only panel. The figure8 plot title says GTX3090 while caption/text say RTX3090; preserve hardware ambiguity as source typo. |
| flash / 31 | 31 | Table13 routes thirteen configurations to result tables. Setup discloses random Q/K/V,100 timing measurements, exclusions, precision exceptions, and unsupported-length versus OOM distinctions. |
| flash / 32 | 32 | Tables14–17 give dropout+mask forward/backward/combined and mask-only forward, milliseconds across sequence128–65536. Exact and approximate methods share table space but are algorithmically distinct. |
| flash / 33 | 33 | Tables18–21 give mask-only backward/combined and dropout-only forward/backward; missing cells require setup interpretation, not zero-time interpretation. |
| flash / 34 | 34 | Tables22–25 give dropout-only combined and neither-dropout-nor-mask forward/backward/combined. The short-length overhead of sparse implementation is visible. |
| flash / 35 | 35 | Table26 gives combined memory MB with neither dropout nor masking. Dense and sparse FlashAttention share displayed memory, and dashes for other methods do not imply equal memory. |

### Complete figure and table inventory

Every item below was opened in original rendered pixels with its caption. Exact image path/hash is recorded per item in JSON.

| Item / location | Observed argument and encoding | Transfer and limit |
| --- | --- | --- |
| Figure1 / flash p2 | Three parts connect bandwidth/capacity pyramid, tiling arrows and stacked milliseconds. Red/blue arrows distinguish outer/inner loops; dotted NxN matrix denotes avoided materialization; orange blocks indicate SRAM work. Timing panel is attention computation, not end-to-end. | Adapt mechanism+cost placement for exact attention; label actual memory objects and measured scope. For waiting fairness, show ready/waiting control flow plus a separately measured metric, never derive fairness from throughput. |
| Figure2 / flash p6 | Left numeric table contrasts increased GFLOPs with reduced GB and ms. Middle dual-axis block-size plot shows diminishing runtime benefit despite fewer HBM accesses. Right sparsity axis is percent nonzero blocks and compares dense reference with sparse cost. | Adapt ablation tied to a mechanism; use separate aligned axes if dual-axis scaling could imply stronger causality than data warrants. |
| Figure3 / flash p9 | Two panels use runtime(ms,log y) and footprint(GB); method line styles and shared legend identify exact/approximate/sparse options. Circled crossover points prevent a universal-winner reading; memory arrows annotate ratios. | Adopt crossover reporting and algorithm-class labels for exact/approx attention. Do not copy speedup lines or extend beyond measured lengths. |
| Figure4 / flash p26 | Four validation-perplexity curves over training steps overlap within each model size; this checks training behavior while runtime is reported elsewhere. | Adopt task-quality/numerical trajectory check beside speed evidence; overlap is not bitwise equality or a formal equivalence test. |
| Figure5 / flash p28 | Profiler Roofline plots FLOP/byte versus performance with memory slopes and compute ceilings. Measured point remains below attainable roof; screenshot contains UI icons and very small axis lettering. | Use analytical bottleneck plot only with own measured counters; redraw native clean plot rather than copying a profiler screenshot. |
| Figure6 / flash p29 | Grouped bars report A100 speedup versus sequence length, with dropout+mask, mask-only and neither configurations. Zero baseline and shared unit permit within-length comparisons. | Adopt configuration disaggregation; state baseline implementation and avoid treating every fused operation combination as the same workload. |
| Figure7 / flash p29 | A100 head dimension128 grouped bars add causal mask and show declining benefit for unmasked/no-dropout at long lengths while causal remains stronger. | Adopt parameter sensitivity including weak regimes; distinguish triangular work reduction from exact full-mask execution. |
| Figure8 / flash p30 | RTX3090 caption/text but plot title GTX3090; grouped bars reuse operation variants and sequence categories. | Adopt hardware sensitivity, verify actual device name from own logs; reject source typo as a labeling model. |
| Figure9 / flash p30 | Two T4 panels separate combined forward/backward from forward-only speedup. Same categories/legend make workload difference explicit. | Adopt scope-separated panels for training/inference, or scheduler latency/throughput; do not silently combine denominators. |
| Table1 / flash p7 | BERT time-to-target in minutes, same initialization and target accuracy, mean±spread over10runs on8A100. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table2 / flash p7 | GPT2 small/medium rows pair perplexity with days and baseline-relative speedup; identical displayed perplexity separates runtime from modeling quality. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table3 / flash p8 | LRA per-task accuracy, average and speedup compare exact and approximate algorithms, with own method group separated by rules. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table4 / flash p8 | GPT2 context length is an explicit changed variable alongside perplexity and days. Caption0.7 conflicts with displayed18.2→17.2; cannot blindly copy. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table5 / flash p8 | MicroF1 across document lengths for two datasets includes nonmonotonic results, making longer-context benefits conditional. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table6 / flash p8 | PathX/Path256 entries distinguish reported nonrandom scores from crossed-out failures; crosses conflate different failure reasons unless text consulted. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table7 / flash p25 | BERT endpoint table extends main comparison to HuggingFace while keeping same hardware and10run summary. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table8 / flash p26 | GPU-count speedup table uses1/2/4/8devices and fixed global batch512, avoiding hidden batch-growth explanation. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table9 / flash p27 | ViT-base300epoch training hours with top1accuracy preserves equal quality at fixed196tokens. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table10 / flash p27 | ViT-large patch-size8/4 comparisons pair sequence length,batch,time and memory; patch/batch differ between groups so compare within groups. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table11 / flash p27 | Compiler/eager/Megatron/Flash timings report forward,backward,total for batch16/32/64; unitsms and mask/no-dropout scope explicit. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table12 / flash p28 | ApexFMHA versus Flash forward/backward/combined times for128/256/512 expose baseline win at128combined and all backward-only cells. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table13 / flash p31 | Configuration index maps dropout/masking/pass to Tables14–26; it is navigation, not experimental evidence. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table14 / flash p32 | forward runtime(ms), dropout+mask, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table15 / flash p32 | backward runtime(ms), dropout+mask, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table16 / flash p32 | combined runtime(ms), dropout+mask, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table17 / flash p32 | forward runtime(ms), mask only, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table18 / flash p33 | backward runtime(ms), mask only, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table19 / flash p33 | combined runtime(ms), mask only, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table20 / flash p33 | forward runtime(ms), dropout only, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table21 / flash p33 | backward runtime(ms), dropout only, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table22 / flash p34 | combined runtime(ms), dropout only, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table23 / flash p34 | forward runtime(ms), neither, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table24 / flash p34 | backward runtime(ms), neither, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table25 / flash p34 | combined runtime(ms), neither, sequence128–65536; bold/underline rank two best cells. Baseline availability and exactness classes must be interpreted usingE.9. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |
| Table26 / flash p35 | MemoryMB by sequence length, no dropout/mask, with dashes for unavailable configurations; Flash dense/sparse equal reported storage. | Adapt explicit metric, workload, baseline and missing-value semantics; retain matching own measurements only. Table13 may inspire a compact appendix index, not main-body result inflation. |

### Five writing dimensions

**organization — pp1–3 intro; §§2–3 pp3–6; §4 pp6–9; §5 pp9–10; AppsA–E pp17–35**

Problem is the mismatch between reduced arithmetic and actual execution cost. The main path teaches only memory facts needed by the method, then exact algorithm/proof summary, sparse extension, training/quality/kernel evidence, and practical limits. Detailed related work is deferred toA while novel mechanism positioning already appears in introduction. AppendixB/C/E separately answer implementability, correctness and reproducibility.

Transfer: Adapt to attention draft: state the semantic target first, teach the relevant cost model, present exact mechanism before approximation, then separate numeric fidelity, kernel latency and task outcomes. Scheduler draft can similarly put state semantics before optimization and failure/fairness evidence.

Limit: Do not impose this order on a geometry exposition whose key result is a dimension derivation. Existing working drafts cannot claim broad training outcomes just because exemplar has them.

**claim_evidence — Theorems1–2 p5; Proposition3 p6; Figure2 p6; Tables1–6 pp7–8; E.6 p28**

Correctness, traffic complexity, measured kernel cost, whole-model speed and longer-context quality use different evidence. Proposition3 quantifier is weaker than a lower bound for everyM. Figure2 challenges FLOP-count alternative; E.6 retains a configuration where tunedFMHAwins. Longer-context quality includes a changed model setting, not a quality change from exact arithmetic alone.

Transfer: Maintain separate own IDs for exactnessproof, floatingpointcheck, timings and any taskquality. Write all-SRAM versus per-SRAM quantifiers precisely. Include a tuned baseline or mark missing; keep negative regimes.

Limit: Do not infer bitwise equality from mathematical exactness or claim GPU/end-to-end benefit from CPU/synthetic observations. Table4 headline inconsistency needs independent source-check if used scientifically.

**figures — Figures1–3 pp2,6,9; Figures4–9 pp26–30; Tables1–26**

Figure1 links hierarchy→data movement→time. Figure2 is mechanism ablation; Figure3 reveals crossover instead of hiding it. Supplement curves establish behavioral consistency and hardware sensitivity; dense tables retain numeric detail. Color/line styles have distinct roles but several smallplots and profiler screenshot are hard to read at column scale.

Transfer: Adopt one conceptual figure and one claim-discriminating quantitative plot using own data. Put raw timing matrices in appendix. Explicitly label exact versus approximate method families and training versus inference.

Limit: Do not copy the GPU triangle, arrows, measured points or screenshot. Geometry figures need spatial dimensions/crops rather than memory hierarchy; fairness figures need per-task service/wait evidence, not aggregate speedup alone.

**rhetoric — §1 pp1–3; §3.1 p4; Proposition3 p6; §4.3/§5 p9; E.6 p28**

The introduction sets a falsifiable mismatch rather than a generic importance claim, names established ingredients, and uses prospective claims that later sections answer. Local paragraph topics are operational: tiling, recomputation, runtime, footprint. Qualifications include known baselines, common lengths and SRAM range; limitation text is concrete. Some promotional extrema and numeric mismatches should not be imitated.

Transfer: Write original topic sentences that name a problem, mechanism and measured consequence. Use verbs such as preserves, bounds, measures and enables only for matching evidence. Keep case/condition next to benefit and acknowledge reused techniques.

Limit: Avoid universalfastest, optimal or newcapability wording without complete comparison and scope. A workingpaper should say shows on these fixtures, not achieves production behavior.

**content — §2 pp3–4; Algorithms0–1 pp4–5; B pp17–21; C pp21–23; E pp25–35**

Background spends space on the hardware bottleneck required for interpretation. Maintext exposes core algorithm, proofconditions and application evidence; appendices preserve detailed masks/dropout/RNG/backward derivation, proofs, hyperparameters, precision exceptions and failures. E.9 explicitly distinguishes unsupported configurations from OOM.

Transfer: Allocate maintext to scientific question, invariant, decisive result and limit; place commands/configuration catalogs in appendix or reproducibility artifact. Keep failure semantics and incomparable baseline settings in the main comparison caption when they affect conclusions.

Limit: Do not manufacture large application sections for small evidence. An experiment matrix is supplementary evidence, not the narrative spine.

## EX05 — GPipe: Efficient Training of Giant Neural Networks using Pipeline Parallelism (NeurIPS 2019)

Publication: https://proceedings.neurips.cc/paper_files/paper/2019/hash/093f65e080a295f8076b1c5722a46aa2-Abstract.html
Identity: `NeurIPS2019:093f65e080a295f8076b1c5722a46aa2`
Selection: Systemspaper connects synchronoussemantics, scheduling mechanism, resourcecost and diverse applicationevidence.
Quality judgment: Published conferencepaper with controlledmicrobatch/partition scaling, explicittradeoffs and consistency checks; limits remain.

### Frozen sources

- official main paper: 10 physical pages; `0fe89870d44301c760883413f2f30006891dbff5c3656bfc194ba66d7e36c52c`; https://proceedings.neurips.cc/paper_files/paper/2019/file/093f65e080a295f8076b1c5722a46aa2-Paper.pdf
- official ZIP member supple.pdf: 6 physical pages; `22f4a08d43521f47c0e73374bc640ccaec4a8f863537ea67e8ed91be3a8ce56e`; https://proceedings.neurips.cc/paper_files/paper/2019/file/093f65e080a295f8076b1c5722a46aa2-Supplemental.zip

### Page-by-page actual reading

| Document / physical page | Printed page | Concrete observation |
| --- | --- | --- |
| gpipe / 1 | 1 | Abstract motivates task-independent scaling then supplies two task examples. Introduction frames memory, communication and model-specific infrastructure as competing constraints; PDF title is GPipe. |
| gpipe / 2 | 2 | Figure1 uses parameter count versus accuracy/BLEU as motivation, not controlled causal proof. Text states synchronous gradient accumulation and describes sequential-layer interface. |
| gpipe / 3 | 3 | Figure2 contrasts naive sequential execution with micro-batching and labels the bubble. Interface, partition-cost balancing, algorithm and batch-normalization caveat lead into rematerialization. |
| gpipe / 4 | 4 | Table1 distinguishes parameter storage from peak activations and device types. Bubble overhead bound is conditioned on M and K; load imbalance limits ideal scaling. |
| gpipe / 5 | 5 | Tables2–3 vary micro-batches/partitions and interconnect setup. Official Table4 is actually a pie chart of measured step costs; recomputation dominates overhead, not the bubble alone. |
| gpipe / 6 | 6 | Table5 juxtaposes target datasets and prior results with public/private pretraining caveats. Translation section explains corpus and depth/width axes. |
| gpipe / 7 | 7 | Figure3 orders languages by resource level and plots delta BLEU to bilingual baselines. Equal-parameter width/depth comparison and training-instability fixes qualify simple capacity claims. |
| gpipe / 8 | 8 | Design trade-offs compare SPMD and asynchronous pipelines, then state single-layer memory and batch-coupled-layer limits. Conclusion returns efficiency/flexibility/reliability, not a new claim. |
| gpipe / 9 | 9 | References1–25 cover model scaling examples, checkpointing, Transformer, Lingvo/frameworks, normalization, and transfer learning. |
| gpipe / 10 | 10 | References26–46 cover augmentation/pretraining, translation, Mesh-TensorFlow, initialization, device placement, DistBelief, historical pipelines and PipeDream. |
| gpipe-supp / 1 | 1 | Supplement restates sequence/subgraph flexibility, introduces consistent-gradient test, and lists image-training hyperparameters; TableS1 shows per-dataset learning rate/decay selected on held-out data. |
| gpipe-supp / 2 | 2 | FigureS1 is a full code listing for a TensorFlow/Lingvo dummy 16-layer convolution model, partition counts1/2/4 and gradient-norm tolerance. The listing contains TensorPipe class names; reading is not execution. |
| gpipe-supp / 3 | 3 | Consistent-training experiment compares repeated baseline accuracy to1/2/4/8 partitions. FigureS2 displays the highly unequal102-language example counts on a logarithmic y-axis; baseline optimization described. |
| gpipe-supp / 4 | 4 | Temperature sampling interpolates empirical versus nearly uniform language distributions with T=5 used. TableS2 varies batch size and reports BLEU/NLL; discussion shifts to depth/generalization. |
| gpipe-supp / 5 | 5 | FigureS3 compares training loss over steps for6/12/64-layer cases. Text holds effective batch, optimizer and width fixed and distinguishes observed convergence from conjectured preconditioning. References1–8 begin. |
| gpipe-supp / 6 | 6 | References9–16 close the supplement with batch-size/generalization and depth/optimization literature; page has no extra table/figure. |

### Complete figure and table inventory

Every item below was opened in original rendered pixels with its caption. Exact image path/hash is recorded per item in JSON.

| Item / location | Observed argument and encoding | Transfer and limit |
| --- | --- | --- |
| Figure1 / gpipe p2 | Two scatterplots map parameters(M/B) to ImageNet top1 and averageBLEU; red highlight marks largest proposed model, black baselines carry direct names. Correlation motivates scaling but confounds architecture/data changes. | Use a problem-evidence panel only with actual comparable data; do not infer scheduler fairness from model-size trends. |
| Figure2 / gpipe p3 | Panel(a) model partitions across four devices links forward/backward; (b) naive time schedule leaves most devices idle; (c) microbatch diagonal wavefront shrinks bubble and delays synchronous updates. Device colors stay consistent. | Strong transfer to waiting-state scheduler: separate dependency graph from time schedule, mark idle/wait intervals, show actual invariants. Do not import pipeline gradient semantics into general job scheduling. |
| Figure3 / gpipe p7 | DeltaBLEU against horizontal bilingual baseline, languages sorted by descending data, multiple depth/width curves and points. Right-side low-resource gains are visible; language identities not labeled. | Adapt ordered heterogeneity view for task wait times/fairness only with stated sorting key and task labels or index mapping. |
| Table1 / gpipe p4 | Maximum model capacity separates parameter count, parameter memory and peak activation, withGPU andTPU blocks and naive/pipeline configurations. | Adopt resource accounting by type; total memory across devices is not per-device capacity. |
| Table2 / gpipe p5 | Normalized throughput varies partitionK and microbatchM for two networks; M1 controls pipeline absence; caption admits batch-size adjustment if memory requires. | Adopt controlled scheduler settings and an inactive-mechanism baseline; disclose workload changes that weaken comparison. |
| Table3 / gpipe p5 | Normalized throughput onGPUs without high-speed interconnect, fixedM32, examines communication assumption rather than just headline scaling. | Adopt stress test of a specific required resource; do not treat TPU andGPU results as hardware-identical. |
| Table4 / gpipe p5 | Officially numbered table is a pie chart: compute65.6%, recompute22.5%, smaller update/imbalance/bubble/setup slices. Components explain lost ideal throughput. | Prefer labeled bar or stacked-duration plot for our small overhead categories; retain official ID in evidence inventory. |
| Table5 / gpipe p6 | Eight image datasets list train/test/classes, accuracy and prior best; caption/asterisks qualify private pretraining and repetitions. | Adopt explicit comparability caveats and per-task metric units; do not claim uniform superiority from a mixed-source table. |
| SupplementFigure1 / gpipe-supp p2 | Syntax-colored code listing builds16convolutions and checks gradient norm for partitions1/2/4 with a fixed seed/tolerance. It is a displayed invariant test. | Move detailed fixture code to appendix and reference the invariant in main text; an image of test code is not an executed test receipt. |
| SupplementFigure2 / gpipe-supp p3 | Descending bar chart of102language data volumes spans roughly35k–2b examples on log y. It reveals the imbalance behind the sampling choice. | Adopt workload distribution before aggregate fairness claims; ensure axis unit and log scale are explicit. |
| SupplementFigure3 / gpipe-supp p5 | Loss over training steps for6/12/64layers shows deeper-model trajectories under fixed batch/optimizer/width; small figure and ticks reduce legibility. | Adopt controlled convergence curve when own longitudinal evidence exists; enlarge to final reading size. |
| SupplementTable1 / gpipe-supp p1 | Per-transfer-dataset learning-rate/L2 settings follow disclosed held-out selection and five repeats. | Keep reproducibility settings in appendix; move only mechanism-critical parameter values into main text. |
| SupplementTable2 / gpipe-supp p4 | Batch260k/1m/4m tokens paired with BLEU andNLL makes batch-scaling result different from model-depth result. | Keep changed independent variables isolated; no transfer of empirical values. |

### Five writing dimensions

**organization — §1 pp1–2; §2 pp2–4; §3 pp4–5; §§4–5 pp5–7; §6 p8**

GPipe moves from general scaling constraint to concrete library interface and schedule, resource/performance analysis, two architecture/task demonstrations, then trade-off comparison. It does not start with installation or API usage. Supplement isolates code example and training recipes.

Transfer: Scheduler draft should lead with failed progress semantics and cost of thatfailure, introduce states/transitions and schedulingrule, evaluate controlled fixtures, then discuss model/host limits. Use implementation details only when needed to explain behavior.

Limit: The librarypaper has evidence from giant realmodels. Our schedulerfixtures and geometryderivations cannot inherit that externalvalidity; do not mimic scale-based opening claims.

**claim_evidence — Figure2 p3; Tables1–4 pp4–5; §5 p7; Supplement§2.2 p3**

Mechanism predicts lower idle time; M×K comparison probes it. Memory capacity, training throughput and downstream accuracy are separate. BalancedTransformer versus unevenAmoebaNet exposes load-balance explanation. Synchronous semantics have a displayed test and an empirical consistency check, although accuracy-within-standarddeviation is not formal equivalence.

Transfer: Distinguish liveness correctness from fairness and throughput. Use a matched no-mechanism baseline, varied waitduration/queueorder, and per-task completion evidence. State tested settings before any generalization.

Limit: Do not label normal waiting as retryfailure; this is our own semantic question, not a result established by GPipe. Do not equate lack of significance with equivalence.

**figures — Figure2 p3; Figure3 p7; Table4 p5; SupplementFigure2 p3**

Figure2 shows both dependency topology and execution timeline with identical device colors. Time-arrow and bubble connect mechanism to lost utilization. Figure3 uses a resource-sorted task axis to expose heterogeneity. Table4 pie provides component proportions but smallslices are hard to compare.

Transfer: Adapt the separate topology/timeline panels to states, eligibility and dispatch. Use clear waiting bands and event labels; show task distributions alongside aggregate cost. Prefer aligned durationbars to overheadpie.

Limit: A scheduler timeline must come from a real trace or be explicitly illustrative; do not render an invented fair schedule as observation.

**rhetoric — §2.2 p3; §3 pp4–5; §5 p7; §6 p8**

Functional subsections explain what each designchoice buys and what it costs. The discussion moves from measured depth/width behavior to qualified suggestions rather than declaring a universal law. Text admits imbalance and single-layer-memory limits. The final three properties summarize earlier evidence.

Transfer: Use claim→reason→bounded evidence paragraphs. Name user-visible effects (progress, starvationprevention, memoryfit) before implementation parameters. End with observed consequence and unresolved boundary.

Limit: Reject adjective-only giant/efficient/reliable claims without scope. GPipe webabstract usesTensorPipe while PDF usesGPipe: pin textualversion, do not combine names casually.

**content — §2.3 pp3–4; §6 p8; supplementpp1–6**

The main body devotes substantial space to recomputation, communication, loadbalance and normalization because these govern portability. Supplemental hyperparameters and code maintain reproducibility without turning maintext into a manual. Language-data imbalance is made visible, not hidden behind averageBLEU.

Transfer: For scheduler keep statecontract, resourcebudget and fairnessassumptions in main; move CLIfixture details/logs to appendix. For geometry keep layer recurrence/croppingconditions in main, tensor dumps in supplement.

Limit: Do not use private data/modelscale as rhetorical decoration. Workload distributions and untested host behavior must remain explicit gaps.

## EX06 — Deep Sets (NIPS 2017)

Publication: https://proceedings.neurips.cc/paper_files/paper/2017/hash/f22e4747da1aa27e363d86d40ff442fe-Abstract.html
Identity: `NIPS2017:f22e4747da1aa27e363d86d40ff442fe`
Selection: Theorem→architecture→applications style and carefulsymmetry assumptions useful for geometry and semanticcontracts.
Quality judgment: Published conferencepaper with explicitrepresentation results, baseline/ablationtasks, negativecases and substantialproofappendix; not all mainrhetoric is equallyprecise.

### Frozen sources

- official main paper: 11 physical pages; `ae1e9a4655b8ada5292b3dd3558dd7e18b05913106ebc36bf9f609c917f163c0`; https://proceedings.neurips.cc/paper_files/paper/2017/file/f22e4747da1aa27e363d86d40ff442fe-Paper.pdf
- official ZIP member deepsets-app.pdf; physical1–18 printed12–29; physical19–21 repeat printed9–11references: 21 physical pages; `39365ff775b89a07d6349c8b87e2e8a13095fe7e64548480b625b84f5d360bd9`; https://proceedings.neurips.cc/paper_files/paper/2017/file/f22e4747da1aa27e363d86d40ff442fe-Supplemental.zip

### Page-by-page actual reading

| Document / physical page | Printed page | Concrete observation |
| --- | --- | --- |
| deepsets / 1 | 1 | Abstract positions invariant/equivariant set functions as the contribution, not merely a pooling implementation. Introduction distinguishes supervised, unsupervised and expansion scenarios before a contribution paragraph. |
| deepsets / 2 | 2 | Property1 and Eq1 separately define invariance and equivariance. Theorem2 is countable-universe; uncountable fixed-cardinality scope is explicit. Lemma3 constrains a standard layer; deFinetti connection begins. |
| deepsets / 3 | 3 | Representer/spectral links lead to invariant and equivariant architectures. Section3.2 acknowledges existing pooling and locates novelty in characterization, parameter sharing and applications. |
| deepsets / 4 | 4 | Figure1 uses four paired statistical tasks; bottom panels vary training-set count. Figure2 tests digit sums beyond trained length. Application section announces scalar/set/expansion/anomaly uses before task-specific settings. |
| deepsets / 5 | 5 | Text-image digit-sum discussion explains accumulated classification error. Table1 distinguishes voxel, view and point-cloud representations; Table2 compares scatter for redshift methods. |
| deepsets / 6 | 6 | Table3 gives retrieval recall,MRR and median rank at multiple vocabulary scales. Equations5–6 derive set expansion scoring; conditioning section identifies relevant metadata. |
| deepsets / 7 | 7 | Retrieval subsection separates methods, evaluation and observations and admits a small-data loss. Table4 reports image-tag precision/recall/F1/N+; feature-access limitations qualify baseline fairness. |
| deepsets / 8 | 8 | Figure3 shows face-set anomaly examples with red truth frames and probability bars. Table5 separates image-blind and conditioned methods. Anomaly baseline fails near chance; summary emphasizes breadth rather than universal best accuracy. |
| deepsets / 9 | 9 | References1–19 cover distribution learning, astronomy, chemistry, symmetry and set models; include older pooling and order-based alternatives. |
| deepsets / 10 | 10 | References20–36 continue multiview/point-cloud models, datasets, cosmology and Bayesian sets. |
| deepsets / 11 | 11 | References37–55 include structured loss, LDA, word embeddings, image-tag methods/datasets, mathematical topology and optimizers; bibliography already contains appendix references. |
| deepsets-supp / 1 | 12 | Printed12: AppendixA proves countable case with injective coding; uncountable case restricts to fixed set size and ordered representative before sum-of-powers Lemma4. |
| deepsets-supp / 2 | 13 | Printed13: Newton–Girard coefficients make power-sum embedding injective. A cited roots/coefficient homeomorphism prepares inverse continuity Lemma6. |
| deepsets-supp / 3 | 14 | Printed14: Compact-domain inverse continuity supports Theorem7. Figure4 sketches embedding then continuous readout; diagram is a proof roadmap, not a learned network. |
| deepsets-supp / 4 | 15 | Printed15: Theorem7 completes continuous fixed-size representation. Kolmogorov–Arnold comparison and Theorem9 approximation state compactness/cardinality assumptions; arbitrary-size extension is conjectural. |
| deepsets-supp / 5 | 16 | Printed16: Worked examples construct sums/products/reciprocal sums and limiting max/second-largest expressions; sparse page intentionally separates examples from next proof. |
| deepsets-supp / 6 | 17 | Printed17: Lemma3 proof converts equivariance to commutation with permutations, assuming bijective sigmoid, then uses transpositions to tie diagonal and off-diagonal entries. |
| deepsets-supp / 7 | 18 | Printed18: Figure5 invariant architecture and Figure6 tied-weight layer accompany derivative and parameter-sharing discussion; optional conditioning is visibly separate. |
| deepsets-supp / 8 | 19 | Printed19: Figure7 equivariant architecture adds shared context without collapsing per-element outputs; Figure8 stacks equivariant layers. Equations22–23 clarify multi-channel shapes and max-pool alternative. |
| deepsets-supp / 9 | 20 | Printed20: AppendixD derives Bayesian set scoring, sufficient statistics, conjugate exponential-family and Beta-binomial forms; links concrete probabilistic construction to later learned aggregation. |
| deepsets-supp / 10 | 21 | Printed21: Binary model algorithmic form and Gaussian inverse-Wishart illustration explain nonlinear element features plus nonlinear aggregate readout; these are motivations, not generic empirical guarantees. |
| deepsets-supp / 11 | 22 | Printed22: Text retrieval details give LDA dataset construction, embeddings/layer widths, competing pooling/concatenation baselines, split and metrics. Small LDA-1k weakness is retained. |
| deepsets-supp / 12 | 23 | Printed23: Figure9 lists six latent topics as dataset examples. Image-tag section distinguishes ESP/IAPR/COCO data and frozen ResNet versus learned word embeddings, plus unavailable baseline code. |
| deepsets-supp / 13 | 24 | Printed24: Figure10 shows positive and failure images/tags using brown/green/red correctness roles. Failures include snowboard/ski, laptop/refrigerator and surfboard/plane confusion. |
| deepsets-supp / 14 | 25 | Printed25: Redshift task motivates grouping; Figure11 shows cluster size, labeled-data scarcity and predictions versus truth. Architecture, optimizer and excluded richness feature clarify comparison. |
| deepsets-supp / 15 | 26 | Printed26: Figure12 shows eight sampled point-cloud classes. Table6 expands ablations including pooling-only and graph convolution; text discloses slower graph baseline limited tuning. |
| deepsets-supp / 16 | 27 | Printed27: Figure13 visualizes maximally activating point clouds at two layers; low-level localized versus higher-level surface structure is interpretation, not proof. Anomaly architecture and dropout details follow. |
| deepsets-supp / 17 | 28 | Printed28: Figure14 expands face-set anomaly examples; red frames mark ground truth and per-image bars scores. Caption refers to attributes on right but no attribute text appears here, a caption/figure mismatch. |
| deepsets-supp / 18 | 29 | Printed29: Figure15 supplies another qualitative face grid with same frame/bar encoding; neither grid alone estimates accuracy or fairness across demographic groups. |
| deepsets-supp / 19 | 9 | Printed9 repeated: Supplement repeats references1–19, including distribution and equivariance context. This physical page was still read; it is not counted as a new paper. |
| deepsets-supp / 20 | 10 | Printed10 repeated: References20–36 repeat model representations, point-cloud datasets and cosmology/Bayesian-set sources. |
| deepsets-supp / 21 | 11 | Printed11 repeated: References37–55 repeat retrieval/tagging, topology and optimization sources; no additional appendix follows. |

### Complete figure and table inventory

Every item below was opened in original rendered pixels with its caption. Exact image path/hash is recorded per item in JSON.

| Item / location | Observed argument and encoding | Transfer and limit |
| --- | --- | --- |
| Figure1 / deepsets p4 | Four columns pair statistical target fits(top) with MSE versus number of training sets(bottom); SDM green circles/triangles and DeepSets red are consistent. Axes differ by task and scale; small-data disadvantage is visible. | Adopt paired mechanism/output and error-versus-budget views; preserve per-panel units, never silently share incomparable MSE scales. |
| Figure2 / deepsets p4 | Text/image digit-sum accuracy against test length, trained length≤10; DeepSets blue persists as recurrent baselines collapse. Image panel decreases gradually due to per-digit error accumulation. | Adopt out-of-training-range stress test with train-range marker; extrapolation here does not validate arbitrary geometry. |
| Figure3 / deepsets p8 | Five face-set rows use red ground-truth frames, green ticks/red cross and per-image probability bars; attributes are described at right. | Adopt qualitative success plus failure examples with explicit truth/prediction distinction; no demographic/fairness inference from portraits. |
| Figure4 / deepsets-supp p3 | Original-space cloud→higher-dimensional embedding→real target illustrates proof construction. Bidirectional homeomorphism versus one-way continuous readout encodes different mathematical roles. | For valid-conv geometry, show domain mapping and conditions, not just boxes; do not claim a homeomorphism for dimension-losing pooling. |
| Figure5 / deepsets-supp p7 | Blue per-element stacks go through sharedphi, sum, thenrho; optional green metadata conditioning is a separate dashed box. | Adapt shared transforms and reduction symbols when mathematically valid; keep ordered spatial axes in image networks. |
| Figure6 / deepsets-supp p7 | Bipartite neurons use two edge colors for diagonal/off-diagonal weight-sharing classes; caption supplies color semantics. | Adopt repeated-weight encoding only for actual shared operators; dense hairball edges can obscure large architectures. |
| Figure7 / deepsets-supp p8 | Equivariant architecture retains blue per-element outputs and combines localLambda with aggregateGamma branch. | Adopt output-shape contrast between reduction and per-element mapping; distinguish invariant from equivariant outputs. |
| Figure8 / deepsets-supp p8 | Two repeated equivariant layers communicate compositional closure; stacks and branch symbols retain the same semantics. | Use repetition labels for repeated image blocks but preserve actual crop/size changes, which this set diagram does not model. |
| Figure9 / deepsets-supp p12 | A six-column word table is numbered as a figure and illustrates coherentLDA topics, not retrieval accuracy. | Keep examples visibly separate from quantitative evidence; retain official figure ID even when its geometry is tabular. |
| Figure10 / deepsets-supp p13 | Six image/tag cases: top successes, bottom failures. Brown marks matchedtruth,green plausible unannotated tags,red wrong tags; caption names three confusion modes. | Adopt a failure taxonomy grounded in individual cases; avoid calling unannotated predictions proven correct without an explicit review rule. |
| Figure11 / deepsets-supp p14 | Two histograms establish cluster-size/labeled-data availability, third scatter compares estimated redshift versus truth with diagonal reference and translucent competing points. | Adopt distribution+error diagnostic where aggregate metric hides composition; shared plottedcloud is illustrative, not a significance test. |
| Figure12 / deepsets-supp p15 | Two instances across eightpoint-cloud class columns use2Dplane projections alongside3Dparticles to reveal spatial structure. | For image geometry use actual tensor/crop coordinate examples; avoid decorative projections that carry no quantitative role. |
| Figure13 / deepsets-supp p16 | Two layers of optimized maximally-activating point clouds, two views per unit; first layer localized and second more surface-like. Lowcontrast requires zoom. | Adopt feature visualization only with an explicit optimization protocol and interpretation limits; increase contrast/readability. |
| Figure14 / deepsets-supp p17 | Expanded face grids show scored examples; truth redframes and probabilitybars persist. Caption mentions right-side attributes absent in this panel. | Reject stale captions when expanding qualitative grids; same sample presentation does not constitute a population estimate. |
| Figure15 / deepsets-supp p18 | Second anomalygrid supplies further scored sets with same encoding, including dispersed probability mass and both easy/difficult examples. | Adopt purposeful case selection with declared rule; avoid page-filling qualitative evidence without distinct question. |
| Table1 / deepsets p5 | ModelNet40 accuracy alongside instance size and representation prevents comparing pointcloud/voxel/multiview as identical input regimes. | Adopt representation and budget columns when comparing exact/approxattention or geometry variants. |
| Table2 / deepsets p5 | Compact redshift scatter comparison states lower is better; few rows keep mechanism improvement legible. | Adopt minimal task-relevant metrics; label metric formula and aggregation in body. |
| Table3 / deepsets p6 | Recall@10/100/1k,MRR,medianrank grouped by3vocabulary scales; bold does not hide weakerLDA1k results. | Adopt stratification plus direction-of-improvement labels; too many metrics in main table may overburden short drafts. |
| Table4 / deepsets p7 | Image-tagP/R/F1/N+ across two datasets records competing precision/recall outcomes; caption admits precision is weaker. | Adopt trade-off reporting over a single winner metric; inputfeature discrepancies belong beside comparison. |
| Table5 / deepsets p8 | COCOtag retrievaltable separates image-blind word and set baselines from conditionedDeepSets, exposing extra-information factor. | Adopt information-availability columns/baseline naming; do not attribute conditioning benefit exclusively to architecture. |
| Table6 / deepsets-supp p15 | Expanded ModelNet table includespointcount,transformations,pooling-only,graph baseline and externalrepresentations. Errorbars derive from test-particle choices over3trials, per nextpage footnote. | Adopt meaningful ablations and exact uncertainty definition; do not rename these intervals training-seed uncertainty. |

### Five writing dimensions

**organization — §1 p1; §2 pp2–3; §3 p3; §4 pp4–8; AppsA–I**

DeepSets begins with a family of objects and desired symmetry, states a representation theorem, translates it into architecture, then spans multiple applications. Connections and relatedwork surround the mathematicalconstruction, so readers can distinguish known pooling from the characterization. Appendix follows proof→architecture→probabilisticmotivation→taskdetails.

Transfer: Geometry draft can define spatialdomain/validconvolution constraints, derive recurrence, show compositional construction, then verify illustrative networks. State what the construction guarantees before presenting implementationchecks.

Limit: Do not force a theorem onto finite test observations. Set symmetries do not justify treating an ordered imagegrid as an unordered set.

**claim_evidence — Theorem2/Lemma3 p2; AppA printed12–16; Table3 pp6–7; Table6 printed26**

The claimfamily is stratified: countable-universe characterization, continuous fixed-cardinality result, approximation and unresolved arbitrary-size conjecture. Task experiments show usefulness but cannot prove universality. Controlled pooling variants and size/representation tables probe alternatives, while weaksmall-data results and graphbaseline tuning limits are disclosed.

Transfer: Make geometry claims conditional on stride/padding/dilation/inputdivisibility and distinguish derived identities from empirical sanitychecks. Attention exactness and approximation must similarly have separate contracts. Retain counterexamples that locate a boundary.

Limit: Do not cite mainabstract alone for a universal allsets theorem; proofassumptions narrow it. Do not use an application benchmark as proof of an architectural invariant.

**figures — Figure1 p4; Figures4–8 printed14,18–19; Figure10 printed24; Figure11 printed25**

Proofdiagram maps spaces while architecturediagrams map data and preserve outputtype. Shared colors encode elementfeatures/conditioning, tiededge colors encode parameterclasses. Applicationfigures pair distribution and prediction, and failures receive an explicit qualitativepanel. Several caption/placement and legibility defects remain despite venuequality.

Transfer: Use a compact mathematicalgeometry panel for input/outputdomain and a separate networkdiagram with dimensions/crops. Use a workedcounterexample panel when naïve sizepropagation fails. Include failures with truth/prediction distinctions.

Limit: Do not copy setstack icons into imagegeometry if they imply permutationinvariance. A visuallyappealing map is not proof of invertibility; labels must state information loss.

**rhetoric — §2.2 p2; §3.2 p3; §4.2.1 p7; AppA printed15**

The paper openly narrows proofscope, acknowledges known pooling, and articulates exact novelty relative to it. Empirical subsections repeat task→method→evaluation→observations, including conjectured reasons for weaknesses rather than asserting them as facts. This consistency helps a broad application paper remain readable.

Transfer: Use definitions before overloadedterms, then explain the function of equations in words. For each test say what question it resolves and what it cannotresolve. Label hypothesized explanations and futureextensions.

Limit: Do not adopt theoremstyle confidence for fixtures or silently omit assumptions to make prose smoother. Avoid repetitive boilerplate if there is only one experimentfamily.

**content — §§2–4 pp2–8; AppC printed18–19; AppsE–I printed22–29**

Main text balances theory and applicationbreadth; appendix retains topologyproofs, multi-channel notation, trainingrecipes, qualitative failures and ablations. Task-specific representation and featureaccess differences matter to interpretation. Repeated references and extra grids add pages but not new conceptual claims.

Transfer: Allocate space according to own contribution: derivationcentral for geometry, state semantics for scheduler, fidelity/costtradeoff for attention. Put ancillary recipes after decisive evidence. Provide a small assumptiontable if several mechanisms reuse symbols differently.

Limit: Do not pad workingpapers with unrelated benchmarksections or redundant qualitative grids. Broad applicability in a published exemplar is not evidence of our methodgenerality.

## Cross-paper lessons

- All three begin with a reader problem and a proposed explanatory mechanism rather than commands, artifactlists or acceptancechecklists. Operational details serve the mechanism and reproducibility, not the introduction.
- Organization follows contributiontype: FlashAttention separates exact algorithm, complexity and hardwareeffects; GPipe connects scheduling to capacity and taskdemonstrations; DeepSets derives architecturalform from formal symmetry. No single fixed section/page formula should be imposed on all3workingpapers.
- Semantics-preservation, performance, downstreamquality and scope of generalization need different evidence. A proof cannot establish measured speed; performance cannot establish correctness/fairness; applicationbreadth cannot prove universality.
- Useful figures answer specific questions: mechanism flow, counterfactual schedule, crossover, condition-sensitive ablation, proofmap, failurecase. Figures should not merely inventory softwaremodules.
- Boundaries are part of the argument: tunedbaseline losses, unbalancedlayers, private/heterogeneousdata, fixedcardinality proof assumptions and limitedtuning. State our missing evidence instead of upgrading a workingpaper to a venue-sized claim.
- Published examples also contain flaws: FlashTable4 numeric mismatch, GPipeHTML/PDF name mismatch, DeepSets repeatedreferencepagination and stale qualitativecaption. Learn the rhetorical purpose while checking every own number and label.

## Handoff to root blueprint

- **systems waiting/fairness** (adapt; EX05 Figure2 pp3–5; EX04 Figure2 p6): Put observable failure and stateinvariant before ready/wait/dispatch algorithm, then separate safety/liveness/fairness/overheadtests. Draw dependency/state view plus actualtrace timeline. Own evidence: MISSING in this readercontext; root must bind actual scheduler fixtures/logs and uncoveredhostlimits.
- **exact/approximate attention** (adapt; EX04 §§3–4; Figure3 p9; E.6 p28): Define exacttarget and approximationcontract separately; prove/validate output before discussing cost. Plot measured crossover and report tunedbaseline or explicitgap. Own evidence: MISSING in this readercontext; root must bind actual implementation,precisionchecks,hardware,timings.
- **valid-convolution image-network geometry** (adapt; EX06 §2 p2; AppA pp12–16; Figures4–8 pp14,18–19): Lead with inputdomain and layerrecurrence assumptions; derive composition and demonstrate dimension/crop counterexamples. Keep proofmap and networkgeometry separate. Own evidence: MISSING in this readercontext; root must bind own symbolicderivation and actual renderednetworkchecks.
- **all3workingpapers** (reject; EX04 AppE; EX05 supplement; EX06 AppsE–I): Do not copy benchmarkbreadth, scientificresults, sourcefigures or contributionstrength. Move reproducibilitydetails to appendices but retain decisive assumptions and limits in maintext. Own evidence: Each draft requires its own evidenceledger; exemplar IDs cannot fill it.

## Acceptance boundary

The requested reading and writing analysis for EX04–EX06 are complete. All selected-version pages, including appendices and repeated reference pages, are covered. Supplemental ZIP links that failed in web extraction were recovered directly from official proceedings URLs; no access bypass was used. No PDF/image was added to the repository, no manuscript or Skill was edited, and no inference is made that these papers establish our results. Root owns final preflight acceptance and independent verification.
