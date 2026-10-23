# HOST-RELOAD-01：纠正热加载保证

2026-10-23核对main01856214，AGENTS.md新增的“agent定义一律启动缓存”“CLAUDE.md每轮注入system prompt”“本轮16agents需重启”不能作为跨宿主或当前运行状态证明。完整基线：01856214263d9a43be3fc3985ccfc37981ed79e9，原文已存私有检查点，Git历史保留。

当前官方原文对照：
- https://code.claude.com/docs/en/sub-agents#write-subagent-files ，检索Write subagent files：既有主/用户agents目录被监听，变更供下次委派使用；新目录、add-dir和disable-slash-commands例外需重启。不是所有文件都必须手动覆盖model。
- https://code.claude.com/docs/en/prompt-caching#editing-claude-md-mid-session ：根/用户CLAUDE.md启动时读取，改动在clear/compact/restart后加载；普通磁盘编辑不改历史上下文。
- https://support.claude.com/en/articles/14553240-give-claude-context-claude-md-and-better-prompts ：How it is loaded说明为system prompt之后的user message且并非逐turn重读；该帮助页还列memory，但当前缓存页操作列表不同，故正文保留当前缓存页明确步骤，不外推所有版本。

采取有条件的宿主说明，保留更新目标与真实readback要求，去掉未核验16agent状态及强制model覆盖。只修AGENTS新增段，不改并发作者的编排自主规则、共享决策协议、模型路由或权限。无Claude CLI实测版本，网页是当前文档而非本机热加载验收；未测性能、token或质量。本次为SYSTEM-99续接，不计整轮完成。

验证：test_concise_engineering加native/plugin wiring共4项通过；修改前新增段以外AGENTS逐字相同，diff --check通过。较广main_ai_contract+concise共8项有1失败：并发提交1a1a90fd已令orchestrator内嵌决策门禁与canonical不同。用未修改HEAD原字节在隔离临时根复现相同失败；本补丁不改该协议、不放松测试、不将失败报通过。该架构冲突待明确统一权威版本后处理，SYSTEM-99不能收官。没有运行CLI热加载实测。
