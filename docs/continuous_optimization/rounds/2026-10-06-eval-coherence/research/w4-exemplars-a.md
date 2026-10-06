# T24 writing-exemplar reading: assigned set A

Reader: `/root/exemplar_read_a`; recorded 2026-10-06T13:10:36.238170+00:00.

3/10 assigned writing exemplars; expanded full reading of previously selective architecture originals; not three new Agent-research papers. All 28 physical pages were read in text and opened as full-page pixels. Coverage is limited to the frozen PDFs below; no external supplement is silently counted. No manuscript was drafted.

## Read receipt and provenance

PyMuPDF text extraction plus 1.5x full-page PNG; every physical page displayed with tools.view_image and read by actor. Rendering alone is not the claimed receipt.

The JSON companion records a SHA-256 for every displayed page PNG and extracted text. PNGs and third-party PDFs remain outside the repository; this file contains original notes only. Actual displays occurred through functions.exec → tools.view_image in this agent context. A hash proves identity, not cognition; per-page observations and figure-specific analyses below are the human-auditable reading evidence.

## EX01 — Attention Is All You Need

Identity: `NIPS2017:3f5ee243547dee91fbd053c1c4a845aa`. Venue: NIPS 2017 / Advances in Neural Information Processing Systems 30. [Publication](https://papers.nips.cc/paper_files/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html); [selected full text](https://papers.nips.cc/paper_files/paper/2017/file/3f5ee243547dee91fbd053c1c4a845aa-Paper.pdf).

Version: conference-hosted full PDF downloaded 2026-10-06; not latest arXiv. PDF SHA-256: `d87d482d5ae7960e2e43d7dd6d21377e60e73e8fce1bf2a01aff7aca8a08c537`. Read pages: 1–11; pixel-viewed pages: 1–11. All figures/tables below actually viewed.

Selection: Same mathematical operator as attention working paper; teaches overview/operator separation and cost-vs-quality argument. Quality basis: Useful because definitions, analytical table and controlled ablations form a traceable argument; reputation alone is not the criterion.

- Official proceedings identity re-opened 2026-10-06 (web ref turn107view0). Its HTML abstract has 27.5/41.1 rather than frozen PDF 28.4/41.0; do not mix versions.
- All 11 selected pages read; external appendix mentioned on p7 not present and not read.
- No training reproduction; exemplar metrics are source facts only.

### Physical-page observations

- p1 (printed 1): Abstract couples an architectural substitution to translation quality and training cost; p1 footer identifies NIPS 2017. Author contribution footnote occupies substantial space, so page count is not a simple prose budget. Pixel receipt: `transformer/p01.png`, SHA-256 `c0c3f883ef0d9be6d5ae7476434a157902af48bebc9d91b8bffd9f1d91a57e2d`.
- p2 (printed 2): Introduction isolates sequential computation as the constraint; background compares convolutional path lengths and admits averaging reduces effective resolution. Encoder/decoder variables precede stack detail. Pixel receipt: `transformer/p02.png`, SHA-256 `f262d204fc8febcf0d304c93bf536b1e57a22d3af50dcd9e5966c7cabcd358bf`.
- p3 (printed 3): Fig1 gives two vertical stacks with cross-attention bridge and shifted decoder inputs. Text states post-norm residual form and why masking plus output shift prevents future-token use. Pixel receipt: `transformer/p03.png`, SHA-256 `fc79969cbc9fa51de2150940375128b2d2ff8dcc2a290aa96dac50058a00e865`.
- p4 (printed 4): Fig2 separates attention primitive from multihead composition; Eq1 puts scaling inside softmax. Large-dot-product gradient explanation is a suspicion supported by variance reasoning in footnote, not an experiment. Pixel receipt: `transformer/p04.png`, SHA-256 `776085b50fde49e817e48a44c21a503df8345055ca9fe8b327191b621c47c522`.
- p5 (printed 5): Multihead parameter shapes precede three application cases; Q/K/V provenance differs by attention type. FFN Eq2 and embedding weight sharing finish implementation before positional encoding motivation. Pixel receipt: `transformer/p05.png`, SHA-256 `1e5f261b8c66dd83110c2412d4215f99ff67548666953196ca9f6102aaeb0146`.
- p6 (printed 6): Table1 distinguishes per-layer complexity, sequential operations, and path length. Positional encoding extrapolation remains a hypothesis; learned encoding is reported nearly equivalent. Speed comparison explicitly conditions on n<d. Pixel receipt: `transformer/p06.png`, SHA-256 `f877681b9aba8a954861be05116bf0987d380612d5d29425f785434d3049cb43`.
- p7 (printed 7): Long-sequence restricted attention is future work. Training specifies corpus sizes, batching by lengths, 8 P100 hardware, step counts, Adam warmup equation and dropout. Appendix attention examples are referenced but absent from this 11-page version. Pixel receipt: `transformer/p07.png`, SHA-256 `62ca5b5dbf0dbc265c0043d5a40bbdbe133fb589e0586cef5ec84df7e5a7978e`.
- p8 (printed 8): Table2 juxtaposes BLEU and estimated training FLOPs; single models and ensembles are separated. Results disclose checkpoint averaging, beam/length penalty, development tuning, FLOP-estimation method; variations use development set without averaging. Pixel receipt: `transformer/p08.png`, SHA-256 `71f26d78a7826843999ec4f4be47d2db6667337a79ff66e642e26ef06bed1c9c`.
- p9 (printed 9): Table3 has controlled parameter deltas and grouped ablations A–E; caption warns wordpiece perplexity differs from word perplexity. Conclusion distinguishes future modalities/local attention from measured translation; acknowledges remaining sequential generation. Pixel receipt: `transformer/p09.png`, SHA-256 `2375ae4b9aa45d5b058c54c8d9e543bc50fe16893f4e8228b2e1e8f3bdaabc68`.
- p10 (printed 10): References1–20 include prior recurrent/attention architectures, residual connections, normalization, optimizer and gradient-flow foundations; these entries show mechanism provenance but were not separately verified as scientific sources in this read. Pixel receipt: `transformer/p10.png`, SHA-256 `c146cdbd5de2b51fef1c4326bceb01d643e6ea5a512381811f983c2230716c10`.
- p11 (printed 11): References21–32 cover attention, embeddings, subword preprocessing, MoE, dropout and translation baselines. Document ends at reference32; no appendix pages or attention heatmaps in this selected conference PDF. Pixel receipt: `transformer/p11.png`, SHA-256 `6af474eaf80468e7fc83db7b7097fbf2b4415bdbe6a24caabfdf8137b642d590`.

### Figure/table inventory and actual pixel coverage

- Figure1, p3 — **viewed**. Full encoder/decoder architecture; color distinguishes operation families, repeated-layer brackets avoid six copies, residual side loops terminate at Add&Norm; cross-attention bridge is the nonlocal connection. Transfer/limit: Adapt hierarchy and explicit state provenance, not specific blocks, to runtime state machine; do not mistake drawing for measured concurrency.
- Figure2, p4 — **viewed**. Two panels: Q/K MatMul→Scale→optional Mask→SoftMax→V MatMul, then projected parallel heads→Concat→Linear. Bottom-up arrows; h marks repetition; no empirical axis. Transfer/limit: Exact-vs-approximation paper must show the changed mathematical operator at this primitive level, with mask/scaling and dimensions preserved.
- Table1, p6 — **viewed**. Four layer types; columns separately encode symbolic complexity, sequential operations and maximum path length with n,d,k,r defined in caption. Transfer/limit: Separate asymptotic work/depth from runtime; restricted-attention row trades path length for work and does not establish accuracy.
- Table2, p8 — **viewed**. Rows separate prior single models, ensembles and Transformer; BLEU by direction and FLOPs by direction are distinct columns; empty cells preserve unreported results. Transfer/limit: Use missing cells honestly and disclose hardware/cost estimation; caption headline is broader than EN-FR ensemble values, so qualify any migrated claim.
- Table3, p9 — **viewed**. Base row fully specified; A–E modify heads, key width, size, regularization and position encoding; metrics include dev PPL, BLEU and parameter millions. Transfer/limit: Adapt delta-to-baseline organization; do not mix development ablations with held-out test wins or infer universal attention approximation behavior.

### Five writing dimensions

**organization — pp1–9 §§1–7**

Problem and background lead to architecture, then analytical justification, reproducible training and outcome/ablation results. The method is defined before the cost argument, so readers can map symbols to operations.

Transfer: For attention study: define exact operator, isolate proposed approximation, derive what changes, then measure error/cost. For runtime study: failure observation→state semantics→scheduler policy→tests.

Counterexample/limit: This neural architecture paper is not a systems template: large training section and leaderboard narrative do not transfer to a small local runtime study.

**claim_evidence — p6 Table1; p8 Table2; p9 Table3**

Analytical parallelism, translation result, and component sensitivity use different evidence objects. n<d qualifies the cost comparison; equal-compute heads ablation narrows a confound.

Transfer: Maintain separate claim IDs for exact algebra, approximation error, measured runtime and downstream quality, each with its own test.

Counterexample/limit: Original estimated FLOPs are not same-hardware benchmark evidence; no own-paper speedup follows from these tables.

**figures — p3 Fig1; p4 Fig2; pp6,8,9 Tables1–3**

System overview and operator detail are separate; tables carry all comparative numerical evidence. Captions define scope and units rather than relying solely on prose.

Transfer: Use one overview plus one changed-operator panel only if both answer distinct questions; include input sizes, precision and units in own performance tables.

Counterexample/limit: Attention heatmap appendix is absent in this version; no heatmap visual-design claim is supported.

**rhetoric — p2 §2; p4 §3.2.1; p6 §3.5; p8 §6.1**

Definitions precede use; suspicion/hypothesis language marks unproven mechanism; EN-FR result is explicitly single-model. Conclusion is stronger and less qualified than some detailed comparisons.

Transfer: Use demonstrates for measured invariant, suggests for mechanism interpretation, and untested for extrapolation; avoid blanket faster or exact language.

Counterexample/limit: Do not borrow first-model or state-of-art rhetoric for an exact-vs-approximation working study; novelty must be independently established.

**content — pp5–8 §§3.2.3–6.2**

Q/K/V sources, mask value, dimensions, training schedule and evaluation decoding are disclosed near relevant mechanism. Label smoothing improves BLEU while worsening perplexity: different metrics can disagree.

Transfer: Place approximation constraints and metric tradeoffs in method/results, not a distant limitations checklist; runtime waiting semantics need analogous explicit definitions.

Counterexample/limit: The PDF lacks modern variance reporting for most translation comparisons and lacks the promised appendix; these are counterexamples, not conventions to reproduce.

## EX02 — Deep Residual Learning for Image Recognition

Identity: `CVPR2016:He_Deep_Residual_Learning:770-778`. Venue: CVPR 2016, pp.770–778. [Publication](https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html); [selected full text](https://openaccess.thecvf.com/content_cvpr_2016/papers/He_Deep_Residual_Learning_CVPR_2016_paper.pdf).

Version: CVF accepted conference version (open-access watermark); full PDF downloaded 2026-10-06. PDF SHA-256: `51b5de45eb0b558b19c3affe49503cff50cb170a32de602983d6e2ec286942a7`. Read pages: 1–9; pixel-viewed pages: 1–9. All figures/tables below actually viewed.

Selection: Provides failure-driven mechanistic narrative directly adaptable to runtime waiting and fairness tests; also illustrates controlled architecture changes. Quality basis: Quality derives from matched plain/residual controls, train/test distinction, ablations and admitted1202 negative boundary, not merely CVPR status.

- CVF full PDF watermark and printed770–778 support publication; existing sources.json retained. Official HTML re-open returned403 (turn107view1), not silently treated as fresh success.
- All9 selected pages read; external appendix not included or read.
- No ResNet training or detection reproduction.

### Physical-page observations

- p1 (printed 770): Fig1 uses train and test curves for plain20/plain56 to show the deeper model has greater training error; this distinguishes optimization failure from ordinary overfitting. Introduction proposes a constructive identity extension, not proof that SGD finds it. Pixel receipt: `resnet/p01.png`, SHA-256 `16c9d2cf8381be329670c7927518b6f7e4bdc0dce83613e0c24bb5ddee109955`.
- p2 (printed 771): Fig2 exposes the residual reformulation before formal method. Related work distinguishes residual representations and shortcuts; highway gates are contrasted with always-open identity paths. Contribution bullets connect optimization and accuracy. Pixel receipt: `resnet/p02.png`, SHA-256 `0b2029869ac4d30d27d494d7ca7eafbb5070167d0e5addb24b2cc2eb30540870`.
- p3 (printed 772): §3.1 separates approximability hypothesis from ease of learning. Eq1 has identity addition; Eq2 covers projection when dimensions differ. Text acknowledges negligible addition cost and reports no observed advantage for one-layer residual function. Pixel receipt: `resnet/p03.png`, SHA-256 `5e0faba5959665cc3af9cd11ff0f18979501d7b13f2d7bb5ccd2abccd8690643`.
- p4 (printed 773): Fig3 aligns VGG19/plain34/residual34 stages with output resolutions, making the controlled architectural difference visible. §3.4 lists augmentation, BN placement, SGD schedule and test-crop protocol; §4 begins data/evaluation definitions. Pixel receipt: `resnet/p04.png`, SHA-256 `c757d3f317358161e3b75fce5ee56204b10fe84a8b9521ff603ce26c58d71399`.
- p5 (printed 774): Table1 enumerates 18/34/50/101/152 architectures. Fig4 separates thin training from bold validation curves; Table2 compares equal-parameter plain/residual nets. Text argues against vanishing gradients and reports 3x longer training did not remove degradation. Pixel receipt: `resnet/p05.png`, SHA-256 `9a68bcb116763cf3432b15b7eee624134c5f5e797dd9458885b0eef99f5f43bc`.
- p6 (printed 775): Tables3–5 separate 10-crop, single-model multi-scale and ensemble comparisons. Fig5 presents basic and bottleneck residual branches. Projection options A/B/C give modest differences; identity shortcut is retained for economy rather than universally best accuracy. Pixel receipt: `resnet/p06.png`, SHA-256 `dd87b91a2796941df7d61f9f0d4ce3eef8a0a4b47fa21952f77c2429e048b823`.
- p7 (printed 776): Table6 reports CIFAR best and mean±std for five ResNet110 runs, includes worse1202 result. Unnumbered architecture table sets 6n+2 stages. CIFAR focus is depth behavior, not pushing the leaderboard; warmup exception is disclosed. Pixel receipt: `resnet/p07.png`, SHA-256 `9432ca2548a1106aae7d9a00a9bb8d60ffa896c805ff63737b57ae163b424859`.
- p8 (printed 777): Fig6 trains plain/residual depths and compares110/1202; caption discloses omitted plain110>60% curve. Fig7 orders layer-response std by original position and sorted magnitude. Tables7/8 test detection backbone replacement. 1202 test degradation despite low training error motivates overfitting discussion. Pixel receipt: `resnet/p08.png`, SHA-256 `3ccaca9e47114a17518538037c98085821397dad40f26f24dfca653d434647f6`.
- p9 (printed 778): References1–49 fill final page and link optimization foundations, benchmarks and architectures. No standalone conclusion section and no appendix follows; external detection appendix is mentioned but absent from selected CVPR PDF. Pixel receipt: `resnet/p09.png`, SHA-256 `ce311113a45f12ca6d83dbf4514f768d4b44095ed9407985e869dcdc3dad2a0c`.

### Figure/table inventory and actual pixel coverage

- Figure1, p1 — **viewed**. Two small panels, error percent vs iterations×1e4; red56 exceeds yellow20 in train and test. Transfer/limit: Adopt failure-first pair of diagnostics for runtime: show retries consumed during normal waiting alongside completion failures; axes must not imply measured wall time if simulated.
- Figure2, p2 — **viewed**. Minimal residual branch of two weight layers with intermediate ReLU, identity side path, addition then ReLU. Transfer/limit: Preserve the changed operation while deferring full network; do not transfer residual addition to concatenating U-Net skips.
- Figure3, p4 — **viewed**. Three tall aligned architectures, pastel stage colors, solid same-dimension and dotted dimension-changing shortcuts; caption includes19.6 vs3.6B FLOPs. Transfer/limit: Use aligned baseline/candidate topology to show exact intervention; verbosity of full layer list is unsuitable for a tiny runtime study.
- Figure4, p5 — **viewed**. Two panels share error-percent and iteration×1e4 axes. Cyan18/red34; thin training/bold validation. Plain34 worse; ResNet34 better. Transfer/limit: Use identical axes/protocol when comparing repair; distinguish mechanism diagnostics from end-task success.
- Figure5, p6 — **viewed**. Basic64→64 pair versus bottleneck256→64→64→256; identity outer path; final ReLU after addition. Transfer/limit: Show comparable designs with channel/dimension invariants, but do not silently insert BN boxes into a faithful interpretation of the original drawing.
- Figure6, p8 — **viewed**. Three panels: plain depths, residual depths,110vs1202. Dashed train/bold test; high plain110 omitted with explicit caption explanation. Transfer/limit: Negative boundary case belongs alongside positive results; if clipping own failures disclose it and retain accessible raw data.
- Figure7, p8 — **viewed**. Two std-vs-layer-index line plots, original layer order then sorted magnitudes; no uncertainty bands; residual lines mostly smaller. Transfer/limit: Use secondary diagnostic only as support for a mechanism, not causal proof; sorting changes the question and must be labeled.
- Table1, p5 — **viewed**. Network stages and output sizes by18/34/50/101/152 depth, repeated-block counts and FLOP row. Transfer/limit: Parameter grid should name configuration choices and hold invariants explicit.
- Table2, p5 — **viewed**. 2×2 comparison: plain/residual at18/34 layers,10-crop top1 error%. Transfer/limit: Strong model for minimal factorial ablation; avoid an uncontrolled long list of successes.
- Table3, p6 — **viewed**. 10-crop top1/top5 error; optionsA/B/C and deeper residual variants. Transfer/limit: Do not claim added projection capacity is free; distinguish intervention options.
- Table4, p6 — **viewed**. Single-model top1/top5; one historical test-set exception marked dagger. Transfer/limit: Expose evaluation-set exceptions rather than merging them silently; prefer homogeneous own measurements.
- Table5, p6 — **viewed**. Ensemble top5 test-server errors; separate from validation and single-model results. Transfer/limit: Aggregate models/attempts must be explicitly labeled, not compared with single-run policy by default.
- Table6, p7 — **viewed**. CIFAR error with layer/parameter counts and five-run best(mean±std) for110;1202 worse despite more parameters. Transfer/limit: Retain regression and distinguish best from distribution; tiny studies should avoid best-run selection.
- TableU1, p7 — **viewed**. Unnumbered CIFAR architecture table:32/16/8 maps,1+2n/2n/2n layers,16/32/64 filters. Transfer/limit: Inventory unnumbered evidence too; stage formulas clarify how scale parameter changes configuration.
- Table7, p8 — **viewed**. PASCAL mAP% by training/test split forVGG16 andResNet101 with common FasterR-CNN. Transfer/limit: State task/split and common wrapper; backbone substitution claim needs unchanged rest-of-pipeline.
- Table8, p8 — **viewed**. COCO mAP@.5 and mAP@[.5,.95]%; same two backbones. Transfer/limit: Separate metric definitions and absolute percentage points from relative percent change.

### Five writing dimensions

**organization — pp1–5 §§1–4.1**

Observable degradation opens the argument, a small residual block supplies the intervention, related work/mathematics precede controlled experiments. Full architecture and settings bridge theory to evidence.

Transfer: Runtime paper should begin with one concrete waiting/retry failure, then state model and invariants, then policy and comparative tests; image study can begin with geometry failure.

Counterexample/limit: No mandatory conclusion exists here; forcing every paper into fixed sections misses the compact empirical narrative.

**claim_evidence — p1 Fig1; p5 Fig4/Table2; p8 Fig6**

Higher training error rules out the simple overfitting story for plain networks; matched depth/width/parameters test shortcuts.1202 case later separates optimization success from generalization.

Transfer: Use competing explanations: normal wait vs failure, fairness vs throughput, exact output equivalence vs approximate quality; pair each with discriminating evidence.

Counterexample/limit: Residual response magnitude inFig7 supports but does not prove the proposed optimization explanation; avoid causal certainty from proxy curves.

**figures — pp1,4–8 Figs1,3–7; Tables1–8**

Motivation curve, minimal mechanism, full topology, controlled curves and boundary case each have different jobs. Shared axes and style encode comparable conditions.

Transfer: Create only figures that answer distinct scientific questions; runtime retry/fairness curves require event count or time units and identical workload.

Counterexample/limit: Many traces have no variance bands and tiny fonts; these are not desirable export choices for new work.

**rhetoric — p3 §3.1; p5 §4.1; pp7–8 §4.2**

Hypotheses, arguments and observations are differentiated; the CIFAR section declares its narrower purpose. The one-layer non-result and1202 failure remain visible.

Transfer: State what the study isolates and does not measure; phrase synthetic verification as local behavioral evidence, not deployed system reliability.

Counterexample/limit: Universal generalization rhetoric in intro and solely-attributable detection phrasing exceed what should be copied into a small working paper.

**content — p4 §3.4; p6 projection/bottleneck; p7 warmup; p8 over1000**

Implementation details are selected for fair comparison. Bottleneck is a practical compute tradeoff; exceptional warmup and negative depth result are disclosed near outcomes.

Transfer: Preserve parameter budget, seed/schedule, timeout assumptions, precision and shape settings near relevant experiment; discuss cost of policy changes.

Counterexample/limit: No external appendix was read; detection implementation details referenced there cannot be claimed available from these nine pages.

## EX03 — U-Net: Convolutional Networks for Biomedical Image Segmentation

Identity: `doi:10.1007/978-3-319-24574-4_28`. Venue: MICCAI 2015, LNCS 9351, pp.234–241. [Publication](https://link.springer.com/chapter/10.1007/978-3-319-24574-4_28); [selected full text](https://arxiv.org/pdf/1505.04597v1).

Version: arXiv:1505.04597v1 (18 May 2015), author-linked preprint; not Springer typeset proceedings. PDF SHA-256: `a3172b2124f38e260dc2c7ed968d87c31bc94dbc19a42a7ab3dcbd7534319c44`. Read pages: 1–8; pixel-viewed pages: 1–8. All figures/tables below actually viewed.

Selection: Closest mechanism and geometry match to valid-convolution image-network working paper; also a useful counterexample on component attribution. Quality basis: Quality comes from explicit geometry, practical border handling and metric transparency; weaker isolated-component evidence is recorded rather than hidden.

- Author-linked arXiv1505.04597v1,18May2015; not Springer typeset proceedings. Official author page turn107view2 and publisher turn110view0 confirm MICCAI2015,9351,234–241 and DOI.
- All8 physical pages read; external supplementary segmentation material not read and not counted.
- No network training, challenge submission or speed reproduction.

### Physical-page observations

- p1 (printed 1): Abstract makes data scarcity and precise localization the joint problem; gives architecture/training strategy, segmentation tasks, speed and public artifact promise. Introduction moves from image-level classification to pixel labels and limited biomedical annotations. Pixel receipt: `unet/p01.png`, SHA-256 `df2e09c8bf842dd402cb1185569bf8400d0099cf44e6a659667c776247de4b6f`.
- p2 (printed 2): Fig1 gives full valid-convolution geometry and operation legend. Introduction diagnoses sliding-window redundancy and context/localization tradeoff, credits FCN, then introduces extending rather than inventing all components. Pixel receipt: `unet/p02.png`, SHA-256 `445f532a2e0b78f95215671fed62b9ed2f32df5934e2f117ac3fa8e4ebf83d36`.
- p3 (printed 3): Fig2 shows yellow output target inside blue required input, with mirrored image context. Text connects valid convolution, overlap tiling and GPU memory; augmentation and touching-cell weighted loss are justified as separate responses to task constraints. Pixel receipt: `unet/p03.png`, SHA-256 `7c3ac389d0e6fa24d1099f51b012f23afe842443555d128f67396401ba53f9b0`.
- p4 (printed 4): §2 defines unpadded3×3 convolutions, pooling, up-convolution, cropping and concatenation; even-sized pooling condition matters for tiling. §3 uses one large image/batch and0.99 momentum; Eq1 printed positive sum of log probabilities needs optimization-sign care. Pixel receipt: `unet/p04.png`, SHA-256 `bd8d03b73085272f13fa34944bd04811142782fea926ba111005cdcb1f17e8d3`.
- p5 (printed 5): Fig3 panels show raw cells, instance labels, binary training mask and pixel weight map. Eq2 defines distances to nearest/two-nearest cells and weight scale; initialization gives numeric incoming-node example. Augmentation subsection begins. Pixel receipt: `unet/p05.png`, SHA-256 `1f1dcc08733fe4e30d71690ea95bbc730d05014161f24a5ea10786cba4a916fe`.
- p6 (printed 6): Elastic deformation specifies3×3 coarse grid,10-pixel displacement std and bicubic interpolation. EM evaluation defines30 labeled images, hidden test labels, thresholded metrics and7 rotated inference versions. Table1 ranks by warping error, not all metrics. Pixel receipt: `unet/p06.png`, SHA-256 `aae2b2efe37bc8625a20bb888803c3324630105d00cd2a0bf99c89bb28f3f53d`.
- p7 (printed 7): Fig4 pairs input/prediction with yellow ground-truth contours for two microscopy settings. Table2 reports IOU with prior-year and second-best2015 rows; text discloses35 and20 partially annotated training images. Conclusion begins; footnote contextualizes competing submissions. Pixel receipt: `unet/p07.png`, SHA-256 `9191895c409681c822e4d41c8a3fbfcb3b67e6a28394ea2d429801f5d28edc86`.
- p8 (printed 8): Conclusion adds10h training on6GB Titan and public Caffe models; confident cross-task extension is prospective. Acknowledgements and14 references finish the8-page v1 PDF; reference14 is challenge website, not a peer-reviewed method source. Pixel receipt: `unet/p08.png`, SHA-256 `9941b5692ad6266cab3234fb899aae5c908874887dfa9b2c4a35db48b3ac88e0`.

### Figure/table inventory and actual pixel coverage

- Figure1, p2 — **viewed**. U-shaped feature-map boxes, channels on top/spatial dimensions alongside; white copied maps, gray crop-copy arrows, blue conv, red pool, green up-conv, cyan1×1.572 input→388 output; four scales down/up. Transfer/limit: Exact geometry is central to valid-convolution study; avoid shrinking labels to mimic original full-network density. Explicitly separate crop/concat from addition.
- Figure2, p3 — **viewed**. Raw EM image and segmentation tile; blue input region exceeds yellow output region; green arrow links them. Mirrored context supports border prediction. Transfer/limit: Use an original geometry schematic with input/output halos and tiling stride. This figure explains context, not seam-free numerical equivalence for every implementation.
- Figure3, p5 — **viewed**. Four panels a rawDIC,b colored instance groundtruth,c binary mask,d weight heatmap with colorbar. Thin high-weight boundaries receive attention. Transfer/limit: Pair mechanism map with the failure it addresses; do not present label-derived weight map as predicted accuracy evidence.
- Figure4, p7 — **viewed**. Four panels two raw inputs plus their colored predictions; yellow groundtruth contours permit local boundary inspection. Transfer/limit: Qualitative examples need groundtruth legend and selection policy; neither two selected images nor plausible appearance proves accuracy.
- Table1, p6 — **viewed**. EM ranking snapshot datedMarch6,2015; warping/Rand/pixel error columns; U-Net leads warping, other rows lead Rand/pixel; human row contextualizes gaps. Transfer/limit: Keep conflicting metrics visible and name ranking criterion; no blanket best segmentation claim from one metric.
- Table2, p7 — **viewed**. IOU onPhC-U373 andDIC-HeLa; prior methods labeled2014 and second-best2015; missing entry is dash. Transfer/limit: Preserve years/settings and missingness; comparisons cannot isolate effect of valid convolution from architecture, augmentation and training.

### Five writing dimensions

**organization — pp1–4 §1; p4 §2; pp4–6 §3; pp6–8 §§4–5**

Long introduction embeds related work, two mechanism figures and task constraints before compact architecture/training sections. Results occupy fewer pages than mechanism explanation.

Transfer: Valid-convolution paper can let geometry motivate the question before implementation; integrate only related work needed to understand crop/tiling choices.

Counterexample/limit: Do not copy four-page introduction into a tiny study: use figure+short derivation once and reserve space for discriminating tests.

**claim_evidence — p3 tiling argument; p4 §2; pp6–7 Tables1–2**

Architecture explains where output support comes from; challenge tables establish task outcomes. Scarce-data success combines network, augmentation and weighted loss.

Transfer: Separate deductive shape/crop assertions from measured seam consistency, accuracy and runtime; own tests need matched padding/tiling configurations.

Counterexample/limit: Challenge rankings do not establish a causal benefit of valid convolution alone; no component ablation supports that inference.

**figures — pp2–3 Figs1–2; p5 Fig3; p7 Fig4**

Architecture, operational tiling, training target/weight and prediction example serve four distinct stages. Legends make color semantics explicit; natural images ground the task.

Transfer: Adopt input/output support diagram and difference-image evaluation as distinct panels; label synthetic examples and mathematical deductions.

Counterexample/limit: Original figure assets cannot be copied; observational segmentation images cannot stand in for an unrun image-network study.

**rhetoric — p2 FCN discussion; p3 design motivations; p6 augmentation; p8 conclusion**

Prior FCN work is credited before modifications. Causal connectors explain why cropping and mirroring are needed. Elastic deformation is described as seeming key; final broad applicability is asserted optimistically.

Transfer: Use concrete subjects and because clauses linking constraint to choice; preserve uncertainty around unablated components.

Counterexample/limit: Reject obviously/more elegant value judgments and confidence about many more tasks as generic working-paper prose.

**content — p4 §§2–3; p5 Eqs1–2; p6 evaluation; p7 data counts**

Practical shape divisibility, tile/batch tradeoff, loss weights and augmentation parameters are adjacent to mechanism; dataset/metric definitions precede rankings.

Transfer: Own image study must specify valid/padded operator, pooling arithmetic, border policy, input/output dimensions and independent test source before results.

Counterexample/limit: Eq1 positive log-probability expression cannot be transplanted as a minimization loss without resolving sign convention; lack of isolated ablations is a scientific gap, not a writing convention.

## Cross-paper transfer, not a manuscript blueprint

- **organization** (EX01 §§3–6; EX02 Fig1/§3/§4; EX03 §§1–4): Different orders work because each follows a concrete reader question: operator then cost, failure then intervention, or task constraint then geometry. Adapt each target around its scientific question; reject a universal section-count template.
- **claim_evidence** (EX01 Tables1–3; EX02 Fig4/Table2/Fig6; EX03 Tables1–2): Analytical cost, matched intervention tests, benchmark rankings and qualitative examples support different claim strengths. For runtime use counterexample+invariant+fairness measure; attention use exactness/error+cost; image use shape derivation+independent output tests.
- **figures** (EX01 Figs1–2; EX02 Figs1–5; EX03 Figs1–4): Mechanism, operational context, evaluation and boundary case are separable visual jobs. Assign a question to each own figure; omit any panel that adds neither mechanism nor evidence.
- **rhetoric** (EX01 §3.5; EX02 §§3.1,4.2; EX03 §3.1/§5): Hypothesis cues are useful; broad concluding optimism is not evidence. Use direct measured verbs for own results, conditional language for mechanisms and explicit untested scope.
- **content** (EX01 §5/§6.1; EX02 §3.4/§4.2; EX03 §§2–4): Details matter when they bind fairness, reproducibility or interpretation, not because they look technical. Include assumptions/configuration needed to reproduce own conclusion; move execution logs and workflow status out of scientific narrative.

Completion boundary: these three selected-PDF reads are complete. The parent must combine all ten exemplars, template/skill verification, synthesis and own-evidence-bound blueprint before drafting. These notes do not establish any target-paper result, architecture collaboration acceptance or submission readiness.
