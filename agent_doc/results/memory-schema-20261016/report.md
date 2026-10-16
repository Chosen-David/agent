# MEM-CHECK-SCHEMA-06：减少记忆有效性校验的重复 schema 查询

仅限 Chosen-David/agent，基线 main `06ed701b30fc6f83c554f1f240b1f05122d387e3`。
本轮根据用户纠正恢复 Agent 范围；TwoLevel 的未发布改动已经暂停。

## 根因与有界修复

`agent_runtime/project_memory.py:44–67,145–196,294–310`：公开 `check()`
对每个唯一祖先完整装配时，重复查询 sqlite_master 判断文档依赖表是否存在。
512层链原来查询512次；普通自有读事务中该 schema 判定只需一次。
只把成功的存在/不存在结果存在本次遍历的状态中，每次check重新建立状态。
完整记忆读取、scope解码、文档绑定、DFS顺序、首错和状态检查全部保留。
handoff的多次有效性校验保持独立，没有减少失效检查机会。

`_get`和直接`_check`保留未缓存契约；类/实例覆盖、替换连接、自定义factory
走原路径。原始Row引用固定在模块初始化，避免全局sqlite3.Row替换绕过判断。
仅支持初始化后替换的这些约定扩展点，不保证私有常量/内置类型任意改写或
隐藏的重入schema修改；SQL trace/authorizer看到的查询数量变化是预期优化。
同连接DDL的可见性不能用“读事务快照”一概抹去。

两版候选都曾达到性能门槛但被拒绝：v1绕过实例入口覆盖，v2错误使用可变Row
符号比较。`reviewer/review-v2.md`保留实际反例。v3是单次版本化正确性修复，
不是原“两候选”预算下的接受或受管预算重置；门槛/输入/计时不变、禁止第四版。
所有负结果保留，v1/v2数字不作为v3通过依据。

## 协议与范围

冻结`plan.json`与`repair-plan-v3.json`。同机、同输入hash、相同DB字节，
Python3.12.14/Clang22.1.3、SQLite3.53.1、Linux6.18.44 x86_64/glibc2.39，
AMD EPYC9V74虚拟机，9可见逻辑CPU、单测量进程，未绑核。
无GPU、模型请求或新增付费资源。主测和独立测串行，未并行运行本任务测试。
21对随机AB/BA，seed61016，每臂warmup3；每样本5次完整public check，
包含路径/连接/事务/所有读取和校验/返回；建库、GC、结果相等检查在计时外。
wall为ns/check；按两臂中位数比值汇总，保留全部样本，不取最小值。
原始输入、SQLite、代码及依赖hash见raw JSON与`reviewer-v3/integrity.json`。

两个512层主场景均需下降≥10%，三个控制各不得退化超过15%。
单条控制主测0.3070→0.3320ms，退化8.16%；独立测反而改善2.40%，因此不主张
小库加速。该门槛不是统计显著性检验或所有硬件的保证。

| 场景 | 主测前→后 ms/check | 主测下降 | 独立下降 |
|---|---:|---:|---:|
| 512层有文档表 | 4.3934→3.7339 | 15.01% | 13.94% |
| 512层旧库无文档表 | 4.1027→3.6040 | 12.16% | 11.22% |
| 单条 | 0.3070→0.3320 | -8.16% | 2.40% |
| 64父节点加根 | 0.9416→0.8731 | 7.27% | 15.14% |
| 128请求根 | 1.4651→1.2874 | 12.13% | 8.79% |

最终源码SHA256 `6daa9f90425763bfc03287b4a68d3dee3dde36068115d9f4791112c50ad65580`，
独立329项固定基线完整返回/异常类型文本差分及原Row反例相等，52项针对性与
handoff测试通过。原生路径用profiler确认4个绑定节点均实际验证文档；真实文档
修改、嵌套对象修改隔离、失败修复再查均通过。独立审阅六项标准与完整边界见
`reviewer-v3/review.md`。手动新上下文usable-with-scope，不是受管可信回执。
原始30分钟预算始于04:13:46UTC；v3测量、独立验证及全库回归于04:28UTC前完成，
没有第四版候选或阈值放宽。

实际最终回归：全库1214项运行，8项跳过，OK（65.939s）；`-O` memory32项OK；
Reader3项OK。原始短日志在`full-tests.log`、`optimized-memory.log`、`reader-tests.log`。
v1的29项旧日志另名保留，不能误作v3验证。

复现：将本目录的plan.json、measure.py及reviewer-v3/完整复制回
`.agent-runs/memory-schema-20261016/`对应位置，在有固定基线git对象的仓库运行：

```bash
PYTHONPATH=. python .agent-runs/memory-schema-20261016/measure.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python .agent-runs/memory-schema-20261016/reviewer-v3/measure-independent.py
PYTHONPATH=. python .agent-runs/memory-schema-20261016/reviewer-v3/independent_check.py
python -m unittest discover -s tests -p 'test_memory*.py' -q
```

runner按冻结路径写出新结果，勿覆盖归档原始数据。复用既有bench_memory_check.py
的全入口配对口径；本轮独立冻结runner用于新增无表/5次批量协议，实际执行的是
此处保存的原始runner，不声称另一参数化脚本已经运行。manifest绑定源代码、
必要依赖与证据；record仅登记历史可发现性，unknown信任状态不伪装自动验收。
发布SHA在实际推送后私有检查点核对，不提前虚构。

## 研究应用及未验证项

沿用[12篇原始论文阅读矩阵](../memory-storage-20261015/research.md)中的分层访问、
原文保留、失效依赖原则；本轮是常规事务局部元数据复用，不冒称新论文算法或
新增十篇全文精读。[SQLite隔离说明](https://www.sqlite.org/isolation.html)
本轮核对了跨连接快照与同连接修改的区别，因而不在通用_get/_check上缓存。
先查已有结果扫描200条，partial=true且60条解析错误；未命中不表示全库没有。
旧check03/04只用作契约/方法上下文，知识检索命中的RL条目与此处前提不符，未采用。

收益仅限合成温缓存SQLite完整check；本轮未测峰值RSS/Python内存、磁盘冷启动、
真实Agent任务QA、token成本、模型KV、GPU内存或TTFT，不作这些收益声明。
真实KV消费者/后端接入和任务质量基准仍是MEM-STORAGE-01的未完成项。
