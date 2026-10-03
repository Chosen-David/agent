---
name: code-reading
description: "只读理解代码库、追踪真实调用链与数据流，核查报告机制和默认/可选配置；以 commit、函数、行号交付证据。适用于代码解释与实现前核查，不自动修改目标或扩展成性能实验。"
---

# 代码阅读

读取 [阅读流程](references/workflow.md) 与 [执行与验收](references/execution.md)。已有定位足够时只追相关切片；可独立调用，也可供实现、科研与伴读任务复用。不复制实现优化角色，不要求外部后端或子 Agent。

用本技能的 [源码证据脚本](scripts/source_evidence.py) 可固定 Git 片段；必须另行判断语义、可达条件与运行证据。尊重用户只读范围，输出放目标仓库外；修改建议交用户或已获授权的实现任务。

跨入口、tensor或模型机制问题按需读 [覆盖核查卡](references/coverage.md)，避免遗漏消费者和跨模型泛化；简单定位不加载。
