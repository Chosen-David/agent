# Memory Tax: net-value reading

2610.34073v1, *Memory Tax: Dissecting the Net Value of Agent Memory*, Xuan He et al.; submitted2026-10-25T05:29:05UTC. Primary: https://arxiv.org/html/2610.34073v1 . This differs from2610.29823, already read in this batch. Official metadata has v1 only; a search mirror's update date is not a version.

Read main§§1–8/Limitations, appendicesA–C/E–F, Tables1–26 and Figure1–17/27–29 captions within those sections. AppendixD case studies, rendered images, author code/raw result replication excluded. Earlier1559partial and1657completion count as one body only after independent source review and public readback.

## Method and experiments

- Raw-history hybrid RAG is the reference: turn/session-aware chunks, BM25+dense union/reranking, single-round and conditional second-round retrieval. Query-level memory benefit/tax is a correctness overlap partition relative to **1-round**RAG; Table1 differences use **2-round**RAG. The difference is descriptive and reference-dependent, not an identified causal effect of one memory operation.
- Eleven memory systems, three QA backbones, three main datasets. PersonaMem-v2 uses40/200corpora; MINT60/595; Luna LongMemEval100/500stratified subset. Learned Mem-T/Memory-R2 retain released policy models while QA changes. Gold-context analyses exclude questions lacking gold evidence; full-context reference can truncate earliest units. Judge accuracy is not verified end-to-end coding-agent quality.
- Retrieval Scope divides exposed retrieval-content tokens by each system's retrievable store, with Qwen3.6-27B tokenizer; content exposure can include retrieval-time LLM reads. Nonsearched metadata is excluded. Authors explicitly say this does **not** equalize absolute inference tokens. Fixed-k exceptions and reported below-RAG RS cells remain: e.g., HippoRAG2 Luna LME1.28% vsRAG1.91%, SimpleMem Q4B MINT4.96% vs6.73%. Do not turn approximate alignment into a hard matched-budget guarantee.
- A/B ablations vary chunking, retrieval, embedding, reranker; BM25-only/dense-only also remove reranking, so they do not isolate just hybridization. Selected default-vs-adjusted k comparisons include regressions, e.g. PM-v2 SimpleMem37.5default→34.7adjusted and HippoRAG247.3→46.5. MemOS postprocessing/reranking and LightMem extraction checks are selective configuration controls, not exhaustive tuning equivalence. A strong RAG reference is useful; no proof this exact RAG is universally best.
- Gold raw-turn→memory mapping is deterministic for some methods, otherwise uses two label-informed LLM selectors and human adjudication. Manual spot checks show extraneous/missing units; oracle-memory vsoracle-raw comparisons therefore remain mapping/packaging-sensitive. Separate500raw-turn human preservation annotations avoid LLM filtering for one-to-many units. Preserved evidence and retrieved evidence must be measured separately.
- Iterative replay excludes already retrieved units and may rerun graph/query refinement. Similarity drift is indicative, using median similarity for one-to-many mappings; embedding similarity is not every system's ranking rule. Cross-backbone robustness can also change retrieval where it calls the LLM, so it is not purely a fixed-evidence QA experiment.
- Broader retrieval-only benchmarking uses one QA backbone and adapted protocols: LoCoMo excludes abstention, ES-MemEval onlyQA, multimodal data becomes VLM captions. Experiential stores freeze after training/dev; top2raw-trajectory RAG can help or harm. BigCodeBench is single-shot, Mind2Web offline gold-step evaluation; they do not establish multi-turn recovery. World-model comparisons use different systems on H100/50steps, not a controlled swap of memory representation within one generator.

## Costs, uncertainty and unresolved references

Reported LLM tokens sum ingestion/maintenance and QA; E tables split build/maintenance/inference, calls and offline/online time. Time is a **single-concurrency equivalent**, not observed user wall time under equal serving; endpoint variation remains. Input/output token sums are not cache-weighted dollar bills, GPU/RAM cost, embeddings/reranker cost, or a complete all-role engineering cost. Store tokens are not physical RAM. Experiential build tokens are amortized over test tasks; no inference-only savings should be called net savings.

Tables18–20 provide selected dataset/backbone cost triples, not every main score cell's full costs. Repeated-run intervals/significance, judge audit sample sizes and concurrency normalization formula are not established in read scope. Human-judge agreement is reported, not an uncertainty guarantee. No statistical reanalysis or author artifact reproduction was performed.

Main§6.1/6.2 claim recovery/recursive-memory improvements but refer to an unnumbered `Table`; no quantitative table for those interventions was located in the read sections. Keep those proposals unverified. Main/appendix figure references and some Table8/9/10 references are inconsistent with adjacent captions; do not silently relabel or infer missing results. AppendixD was not read, so do not claim an exhaustive source audit.

## Repository applicability

采用评价方向：对照同任务的原始证据检索与现有记忆路径，分别保留双方成功、记忆新增成功、原始检索成功而记忆失败及共同失败；同时区分存储保真、候选可达、完整依据包与最终模型使用。冻结问题/原始来源/版本、记录绝对完整输入和全角色成本，更正/异议/依赖不能被短上下文隐藏。此方向不等于新实验批准或本库收益。

源码关系：KnowledgeStore.context装入完整已声明先决包，超预算显式partial；check_refs只验已发布身份/先决闭包，非语义适用性。basis_context保留候选/拒绝声明、必需引用和祖先；缓存提示须是当前消费者实际持有。artifact_context恢复两版精确字节和宿主绑定，但不能证明当前来源新鲜或模型理解。不可把引用完整、无损编码或查询命中当成任务质量。

暂缓新增并行原始检索、自动递归写回、学习选择器、频率降权/删记忆或agent_doc迁移。恢复条件：本库真实宿主、留出任务、引用与更正保留、完整模型输入、全角色费用及最终质量的同条件独立验收。没有新生产实现或旧实现副本；无测试执行/实验模型或后端调用/性能提升。独立AI审核1次，全角色tokens/费用unknown；手工审核非受信runtime认证，历史登记unknown。Plan54和旧耗尽门禁保持；SYSTEM99未完成，同批27→28仅限公开可恢复阅读链。
