# TOKEN-TOTAL-18 独立计划审核

决定：**approve（仅准许进入此有界实现及验证，不构成发布验收）**。

审核身份：宿主新子上下文 `/root/token_total18_review` 的手工源码与计划审核；未创建或声称受管 ReviewSession。未运行测试、模型调用或计时，未修改生产代码。仅访问 Agent。

绑定：计划 v1 SHA256 `de58f0b85f131fd1e2393798d05493d88fe9cc89708618649322dc646e6471fd`；`agent_runtime/token_usage.py` SHA256 `a2174b54938aa9a5048183bd36f0b54ca1efc9713dcce444365e5001d8069043`；基线计划指定 `91d7545b75b090a9eea977af185a6f8d13b5a736`，发布者仍须重新 fetch 核验。

## 核查依据

已读 AGENTS.md、prompts/decision_review.md、workflows/project_document_workflow.md、当前空白人类 GUIDE、任务索引 MEM-STORAGE-01 条目、计划、prior-search.json、全部五个命中 record 的 scope/summary、当前 token_usage.py、tests/test_prompt_context.py，及真实 RPC producer 的调用片段（token-001b-control-20261009/producer.py:165）。原先尝试 tests/test_token_usage.py 不存在，已用检索定位实际测试，未把缺文件当无测试。

源码最后一个 snapshot 的 last 每字段以 `type(...) is int` 校验；total 只用 Python 数值相等校验。故 JSON 真实类型中的等值浮点数以及数值 0/1 对应 bool 能通过 total 的 freshness 一致性校验。这是明确、低维护成本且与现有 last 精确类型契约一致的输入验证缺口；无需另加 schema 依赖或改变事件结构。当前测试覆盖累计历史不同、失败、工具、算术不一致、重复终止和最终 snapshot，但未覆盖此等值异型输入。

此缺口不能推导成金额算错：返回的计数依旧来自已通过精确整数校验的 last；没有历史 RPC 数据损坏、账单偏差或任务质量退化证据。修复收益只能描述为拒绝原本被接受的非法 total 字段，恢复严格输入契约；不得宣称 token 节省、KV 加速、计费修复或历史实验已污染。

prior-search 实际返回 226 条扫描、partial=true 和 65 项缺路径错误（完整覆盖不可推断）。五个实际命中均为本地 SQLite 通信或路由实验，其代码与 metric/scope 不匹配 RPC token 字段类型；不作为本次修复正确性证据或免测依据。

## 实施及验收边界

1. 最小新增 total 精确整数/非负 guard 后保留原有 total==last 和 last 内部算术约束；不得顺手调整 earlier snapshot 规则、工具/event 协议、JSONL API 或吞掉未覆盖异常。
2. 每个 total 字段应分别以 JSON 往返后的等值 float 检查；bool 包括 false/0 与 true/1，且 last 保持对应合法整数及总量关系。必须保留修前实际失败和修后普通、-O 通过证据；不能只静态论证。
3. 合法全零、常规计数、多 snapshot、累计历史拒绝等既有行为保留，并以完整返回对象比较确认无字段变化；非负 guard 与 last 的约束一致。
4. 独立结果复核另行绑定补丁及测试原始输出；本计划审核不替代该阶段。全库与 Reader 串行执行，公开报告需准确写 run/skip/error，校验开销未测。
5. 仅明确文件发布、保护人类指南和冻结历史，重新 fetch 处理并发并核验远端 SHA/内容；MEM-STORAGE-01 真实 KV/质量目标仍未完成。

本修复属于同接口低风险可靠性工作，符合已有 Agent 授权，无需扩大用户范围或为这一个语言类型机制凑论文。批准不证明整个 token API 无其他边界缺陷。
