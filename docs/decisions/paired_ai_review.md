# 主 AI / 审查 AI：调研与采用决定

核查日期：2026-11-17。范围是用户要求的 AI–人类 / 双 AI 两种反馈模式。当前完成研究、协作契约整合与已有审核机制回归；没有启动第二模型，也没有把旧计划自动切换到双模型。

## 演讲与方法

| 来源 | 实际读取 | 采用与边界 |
| --- | --- | --- |
| [Lauren Tan：All Code Is Slop (Except Mine)](https://ai.engineer/code/2026/talks/lauren-tan)，2026-11-11 | 官方演讲阅读版及对应时间段文字；直播时间戳 1:03:09、1:08:23、1:11:00 | 先把重复错误变为结构约束和行为验收，再自动化外层循环。不是“两模型达成一致即可通过”的论据；报告的产出和回滚率不作为本库收益 |
| [Itamar Friedman：The Last Human Code Review](https://ai.engineer/talks/s-aixZYJG4c-last-human-code-review-building-trust)，AI Engineer World's Fair 2026（页面未给精确日期） | 官方阅读版，尤其 01:59、08:53、10:40、12:24、15:47 | 区分验证与意图对齐/学习；审查发现连回具体规则和代码，将问题交回实现者。演示产品不等于可直接移植的开源实现；“100 PR”是演讲启发式，不采用为安全阈值 |
| [Anthropic：Building effective agents](https://www.anthropic.com/research/building-effective-agents)，2024-12-19 | evaluator-optimizer、Agents、simple composable patterns | 使用有明确验收的生成→评估→返修；有停止条件及真实工具反馈。文章不是本库效果评测，不能推出两模型一定优于一模型 |

本轮读取文字资料，没有声称观看完整视频或复现演讲系统。

## 开源代码核查

固定本次读取版本；不按 star 或仓库宣传选择。仅借鉴机制并写本库协议，没有复制/安装整套上游代码。

### Superpowers：采用任务级独立审查，调整验证策略

版本 `22f0b463e7a5e579904dd6211a520321035526f7`（分支头提交 2026-11-03）。实际读 [task-reviewer-prompt.md](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/task-reviewer-prompt.md)，根 LICENSE 为 MIT。

采用：同一审查者分别判断需求符合性和代码质量；固定 base/head 与任务 brief；实现者报告是待核查主张；审查者不修改主工作树、不再派生审查者。只有具体跨模块风险才扩大读取范围，避免每小步重审全库。

调整：不照搬“实现者已跑所以审查者不重跑”的绝对限制。先核查证据版本和原始输出；独立验收合同要求或有明确疑点时，审查者在隔离环境复跑最小检查。也不采用套件的无条件跨任务自动继续来覆盖用户逐步共审。

### LangGraph-Reflection：采用轮转结构，拒绝把结束当通过

版本 `888d007163f1479e1e7a734f66dc7dcbd12424d7`（分支头提交 2025-03-18）。实际读 [src/langgraph_reflection/__init__.py](https://github.com/langchain-ai/langgraph-reflection/blob/888d007163f1479e1e7a734f66dc7dcbd12424d7/src/langgraph_reflection/__init__.py)。本次根 LICENSE 路径读取失败，未据此推断无许可；若引入代码须另核许可与依赖。

代码确实有 graph→reflection 条件回边；`end_or_reflect` 在剩余步数小于 2、消息为空或末条不是 HumanMessage 时返回 END。可借鉴反馈循环，但 END 不携带“验收通过”证明，消息角色也不认证真实人类。我们的预算耗尽/空报告必须未完成，不能把 reviewer 文本伪装为用户指令。

### Aider：只借鉴模型分工，不能替代独立审查

版本 `5dc9490bb35f9729ef2c95d00a19ccd30c26339c`（分支头提交 2026-05-22）。实际读 [aider/coders/architect_coder.py](https://github.com/Aider-AI/aider/blob/5dc9490bb35f9729ef2c95d00a19ccd30c26339c/aider/coders/architect_coder.py)。本次根 LICENSE 路径读取失败，未复用源码。

architect 提出方案后 editor 写代码；editor 可以显式配置，否则回退主模型。代码清空 editor 消息列表再传方案。采用显式模型配置和受控交接思想，但第二个写代码的模型不是检查结果的 reviewer；我们的双 AI 模式不能默默回退到同模型后仍标“双模型”。

### Anthropic code-review：采用发现复核，拒绝漏掉状态相关缺陷

版本 `fd30cee3ecd5a8ee772733c5d20c0f2bae2da2f0`（分支头提交 2026-11-16）。实际读 [commands/code-review.md](https://github.com/anthropics/claude-plugins-official/blob/fd30cee3ecd5a8ee772733c5d20c0f2bae2da2f0/plugins/code-review/commands/code-review.md)，根 LICENSE 为 Apache-2.0。

采用：发现先核实，绑定规则作用域和具体代码，去重并提供可行动反馈。调整为单一审查 AI 串行检查，不采用多批并行子 agent；不采用其忽略依赖特定输入/状态的问题的过滤规则，因为重试、取消和并发缺陷正属于这类问题。也不假定所有工具永远可用。

README 搜索结果提到 0–100 置信分及 80 阈值，但本次固定版本的命令正文采用二次问题核实，没有这个数字门槛。采用实际命令机制，不将自评分数当校准概率或正确性证明。

## 本库整合

权威行为规范仍是 `workflows/collaborative_implementation_workflow.md`，本文件只保留来源与取舍。

- 默认 AI–人类；任务显式选择双 AI 后，目标角色为主 AI + 审查 AI，两种模型、独立上下文、实现/审查串行。
- 审查同时覆盖测试之前的需求/验收设计和实现之后的实际 diff/行为。用户的原始要求与确认保留为原始输入，不能只有主 AI 摘要。
- 一份冻结审查包：需求/规格版本、base/head 或工作树快照、测试及其版本、原始运行结果、未决问题、变异结果和历轮发现。按要求逐项核对，代码改动使相关审查失效。
- 返回需求符合性和代码质量两个判断；问题包含位置、触发输入/状态、影响、依据、修复方向与复验。信息不足保持 unknown，不机械批准或打回。
- 关键语义交回人类；预算耗尽保持未完成；不同模型的共同盲点仍可能存在。

## 现有代码可复用处与缺口

`agent_runtime.plan_review.ReviewSession` 已有完整计划哈希、真实宿主认证回调、独立调用/上下文检查、完整反馈保存、跨 run 预算与 stale/revoked 回执拒绝。`single_main=True` 是作者自检，不是人类批准。旧独立协议允许同模型，不符合用户本次“不同模型”的完整要求。

没有改成另一套自报 JSON 门禁。后续运行时要在已有入口上接入：

1. 可信宿主解析实际 provider / model 的规范身份，区分别名与真实不同模型；不同上下文和不同模型分别核验。作者自填字段不认证身份。
2. 显式任务模式、同一逻辑任务的模式绑定及恢复；不能靠换 run ID 降级旧保护。
3. 只读冻结代码与隔离测试环境、单写者、取消、超时、token/费用上限；按结果明确进入返修或人类决策。
4. 对真实模型运行相同任务，评估已知缺陷检出、误报、遗漏要求、返修收敛、成本/时延及人类介入。未复现反例与真实收益不混报。

本轮不安装 LangGraph、不复活旧双主控自动执行，不修改人类 GUIDE；当前仍按单主执行研究与整合。新增 CPU 测试只验证既有审核 API 的拒绝行为，不能证明双模型已运行或代码质量提高。

## 2026-11-17 运行时进展

新增可选 dual-model-plan-review/v1，复用 ReviewSession 的账本/预算，绑定两个规范模型身份、两阶段规格/测试/代码文件和独立需求符合性/代码质量判断。CLI 默认 human，可显式 dual-ai。详见协作流程的运行时接入；尚无真实双模型质量收益验证，原调研的宿主能力缺口仍需真实接入验收。用户现选择批量实现后统一测试。
