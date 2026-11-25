# 工程审查应先得到什么证据

主写调研，2026-11-25。适用于 chosen-agent 的只读审查包与 ResultStore 路由。设计复核来自 gpt-6.2-sol，批准调用 01a210a0-d41e-7780-9842-936ea03764fe。结论范围为设计。

| 一手来源 | 本项目的取舍 |
|---|---|
| [Barry Zhang，AI Engineer Summit 演讲，7:46 段](https://ai.engineer/talks/D7_ipDqhtwk-effective-ai-agents) | adopt。从 reviewer 实际看到的输入出发。只有 diff 和检查收据时，不能要求它凭空比较上游；主写提供已核查的来源和热点上下文。 |
| [Yang 等，SWE-agent](https://arxiv.org/abs/2405.15793) | adapt。论文研究 agent 如何利用专门设计的界面操作仓库。本项目把已有结果的目录、命中行、行哈希暴露在现有检索接口。论文未评估本项目的查重成功率。 |
| [Gloaguen 等，Evaluating AGENTS.md，2026](https://arxiv.org/abs/2602.11988) | adapt。作者在其编码任务上发现通用上下文可能增加成本。按查询给 reviewer 少量依据；避免每次塞入整份历史清单。README 命中的实际节约仍待长期评估。 |
| [Khatri，2026 年双 agent 上下文消融](https://arxiv.org/abs/2607.27250) | defer。其有限仓库和任务中没有测到稳定的正确性提升。后续用真实历史任务比较能否定位适用旧 run、误复用次数及审查成本，再决定是否扩大召回。 |

代码入口为 agent_runtime/codex_host.py 的 _invoke、result_store.py 的 search、task_manifest.py 的派发检查。当前设计沿用同一个主写和只读 reviewer。建议后续抽取重复任务做盲测：比较纯记录搜索和 README 路由的正确定位率、无效重跑与错误复用；若只能增加上下文却未改善定位，就收缩匹配范围。此项尚未实测。
