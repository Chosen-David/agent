# [COH-T27] 在已发布通信层执行真实独立发现→责任方返修→独立复验；保存旧失败、消息与产物版本，区分ACK和发现关闭，检查旧版本拒收、幂等及恢复。不将本地人工宿主适配计为后台模型调度或通信质量A/B。

Task-ID: COH-T27
Date: 2026-10-06

## Plan

在已发布通信层执行真实独立发现→责任方返修→独立复验；保存旧失败、消息与产物版本，区分ACK和发现关闭，检查旧版本拒收、幂等及恢复。不将本地人工宿主适配计为后台模型调度或通信质量A/B。

## Progress

### Preserved implementation and evidence

- [x] [COH-T27] 在已发布通信层执行真实独立发现→责任方返修→独立复验；保存旧失败、消息与产物版本，区分ACK和发现关闭，检查旧版本拒收、幂等及恢复。不将本地人工宿主适配计为后台模型调度或通信质量A/B。

COH-T21/23/27检查点：候选263958510f78789e33dd29676d510a672900ce26与338项实际源码一致；15/15角色及5/5主AI/交接案例已独立验收，两个角色经明确反馈返修，150个产物哈希复核。程序472项中464通过/8跳过。通信语义复验4/4，但实际5事件/9投递只有7回执，返修接收者seq4/5因超过180秒预算约33秒而被拒绝。保留原失败及两条待回执，不重置预算、不代签、不勾选完成；本批未commit/push。下一接续点是分析实际调度/工具往返耗时并预注册不同的有界恢复实验，证据`evidence/root-communication-gate.json`，不重做已验证论文/图稿、不计收敛轮次。

COH-T27新有界实验通过：相同180秒预算、相同原接收角色和原消息，合并实际读取并由角色自写两条回执，111.030秒完成。主AI独立核对5事件/9投递/9回执/0待办；原22项引用/源码、16项W4公开文件及旧超时记录完全保留。旧失败仍是失败，新实验是反馈后的有界恢复，不是公平模型性能A/B。证据`evidence/root-w5-communication-gate.json`。COH-T21/23等待最终发布与远端读回。

COH-T21/23发布核对：main `69cb8f22d751d8196ae80555f0127cf2e7976395`、tree `b651fd40844c6baa7aea862dfc5dc96e465b354e` 与最终冻结内容一致；191个改动文件有稳定TASK归属，观察器真实记录tested→committed→pushed→remote_verified，GitHub与Git双通道读回核对。普通非强制更新，未建PR/升级分支，保留并发main。十篇研究、全部角色、完整稿/现代图及通信门禁均有证据，失败仍保留；仅科学工作稿和固定案例通过，不声称模型质量或服务器部署提升。本批主体已发布，当前状态收尾仅文档，仍须最终main读回。

### Historical context

Original task: [line 198](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L198).
Shared methods, results and evidence: [source section, lines 178–205](../legacy/TASK.5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021.md#L178-L205).
Source SHA256: 5a4d2403378d39f88f7a70dbf8f49c8f80d93e1be500f16092f702c2a1320021
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
