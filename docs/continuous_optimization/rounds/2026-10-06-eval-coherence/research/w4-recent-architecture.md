# Recent architecture stress tests — source preflight

Requirement: T25, user2026-10-06 extension. ClassicTransformer/ResNet/U-Net results are foundational checks only. This is a frozen three-case addition, not an assertion of exhaustive CCF A coverage or completed tests. Root verified the2026CCF originalclassification: TPAMI A(p.51), CVPR/ICML A(p.57); see w4-ccf-classification.json.

|Case|Publication/version|Mechanism difficulty|Read scope|Decision|
|---|---|---|---|---|
|gazing2026|[Attend Before Attention: Efficient and Scalable Video Understanding via Autoregressive Gazing](https://openaccess.thecvf.com/content/CVPR2026/html/Shi_Attend_Before_Attention_Efficient_and_Scalable_Video_Understanding_via_Autoregressive_CVPR_2026_paper.html); CVF accepted-paper open-access version, pp.17022–17034|Autoregressive temporal history; multi-scale index vocabulary; prediction-controlled stopping; training-only reconstruction reward; downstream pre-ViT selection.|Main Sec.3.1–3.3, Eqs.1–4, Fig.1/3 and captions (physical pp.1,3–5); author arXiv v1 Appendix A/B pp.14–15 and Limitations G p.16 as explicitly distinct supplementary evidence.|Admit to actualproduction and independent semantic/visual tests; notpassed|
|doubt2026|[DOUBT: Decoupled Object-level Understanding and Bridging via vMF-based Trustworthiness for Hallucination Detection in MLLMs](https://proceedings.mlr.press/v306/chen26dl.html); PMLR306 pp.16418–16441, official24page PDF|Parallel sampling versus sequential object bridging; frozen sentence encoder; normalization/operator order; two-set score fusion; threshold polarity; reference-answer/evaluation isolation.|Sec.3 pp.3–5 in full, Fig.2 and Algorithm1 p.4, Eqs.1–6 p.4–5, implementation details p.6, stated object-error propagation p.4–5; conclusion and scope p.9–10. No claim of full24page deep reading.|Admit to actualproduction and independent semantic/visual tests; notpassed|
|ditfuse2026|[Towards Unified Semantic and Controllable Image Fusion: A Diffusion Transformer Approach](https://ieeexplore.ieee.org/document/11297852/); arXiv2512.07170v1 author manuscript, associated DOI10.1109/TPAMI.2025.3642842; not claimed typeset IEEEversion|Two image conditions plus text and distinct noisy target; trainable-LoRA/frozen paths; hybrid block mask; recurrent50step inference; M3 corruption/target pipeline; paper/code version conflict.|Method Sec.III pp.4–7, Fig.1/2 p.2, Fig.3 p.5, Fig.4/5 p.6, Fig.6 p.7 and captions/Eqs.1–5; supplementary evaluation pipeline Fig.13 p.12 read to distinguish from architecture. No full18page deep-read claim.|Admit to actualproduction and independent semantic/visual tests; notpassed|

## Evidence and frozen acceptance

Each case has8scientific invariants plus4visual/reproducibility criteria,36total. Acceptance requires3/3actualcases and36/36criteria; missing execution is notpass. Fullrubric, IDs and paragraph/figure locations are in the JSON; hosttasks/rubric and producer-only fixtures are in scratch recent-architecture-sources. Existing agent_eval_pipeline must hostactualexecution. Primary PDFhashes and exactreadranges prevent classic/sourceversion substitution. No originalPDFs/screenshots committed. A sourcebrief is not an output or successfulexecution.

Sourcevisibility is frozen: AutoGaze and DiTFuse are reference-visible originalredesign; DOUBT is a heldout reference-hidden method-to-diagram task. Only the independentgrader may view DOUBT originalfigure; producer gets groundedmethodfacts, no visualreference. This isolates sourcecomprehension/layout construction from templatecopying.

## Findings that make the new cases discriminative

- AutoGaze: image resolutions32/64/112/224 are not patchside lengths. TrainingactualVideoMAE reward must not become a mandatoryinferencepath; stopping uses predictedloss. Temporalhistory and multiscalepre-ViTgather are separate constraints.
- DOUBT: correctoperatororder is normalize individual embeddings, compute2independent mean-resultant norms, then average2scalars. Pooling2Kembeddings or reversingthreshold polarity breaks the method. Frozenencoder and reference-answer/evaluation boundaries are explicit.
- DiTFuse: noisyoutputlatent differs from the2conditionimages; M3 target is available despite broad absence-of-fused-groundtruth claims. Hybridmask is not unrestrictedall-to-all attention. Current authorcode LoRA targets qkv_proj/o_proj while selectedpaper says alllinear layers; diagram must name its paperscope and disclose mismatch. The unrelatedGPT4o evaluation is excluded from generation.

## Cost and limitations

Read-onlydownloads, CPUtextextraction and renderedpageinspection; no weights, externalruntime, GPUtraining or paidservices. DOUBTcode pin attempt hit GitHub403ratelimit; not retried, codeevidence omitted. CVFHTMLwebopen403 but officialpublicPDF download succeeded. SelectedDiTFusefulltext is authorv1, not IEEEtypesetversion; journalissue metadata is corroborated by officialauthorrepo citation and DOIlandingidentity (rootverification). These are carefully sourced redrawtests, not scientificreplication nor generalproof of diagramquality.

## Next owner/action

Root verifies latestcategory and freezes finalcandidateSkill, then real research-diagrams produces eachcase from ownsourcefixtures; independentreader checks source topology/operators and actualfinalPDF/color/grayscale. Report originalsversusredraws and failures. Do notlowerdenominator ormarkT25complete until actualnewcasespass.
