# VALIDATION-FD-87 实际结果

日期2026-10-20，基线 `80e7bf3ba8de99e0aee55505091172c6a5816c40`。问题为 `agent_runtime/validation_context.py:61–79` 的回执写入fd所有权；真实入口 `scripts/validate_experiment_result.py:33–34 --context-dir` → write_validation_context → restore_validation_context。输出仅显示观察，不授予结果验收信任。

## 修复与指标

os.open成功后，旧代码在fdopen构造失败时没有释放原始fd；多次失败可能累积资源。新代码以closefd=False让流借用fd，finally负责一次关闭，保留write/flush/fsync顺序、字节格式、独占创建和现有错误语义。没有引入依赖、替换算法或新增模型调用。

先新增8个测试，基线3失败；修后普通及-O专项各32项通过。独立配对20组调用/臂中各19次成功open，修前12个fd仍存活，修后0；新实现19次明确close。构造OSError重复10次、构造KeyboardInterrupt及context进入失败各1次是故障注入，不是生产故障发生率。其他路径覆盖open/write/flush/fsync/exit及三种状态的真实fsync成功，字节和异常身份保持；详见independent_raw.json、independent_probe.py及独立review.md。原测试成功分支mock了fsync；独立成功分支调用真实fsync补验。

实测范围：Linux x86_64/glibc2.39，Python3.12.14/Clang22.1.3，标准库临时目录，无GPU/模型/provider/付费资源。计数通过对本次os.open返回的精确fd执行fstat判定EBADF，不使用易受其他线程干扰的进程总fd数。基线泄漏在观测后仅关闭本探针拥有的fd，避免污染后续样本。

原始短日志：

```text
before: Ran 8 tests; FAILED (failures=3)
after: Ran 32 tests; OK
after-O: Ran 32 tests; OK
full: Ran 1331 tests in 89.774s; OK (skipped=8)
reader: Ran 3 tests in 1.578s; OK
independent: 20 paired cases; leaked descriptors 12 -> 0
```

完整日志保留本目录。测试运行秒数只是日志元数据，非修前修后性能比较。不宣称wall、token、模型任务成功率或内存峰值改善。新的可靠性/资源指标为异常注入下fd泄漏清零。

源码SHA256 `a1cf803a2141e2bd09cc082a1da1c5722fbebe3059f4f44af7bc522047329fd3`；测试SHA256 `0a36d1f4399f7dd468de1890d218a82b5c6dea49b7890d1ae06ca8072dc3d088`。精确输入与环境绑定见独立raw及probe哈希。采用research-implement-optimize的故障复现→单一所有权修复→实际fd计数→独立验收；[研究与十篇历史阅读](research.md)没有被用来替代生产代码证据。

## 限制、历史影响与后续

- 没有证据说明某次真实历史任务耗尽fd，不修改历史结果或验收标签；只覆盖此writer，其他类似IO路径需单独核验。
- 失败写入仍可能留下空/部分回执；重试拒绝不完整文件且不覆写，这是本次保留的失败封闭规则，不声称已实现原子写入或自动恢复。
- 真实ENOMEM、磁盘满、进程崩溃、强制终止、os.close自身异常及敌对fd复用未模拟，不能泛化。
- 8项skip代表可选依赖/显式集成未执行，不能以全库其余通过宣称外部部署验收。没有启动监督服务。
- 最终发布依赖独立review的usable-with-scope、fresh fetch及非强制原子main更新；随后回读远端SHA/tree。此文件不预先声称发布成功。
