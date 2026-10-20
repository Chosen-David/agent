# CONCISE-98

Task-ID: CONCISE-98
Date: 2026-10-20

## Plan

Version: 2

用户2026-10-20要求精简注释/AI文档，并改进CLAUDE.md、AGENTS.md及仓库组织。基线50c1ca1。
采用现有实现、组织、主控Skill的按需补充，不新增角色或导入整套插件。
独立审核→短规则与入口修复→结构回归/盲测→独立验收→fetch/普通main发布。
主控独占源码、规则、TASK；审核者仅写results/concise98/independent*。

- CLAUDE.md已有`@AGENTS.md`，却重复维护旧doc/task、doc/guide、doc/results路径；改为平台薄入口，保留主控与首次安装指引。AGENTS.md保留完整权威规则，不在本轮大重写。
- 新增一个共享精简工作流，同步到现有3个Skill本地引用；保留原因、接口、风险、证据、许可、工具指令，不按行数机械删除。
- 允许同步器MAPPINGS与专项测试调整，不改运行算法；不给历史报告做追溯改写，不碰人类guide，不搬活跃文件。AGENTS只增加短导航，原权限/验收规则逐字保留。
- 验收：CLAUDE错误旧路径8处→0、字节减少且权限/任务/验收要求通过AGENTS导入可达；Skill镜像一致、链接闭合；独立新上下文编辑样例保留关键事实和可执行token。
- 结构测试不是模型遵循率；字符不是token，不宣称推理加速。盲测失败则改规则后再测，最多2次。不调用外部付费模型。
- 前向样例在实施前固定：Python片段含直译注释、运算顺序原因、noqa、SPDX、公开docstring；报告含重复总结、N=40、3.2ms、CPU限定、未测GPU、证据路径；上下文片段含两个互相冲突命令、授权边界及人类guide路径。交给新上下文的只有输入和Skill，不给答案。保留可执行token/许可/工具标记/docstring、数值/否定/限定/证据；冲突不得猜选、guide不得改；已简洁材料可零修改。漏任一硬约束判失败，减少字符只能次要计量。
- 论文记录含精确版本、实际读取章节、实验/消融/局限和本库采用/拒绝理由；每次执行需新的正文阅读记录，历史10篇不抵本次。当前批次10篇要求未凑齐就标未完成，不把摘要、不可读全文或重复材料计入。

历史检索`concise comments documentation skills`，limit3/max-scan200：scanned199/partial，命中advice-context-20261009、combined-corpus-delta-v2-20261007、combined-corpus-v4-20261007；仅前者涉及上下文裁剪，均无本次注释/入口样例证据，不复用数值。已有同步器是唯一镜像生成器。
资料：已读Anthropic code-simplifier及obra writing-clearly-and-concisely；只借鉴原则、自写中文规则，不复制上游正文或安装脚本。精读2602.11988v1正文§1–6及附录A文字；附录B HTML缺提示词正文，不计完整附录阅读。本轮新论文数量单独记录，旧10篇不重计。

## Progress

独立计划v1返修、v2批准；范围为入口与Skill规则，不是运行时架构改造。已保留修前3项失败/错误并实施，专项4项通过；新上下文编辑样例已完成，结果待独立验收。RESULT-TIME-97保存诊断待接续；不因转向文档而宣称日期bug已修。

用户追加询问advice膨胀、多AI协作与记忆/任务组织：只读核验已有增量导航、任务归属、MemoryLedger和交接接口，组织建议记录在本轮report；未实施TASK历史迁移或降低全局建议验收。后续实际变更须独立版本化计划。

有界规则/入口修复已获[独立验收](../../results/concise98/independent-result.md) usable-with-scope；专项4项、全库1350项（8跳过）、Reader3项通过，样例保真通过。详见[报告](../../results/concise98/report.md)。本批阅读仅2/10，保留未完成，不将发布当阅读达标。当前准备普通main发布，远端SHA待回读；下一步补正文阅读及在独立方案下评估活跃任务视图/任务上下文包。
