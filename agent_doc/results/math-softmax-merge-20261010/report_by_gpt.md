# MATH-73：分块softmax合并，本轮证据与限制

本轮仅增加按需文档候选candidate.softmax-block-merge@1，未加入canonical条目/Skill/生产行为。经典normalizer合并补全为weighted-value state，给实数结合/交换证明、显式empty单位元及LSE单位接口；公开反例覆盖直接平均、局部重试重复、遗漏、全空、不同head、浮点重排与过小质量/大value。跨域离散Gibbs对应保留指数权重与线性观测，不套到温度不一致/无限极限。

迁移结论：完整同row near/far分片可按真实质量合并；far候选只能认证保留并集，不能恢复完整attention mass。分片协议需要query/head/layer/KV/mask/位置与statistic版本、唯一分区及attempt去重。当前只是规范建议，未验证生产通信或SGLang源码，无新bug确认；轻量逐层参数求解器/速度/模型质量未测，不能宣称提升。

实际验证：公开解析开发题和普通独立文档审核；不是CPU数值实验、模型检索/拒用测试、GPU/Lean/未见验收，也不是可信ReviewSession或受管结果验收。阅后公开开发题不再算未见。首次审核发现knowledge_ref复合hash误写全文hash，已更正并重绑定；不改变数学主张。精确最终SHA和独立审查见document_review.md。

历史检索真实scanned119、partial=true，带缺record错误，不能声称完整无既有结果；三个首选命中结构不同未复用实验。已按对象核对真实math.softmax-barycenter-error@1，拒绝adapter merge等词法误命中；候选导航同时提供algebra/numerical-analysis/statistical-physics及问题结构索引，canonical检索/计数/旧学习游标保持。

近期筛选固定2606.01502v1的partial/cost相关节，保留abs错误、title差异、最新版本与发表状态未知；作者有限数值结果不证明浮点一般结合律，其速度不是本机测量。classic1805.02867v2相关定理与式4核对，不移植V100速度。

下一步：有固定真实kernel/合法分片、硬件/独立数值验证资源后，按advice实验矩阵检验输出误差、全链路通信/调度总成本及same-budget模型质量。缺这些证据，本轮没有值得接入生产的改进。MATH65旧失败、预算和暂停状态不变。

提交：按用户授权发布前fetch同步，直接main，不建PR；远端SHA/parent/tree核对在交付时报告，不能用本地commit代替远端成功。
