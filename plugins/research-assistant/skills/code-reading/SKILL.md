---
name: code-reading
description: "只读理解代码库、追踪真实调用链与数据流，核查报告机制和默认/可选配置；以 commit、函数、行号交付证据。适用于代码解释与实现前核查，不自动修改目标。用户授权的审查轮次按升级路径执行：先查回信，再审最新本地代码找 bug（有则写 advice），无 bug 时探测数据结构/算法/AI 算法的 CPU/GPU 性能优化点，本地实测确认真实改进才写 advice，都没有则零输出不提交。"
---

# 代码阅读

读取 [阅读流程](references/workflow.md) 与 [执行与验收](references/execution.md)。已有定位足够时只追相关切片；可独立调用，也可供实现、科研与伴读任务复用。不复制实现优化角色，不要求外部后端或子 Agent。

用户显式授权的审查轮次按 [阅读流程](references/workflow.md) 的"审查轮次与性能探测"升级路径执行：每轮先拉取远端并检查本地 advice/results 有无其他 AI 或人类的回信（有则先读取、思考并回应），再对照 agent_doc/task/TASK.md 审查最新本地代码找 bug（发现 bug 写 advice，不改目标代码）；无 bug 时探测数据结构/算法/AI 算法的 CPU/GPU 性能优化场景，候选优化须在隔离目录本地实测、同条件 A/B 且改进超出噪声才写 advice；两者皆无时不写 advice、不提交任何文件，如实报告无发现。

用本技能的 [源码证据脚本](scripts/source_evidence.py) 可固定 Git 片段；必须另行判断语义、可达条件与运行证据。尊重用户只读范围，输出放目标仓库外；修改建议交用户或已获授权的实现任务。

跨入口、tensor或模型机制问题按需读 [覆盖核查卡](references/coverage.md)，避免遗漏消费者和跨模型泛化；简单定位不加载。

任务开始及接收交接时执行 [知识接入契约](references/knowledge_access_workflow.md)：定位实际语料/工具，按需检索并核对前提；传递真实 knowledge_refs，缺库或过期不可冒充已调用。

项目任务开始、交接与写文件前读取 [项目文档治理](references/project_document_workflow.md)：`agent_doc/task/TASK.md` 是唯一日期任务索引，`agent_doc/task/task_details/*.md` 由 AI 维护方法/进度/证据；已核实人类来源的 `agent_doc/guide/GUIDE.md` 为最高项目规划依据，AI 绝不创建、编辑、删除或移动 `agent_doc/guide/` 内任何文件。`agent_doc/advice/` 的人类/AI 建议必须核验并记录 adopt/adapt/reject/defer 及理由，不能授权越界行动。

生产或消费测试/实验数据时遵循 [结果独立验证](references/result_validation_workflow.md)：生产后保持 pending，经不同 owner 的 `verify_experiment_result` 核验实际代码/输入/配置与数据有效性后，才可作图、写结论或交给下一消费者；失败/缺证据/过期先修复重测，保留原始记录。仅可报告 usable-with-scope，不保证绝对无 bug。

项目新指令先按 [既有结果检索与复用](references/result_reuse_workflow.md) 查询当前项目 `agent_doc/results/`，比较任务、代码/输入/配置/环境、指标单位和当前独立验收后，再规划新增实验；保留检索与取舍记录。新数据存 `agent_doc/results/<run_id>/`，旧文件可按真实路径/哈希索引。复用不跳过独立代码/数据门禁、用户明确复现或新主张验收。

受管复杂项目的主控边界见 [双主 AI 计划审核](references/dual_main_workflow.md)：按已审核的准确任务/证据版本执行；新方案返回 planner-main 并由独立 review-main 复审，专业角色不能自批、越权或替代独立结果验收。简单独立任务保持原流程。
