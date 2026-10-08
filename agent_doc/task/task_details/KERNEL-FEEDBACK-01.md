# [KERNEL-FEEDBACK-01] 代码 Agent 编译反馈与条件化优化

Task-ID: KERNEL-FEEDBACK-01
Date: 2026-10-08

## Plan

用户明确要求将博客/trick 调研落实到 agent 库并推送 main。PROJECT_ROOT 与 WORKFLOW_ROOT 均为本库；不修改 SGLang、人类 guide、其他角色契约或既有批次结论。主 AI 单写 TASK。

主要缺口：现有代码角色有计时与噪声校验，但没有可执行的 PTXAS 诊断提取，容易将资源数量直接当性能结论。基线 9d0d05bfca88faf5c8fc57420bad4d5abf3b01a4；未改动时仍只能手工提取且没有本地结构化行号/日志哈希。此前未提交 HOST 证据完整保存在 baseline.json 指定的 stash，不混入本次代码发布。

范围：标准库只读 PTXAS 日志提取器；按需加载的编译/性能反馈参考；接入现有代码与主控包。复用 measurement_review.py、gpu_adapter.py，不新增运行时或测量调度器。外部资料只作方法来源，不授予执行权限。

预先验收：正常、多函数/架构、缺字段、冲突/截断、错误日志、格式未知的有限输入；每个提取值能回指原日志行，缺值为 null，不能串到其他函数；无覆盖写入或子进程执行；CLI 与独立 Skill 离线调用可用。最小有意义收益为将已支持字段可靠变成可核查 JSON，语义错误容忍 0。不主张模型成功率、GPU 性能或 token 改善。

先运行针对性与包同步检查，独立新上下文按真实任务使用入口并检查结果代码/数据，最后必要仓库回归与并发 main 核对。每次失败保留再修复；没有 GPU 仅验证解析与工作流，不接受 GPU 加速结论。预算：一个小脚本、一个参考工作流、最多两次针对性修复；复杂格式退回原日志，拒绝扩大为通用编译器框架。

附带修订 v2：三个已完成 CONT 详情缺少契约规定的 Plan 标题和 Task-ID/Date，导致整个索引验证失败；只修复结构元数据，保留原计划/状态及历史引用。独立检查确认没有目标或权限变化。

## Progress

2026-10-08：已干净 fast-forward main；先检索既有结果，返回 incomplete/无命中并保留具体缺失 record.json；知识查询/正文实际读取，拒绝将 B200 attention 卡迁移为本次性能证据。原自动优化批次、论文进度与收敛计数不改写。本次博客阅读新增全文论文数为 0。

证据目录：`agent_doc/results/kernel-feedback-20261008/`。发布状态 pending；目标为当前明确要求的有界代码 Agent 改进，原 HOST 批次全部门禁仍保留，不能宣称完成该批次。

2026-10-08 范围修订 v2：发布前文档校验发现远端 main 的三个已完成 CONT 详情使用 `## Plan v1`，违反现有精确 `## Plan` 契约；baseline 哈希和失败已保存。仅规范标题、原 version 移为正文，保持原计划内容/状态，历史派发不重激活。纳入独立审核。

2026-10-08：修复独立审核发现的两项解析缺陷并保留失败，最终 813 项全仓（805 passed/8 skipped）、Reader 3/3、包同步与文档校验通过；真实独立角色完成合成诊断任务并在修复后重跑。报告 `agent_doc/results/kernel-feedback-20261008/report_by_gpt.md`。CLI 缺写凭据，改走连接的 GitHub 接口；远端发布尚待实际读回。

2026-10-08：真实独立审核身份/回执哈希经主控核实，调用既有 inspect_result 返回 usable-with-scope，见 host-acceptance.json；不把记录文件当永久可信 adapter。准备最终内容树与普通 main 更新。
