# [MATH-60] FIFO 完成量的按需知识入口

Task-ID: MATH-60
Date: 2026-10-09

## Plan

### 目标与验收
持续知识建设与直接main授权。将MATH-59的有界经典部分整理为math.packetized-completion@1，已有Skill/KnowledgeStore.search/show/context按需消费；不改SGLang、guide、生产调度或新建Skill。105 published/5 candidate基线；保留上游candidate，不把镜像同步当核验。一般证明、边界/反例、公开CPU与检索检查经独立审核才发布。无模型实测只报告知识/结构检查，不主张性能、token或真实多机认证。

### 实现方法
正长度l_i≤L、Q_n→∞、P(x)=max{Q_n≤x}；packetized A、同序无丢弃FIFO、边界即时可见D_c=P(D_f)。证明截断差/积压差、同边界阈值延迟相同、服务弱化[β−L]_+；明确末端packetizer与串联系统不能混淆。自包含证明，无额外强依赖，关系链接现有PagedAttention仅为非定理迁移边界。经典源LNCS2050在线2022-08-23版§1.7.2 Thm1.7.1/Remark1.7.1；2026 ECRTS正式论文筛选§2/§4.2/§6相关范围，不复现其性能。六月arXiv仅元数据、全文不可用，defer。

先保存实际结果检索(incomplete/scanned54/hits0)与知识检索；MATH-59是文档非可复用测量。新Fraction有限fixture包括完整边界、边界前、无界等待/非边界目标、乱序与可见延迟、串联反例。固定公开自然问题含无定理名/跨域/前提失效，file+SQLite各top3与实际chars/seconds；人工前提核对不冒充模型拒绝。未见模型holdout本轮不设计、不加载，保留未来独立测试缺口。53相关知识回归一次、知识快照字节一致；全局镜像已知code-reading stale不扩大修复。

root唯一TASK作者；独立fresh plan approve→produce→不同fresh verify_experiment_result→consumer/publication。相同冻结合同贯穿三个节点。1200秒、最多2返修周期/2attempts；仅真实本地宿主调用，非部署ReviewSession/远端监督器，无GPU/监控服务时继续本地独立工作。write范围为新卡/knowledge README coverage state及生成knowledge快照、当前结果目录、当前详情/索引。新证据稳定Plan改变则返修；推送fresh fetch/CAS、远端SHA/tree核对，无force。

计划v2返修：绑定MATH-59 advice/文档manifest/最终独立审核，以及coverage/upstreams/5candidate原始哈希；10固定公开case、3问题×2后端Top3全部命中、单卡全文context≤8500chars、53回归、候选字节不变为明确验收。保留cycle1计划/合同/标准与完整反馈，不覆盖旧失败。

## Progress

- clean main fast-forward到da67ace275c66038eb0dda5d5ea4a9430dd385d7；读取AGENTS/TASK/角色/知识/状态。未见相同active任务。本地没有真实模型/GPU/服务器监督适配器，均不宣称部署。

- 独立计划cycle2 approve；不同fresh结果审核usable-with-scope。首次ResultStore登记失败（card正式路径在outputs），保留attempt1，复制字节相同结果目录快照后，经原独立审核第二次实际FINAL重绑；父级观察两次FINAL后inject可信本地回调，最终验收/登记成功。10精确case、6结构检索/context4811chars、53回归、230镜像及5candidate保留。无模型/GPU/Lean/token/e2e/未见题测试；global既有code-reading stale未修；准备main发布。
