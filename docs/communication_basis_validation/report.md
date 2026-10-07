# 知识与通信依据升级验证（2026-10-07）

目的：落实用户认可的知识/通信建议，并显式约束上下文成本。开发基线 main 8411705 已提供 check_handoff_knowledge，本轮复用而非另建检索、Skill 或图数据库。发布前合并 a35a102 的工程知识/复用入口，双方 TASK/CODEMAP/主入口追加内容均保留，重新验证合并语料。数据是公开合成程序 fixture，未调用模型。

## 实际改变与消费者

- 通信 consume_handoff 接入统一 check_handoff_basis。知识根和必需引用由独立消费者决定；项目 MemoryLedger 的漏报、unknown/candidate/stale/superseded 同时阻断。knowledge_required/memory_required 允许消费者在具体 ID 尚未知时要求真实声明；旧无依据交接兼容。
- evidence_claims 记录知识/记忆/产物→结论→下游结论，以及前提和可观察证据。supported 不允许未知前提、无前提证据或不支持的父结论；程序不判断证据内容真伪或定理适用性。actual artifact 哈希仍由原 handoff 校验负责。
- 已校验交接及独立 request 在原 SQLite 中固定绑定，impact 动态重新核验并返回实际接收者、受影响结论。知识前置依赖和 MemoryLedger 祖先更正可传递；manifest/消息引用失效属于整包来源失败。ACK/原数据保持原样，修订由可信主 AI按已批准 correction 路由推进，不自动科学关单。
- prepare_context 是现有 Mailbox 的可调用 host 入口，CLI context/impact/usage 同时验证。大产物只保留引用；必要知识和项目记忆完整依赖才可发送，超预算拒绝而不截断。缓存仅来自该消费者当前上下文，内容身份和状态重新核验；只缓存记忆叶节点不会漏掉未加载的祖先。
- context_max_chars/context_max_tokens 为消费者硬限；实际 tokenizer 回调计数完整 payload，没有 tokenizer 不伪造 token。max_delivery_bytes 约束累计 fan-out 字节，重复事件不再计费、预算失败不部分投递。整轮真实输入/输出/推理 token、工具包壳及重试费用仍由实际 host 的总预算接口负责。
- 通用主入口、科研主入口、规范及独立插件引用同步。没有启动服务、模型后台 adapter 或升级用户旧安装；不修改 SGLang。

## 验证

19 项专项测试覆盖：缺少/额外/失效知识和记忆、前提 unknown、候选/拒用、依赖环、必需结论、请求不可变、合法无关库更新、知识前置更正、记忆祖先更正、产物/manifest 变化、完整缓存依赖、CLI、字符及 tokenizer 回调预算、投递 fan-out 幂等和拒绝。

原子拒收不 ACK；impact 只登记 validated_handoff，不把读取/检索当科学应用。合成更正使 certificate/paper 失效，独立结论仍不在影响列表，两个已校验消费者可定位。缺少显式依赖无法推断；无 claims 的旧包只有整包 stale 粒度。整包消费失败后，可信主 AI可新建不受影响的独立任务/产物继续，不伪称原包已验收。

精确成本见 verification.json；复现 `python docs/communication_basis_validation/verify_upgrade.py`。冷上下文 4497 字符/6142 UTF-8 字节；同一消费者仍实际保有全部依据时，复用上下文 1007 字符/1007 字节。所有引用、结论/前提和产物列表保持相同；重复正文减少 3490 字符。两消费者两轮、包含首次加载的合成序列化总量 17988→11008 字符。这是负载构造对照，不是模型公平 A/B、真实 tokenizer 成本或质量收益。

合并后全仓 513 项：505 通过/8 跳过；reader 3/3、专项 19/19。结果见 program-tests.log/reader-tests.log/basis-tests.log。并发新增的嵌套 infra.flashattention-io 工程卡沿同一依据/预算接口验证通过（科学适用性未验收），见 verification.json。机器校验不是形式化证明、自然语言独立评审或未见模型验收；公开开发题不能再当 holdout。当前没有 tiktoken/transformers 或模型 host adapter，真实 token、质量、LLM 延迟均未测；当前宿主无 tmux，不声明后台监督。

## 最新研究对应与取舍

检索/回查日期 2026-10-07，固定下列原始 v1；均按预印本记录，正式接收/发表状态未核验。沿用上一轮已读方法，本轮复查相关方法与成本段，没有将论文收益数字移植为本仓库收益。

| 来源 | 读到的机制 | 本轮采纳/限制 |
|---|---|---|
| [MAP-Graph](https://arxiv.org/html/2608.10509v1)，2608.10509v1，2026-08-11；§2–3、4.1/限制 | 执行来源图、祖先影响、动作前重核 | 复用现有 SQLite/MemoryLedger 保存声明的依据与结论依赖；不是复现它的完整权限/信任评分策略。作者实验为受控合成任务，不能证明开放科研真值。 |
| [CoMem](https://arxiv.org/html/2609.15009v1)，2026-09-14；§3.1–3.4、4.3–4.4 | 私有/集体经验分层、经验晋升；双检索与验证存在 token 成本 | 保持项目经验与通用知识不同层，候选需独立验收；不用使用频率/平均奖励替代数学证明，不删稀有正确定理；不新增未经测量的双流检索或模型反思调用。 |
| [ShareMem](https://arxiv.org/html/2609.32511v1)，2026-09-26；§3、附录B.2 | 适用范围优先、共享经验与偏好分离、检索预算 | 采用当前任务依据与消费者预算，拒绝无关共享内容。缓存复用是本轮工程实现，不声称论文已证明这个实现；不照搬其 K=5 到数学库。 |

本轮没有采用学习式通信剪枝、自动摘要/晋升或跨主机协议；这些需要同模型同工具与总 token 预算的独立对照。下一步：在支持真实模型调用的 host 中固定 relay/broadcast/targeted 三组，记录首轮+重复加载的全部输入/输出/推理 token、时间、正确结论、拒用、返修及未见问题；已公开 fixture 单列回归。实际收益未证明前不调整生产检索权重或模型行为。

## TASK 与发布

BASIS-01 对应统一门禁和结论依赖；BASIS-02 对应影响追踪和有界上下文；BASIS-03 对应程序/成本检查、引用同步及普通 main 发布。单一作者主 AI，本轮没有子 agent 委派、没有无关路径移动/删除，旧持续任务保持接续。发布提交与远端读回由私有 publication ledger 和最终用户汇报记录，报告不伪造自身提交 ID。
