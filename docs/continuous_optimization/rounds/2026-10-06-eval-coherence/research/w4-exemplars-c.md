# T24 writing exemplars — reader C

Recorded 2026-10-06T13:16:00.248018+00:00. Reader `/root/exemplar_read_c`. Four published original papers, 71 physical pages; 46 original-numbered figures/tables and four additional algorithm boxes actually viewed. All text pages, references and selected-version appendices read. Text-only pages are not represented as pixel reads. This is writing-exemplar preparation, not a new Agent-research-paper count.

The exact page receipts, PDF/render/text SHA256 values, complete figure inventory and five-dimension analyses are in `w4-exemplars-c.json`; third-party PDFs and images remain outside the repository. Root must verify the ten-paper corpus and complete synthesis/blueprint before drafting.

## EX07 — Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift

Published: ICML / PMLR37 (2015); [official record](https://proceedings.mlr.press/v37/ioffe15.html).

Official proceedings PDF,9pages,pp448–456.

PDF SHA256: `f2eb20b4e97409aef516a6506ea76c7c051860eeded3006a6d9687c364847b27`. Coverage: physical pages1–9; 4 figures/tables.

**organization — pp1–3 Sections1–3;pp5–8 Sections4–5.** The paper turns a familiar optimization issue into a local network problem, then rejects an intuitive but defective normalization approach before giving the implementable transform. Small diagnostic experiments precede full ImageNet results. Transfer/limit: Adapt failure-example→mechanism→small diagnostic→broader evaluation for waiting/fairness; limit broad evaluation to available original data.

**claim_evidence — p2 bias counterexample;p5 Section3.3;p6 Section4.2.1;p7 Figures2–3.** Mechanism derivation, speculative Jacobian story, and measured acceleration coexist but have different certainty. The headline fastest variant includes multiple changes, whereasBN-baseline isolates the normalizer. Transfer/limit: Adopt an explicit claim ladder and separate minimal fix from tuning bundle; do not claim14x or normalization causality for new tasks.

**figures — p6 Figure1;p7 Figures2–3;p8 Figure4.** Diagnostic and outcome traces answer different questions; target-step table makes the fixed-quality comparison exact; final table discloses inference budgets. Transfer/limit: Adapt a scheduler-state diagnostic next to outcome evidence, and separate latency/work/quality rather than treating one metric as system utility.

**rhetoric — p5 Section3.3;p6 Section4.1;p8 conclusion.** The author signals conjecture and false idealizing assumptions, states why MNIST is not anSOTA experiment, and reserves untested extensions for future work. Some broader mechanistic language remains stronger than its identification evidence. Transfer/limit: Adopt explicit verbs by evidence type: derive, measure, hypothesize. Reject inherited grand claims or implying observed association proves mechanism.

**content — pp3–5 algorithms and inference;pp6–7 setup and variant list;p8 limitations.** Enough mathematical and algorithm detail appears before results to identify the intervention; full training modifications are disclosed before comparing them. Limits occupy substantial conclusion space. Transfer/limit: Adapt a concise state/invariant specification before results; move routine implementation listings to reproducibility material, retain confounders and boundaries in main text.

### Page-by-page observations

- p1: Abstract defines a changing internal input distribution and makes a training-step claim. Introduction starts from minibatch SGD and decomposes a network into F1 and F2 to explain the reader problem.
- p2: Introduction links sigmoid saturation to moving inputs; Section 2 uses a bias-only normalization counterexample to explain why normalization must participate in differentiation. This is a mechanism argument, not simply a performance promise.
- p3: Section 3 states two simplifications explicitly: per-feature moments instead of full whitening, then minibatch estimates. Learned gamma/beta restore representational freedom; examples in a minibatch remain coupled.
- p4: Algorithm 1 and derivative equations specify the transform. Section 3.1 separates training minibatch statistics from deterministic population-statistic inference; Section 3.2 begins placement before nonlinearity.
- p5: Algorithm 2 gives train-to-inference conversion. Convolution shares statistics over batch and spatial positions. Section 3.3 distinguishes a scale-invariance derivation from a Jacobian conjecture with knowingly unrealistic Gaussian/linear assumptions.
- p6: Figure 1 pairs MNIST test-accuracy trajectory with sigmoid-input percentile trajectories. The text explicitly rejects a MNIST state-of-art purpose. Section 4.2 defines the Inception variant and enumerates additional tuning changes.
- p7: Figures 2/3 compare training curves and steps to a fixed accuracy. BN-only and jointly tuned variants are distinct. BN-x30 starts slower than BN-x5 but ends higher; the text leaves this counterintuitive result open. Ensemble protocol follows.
- p8: Figure 4 is a table of resolution/crops/model count/errors and marks test-server results separately. Conclusion repeats the mechanism and identifies untested RNN, regularization, domain-adaptation, and theoretical directions.
- p9: References span initialization, optimization, domain adaptation, normalization, ImageNet and architecture sources. The selected 9-page proceedings PDF ends here; it contains no appendix.

### Complete figure/table inventory (actual pixel views)

- **Figure1, p6**: Three panels: test accuracy versus training steps; without/withBN sigmoid-input15/50/85 percentiles. Percentiles are distributions, not confidence intervals. Tiny panels depend on caption for meaning. Transfer: Adapt paired outcome/diagnostic panels; keep units and diagnostic status explicit; do not infer causality from one activation.
- **Figure2, p7**: Single-crop validation accuracy versus steps in millions; color and line style distinguish five variants, diamonds mark a common72.2% target. No replicate uncertainty is shown. Transfer: Adapt fixed-target comparison only where own measurement supports an equal-quality target; prefer direct units and accessible redundant marks.
- **Figure3, p7**: Tabular figure separates steps-to-target from maximum accuracy; sigmoid row has no target-step value because it did not reach the target. Transfer: Adopt distinct target attainment and best-result columns; preserve failed/unreached cases rather than dropping them.
- **Figure4, p8**: Tabular figure includes resolution, crop count, model count, top1/top5; asterisks distinguish test-server results from validation. Transfer: Adopt explicit evaluation-budget and split columns; reject pooling incompatible protocols under one ranking.

## EX08 — Dropout: A Simple Way to Prevent Neural Networks from Overfitting

Published: JMLR15(56) (2014); [official record](https://jmlr.org/papers/v15/srivastava14a.html).

Published journal full text,30pages,pp1929–1958,includingAppendicesA/B.

PDF SHA256: `9c196ccbe6c6a595a1adba6cd030d35f7c2e548bbf5e7f1278b0109d8dd9ebaa`. Coverage: physical pages1–30; 23 figures/tables.

**organization — pp1–7 conceptual/model/learning;pp8–14 utility;pp15–23 diagnostics/extensions;pp24–27 appendices.** The long journal format allows intuitive mechanism, formal specification, application breadth, controlled diagnostics, mathematical special cases and practical recipe to serve distinct reader needs. Transfer/limit: Adapt the separation of utility, mechanism and reproduction; reject copying a30-page journal structure into short working papers or adding irrelevant domains.

**claim_evidence — p14 Table8;p17 Figure9;p18 Figures10–11;p22 Section9.1.** The paper asks where the method loses, changes controls to distinguish capacity from retention, keeps negative small-data cases, and restricts analytic equivalence to linear regression. Transfer/limit: Adopt exact-vs-approximate trade-off evaluation and negative cases; for geometry make derivations exact only under named assumptions; no original benchmark gains become own evidence.

**figures — pp2–6 Figures1–3;p17 Figure9;p18 Figure11.** Overview, inference contract and local operation receive separate diagrams rather than one overloaded picture. Two controlled experimental frames and a cost/approximation comparison guide interpretation. Transfer/limit: Adapt a two-level geometry/state figure plus a separate exact/approximate error/cost plot where data exist. Fix undefined uncertainty and avoid unlabeled dense trajectories.

**rhetoric — p13 Section6.4;p16 Section7.1;p22 Section9.2;p24 conclusion.** The text openly anticipates losing toBayesian averaging, names a coadaptation hypothesis, limits deep-network marginalization, and acknowledges training overhead. Biological/conspiracy analogies are memorable but lengthy and non-evidentiary. Transfer/limit: Adopt candid limitations and explain what each experiment tests. Reject metaphor-heavy motivation, subjective filter beauty as proof, and superlatives unsupported by current evidence.

**content — pp6–7 training options;pp23–27 noise extension/limitations/AppendicesA–B.** Broad tables establish usefulness; fixed-architecture and sensitivity studies diagnose it; concrete split/tuning/architecture details live in appendices with caveats about validation refit and runtime overhead. Transfer/limit: Adapt independent evidence sections and reproducibility appendix. Keep essential experimental unit, protocol and uncertainty definitions near results; do not defer conditions that change interpretation.

### Page-by-page observations

- p1: Abstract frames both overfitting and expensive ensemble inference. Introduction motivates regularization through finite-data sampling noise and then moves toward model averaging.
- p2: Figure1 introduces deletion of units and edges through a paired network drawing. Prose defines temporary stochastic thinning and shared parameters, then distinguishes hidden/input retention probabilities.
- p3: Figure2 separates training randomness and deterministic scaled inference. The text repeatedly calls ensemble averaging approximate and gives a roadmap covering mechanism, experiments, analysis and appendices.
- p4: Section2 offers evolutionary mixability and conspiracy analogies for coadaptation; they supply intuition but no scientific proof. Related work begins by locating noise injection in denoising autoencoders.
- p5: Related work distinguishes expected-noise loss from adversarial deletion. Section4 aligns standard and dropout feed-forward equations using independent Bernoulli masks and elementwise products.
- p6: Figure3 aligns the unchanged weighted-sum/nonlinearity path with inserted masking operations. Section5.1 states that unused parameters contribute zero gradient and introduces max-norm constraints.
- p7: Learning section distinguishes dropout alone from dropout with large learning rates/momentum/max-norm; pretraining fine-tuning needs smaller rates. Experimental section begins with a domain-diverse dataset list.
- p8: Table1 summarizes domains/dimensions/splits; Table2 separates activations, architecture and pretraining in MNIST comparisons. Table1’s CIFAR training count60K conflicts with AppendixB.3’s50K; preserve this as a source inconsistency.
- p9: Figure4 shows paired clusters of six architecture trajectories without architecture-specific retuning. MNIST interpretation excludes spatial augmentation. SVHN setup begins with convolutional and fully connected layers.
- p10: Table3 includes external feature baselines, internal dropout-placement ablations and human reference. Text distinguishes fully-connected-only from all-layer dropout. CIFAR setup points to the appendix.
- p11: Figure5 illustrates within-class variation rather than performance. Table4 separates CIFAR10/100. ImageNet discussion explains top1/top5 and the availability of ILSVRC2010 test labels.
- p12: Figure6 includes plausible mistakes and ground-truth labels in qualitative examples. Tables5/6 separate competition years and validation/test values, and single networks versus ensembles. TIMIT setup begins.
- p13: Table7 shows pretraining/depth/dropout combinations for speech. Reuters has a smaller gain, stated candidly. Bayesian-network comparison is explicitly designed to reveal what the approximation loses.
- p14: Table8 keeps Bayesian NN above dropout on code quality. Section6.5 fixes one MNIST architecture and tunes each regularizer via validation to compare methods. Section7 announces diagnostic rather than benchmark questions.
- p15: Table9 isolates regularizer combinations. Figure7 contrasts learned autoencoder filters; Section7.1 frames coadaptation as a hypothesis. Filter appearance is qualitative support, not independent identification of a general causal mechanism.
- p16: Figure8 separates mean-activation histograms from individual activations and reveals increased mass at zero. Text reports both models had similar reconstruction error, which prevents equating prettier filters with better reconstruction.
- p17: Figure9 uses two experimental controls: fixed network size and fixed expected retained size. Train and test errors distinguish underfitting at low retention from high-retention overfitting.
- p18: Figure10 shows dropout does not improve extremely small datasets. Figure11 compares costly Monte Carlo averaging with weight scaling across sample count, with uncertainty bars; adjacent prose motivates the approximation question.
- p19: Text interprets MonteCarlo differences as within one standard deviation. Section8 gives the joint dropoutRBM distribution and explicit masking constraint, rather than assuming feed-forward notation transfers without change.
- p20: Figure12 shows RBM filters ordered by norm. Conditional distributions and CD1 training explain how masking changes the generative model while preserving a usable learning procedure.
- p21: Figure13 shows RBM activation sparsity. Section9 separates analytic marginalization from stochastic simulation and reviews deterministic feature-deletion-related work.
- p22: Section9.1 derives linear dropout’s expected squared-error objective as weighted ridge regularization. Section9.2 warns that approximate marginalization assumptions weaken with depth; the linear result is not promoted to a deep-net theorem.
- p23: Table 10 compares Bernoulli/Gaussian noise over10 random seeds but does not explicitly name the plus/minus statistic. Section10 matches first two moments, calls evidence preliminary and explains train-time inverse-retention scaling.
- p24: Conclusion states a training-time drawback (typically2–3x for same architecture) and a regularization/time trade-off. AppendixA begins practical heuristics and explicitly says hyperparameter tuning remains necessary.
- p25: AppendixA gives learning-rate/momentum/max-norm/retention heuristics. AppendixB begins reproducibility details and MNIST validation-then-refit procedure, which differs from generic early stopping.
- p26: AppendixB names the six MNIST architectures, preserves worse3-layer wide results, gives SVHN validation sampling and layer/filter sizes, and defines CIFAR50K/10K with contrast normalization/ZCA.
- p27: AppendixB completes TIMIT preprocessing/decay/pretraining, Reuters single-label subset and split, and alternative-splicing code-quality formula plus5-fold averaging. These are necessary operational definitions absent from headline tables.
- p28: References begin with marginalized autoencoders, dropout comparators, convolutional models, biological motivation and CUDA tooling. They preserve provenance for benchmark baselines and implementation components.
- p29: References continue speech, Bayesian methods, data, Kaldi, regularization, optimization and the precursor thesis. This is not a further result page.
- p30: References end with Tikhonov, noise marginalization, denoising, fast dropout, alternative splicing and stochastic pooling. The30-page published JMLR article ends here; all appendices and reference pages were read.

### Complete figure/table inventory (actual pixel views)

- **Figure1, p2**: Paired layered graphs share node positions; crossed circles and removed edges distinguish one sampled thinned net. Black-only encoding is readable but edges are dense. Transfer: Adapt aligned before/after topology with unchanged layout; reduce edges or aggregate when graph density obscures the actual change.
- **Figure2, p3**: Two simple unit drawings contrast random presence/w with deterministic presence/pw; caption explains the local expected contribution. Transfer: Adapt train/inference or exact/approximate contract contrast, while explicitly avoiding an unsupported claim of full nonlinear equivalence.
- **Figure3, p6**: Aligned node equations show Bernoulli gates inserted before weighted sum; bias and nonlinearity remain visible. Transfer: Adopt local operation expansion adjacent to formal equations; preserve tensor/index semantics and distinguish unchanged parts.
- **Figure4, p9**: Many architecture trajectories in two clusters show classification error% versus weight updates; direct arrows label dropout/no-dropout, but individual architecture colors are not mapped in legend. Transfer: Adapt direct condition labels, reject unmapped traces where per-workload identity matters.
- **Figure5, p11**: SVHN/CIFAR image grids use rows as categories to convey appearance and variability, not performance. Transfer: Use example inputs only when representation is part of the reader problem; no decorative benchmark grids for scheduler or attention papers.
- **Figure6, p12**: Four image examples with four prediction bars each; pink highlights ground truth and bar length probability. Two examples show plausible wrong top predictions. Transfer: Adapt representative success/failure examples if sampling and provenance are disclosed; qualitative examples do not establish population accuracy.
- **Figure7, p15**: Two256-filter mosaics compare autoencoder features; dropout yields visibly localized strokes/spots. No statistical sampling evidence accompanies visual appeal. Transfer: Use such diagnostics as qualitative evidence only; do not make geometry correctness depend on visual plausibility.
- **Figure8, p16**: Four histograms: mean activation and individual activation for each condition. Count ranges differ markedly and the latter dropout histogram has a dominant zero bin. Transfer: Adopt separating distribution of means from distribution of observations; use compatible axes or clearly mark count-range changes.
- **Figure9, p17**: Two panels compare retention probability under fixedn versus fixedpn; train/test colored errorbar series expose underfitting/overfitting. Caption does not define interval statistic or n. Transfer: Adopt controlled-resource versus controlled-architecture distinction; reject undefined error bars in new manuscripts.
- **Figure10, p18**: Error% versus logarithmic dataset size with connected measured points and error bars; no improvement at smallest sizes is retained. Interval definition/replicate count is not explicit here. Transfer: Adopt retaining negative regimes and declaring log scaling; require own uncertainty definitions and avoid extrapolating connected points.
- **Figure11, p18**: MonteCarlo sample count versus test error; weight-scaling reference horizontal with errors, MC blue points/bars approach it. Next-page text mentions oneSD but does not fully specify replication unit here. Transfer: Adapt cost/approximation-quality comparison for attention only with separately measured quality/cost and clear sampling unit.
- **Figure12, p20**: RBM filter mosaics are ordered byL2 norm; dropout/non-dropout may occupy different positions because order is condition-specific. Transfer: Adapt sorted diagnostics only when sorting is disclosed; do not imply same grid position is a matched unit.
- **Figure13, p21**: Mean and individualRBM activation histograms for both conditions, with varying count scales and high zero mass under dropout. Transfer: Adapt distribution diagnostics with explicit denominators and shared binning; never confuse activation dispersion with estimator uncertainty.
- **Table1, p8**: Dataset/domain/dimension/train/test overview grounds experimental breadth; CIFAR training60K differs from AppendixB.3’s50K. Transfer: Adopt setup overview, independently crosscheck totals against source data and appendix.
- **Table2, p8**: MNIST methods, unit types, architecture and error grouped by pretraining status. Comparisons vary more than dropout alone. Transfer: Adopt configuration metadata; distinguish matched ablations from cross-paper rankings.
- **Table3, p10**: SVHN rows include external baselines, dropout placements and human reference; error% column. Transfer: Adopt clear baseline provenance and component changes; avoid implying all rows share identical training.
- **Table4, p11**: Two dataset columns expose that maxout/dropout-all-layer rankings differ betweenCIFAR10/100. Transfer: Adopt per-task results and preserve inconsistent rankings rather than only aggregate wins.
- **Table5, p12**: ILSVRC2010 test top1/top5 errors compare feature systems withCNN+dropout. Transfer: Adopt dataset-year/split labels; do not attribute architecture-system gain solely to dropout.
- **Table6, p12**: ILSVRC2012 validation/test and ensemble count are distinct columns/rows; missing values use dashes. Transfer: Adopt explicit missing results rather than invented values or merged validation/test claims.
- **Table7, p13**: Speech phone-error table groupsNN/pretrained variants with depth metadata. Transfer: Adopt important preprocessing/model configuration alongside task metric.
- **Table8, p14**: Code-quality bits is higher-better; BayesianNN exceeds dropout, prominently retained. Transfer: Adopt strongest unfavorable comparator and explain the intended cost/quality trade-off.
- **Table9, p15**: Fixed-architecture regularization comparison isolates combinations more closely than benchmark tables. Transfer: Adopt focused ablation after broad utility results; preserve matched protocol conditions.
- **Table 10, p23**: Two datasets and architecture descriptions compare Bernoulli/Gaussian errors as mean±value over10 seeds; exact plus/minus meaning is unspecified. Transfer: Adopt reporting seeds and configurations; explicitly defineSD/SE/CI and avoid superiority from tiny overlapping differences.

## EX09 — Adam: A Method for Stochastic Optimization

Published: ICLR conference track (2015); [official record](https://iclr.cc/archive/www/2015.html).

Author original paper,selected arXivv9 dated2017-01-30,15pages. OfficialICLR2015 May9 conference-poster list identifiesAdam; this revision is not claimed byte-identical to2015 submission.

PDF SHA256: `eab9c73ae2ceda884b94830bda99312254bac4806f6c9f045cbab90721ecda31`. Coverage: physical pages1–15; 4 figures/tables.

**organization — pp1–5 Sections1–5;pp5–9 Sections6–8;pp12–15 appendix.** Algorithm appears early, explanation isolates bias correction, theory is separate, related work explains mechanism differences, then experiments progress convex→nonconvex→ablation→extension. Transfer/limit: Adapt formal contract early in exact/approximate attention and scheduler papers; order experiments by reader questions, not commit chronology.

**claim_evidence — p3 bias derivation;p4 theorem;p6 Section6.2;p8 Figure4.** A specific correction has a derivation and direct ablation; convex guarantees are explicitly not applied to neural networks. A claimed proof is a source claim, not independently validated by this reading. Transfer/limit: Adopt proposition assumptions adjacent to conclusions and test the changed mechanism. No theorem transfer or correctness certification from exemplar status.

**figures — p7 Figures2–3;p8 Figure4.** Iteration and walltime cost are separated; early/late plots reveal time-dependent ranking; ablation panels span nuisance settings. Small panels and red/green encoding are weaknesses. Transfer/limit: Adapt fair work/time comparison and sweep coverage, enlarge final-size labels and use redundant markers/styles.

**rhetoric — p6 Section6.2;p7 Section6.3;p9 Section7.** Direct caveats distinguish theory scope; CNN comparison describes a marginal gain instead of uniformly dominant behavior; extensions are named separately from the base method. Transfer/limit: Adopt bounded claims for toy workloads and exact geometry propositions. Reject universal robustness or efficiency language without own scope-matched evidence.

**content — p2 Algorithm1;p5 common initialization/grid search;pp12–15 proof.** Operational states/defaults are compact; comparisons disclose tuning. Proof detail is deferred without hiding assumptions from main text. Bibliography and acknowledgment also reveal provenance and corrections. Transfer/limit: Adapt concise pseudocode plus main-text assumptions and appendices for derivations; preserve prior failures/corrections and avoid a lab-log narrative.

### Page-by-page observations

- p1: Author PDF says ICLR2015 and visibly identifies arXiv1412.6980v9, 30Jan2017. Abstract lists operational properties, theory and empirical scope; introduction narrows to noisy first-order high-dimensional objectives.
- p2: Algorithm1 precedes most explanation and defines states, bias corrections and defaults. Section2 derives the meaning of first/second moments; an explicitly less-clear reordered implementation is kept in prose.
- p3: Update-rule discussion uses approximate step-bound/trust-region intuition and rescaling cancellation. Section3 derives zero-initialization bias through a finite geometric sum, with a nonstationarity residual rather than silently assuming stationarity.
- p4: Section4 states online-convex regret, bounded gradients/iterates, decaying step size and beta1 schedule; proof is deferred. These assumptions are distinct from the constant-default algorithm presented earlier. Related-work section begins.
- p5: Related work compares mechanisms and memory demands, especially RMSProp bias correction and the Adagrad limit. Evaluation fixes common initialization, searches a dense hyperparameter grid, and begins convex MNIST/IMDB logistic regression.
- p6: Figure1 separates dense MNIST and sparse IMDB convergence. Section6.2 explicitly says convex theory does not apply to neural nets. SFO comparison distinguishes iteration cost and walltime and discloses its stochastic-regularization failure.
- p7: Figure2 includes dropout optimization and SFO iteration/walltime views. Figure3 shows early linear-scale and long-horizon log-scale CNN costs. Text admits only marginal advantage over momentum SGD and offers a task-dependent explanation.
- p8: Figure4 is a 12-panel bias-correction ablation: two beta1 rows, three beta2 columns, two horizons. Section6.4 ties the observed instability regime to the earlier bias argument. Section7 starts the infinity-norm extension.
- p9: Algorithm2 and equations8–12 derive AdaMax via the p-norm limit. Temporal averaging is a separate extension. Conclusion begins after extensions rather than allowing auxiliary variants to interrupt main evaluation.
- p10: Conclusion confines practical findings to investigated optimization problems. Acknowledgments disclose an earlier AdaMax derivation error. References begin with optimization geometry and empirical model/data sources.
- p11: References end with RMSProp course material, fast dropout, AdaDelta and online convex programming. No additional figures/tables occur on this reference-only page.
- p12: Appendix10.1 defines convexity, tangent lower bound and a supporting gradient-history lemma; induction steps are explicit. Read as original claimed proof, not independently certified mathematics.
- p13: Appendix expands biased/corrected moment sums, bounds a weighted gradient-history quantity, invokes a geometric-series bound, and introduces the main theorem. Several inequalities merit independent proof review before scientific reuse.
- p14: Appendix proof substitutes the update into squared coordinate distances, applies Young’s inequality, and sums across time and dimensions. The telescoping/weighted-distance step is a crucial dependency, not empirical evidence.
- p15: Final appendix page bounds the decaying-beta contribution by an arithmetic-geometric series and presents the regret expression. Full selected PDF ends here; no appendix is omitted.

### Complete figure/table inventory (actual pixel views)

- **Figure1, p6**: Two linear cost-versus-epoch plots use different ranges/datasets. Dense MNIST and sparseIMDB reveal different competitor behavior; colors alone carry most series identity. No uncertainty shown. Transfer: Adapt regime-separated comparisons, adding redundant line styles and explicit independence of axes; avoid global superiority claims.
- **Figure2, p7**: Left dropout-MNIST cost has log y; right nested panels compare SFO/Adam on epochs and normalized walltime with log y. Small right panels required detail view. Transfer: Adopt both work and elapsed-time views for waiting/fairness when actual timings exist; enlarge panels and use seconds rather than unexplained normalization.
- **Figure3, p7**: Early3-epoch linear cost panel and45-epoch log cost panel share methods, with/without dropout. Rank changes across horizon are visible; ranges are not directly comparable. Transfer: Adapt explicit early/late horizons only if scientific question needs both; declare scale changes and avoid cherry-picked endpoints.
- **Figure4, p8**: Two horizon blocks each form2x3 beta-grid; loss versus log10 learning rate, red correction and green no-correction, x markers. Instability appears as curves exiting axes; no intervals. Transfer: Adapt mechanism ablation across nuisance parameters; replace red/green-only distinction and disclose clipped/divergent runs rather than interpreting disappearance as success.

## EX10 — Group Normalization

Published: ECCV (2018); [official record](https://openaccess.thecvf.com/content_ECCV_2018/html/Yuxin_Wu_Group_Normalization_ECCV_2018_paper.html).

OfficialCVF author-created proceedings version,17pages,pp3–19; selectedPDF has no appendix.

PDF SHA256: `32a162383c6f47dbd6f2158c18daddbeb512bde205928b5687e79467aa923f17`. Coverage: physical pages1–17; 15 figures/tables.

**organization — pp1–3 failure-regime introduction;pp4–6 method;pp7–14 experiments.** A concrete batch-size failure makes the need legible before an index-set unification explains the alternative; classification, detection and video test progressively different deployment constraints. Transfer/limit: Adapt problem-regime opening for normal-wait retries and attention memory constraints; do not borrow cross-domain validation that the new work lacks.

**claim_evidence — p7 Table1;p8 Table2;p12 Tables5–6;p14 Table8.** Normal-batch disadvantage is preserved; sensitivity addresses the claimed problem; head/backbone/long-schedule ablations distinguish sources of gain; clip length and batch size separate a coupled confounder. Transfer/limit: Adopt unfavorable regimes and orthogonal factor controls. Use measured validation and theoretical invariants separately for validconv geometry.

**figures — p4 Figure2;p8 Figure5;p10 Figure6;p14 Figure7.** Identical tensor frames make one changed axis-set visible; matched sensitivity panels expose stability; percentiles and protocol-specific monitoring are clearly different evidence kinds, with some caption errors. Transfer/limit: Adapt invariant coordinate frames and aligned panels. Reject unmarked scale differences, ambiguous percentage language and unchecked caption references.

**rhetoric — p1 footnote1;p2 normal-batch qualification;p8 regularization interpretation;p14 discussion.** Terms are scoped early and ordinary-case shortcomings appear near the motivating claim; causal interpretations use explanatory language while discussion admits inherited tuning choices. Transfer/limit: Adopt first-use definitions of wait/retry/fairness and exact/approximate semantics. Use cautious causal language unless controlled evidence excludes alternatives.

**content — p5 equations1–6;p6 equation7/code;p7 setup;p11 BN* definition.** A common formalism replaces repeated standalone method descriptions; implementation is a short shape-explicit box; evaluation states baseline semantics, initialization, hyperparameters and metrics. Transfer/limit: Adapt one common operation/state formalism with only changed terms highlighted. Keep baseline frozen/live semantics and validconv padding/cropping definitions in main text.

### Page-by-page observations

- p1: Abstract identifies a specific BN failure regime before presenting GN. Introduction footnote defines batch size as samples per worker, with unsynchronized statistics; this prevents a global-batch/per-worker ambiguity.
- p2: Figure1 puts the failure-regime result before method detail. Introduction connects small batches to detection/video memory constraints, preserves the normal-batch disadvantage, and limits untested sequential/generative extensions.
- p3: Related work separates normalization axes, small-batch remedies and hardware synchronization. The ending states the design distinction: avoid batch-statistic dependence itself rather than repair its estimate.
- p4: Figure2 holds the tensor drawing constant and changes the highlighted normalization set. Group computation is contextualized without requiring group convolutions. Section3 uses classical grouped features as motivation, not proof.
- p5: Equations1–6 define normalization once with index set Si, then instantiate BN/LN/IN. The shared per-channel affine transform keeps method comparison aligned around the one changing axis-set choice.
- p6: Figure3 is executable-style pseudocode. Equation7 defines GN’s group-membership predicate, then the text gives LN and IN as endpoint cases. Normalization grouping and learned per-channel affine parameters are distinct.
- p7: Figure4 pairs training and validation error; Table1 retains BN’s advantage at batch32. Implementation details specify 8GPUs, initialization, weight decay, schedule, crops, and the final-five-epoch median (not replicate uncertainty).
- p8: Figure5 and Table2 show sensitivity across per-GPU batch sizes. Caption mistakenly says LN for the right-hand panel that is labeled GN. Text offers regularization as an explanation for train/validation reversal, rather than a controlled causal identification.
- p9: Table3 separates fixed group count from fixed channels per group. Learning-rate scaling and unchanged epoch budget are explicit. Small-batch results, Batch Renorm comparison and channel-group sweep test distinct questions.
- p10: Figure6 juxtaposes feature percentiles and classification error on VGG16. The unnormalized panel has a much wider vertical scale. Prose reverses Table3 left/right references; observed table headers establish the intended mapping.
- p11: Table4 introduces detection/segmentation with frozen BN denoted BN*. Text states poor results when fine-tuning ordinary BN, identifies COCO splits and metrics, and distinguishes transfer training from classification pretraining.
- p12: Table5 adds GN to the box head before changing the backbone; Table6 separates full GN and longer training. This layered ablation avoids assigning all detection gain to the pretraining backbone.
- p13: Table7 presents from-scratch detection separately. Kinetics setup specifies temporal sampling, 10-clip test averaging, and the clip-length/batch-size memory trade-off; results begin with matched temporal length.
- p14: Figure7 compares 1-clip augmented monitoring curves; Table8 reports 10-clip unaugmented accuracy and says so explicitly. Discussion notes that existing systems and hyperparameters were designed for BN and may not suit GN.
- p15: References1–24 locate BN, vision architectures/tasks, classical descriptors, other normalizations and recurrent/generative foundations. No new result or appendix starts.
- p16: References25–47 cover LRN, domain shifts, batch renormalization/synchronizedBN, group convolution and classical normalization motivation; bibliography separates neuroscience inspiration from empirical method evidence.
- p17: References48–63 include frameworks, initialization, batch-size scaling, Detectron and detection/video backbones. Selected17-page official CVF PDF ends with references; no appendix is present.

### Complete figure/table inventory (actual pixel views)

- **Figure1, p2**: Opening result plots error% against batch sizes32,16,8,4,2 in descending geometric spacing. Blue plusBN/red circleGN remain identifiable by marker. It summarizes Table2 without uncertainty. Transfer: Adopt one motivating failure-regime plot only if own complete data justify it; make order/spacing explicit and state per-worker units.
- **Figure2, p4**: Four identical tensor grids showN,C,HW axes; blue cells denote one shared-statistic set, neutral cells context. BN spansN/HW; LN spansC/HW; IN spansHW; GN spans a channel subset/HW. No arrows because set membership is the relationship. Transfer: Adapt invariant tensor/context plus highlighted changed region for validconv geometry; not a runtime-flow diagram. Preserve axes and distinguish illustrative group count from a trained setting.
- **Figure3, p6**: Monospaced code box gives shapes, reshape, moment axes and learned affine transform. It is numbered as a figure though it is code, not a chart. Transfer: Adapt a minimal executable specification only when it clarifies index-set semantics; do not fill a paper with repository implementation details.
- **Figure4, p7**: Aligned train/validation error panels use shared ranges and epochs, legends plus in-plot method labels, and line-style differences. GN lower training error but slightly worse validation remains visible. Transfer: Adopt matched panels that expose metric disagreement; do not equate an internal diagnostic improvement with end-task gain.
- **Figure5, p8**: BN/GN sensitivity panels share axes and method ordering; five batch-size curves spread onBN but overlap onGN. Caption erroneously names LN for rightGN panel. Transfer: Adapt paired sensitivity plots with same scales; independently verify every caption/legend/series identity.
- **Figure6, p10**: Three percentile-trajectory panels plus an error table; unnormalized y-range roughly-80..20 versus-5..3 forBN/GN. Red/green/blue/black represent percentiles, not treatments. Transfer: Adapt diagnostic-plus-outcome structure but visibly declare changed scales; do not compare raw apparent slopes across unequal axes or treat percentiles as run uncertainty.
- **Figure7, p14**: BN/GN validation-error curves compare8/4clips perGPU. Caption discloses1-clip augmented monitoring versus10-clip final Table8 evaluation. Transfer: Adopt monitor-versus-final metric disclosure; never combine their values into one trend or improvement percentage.
- **Table1, p7**: Four methods at batch32 with validation error and delta versusBN; best isBN, notGN. Transfer: Adopt honest best-baseline case and signed deltas with defined direction.
- **Table2, p8**: PerGPU batch-size columns compareBN/GN error and signed differences, retainingGN’s ordinary-batch disadvantage. Transfer: Adopt full regime sweep with negative and positive changes; report percentage points accurately.
- **Table3, p9**: Two side-by-side sweeps: fixedG on left and channels/group on right. Endpoint labels connectLN/IN to the method definition. Prose onp10 swaps left/right references. Transfer: Adopt endpoint ablations for exact/approximate attention or geometry only where actual endpoint identities hold; check reference mapping.
- **Table4, p11**: C4 MaskRCNN rows compare frozenBN* andGN over six box/mask AP metrics. Transfer: Adopt explicit baseline state and multiple task metrics, not a single unexplained aggregate.
- **Table5, p12**: FPN table separates backbone choice and GN box-head addition; three rows localize changes. Transfer: Adopt one-factor-at-a-time component exposure for scheduler fixes/attention variants, with independently measured evidence.
- **Table6, p12**: GroupedR50/R101 rows separateBN*,GN andGN-long; horizontal rules and long label disclose budget variation. Transfer: Adopt visible training/compute-budget metadata rather than conflating extra budget with method gain.
- **Table7, p13**: From-scratchR50/R101 results are a separate table, not mixed with pretrained rows. Transfer: Adopt protocol separation for cold/warm runs or analytic/empirical results.
- **Table8, p14**: Columns jointly encode clip length and batch size; each cell reports top1/top5. This makes the coupled memory/design trade-off inspectable. Transfer: Adapt a small exact factorial table when factors would be hidden by a single summary curve; label every pair component.

## Transfer handoff to root

- Waiting/fairness: adaptGN’s failure-regime opening and component ablations;BN’s minimal-method versus tuning-bundle split;Adam’s separate work/time outcomes. Main-text state semantics must distinguish waiting,attempts and failure, and fairness evidence must come from the project’s own traces.
- Exact/approximate attention: adaptDropout’s explicit approximation contract and MonteCarlo-versus-cheap-inference comparison; separate exact identities, numerical approximation error, task quality and measured runtime. Adam’s theorem/empirical scope distinction prevents turning an analytic statement into deployment evidence.
- Valid-convolution geometry: adaptGN’s constant-coordinate tensor comparison and common index-set formalism; useDropout’s overview/local-operation separation where needed. Preserve actual shape,crop,stride andboundary invariants; benchmark method gains do not support geometric correctness.
- Avoid a technical-report voice by organizing around reader questions: what fails, why it fails, what changes, what follows exactly, what measurements show, and where the conclusion stops. Reproduction logs and parameter dumps belong in appendices unless they change interpretation.

## Explicit weaknesses retained

- GN Fig5caption namesLNwhere its right panel isGN; p10 reversesTable3panelreferences.
- Dropout Table1CIFARtraincount60K conflicts with AppendixB.3’s50K. Errorbar definitions inFigs 9–10 and plus/minus semantics inTable 10 are incomplete locally; Fig 11 text mentionsSD but does not fully state replication unit.
- BNheadline acceleration combines normalization with other training changes; do not attribute the entire tuned gain to one intervention.
- Adam selected PDF is 2017 v9 of the ICLR 2015 paper. Its claimed convergence proof was read, not independently verified. Dense figure panels and red/green-only encoding are lessons to improve, not templates to copy.

## Data-figure and architecture handoff

Eight visual-design dimensions are recorded for every paper in the JSON: comparison/chart, axes/baselines, uncertainty, encoding/accessibility, palette/legend, typography, layout/density, and panels. These complement the complete per-figure inventory. Architecture source observations cover GN Figure 2 and Dropout Figures 1 and 3, with focus, hierarchy, abstraction, layout/flow, color semantics, type/whitespace, panel roles, and transfer constraints.

This is a reader handoff only. Independent diagram/data-visualization collaboration, target-specific design briefs and manuscript implementation remain root-owned steps.
