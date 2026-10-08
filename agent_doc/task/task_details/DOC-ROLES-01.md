# [DOC-ROLES-01] 用目录 README 明确文档分工与逐项回应责任

Task-ID: DOC-ROLES-01
Date: 2026-10-08

## Plan

按用户要求为 advice、guide、task、results 提供 README，并更新 agent_doc 总入口；说明维护者、输入、AI 如何处理及输出位置。Plan v2：task_details 的职责并入 task/README.md，详情目录只放已登记任务。人工指南优先约束编排，AI 对要求逐项回应；建议经核验取舍后才进入唯一 TASK。用户本次明确授权创建 guide/README.md，仅用于目录职责说明，不填写或修改 GUIDE.md，不放宽通用写入/发布守卫。原始数据、历史任务和普通项目 doc 保留。

这是文档任务，不修改运行时、初始化行为或安装器，也不自动向其他项目写入。人工复核文字、相对链接、差异与 GUIDE 原文；不新增实验、不重复上一轮全量测试。发布前再次 fetch，普通发布 main 后独立读回完整树并同步技能。

## Progress

开始前已 pull 并核对 HEAD 与 origin/main 都为 e837d17c5c894ef468e301e4db966984c0be1ffb；setup_codex 与 --check 通过（15技能444文件，无更新）。实际搜索当前结果库：agent_doc README directory responsibilities，扫描28项，返回三个语料维护词汇候选，均与目录说明无关且验收pending，拒绝复用为本次证据；搜索因10个历史目录缺少record而partial，不宣称完整覆盖。上一轮 namespace 仅作为路径/职责背景，不复用其测试通过状态来证明新文案。

文案初案额外创建 task_details/README.md。只读追踪 agent_runtime/project_docs.py 的 snapshot_project_docs 发现，该目录所有文件必须与已登记任务一一匹配，因此发布前撤回这个新建说明文件，将内容与链接并入 task/README.md，Plan 升为 v2；无运行时、初始化器或守卫变更。

已人工复核五个 README 的文字、相对链接与责任归属，并核对 git diff --check。GUIDE.md 仍为空文件，SHA256 为 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855，未改原文。没有生成测试/实验数据或声称新的回归通过；普通发布与远端验证待完成。
