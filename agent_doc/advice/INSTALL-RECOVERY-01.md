# INSTALL-RECOVERY-01：发现后配置不可恢复、用户输出被覆盖

adopt：基线61a7ee34，setup.py:461起显式discover将结果先写项目同名inventory，再做安装预检，首次安装父目录不存在亦失败。doctor:479起改了角色model和routing，却不更新installation.json库存/hash，也不刷新返回报告；真实离线安装复现生成opus但报告None、check4错误、重复install被拦截。

修复使用独占临时发现输出和30秒上限，错误走既有setup blocked；doctor先核对manifest身份、文件hash所有权和全部目标路径，拒绝本地模型编辑/链接/缺所有权后才写受管policy/routing/agents，同步权威manifest库存/hash并重新check。非模型配置、用户正文、skills/copy清单、未知字段和已有孤立inventory保留；不把doctor当初次安装。

最终专项16项普通/-O、相关57项通过；先前11项基线14failure/3error保留。首次集成1失败是旧mock夹具缺实际安装manifest；按本次明确“无manifest不发现”契约补真实安装前置，再57通过，原失败不删。[代码/原始日志与独审](../results/install-recovery-1756/manifest.json)记录实际版本、hash与命令。相关实现setup.py discover/update_model_inventory/doctor，回归tests/test_install_recovery.py及tests/test_setup_doctor.py:32。

独审v1另发现顶层非对象manifest在check先崩溃；Plan v2经重新审核后补dict检查及错误状态重置，2项修前6error保留。诊断回退不授予写入权，更新仍重新读取原manifest作所有权校验。

证据边界：生产optimized-v3日志最后读不完整，保留原字节与差异记录；最终计数依公开完整独立普通/-O与集成日志，不把缺summary当通过。

仅本地fixture验证模型发现输出交给真实安装/检查/恢复消费者，未运行网关或模型。单文件原子写不保证多文件掉电/并发事务；不以此宣称速度、任务质量、tmux功能或SYSTEM99完成。能力名启发式与tmux异常恢复继续defer，需后续真实基线与验证。
