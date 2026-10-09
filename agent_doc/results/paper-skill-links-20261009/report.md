# 论文技能§9链接兼容修复

任务PAPER-LINK-20261009-01。起点/测试基线7c2449ed16f979ca9f59579651f8f9d022525c02；修复4356730811a4fa603de4d610089b56946bdc9cbd引入的7处章节链接与现有文件路径契约不兼容。

baseline-minimal.log真实失败，test_eval_catalog.py:26–28直接对完整target（含#fragment）调用is_file。仅改7个SKILL.md：文件链接references/paper_exemplar_learning.md，邻近保留§9（evidence-to-contribution）及只加载该节的语义。源工作流、镜像正文、tests/runtime/guide/knowledge/evals均未改；七角色执行入口存在，镜像与同步源一致。知识候选没有进入本worktree或提交。

repaired-commands.json保留实际命令/日志sha：catalog2/2；全量852项851通过、1真实tmux opt-in跳过、0失败；reader3/3；sync/check、links、diff均通过。独立review.md/json核对实际diff、source、测试逻辑与原始结果。测试证明文档兼容与静态契约，不证明模型阅读效果或已部署插件。

postfetch.json记录再次获取远端后SHA未变及针对性复测全通过。七个精确测试源文件hash见link-checks.json；对应提交身份和远端SHA/文件/CI读回将在publication.json记录。无测试权限提交、无force push，发布完成前不声称远端已更新。

实现已非force发布：`4004d5097a4f4289dd67ca9ec740ea34690c1939`；远端SHA与七文件hash读回一致。CI三项查询Forbidden，必要检查配置亦未知。publication.json保存真实结果，未把API失败解释成Git推送拒绝。任务保持CI待核实状态。
