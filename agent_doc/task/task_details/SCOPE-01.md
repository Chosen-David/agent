# [SCOPE-01] 接入项目的文档归属与显式初始化

Task-ID: SCOPE-01
Date: 2026-10-08

## Plan

用户希望 Project A 的指南、任务、建议和结果属于 Project A/doc；只有维护 agent 本身时才使用 agent/doc。保留工作流源码和目标项目两个根目录，不复制历史任务，不自动编写人类指南。

新增必须指定 --root 的项目文档初始化命令；预检目标、目录冲突、链接和旧任务清单后，只创建空目录和空任务索引。更新 README、安装入口和共享角色契约，明确缺少项目指南不能回退到 agent/doc。

## Progress

已 fetch/fast-forward 到 03cae12627d3b586494226d182ed5f58ef716320，核对 HEAD 并同步/检查 15 个本机技能。此前失败的 neuroscience 批次保存在 agent/preserved-engineering-092539 和 stash 18e24f3，不纳入本轮发布。

### 2026-10-08 ??

??? --root init?Project A/B ??????README/Codex/Claude ??? 15 ???????????????????????????????????
