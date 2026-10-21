# SYSTEM-99 阶段Q：结果目录确定性与并发容量

问题ID：`CHAIN-RESULT-SCAN-ORDER`。基线：
`2c691878ccff1bf1461ffdda0a235f2869de2e3c`。范围仅为结果目录枚举与本机协作登记；
不改变record schema、检索打分、历史身份或信任语义。

## 缺陷、修前失败与修复

基线 `2c691878` 的 `agent_runtime/result_store.py:230-248` 旧实现先按 `os.scandir`
原生顺序截断，再排序已选项。
三个真实历史record在同一查询、`max_scan=2` 下，只反转枚举顺序，候选从
`alpha,middle` 变为 `middle,zeta`；含README和两个record时只扫描一个目录；超过模拟上限时仍返回
原生顺序前缀。三条修前回归均失败，分别得到：

```text
reversed enumeration: ['middle', 'zeta'] != ['alpha', 'middle']
README + two records: scanned 1 != 2
over capacity: scanned 3 != 0
Ran 3 tests; FAILED (failures=3)
```

候选修复位于 `agent_runtime/result_store.py:33-34,226-348`：在5000项安全上限内完整枚举、校验
symlink与目录ID、排序目录名后再切 `max_scan`；普通文件计入全局安全上限但不占目录扫描名额。
观察到第5001项即返回空成员、`partial=true`，搜索只能为`incomplete/scanned=0`，登记也拒绝。

登记端使用结果目录之外的稳定 `.agent-runs/result-store.lock`。锁内完成重扫、容量、大小写
冲突和新run目录预留；锁外仍用原有临时文件、`fsync`和不可覆盖硬链接发布。POSIX使用
`flock`；Windows分支固定锁首字节、遇可重试争用继续等待。锁FD必须是普通文件，最终组件
symlink、FIFO和symlink父目录均拒绝；显式解锁即使报错也由嵌套`finally`关闭FD，避免同进程
锁泄漏。进程在预留第5000目录后退出，最多留下显式缺record
目录；OS释放锁，同run可恢复，另一run不能创建第5001目录。

## 验收与实际边界

缩小上限为3的真实多进程验收覆盖：2→3并发不同run只有一个成功；同run和大小写冲突均只有
一个目录/record；持锁进程预留第3目录后被强制终止，竞争者先阻塞、终止后拒绝第4目录，原run
可补record。另覆盖3项已有目标、4项超限空结果、截断项后的symlink、稳定锁文件和Windows首
字节争用重试。中断最终硬链接只新增忽略区内的单字节稳定锁，旧产品文件字节不变且可恢复。

当前真实树输入为253个顶层项，排序名称清单SHA256为
`844a75d14fbf9725d44d572dfae923c6acfbd4bdb34f73318fac7422ec84047b`。固定查询
`prior_result_search scanned drift` 重复三次逐字节一致：

| max_scan | scanned | partial | errors | status | JSON SHA256 |
|---:|---:|---|---:|---|---|
| 200 | 200 | true | 9 | incomplete | `38aeb8102303bebd946b81e9cbd9230367865dfae0a0983dd7976b0e9bf0cdd9` |
| 5000 | 252 | false | 12 | incomplete | `41e1f3c057694a275222a2e073a5bdc42d58cc86fca626d98b2109f450744cc6` |

同机1000次、同253项输入、预热20次的目录选择对照：旧实现中位179.445微秒、p95
314.953微秒并只选199个目录；新实现中位284.582微秒、p95 474.312微秒并确定性选满200个。
这是为完整观察和确定性支付的实测安全开销，不是性能提升；未宣称完整检索、token、模型质量
或请求延迟改善。

最终验证环境为Linux 6.18.55 x86_64、CPython 3.12.14，无GPU/模型调用：普通及`-O`下
ResultStore、复用验收与检索漂移各71项通过；全库1417项中1409项通过、8项既有平台跳过；Reader 3项通过；
`sync_plugin_references.py --check`、`py_compile`和`git diff --check`均通过。最初全库1415项曾因
旧测试把稳定锁算作产品结果而1项失败；该测试现明确只允许这个锁，仍逐字节比较全部原产品文件。
独立审查先因解锁异常会泄漏FD及两处报告错误退回；修复、补测并更正原始证据后才重新送审。
最终独立验收为`APPROVE`，详见[独立验收](independent-stage-q.md)。

未验证边界：没有Windows真机、跨主机共享文件系统或绕过API的直接写者测试；5000项身份/分片
架构和剩余12个非标准目录仍未改变。运行审查还发现任务/计划/交接等外部JSON存在无界跟随读取，
可被FIFO永久阻塞并占住启动锁；该系统性缺陷进入同一SYSTEM-99批次的下一阶段，不以阶段Q完成
冒充整批完成。
