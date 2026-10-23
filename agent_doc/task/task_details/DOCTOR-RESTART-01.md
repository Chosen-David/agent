# DOCTOR-RESTART-01

Task-ID: DOCTOR-RESTART-01
Date: 2026-10-22

## Plan

同一SYSTEM-99批次的低风险诊断提示修复；基线bb33a88a9c35fcecb7ef58f0a892ba95a84fa3f7。用户授权Agent代码/测试/必要文档及验证后普通直推main。guide为空且只读。needs_restart仅描述本次doctor是否确实改变/恢复受管模型配置，不推断当前Claude会话已加载状态；tmux-only与无更改不要求重启。保持完整预检、原错误、库存/manifest同步；不新增host能力、监督器、架构或付费资源。

验收：保留修前失败，覆盖无安装/无网关/发现失败/同库存/真实配置变更/缺文件恢复/重复诊断/tmux及冲突拒绝。执行普通与-O专项、安装相邻回归、独立必要复核，fetch后只提交本次文件，普通发布并回读；本地回归不代表live网关/tmux/模型或性能验收。

## Progress

- 修前test_setup_doctor 8项中5失败；候选8/8普通及-O通过，安装恢复16/16普通及-O通过，setup相关29/29通过。原日志暂存.agent-runs/doctor-restart-2302/；公开短证据见advice。
- update_model_inventory在既有预检读取时比较新旧内容并返回变化；doctor据此给出needs_restart及明确的restart_scope/提示，不增加文件扫描。缺失受管文件恢复计为变化。
- 独立复核接受usable-with-scope：独立普通/-O各8与16通过，另验真实安装目标CLI、路由变更/重复调用、同内容/缺文件恢复及冲突前字节不变。短证据见../../results/doctor-restart-20261022/。发布回读待完成；SYSTEM99真实任务质量/usage/成本、tmux等原缺口仍open，不计新轮。新增论文2610.10590v1正文§§1–9已读，原始阅读私有检查点因维护清理不可冒充现存；本次仅1篇新增，不声明十篇新阅读或性能收益。
