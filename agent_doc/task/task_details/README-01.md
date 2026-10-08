# [README-01] 首页信息架构与视觉升级

Task-ID: README-01
Date: 2026-10-08

## Plan

用户明确要求升级总 README，使用相关 Agent 绘制架构图/可视化，使首页更美观易懂；沿用 main 发布授权。EXECUTE：这是文档呈现变更，不改产品契约、技能、运行时或 SGLang。PROJECT_ROOT=WORKFLOW_ROOT=本库，人类 guide 为空且保持原字节。main 基线 c60f576eab9545ceaf123b29306e81a604477115，干净 pull 已核对。既有自动优化批次/检查点不变。

问题：旧 README 约 26 KB，开头治理与历史升级信息重复，安装入口分散，技能列表数量与列举不一致，并有离线伴读/本地 Web 阅读器能力混读风险。反事实：只添加装饰会保留入口歧义。采用首页分层与源码核对的 SVG，详细流程继续链接原文。

验收预先确定：首屏说明用途与接入入口；通用主 AI、科研、旅行、代码阅读、知识和 Claude marketplace 均可找到；所有相对链接与锚点有效；Project A 文档归属明确；无虚构评分/徽章/性能/部署主张；两张可编辑 SVG 真实渲染并查看桌面/窄屏尺寸，独立核对语义与最终 README。只做必要文档/链接检查，不为纯展示修改重跑 GPU 或冒充模型效果 A/B。

分工：主 AI 唯一维护 README/TASK/CODEMAP/发布；readme_visuals 独占 docs/assets/readme/；独立审阅者只写验收报告。预算两次图形修订，无新增依赖服务/运行时，不部署监控。

## Progress

2026-10-08：读取最新 main、AGENTS、决策与文档/记忆规则及角色注册表。result_store search 查询 README architecture onboarding 返回三个知识语料候选及 partial/missing-record；这些结果不适用于首页视觉验收，未复用旧 pass。无数学/科学知识推断需求，能力事实直接核对仓库入口、脚本和注册表，未声称加载知识库。

2026-10-08：首页、两张 SVG 已完成；独立审阅通过 usable-with-scope，初审的安装检查路径问题已修。52 个相对目标与页内锚点通过；全部15角色及2插件核对；SVG真实桌面/窄屏渲染与主控消费检查完成。报告 agent_doc/results/readme-20261008/report_by_gpt.md，独立意见 review_by_gpt.md，机器检查 checks.json。未变更生产契约，不宣称模型能力/性能或原研究批次完成。已复查远端仍为基线；本条随已验收首页候选发布，发布结果以 GitHub main 回读为准。
