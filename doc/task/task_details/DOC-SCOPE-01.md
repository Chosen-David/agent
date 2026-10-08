# [DOC-SCOPE-01] 目标项目文档归属纠正

Task-ID: DOC-SCOPE-01
Date: 2026-10-08

## Plan

用户明确纠正：doc/guide/GUIDE.md 是接入项目的人类指南；Project A 使用 Project A/doc/。Agent 自身升级才维护 agent/doc/。这是澄清原意，不是将所有项目迁入 Agent 仓库。

基线：03cae12627d3b586494226d182ed5f58ef716320。工具 project_docs 已要求显式 --root，Claude 安装器也接收 target；未观察到工具强制写回 Agent 的缺陷。问题是入口对规则来源根与目标项目根的区分不够明确，README 链接易被当成通用任务入口。

最小改动：共享文档契约定义 agent_source_root/project_root 及 Project A/B/Agent 自身的归属；README、doc/README、Codex/Claude 入口与主调度明确同一边界；沿已有脚本同步插件引用。不改变运行时接口，不移动任何项目历史，不触碰 doc/guide 内文件。

预先验收：生成副本一致；现有安装/项目文档检查无新增失败；明确缺失指南不得回退，临时 cwd 不得改变绑定。程序检查不证明模型行为改善。Windows 目标安装未访问，不声称已部署。完整持续优化批次仍保留原门禁，不以本澄清完成一轮。2026-10-08 用户再次明确要求检查远端最新实现并将本修正直接推送 main；本次发布仅覆盖文档归属契约及入口说明，不捆绑旧 HOST 科研/通信批次。

## Progress

已在干净树 fast-forward 到上述 main，再恢复旧 HOST 未发布检查点；CODEMAP 冲突同时保留上游数学条目及 HOST 连续性条目。旧 stash 保留，不丢弃历史。

已查询项目结果库：query=project_root doc guide 项目路径，limit=5，max-scan=200。五项词法候选并非本次目标项目归属验收；未用旧 pass 抵扣本次核验。部分历史 record.json 缺失仍为缺口。该用户意图与路径契约更正无需数学/外部事实知识，不伪造知识库引用。

共享源与 15 份插件引用已同步。原有安装检查 10/10、项目文档检查 33/33、生成副本 check 和 git diff --check 通过；原始日志见 doc/results/project-doc-scope-20261008/，实现文件 hash 见 implementation.json。独立上下文复核为 usable-with-scope，无阻断发现，记录见 independent-review.json；这些是程序/契约核验，不是实际多模型项目隔离效果或部署证明。尚未提交、发布或更新 Windows 安装。

下一接续点：在具备目标项目的实际宿主上验证指南缺失/切换项目/工具目录变化的真实行为，继续原 HOST 批次证据恢复与发布门禁。测试日志缺测试时源码 hash 绑定，候选实现清单是随后保存的快照；不将这些日志直接提升为完整发布凭证。

### 明确发布请求后的范围与验证

用户询问远端是否已更新并明确要求推送本修正。再次在保留旧工作后的干净树 pull --ff-only，GitHub 连接器回读同为 03cae12627d3b586494226d182ed5f58ef716320。该版本已包含 ed6b7a2 的项目文档治理及后续安装/审核改进；本补丁复用现有 target/--root 接口，仅补清规则来源与项目归属、缺失指南、项目切换和 cwd 边界。

原先将这一明确的小型修正捆绑旧持续优化大批次是范围判断过宽，不是 GitHub 权限拒绝。旧批次与未完成实验保留原状态，不借此发布、不清零论文进度、不计完成一轮。

发布核验输入 hash 在 release-check/inputs.json 预先冻结，测试后核对不变；57 项现有检查通过（安装10、文档33、Codex13、引用同步1），另有同步 check 通过。原有43项日志只作历史记录，新记录补齐测试时源码绑定并覆盖 Codex 更新保护。程序检查与契约独立审核不证明模型效果，也不代表 Windows 安装已同步。

此记录为提交前状态；发布须普通非强制更新 main，并以实际远端 SHA/内容回读为准。独立审核结果见 release-check/independent-review.json。

### 并发 main 更新后的重新整合

发布前 fetch 发现上游 6b4b0be / 5a53c43，新增显式项目 init 和安装清单 project_root。原未推候选 ee340ba 冻结为历史，rebase 到 5a53c43；完全保留上游运行时代码、README/doc/README 和初始化功能。拒绝重复添加根目录定义和表格，仅补切换项目时重新加载指南/任务/记忆/证据、交接/恢复核对 project_root，以及使用绝对工具/目标路径的示例；术语沿用上游 WORKFLOW_ROOT / PROJECT_ROOT。

初版 implementation.json、release-check/ 的源码指纹不再代表最终发布内容。当前验收入口为 integrated-check/：整合后的28个实现/测试/角色契约文件预先固定hash，测试后保持一致；新增init9项连同原相关57项共66项检查通过，另有引用同步 check。独立复核见 integrated-check/independent-review.json；上游新增程序测试为程序证据，仍不等于实际模型/Windows验收。最终普通推送前需再次fetch并核对父提交，发布后回读提交和内容。
