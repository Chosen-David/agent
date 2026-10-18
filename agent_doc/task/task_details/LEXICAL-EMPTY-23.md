# LEXICAL-EMPTY-23：空词查询避免全库分词

Task-ID: LEXICAL-EMPTY-23
Date: 2026-10-19

## Plan

基线33ff30a0e068c4ad6e17cb6bf18a79b041fdef11。用户授权Agent仓库实现、测试和main发布。
仅在KnowledgeStore.search完成原有query/limit校验和分词后，空词集合直接返回相同空结果信封。
同步插件副本，不改分词语义、不增加缓存、不改语料；主AI唯一实现与TASK作者。
GUIDE为空且只读；无新advice作为授权。人工有界DAG：历史/知识检索→独立计划审核→
修前失败/实现/测量→独立结果验收→回归/报告→fresh fetch/main发布回读。
未安装原生ReviewSession/tmux适配器，不声称原生监督或认证；预算45分钟、1种实现，无付费API。

历史搜索231目录partial=true（缺失record错误）；combined-corpus两项、comm-confirm、
math-discrete-lyapunov、math-fano-message均非本函数性能证据，不能复用计时。
知识检索命中algo.gqa-uptraining和math.weighted-bilinear-low-rank，不适配此集合空判定，拒作证明。
沿用memory-storage-20261015/research.md的12篇既有阅读矩阵，不称本轮新精读10篇。
本轮打开LongMemEval原文核验检索/阅读分层；优化依据是空集交集恒为空的代码语义，
不声称论文提出此优化或模型质量提升。

验收预先冻结：实际knowledge语料，固定PYTHONHASHSEED=0；完整search调用，load在计时外。
查询!!!、🙂、Ω以及memory retrieval、low rank、量纲、topk、zzqxnonexistent、ＡＢＣ。
一对warmup、7对交替AB/BA，每样本5次；全部原始wall样本与输入/源码hash保留。
前三个空词查询均至少降低50%中位耗时，其他查询不慢于max(基线×1.15,基线+0.5ms)。
全JSON差分、非法query/limit仍拒绝、Unicode兼容归一化仍检索、返回隔离、镜像一致。
新增一次分词回归修前必须失败。独立验证实际代码/基线/原始数据/计时口径/复测六项，
只有usable-with-scope后消费结论。结果目录agent_doc/results/lexical-empty23-20261019。
不把热store局部收益当CLI启动、模型推理或真实任务质量收益；无收益则保留负结果不发布。

## Progress

fresh fetch后main仍为基线，工作区干净；待独立计划审核。

独立计划审核先要求补TASK索引，回读后approve；随后补齐详情Task-ID/Date元数据，
技术Plan不变，文档校验通过。三行生产改动及镜像保持CRLF。
修前6子场景失败，修后3测试通过；主测/独立各9查询63对完整JSON相等，阈值全部通过。
独立144组边界差分及六项验收usable-with-scope，原始证据与限制在结果目录。
全库1276测试（8跳过）、Reader3通过；无模型质量或整体推理提速主张。
剩余：主控fresh fetch、原子main发布并回读；后续继续正常查询成本与真实任务评估。
