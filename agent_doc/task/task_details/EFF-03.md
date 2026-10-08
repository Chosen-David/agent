# [EFF-03] 同输入冷/复用场景测量真实编码 token、上下文结构和确定性消费者结果；必要回归、插件同步、main直接发布及远端读回。真实模型质量/收费 A/B 未执行时准确标明。

Task-ID: EFF-03
Date: 2026-10-07

## Plan

同输入冷/复用场景测量真实编码 token、上下文结构和确定性消费者结果；必要回归、插件同步、main直接发布及远端读回。真实模型质量/收费 A/B 未执行时准确标明。

## Progress

### Preserved implementation and evidence

- [x] [EFF-03] 同输入冷/复用场景测量真实编码 token、上下文结构和确定性消费者结果；必要回归、插件同步、main直接发布及远端读回。真实模型质量/收费 A/B 未执行时准确标明。

用户授权继续优化 Agent 交互以兼顾效率、token 和效果；主 AI为单一写入者。本轮证据 `docs/communication_efficiency/2026-10-07-selective/`；临时 tokenizer 仅安装于私有运行目录，不改全局环境，不修改 SGLang。

EFF-01/02验收：最新预印本LatCom（2026-09-29 v1）、HEAR（2026-10-05 v1）及AgentPrune正式来源已核查，潜变量/学习拓扑/引擎调度仅作候选。消费者完整结论闭包与命名编码硬限已接入原Mailbox，必需声明及候选/拒用保留。tiktoken0.12.0两编码、3个公开合成任务同输入返回JSON冷加载减少49.6%–76.0%；全选无收益且增加65token。确定性小消费者和CLI通过；不是模型质量、总会话或收费A/B。发布前合入并发Codex安装提交c0347c1，保留其部署记录；合并后全仓538项（530通过/8跳过）、专项15项、reader3/3，引用同步通过；EFF-03等待实际main发布读回。

EFF-03发布读回：实现提交 `154c5ae948f72bcc4c7edc6aa28c2df11c7a1acf`、tree `5112d9735f036aac19c29272ef36fa38ea9c77be` 与完整本地验收树一致，已普通非强制expected_sha发布并经API/pull/独立ls-remote核对。PublicationLedger实际remote_verified；本轮结构及编码成本通过，真实模型质量/账单和目标宿主安装未验证。公开记录 `docs/communication_efficiency/2026-10-07-selective/publication.json`；后续按固定模型/权限/预算测总成本与质量非退化。收尾仅TASK和发布元数据，既有任务与原始证据保留。

### Historical context

Original task: [line 287](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L287).
Shared methods, results and evidence: [source section, lines 283–294](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L283-L294).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
