# MEM-CLAIM-12：深链声明依赖校验

`agent_runtime/handoff_basis.py:49–83,121–138`：`claim_graph`原实现每代扫描全部剩余节点，长链产生二次重复工作。保留两轮原扫描；仅对剩余至少64节点、依赖数不超过剩余节点四倍的普通稀疏图尝试入度/反向邻接遍历。特殊类型、未知父、支持状态错误或环回退原检查，不改字段校验、完整返回对象、插入顺序与同进程错误诊断。

这是经典拓扑算法在真实handoff检查入口的应用，不是新论文算法。调用路径为Mailbox.prepare_context → basis_context → check_handoff_basis → claim_graph；本次计时只覆盖完整claim_graph函数，**不覆盖完整Mailbox或请求**。

## 实测及代价

固定输入hash见producer.json/independent.json。每路径3个warmup批次、21对交错测量；小图每样本100次、空图1000次，其余1次。构造在计时外，schema/图检查在计时内，无缓存结果。预先批准门槛：512链下降至少25%，每个其他场景退化不超过15%；生产者与独立复测都必须通过。

| 合成输入 | 主测下降 | 独立修前→修后 ms | 独立下降 |
|---|---:|---:|---:|
| 512节点链 | 87.10% | 25.422438→3.052468 | 87.99% |
| 256节点共享DAG | 47.56% | 3.552219→1.892848 | 46.71% |
| 8节点链 | 0.15% | 0.044925→0.045297 | -0.83% |
| 空图 | -0.03% | 0.000585→0.000596 | -1.88% |
| 512节点星形 | -6.67% | 2.601389→2.627457 | -1.00% |
| 256节点密集DAG | -0.72% | 168.811232→169.193711 | -0.23% |

独立单次tracemalloc峰值：链48568→115584字节，共享25704→58608字节，分别增加67016/32904字节；这是临时Python分配，不能解释为RSS/显存。用空间换重复扫描，命中图遍历期望O(V+E)时间和辅助空间；字段校验和未命中路线不承诺该复杂度。独立非法图诊断中未知父/支持错误/环回退耗时分别增加6.20%/5.12%/3.84%，没有全输入加速结论。

环境：Python3.12.14/Clang22.1.3、Linux6.18.44 x86_64/glibc2.39、AMD EPYC9V74，9个可见CPU，PYTHONHASHSEED=12。共享CPU未独占、未锁频/绑核；没有GPU、模型或新付费资源。

## 验证、负结果与边界

修前源码是main `4e4199d789812c6964329c02231733472d65a700`中的真实文件，SHA256 `43b6c6d0c281d833d22f32d9497e4d46947957b7620297592dfc82b49781d15a`；候选SHA256 `6e1057ce0c76d576898996011bb5ec39a6acad4b821388954a143c9d33fe0aaa`。659项差分在两执行者均通过，其中512个三节点全有向图与标准库graphlib对照；独立另252项覆盖准入63/64/65、密度边界、混合失败和定制对象操作序列。新增4项持久回归，普通及-O均通过。

计划v1/v2因遗漏历史浅图退化、控制门槛/批量口径而返修，v3测量前批准；原文件全部保留。六项validation-plan投影在主测后、独立验收前写入，未改变原v3门槛，不冒称原先已有该文件。独立诊断脚本首版路径错误导致未保存输出，修正后完整重跑；一次-O补充脚本的assert被关闭，其结果明确排除，-O验收仅使用unittest断言。见独立完整审查及失败记录。

历史`dag-cycle-20261013-1601/report.md`曾记录立即构建邻接表使星形慢21.29%；本次据此采用深度/密度准入，未复用旧耗时当新证据。结果检索扫描223条、partial=true且65条错误，相关历史由独立源码审查补发现，不声称未命中即不存在。原12篇论文机制矩阵与后续阅读保留；本次方法依据另见source-screen.md和[Python graphlib官方文档](https://docs.python.org/3/library/graphlib.html)。没有新增模型KV、工具调用质量、token或TTFT结果。

完整串行回归1243项运行、8跳过、无失败/错误；Reader3项通过，源码hash前后不变，见final-regression.json。发布核验见release-review.md及实际远端提交；手动独立上下文复核，不冒称已部署ManagedEngine/ReviewSession/监督器。MEM-STORAGE-01持续任务仍打开，实际图频次与完整消费者收益、模型KV接口仍待验证。

## 复现

冻结check.py保留原执行路径假设；在仓库根复制到相同深度再运行，不改已测脚本字节：

```bash
mkdir -p .agent-runs/claim12-replay
cp agent_doc/results/memory-claim12-20261017/baseline.py agent_doc/results/memory-claim12-20261017/check.py .agent-runs/claim12-replay/
PYTHONHASHSEED=12 python .agent-runs/claim12-replay/check.py --out replay.json
python -m unittest discover -s tests -p test_claim_graph_residual.py -v
python -O -m unittest discover -s tests -p test_claim_graph_residual.py -v
```

全部21对原始样本保留；候选为当前生产模块，若main随后变化应按上列SHA核对后再复现，不把不同代码的结果合并。
