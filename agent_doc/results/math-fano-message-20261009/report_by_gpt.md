# 有限消息容量与压缩任务风险_by_gpt

Task-ID: MATH-63　Date: 2026-10-09

新增可检索知识 `math.fano-message-budget@1`，沿用现有知识Skill，未新增常驻提示。其用途是检查有限任务标签、接收者旁信息、合法消息字母与错误率之间的必要条件；前置为已有DPI/任务充分性条目。域与问题结构索引均由卡片字段及coverage维护。

## 本轮实际增量

条件Fano的熵链式证明、随机解码独立性、有限字母容量和top-C后验计数界；拒绝将变长消息当固定bit、忽略先验、漏算检索/共享状态或将必要界误报为可达模型能力。均匀8分片仅两消息无旁信息最多1/4成功；真实四组组号加两消息可完美路由。一般结论靠非形式化证明，公开枚举只是最小边界验证。

FOCUS [2609.37590v1](https://arxiv.org/abs/2609.37590v1)，2026-09-29提交，检索2026-10-09，原文Under Review。选择性核查方法、假设、成本和失败段；其“保留遍历流程但丢了联系人身份”的案例提示应另测待办ID完整覆盖。草稿引用频率只是效用代理；论文所报效果未复现。默认草稿rollout和防御核验也应计入所有token/调用预算。

## 验收与限制

8个公开精确Fraction案例通过，熵浮点sanity容差1e-12；6次公开Top3查询命中，两条目上下文9670字符。文件后端为files-lexical-v1，索引实际为sqlite-fts5-rrf-v1（协议外层沿用sqlite-lexical-v1标签）；FTS5/BM25-RRF加curated alias词法路径，不是语义模型检索。

知识和索引34项回归通过；独立审查重算、重放并核验冻结254个绑定。初始requires schema错误已修正，失败日志保留。回归12.085秒，枚举约0.0027秒，6查询合计约0.0341秒；均为本机诊断，不能当性能对比。真实token成本、模型检索/拒绝准确率、多机效果、e2e和Lean均未测。公开案例不再是未见测试；未用holdout内容不读取，原字节保留。

候选“紧凑计划＋完整ID清单/验证检索”未接生产；必须同模型、工具与完整调用预算对照后才能采用。本轮没有值得声称为生产性能提升的改进。全局任务文档检查被现有COMM20-01身份/日期元数据问题阻塞；知识范围的通过不等于仓库整体通过。

## 证据与续接

fixtures/verify/raw、retrieval_protocol/retrieve/retrieval、sources、plan及两轮计划审查、manifest、独立receipt与review、regression和preservation_check均在本目录。主AI以实际reviewer完成事件及receipt摘要钉定原生验收，登记仅允许已审范围消费。coverage、状态和任务索引更新，保留原GPU/其他域后续游标。下一轮应定义真实消息字母、缓存/工具旁信息和全部成本计量；不得由消息计数界直接推断LLM节省token且效果提升。

提交状态见同目录publication.json；仅agent仓库，未改SGLang或human-only guide。
