# VALIDATION-RECORD-DIAG-01 v1（SYSTEM-99 / Plan54 诊断续接）

只诊断 agent_runtime.validation_context.write_validation_context 的一次普通流构造失败是否留下最终哈希命名文件并阻断相同请求恢复。源码目前 O_EXCL 建最终路径后才 fdopen，失败finally只关闭FD，未清理；这是源码候选，不预判测试结果。本次不修生产、不改稳定Plan、不建立第二TASK、不调后端/模型，不重跑旧受阻/耗尽范围。与既有VALIDATION-UTF8显示编码修复不同，不重启其测试预算。

先查结果：335目录partial=true/25errors，三个候选advice-context及combined-corpus delta-v2/v3为不同操作/输入/失败条件；原始JSON已保留，不足以复用本次失败恢复结论。未做性能/准确率/模型实验，只用临时本地夹具验证确定性异常边界；仍按用户要求保存原始失败和独立源码/结果复核。

固定3方法脚本 diagnose.py：一例注入validation_context.os.fdopen抛OSError，调用真实writer，观察最终validation-*.json及一次无注入恢复调用。外部恢复契约为异常不发布不完整最终记录，相同有效请求在故障消失后无需删文件可恢复；保留原始失败，不把失败断言数当独立根因。两对照为成功完整roundtrip/idempotency、既有被修改记录拒绝且字节不变。明确不检查父目录恶意替换、全并发原子性/断电持久化、fsync/write失败、磁盘耗尽、Windows/macOS原生或真实CLI/可信验收器部署，不据此宣称完整修复。

固定命令：`python -B .agent-runs/validation-record-diagnosis-2059/diagnose.py`，cwd项目根。预先单独独立方案/源码审核，approve才运行。一次producer和一次独立verify运行，各命令30秒，全部共享10分钟；方案最多1次调用，结果复核最多1次调用，不重试/替换/reset。退出1可为预期diagnostic failure而非通过，必须逐例解释。结果尚未独立验收不得公开作确定缺陷结论；验证检查implementation/reference、完整3例/raw/源码hash/输入/environment、无性能N/A、同协议单次独立复跑。没有可信runtime receipt则历史登记unknown，不伪造自动认证。

只写本次 .agent-runs/validation-record-diagnosis-2059/，main唯一writer；独立审核只读/执行固定诊断产生自己的stdout交接，不改其它文件。所有夹具TemporaryDirectory仅清理本例自己创建root，保留无关untracked归档。若独审revise/block或超预算，停止依赖步骤并保存检查点。生产修复须另一个版本化且独立审核的方案，不能以本次诊断授权直接实施。
