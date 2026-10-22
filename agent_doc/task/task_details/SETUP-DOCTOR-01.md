# SETUP-DOCTOR-01：doctor 条件导入导致崩溃

Task-ID: SETUP-DOCTOR-01
Date: 2026-10-22

## Plan

Version: 1

SYSTEM-99 同批安装入口审查；基线 c4a0311bf9d059ac97a865b91f0f5c195cf864a7。EXECUTE：用户已授权正确性修复、回归与 main 普通发布。本任务只恢复 doctor 的模块级 os 引用，不改模型策略、能力判断、文件更新策略或 tmux 参数。GUIDE.md 为空，目录 README 已读，只读边界不变。上一 MODEL-DISCOVERY-02 独审已指出局部导入疑点但未验证；本次真实空目标、清空环境调用 doctor 已复现 UnboundLocalError，不复用旧通过记录作本修复验收。

方法：删除成功发现条件块中冗余的局部 import re, os；两者已经在模块顶部导入。先在旧源码运行新回归保存失败，覆盖无网关的新目标、所有 fallback 且发现为空、已有非 fallback 路由、TMUX 存在/不存在和 subprocess 参数。再测真实安装→doctor→check→uninstall，保留用户 CLAUDE.md 与缺配置的 needs_setup 状态；CLI JSON 返回须明确可解析且无 traceback。tmux 仅 mock，不部署服务器或修改用户会话。

验收：专项普通/-O、已有 setup/发现/model routing 集成通过，独立源码/修前失败/结果复核后才发布。无真实网关、tmux server、Windows 或模型质量/性能主张。显式 discover 写项目 inventory、doctor 模型快照和报告更新问题仍未决；本地补丁不计新一轮或整个 doctor 已完善。保留同批论文阅读检查点，本次纯正确性修复不计新增阅读。

独立计划审核→实现及回归→独立结果审核→精确暂存→fetch/CAS 普通发布→远端 SHA/整树核验；主 AI 为本详情、TASK 和源码/测试唯一作者，审核者仅写分配的 .agent-runs/doctor-1713/ 审核文件。不改其它活跃 worktree。

## Progress

- 原始空目标、无网关调用复现：UnboundLocalError: cannot access local variable 'os' where it is not associated with a value。

- 独立计划 APPROVE。生产改动仅 setup.py 删除成功发现分支的局部 `import re, os`；使用原有模块级导入。
- 原6项修前 failures=2/errors=5；候选普通/-O各6通过，相关 setup/portable/discovery/model-routing/install-profile/role-process 合计51通过。候选首版唯一失败源于对原卸载保留空行的错误期望，完整初始日志保留；最终测试直接绑定 doctor 前后 CLAUDE/manifest 字节，卸载核验用户正文及受管块移除。
- 独立结果审核正在核对最终源码/测试、git-show旧源码失败与真实CLI、有限成功发现fixture；公开证据在 agent_doc/results/doctor-1713/。无模型或性能结论，发布待独审完成及最新main回读。SYSTEM-99继续open。

- 最终独审 ACCEPT usable-with-scope；独立普通/-O各6、51集成及git-show修前失败复现，成功发现fixture确认全局re/os引用。仅恢复条件路径可运行；模型快照/清单一致性、过期报告、真实tmux/网关仍未验。发布前fetch及远端整树回读由主控最后执行，不把本检查点计新一轮。
