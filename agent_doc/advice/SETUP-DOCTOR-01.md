# SETUP-DOCTOR-01：doctor 普通路径崩溃

adopt：c4a0311b 的 setup.py:500 条件块内 `import re, os` 把 os 标为整个 doctor 的局部变量；未发现模型时跳过赋值，后续 TMUX 检查抛 UnboundLocalError。无网关新目标、已安装且无网关、非 fallback 路由都可触发，CLI 输出 traceback 而非健康 JSON。

修复仅删除冗余条件导入；模块级已有 os/re，发现成功分支语义保持。setup.py:475 起和 tests/test_setup_doctor.py 提供定位。基线新回归6项 failures=2/errors=5（其中一个断言是 subtest 异常后 run 未调用的后果）；最终专项普通/-O各6、相关集成51通过。首版候选测试把既有 uninstall 保留空行误判为正文丢失，原失败保留；最终精确核对 doctor 前后 CLAUDE/manifest 字节，卸载检查正文保留/受管块删除，不冒称卸载字节完全还原。

[完整短日志与独立审核](../results/doctor-1713/)保留实际 Python/Linux、源码哈希和复现命令。tmux 成功/失败仅进程替身，CLI/安装生命周期实际运行；无性能、模型质量或真实网关/tmux 功能结论。

defer：显式 discover 项目输出所有权、doctor 成功发现后模型快照/manifest 与当前报告一致性仍需单独复现/修复；SYSTEM-99 未完成。此提交不计新轮、未新增论文阅读。
