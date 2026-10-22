# DISPATCH-SCOPE-01：子任务输出范围遗漏保留路径

基线`92a961a13cf27bf63024838c543da9f5a115e98b`，`agent_runtime/dispatch_context.py:35–52`。
派发前只检查字面guide路径和精确TASK索引名，仍接受`.`、`agent_doc`、`agent_doc/task`，
以及指向guide目录/TASK文件的符号链接别名。真实API探针5/5被接受；没有执行派发或写入guide。
现同时检查提交路径和解析后的路径，拒绝保留区域的父目录/后代；循环链接转为ValueError，
CLI返回exit1完整JSON。空只读范围、默认任务详情/运行目录、普通输出和安全内部别名保留，
不改写提交的安全路径或原生model/sandbox/approval/config，不增加权限。

修前9项测试21个失败/1个错误；修后普通与-O各9通过，相关集成各31通过；
独审另跑专项普通/-O各9、集成31及34条路径/CLI探针，接受有限校验范围。
原始短日志：`Ran 9 tests ... FAILED (failures=21, errors=1)` → `Ran 9 tests ... OK`。
[独立记录](../results/system99/dispatch-scope-01/review.json)、
[字节绑定](../results/system99/dispatch-scope-01/manifest.json)及同目录originals.tar.gz保存
方案、修前源码/复现、候选、全部测试日志、独审脚本与边界记录，旧失败不覆盖。
复验：`python -m unittest tests.test_dispatch_context`，另加`-O`运行；普通正确性回归，无性能实验。
环境Linux x86_64/glibc2.39、CPython3.12.14；同步与diff检查通过，未全库重跑。

只保证校验时的路径声明，不是OS沙箱；硬链接别名、检查后替换/竞态、原生Windows、真实模型
与完整任务质量未验。不宣称速度/token/质量收益或完成新一轮；SYSTEM-99同批继续，guide未改。
