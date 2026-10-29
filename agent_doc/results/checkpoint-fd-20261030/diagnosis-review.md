# CHECKPOINT-FD-DIAG-01 独立结果复核

Decision: **usable-with-scope**，限诊断证据。未通过的是目标函数的 FD 释放断言，不是独立审核失败；未实施修复，不能称修复验收通过。无需重试或扩大测试。

项目根 `/workspace/scratch/95d615402a52/agent-run-1202`，SYSTEM-99 Plan56。沿用本目录 plan-review.md 的已批准冻结输入与七域边界，本次不是第二次方案审核。独立执行在2026-10-29T18:07:07.908621Z开始，18:07:08.073233Z结束；一次、无timeout、exit1。环境 Linux6.18.55 x86_64/glibc2.39、CPython3.12.14/Clang22.1.3，与 producer 元数据相同。

## 代码与执行身份

实际独立 argv 为 `[/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python, -B, .agent-runs/checkpoint-fd-diag-0200/diagnosis.py]`，cwd为项目根。包装器以自身 sys.executable 生成该 argv，一次 subprocess.run，25秒超时上限，为每命令30秒留余量；未修改 runner 或追加其他测试。全部执行发生在共同18:18:36.910942Z截止前。

| 冻结输入 | 执行前及后实读 SHA256 |
| --- | --- |
| plan.json | `ae0e44cf6813231bb4517c4bdfc1938614d92b5d5fc1afbe460e0ad1c40bf71e` |
| diagnosis.py | `027fb51e791230eb9379211f44bb3623e9594192b073649c22bd77062b038092` |
| agent_runtime/task_manifest.py | `69c4fe53bf09b101bdffda7e5a3d9a8b3a71ba40ddc25174402c2b7260979425` |

已读实际源码与完整 runner，并核原始 producer 与 independent stdout/stderr，未仅凭 exit/JSON pass 验收。独立原始证据位于本目录 `independent/{stdout.log,stderr.log,execution.json}`；producer 仍在其原目录，未改动。

## 原始数据

| 证据 | SHA256 |
| --- | --- |
| producer stdout | `1f5e16520855a6565b1e5acc93f41e735d7fdbc3989dc0d27db04929659e95b3` |
| producer stderr | `0329dda3deff67c5d780b67fe5b8ccc3cee5cbadd9bb6ad9c1d80fb4ad7f7f33` |
| independent stdout | `1f5e16520855a6565b1e5acc93f41e735d7fdbc3989dc0d27db04929659e95b3` |
| independent stderr | `8ca3c9e5c27443463212a179f2155cff2853c22cf14e0b8bc109d6d19edc29da` |

两个 stdout 逐字同哈希。完整 stderr 均为3方法、2失败断言、0error/skip；差异为末尾 unittest 运行计时：producer 0.009s、independent 0.008s，不解释为性能差异。两次均只有同一构造故障方法的 existing=False/True 两个 `raw descriptor closed` 子场景失败。

| 场景 | producer / independent 实际观察 |
| --- | --- |
| Unicode 正常写入 | 方法ok；完整预期UTF-8/换行字节、JSON内容、FD关闭与临时名移除断言通过。 |
| NaN序列化失败 | 方法ok；ValueError、旧目标字节保持、FD关闭、临时名移除及唯一目录成员断言通过。 |
| 构造失败，目标原不存在 | 同一注入OSError传出；目标保持不存在，临时名移除；原FD在清理前fstat成功，关闭断言失败；去故障后retry完整，目录仅最终目标。 |
| 构造失败，目标原存在 | 同一注入OSError传出；旧目标原字节保持，临时名移除；原FD在清理前fstat成功，关闭断言失败；去故障后retry完整，目录仅最终目标。 |

构造行输出明确为 `fd_closed_before_retry:false, temporary_removed:true, retry_complete:true`，两个 existing 值各一行。状态/字节/目录断言位于输出前且无对应失败，因而不是仅相信打印字段。两次执行是复核同一两个场景，不是四个独立缺陷；本报告不把断言数当根因数。

## oracle、异常与清理

目标先取得真实 mkstemp FD，再以默认closefd=True调用fdopen；注入在调用入口抛出指定OSError，流尚未构造/进入with。target finally移除临时路径，但没有关闭原FD的分支。runner记录实际 mkstemp 返回，assertIs核异常身份；`closed(fd)`以os.fstat为独立系统调用oracle，只认EBADF为关闭，其余OSError传播。`is_closed=closed(fd)`在invoke返回前、retry前及本方cleanup前计算。本次两个false因此是当时的实际FD观测，不由后续测试关闭伪造。

嵌套subTest捕获预期断言失败，随后retry与打印均实际发生，控制流再进入每个子场景finally，检查未关闭的本方FD并os.close；TemporaryDirectory退出回收合成检查点。日志无cleanup异常或unittest error，子进程已正常结束而非超时/强杀，故本次诊断不会以长驻子进程持有泄漏FD。原始FD关闭后的第二次fstat未被额外记录；不能把代码路径检查说成另做了清理后测量。标准库close/unlink/TemporaryDirectory清理自身失败未注入或独立测量。本次执行无清理异常的结果与所审代码一致。

所有写入目标在runner自建TemporaryDirectory内；没有用户路径输入、模型/tmux/后台作业。独立包装器只写本角色independent目录。producer、plan、runner、生产源码、TASK与guide未改写；执行前后哈希匹配。本报告未重跑result-fd95、validation_context或任何旧runner。

## 上下文与可用范围

接受结论：**当前源码在本机该确定性fdopen构造失败注入下，两种目标存在状态均留下仍打开的mkstemp原始FD；临时名仍会清理，旧目标状态/字节保持，撤销故障后可正常写入。成功构造后的正常/NaN路径对照会关闭FD。**

这是当前generic task_manifest.atomic_json的直接证据；ResultStore旧结果与validation_context空最终记录机制仅为历史区别，不承担本函数验收。默认closefd=True只说明成功构造后流的所有权；当前注入发生在构造前，不能据此声称标准库真实构造异常必然按本注入模式发生。

未测真实发生率、线上资源耗尽、原生Windows/macOS、close/unlink失败、敌意父目录/临时名替换、并发FD复用、进程崩溃恢复、完整E2E、性能、模型质量或总费用。SYSTEM-99及原有宿主/全输入/最终质量/并发恢复等未决不关闭。知识检索空结果与25历史检索错误不等于知识/历史全覆盖。

## 资源与后续

planreview1/1、producer1/1、independent execution1/1均已使用，独立只执行本次一次，无重试、重置或附加变体。全角色tokens/费用unknown。手工AI审核非受信runtime回执、ReviewSession或部署。主控可按冻结范围发布诊断检查点并保留原始失败；修复需另行限域方案与授权，不能把本结果当修复或系统整轮完成。
