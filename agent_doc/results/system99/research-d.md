# SYSTEM-99 正文阅读 D

2026-10-20新增1篇，同一未结束批次累计12篇。事先检索本库results/knowledge/docs未见该ID或PlanFence；不以摘要抵正文。

Chen等，[Fresh Memory, Stale Plans: Derivation Currency for Distributed LLM-Agent Memory](https://arxiv.org/abs/2609.03340v2)，`2609.03340v2`，2026-09-27修订。实际原PDF42页，SHA256 `71c547d4aa0d49b82d0669abeffd718ed451f40e743ff990257325373cbb6e3e`；v1 HTML/PDF入口失败，改取v2。正文§1–7（页1–13）、附录E/F（页33–38）已读；表1原页已视觉核对，其余附录/图未完整审读，代码未复现。

- 方法：记录计划的真实输入版本，沿声明依赖恢复来源，在动作前比对owner当前版本；只准一次重规划，缺件或冲突则阻塞。
- 实验/消融：固定S-Bus验证器，仅补继承版本，使handoff冲突检出0/30→30/30；PlanFence有初始化失败，保留分母。五角色、三任务族的30个live案例不能推广所有任务。F中相关持续更改可耗尽恢复预算，无关更改对照不阻塞。
- 局限：依赖由应用声明；版本有效不等于语义正确、授权或动作时原子一致。通信成本实验隔离了模型生成，不是完整请求提速。
- 本库adapt：保持已审计划/handler输入与新查询观察分离；F仅评估完整无错响应的纯scanned变化。reject：按论文默认忽略检索缺口、自动重规划或引入新记忆服务。作者成绩不算本库收益。
