# DOCTOR-RESTART-01：按实际变更提示重启

基线bb33a88a；setup.py:518–564的doctor无条件needs_restart=True并宣称配置已更新，无安装/无网关/同库存或仅tmux诊断也如此。修复在既有update_model_inventory预检中比较受管模型文件，返回实际变化；doctor只在本次更改或恢复模型文件后要求重启。新增restart_scope明确范围；无变化时提示会话加载状态未经检查，避免把False解释成已加载最新配置。manifest更新、所有权/冲突预检及异常语义保留。

实际短日志（Python3.12.14/Linux6.18.55-x86_64-glibc2.39；纯离线库存/子进程fixture，不代表真实网关）：

```text
before: test_setup_doctor — Ran 8 tests; FAILED (failures=5)
after / -O: test_setup_doctor — Ran 8 tests; OK
recovery / -O: test_install_recovery — Ran 16 tests; OK
setup-suite: test_setup*.py — Ran 29 tests; OK
```

修前/修后修前原始短日志、主验摘要和独立审查保存在[结果目录](../results/doctor-restart-20261022/)，完整回归日志暂存本次私有.agent-runs/doctor-restart-2302/；不含凭据。普通模式真实CLI、install→doctor→check→uninstall和重复诊断由现有/新增回归覆盖；tmux仅mock。独立普通/-O各8/16及额外CLI/变更/冲突探针接受usable-with-scope；发布回读由主控另核。无性能、模型质量或SYSTEM99整轮完成主张；真实服务、多文件掉电事务和跨平台仍未验。
