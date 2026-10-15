# MEM-CHECK-03：复用事务内已校验请求根

2026-10-16；本地验收 **usable-with-scope**，不代表 MEM-STORAGE-01 或真实模型
KV任务完成。发布状态以实际远端回读为准。

## 入口、根因与修复

基线main `9b6cc775a900f2c0d26d97f88de5622129eec014`。
`agent_runtime/project_memory.py:138–174` 的 `_check` 由公开check/CLI及任务
派发、验收、发布的check_task_memory调用。DFS已经完整读取并验证每个请求根，
返回时又逐根_get，重复装配content/scope/document/deps。这是性能浪费，不是
已确认的正确性缺陷。

修前四节点菱形、refs=[leaf,parent,a]：读取顺序为
`leaf,a,parent,b,leaf,parent,a`；新增6项测试有1项失败，期望前四项即可。
候选仅保留本次已校验请求根，并按refs原顺序返回；不额外保留全部祖先，不跨
调用/事务缓存。状态、依赖、文档哈希检查仍每次完整执行，schema/API/纠错规则
不变。V个可达唯一节点、R个请求根的装配次数由V+R降至V，额外O(R)引用。
返回包本就需要R个根；未测RSS，不宣称降低递归深度或消除全部N+1。

冻结候选源码SHA256：
`b9f939410eee1e7c7477982ff9b0a1c95bd7d952ec706b5b179707d0d598ccf6`。

## 同机配对测量

完整check入口含路径守卫、连接、BEGIN、SQL/JSON/校验、装配、返回与关闭。
建库、Git加载、warmup和等值检查不计时。固定seed1603，6场景，各21对随机
交错；每次完整返回与同DB基线相等，前后DB哈希不变，独立重建字节也相同。
原始样本/顺序：[主测](raw-primary.json)、[独立复测](independent-raw.json)、
[固定配置](config.json)。下降=1−median(after)/median(before)。

| 场景 | 主测before→after ms | 主测耗时下降 | 独立耗时下降 |
|---|---:|---:|---:|
| 512根，128B内容 | 8.244818→4.551791 | 44.79% | 43.87% |
| 512根，8192B内容 | 11.343471→7.252554 | 36.06% | 39.26% |
| 单根控制 | 0.230773→0.220417 | 4.49% | 11.05% |
| 8根小批控制 | 0.358463→0.308208 | 14.02% | 17.54% |
| 128节点链/一个叶根 | 1.354883→1.362103 | −0.53% | −2.40% |
| 32根共享父节点 | 0.775392→0.537088 | 30.73% | 33.18% |

两大场景两次均超过预定20%门槛，控制最大退化2.40%低于15%。小控制变化不
推广成稳定通用收益。性能fixture无文档绑定，不能推断文档hash重负载收益；
文档变更做正确性测试。无CPU独占/affinity，虚拟主机噪声和所有样本均保留。

## 实际检查、环境与复现

- 普通/-O记忆回归各33项通过。全库1200项运行、8跳过，通过；Reader3项
  通过；项目文档validate退出0。[短日志](checks.log)。
  最终文档定向回归74项通过；此前两次测试选择/导入路径错误在短日志保留。
- 独立新上下文实际执行4306次完整输出/异常差分，另5项freshness、3项结构
  和12项raw案例检查通过。覆盖根顺序/祖先交叉、状态、JSON/BLOB、旧/缺失
  schema、悬空边/环、失败修复、纠错、调用方修改及真实task文档变更。
  保持旧环语义，不声称新增环检测。[独立审查](independent-review.md)。
- 独立计时复用已审查runner，不称两套独立计时器；手动代码数据复验不是
  受管runtime verifier或ReviewSession回执。
- AMD EPYC9V74/KVM x86_64，9可见逻辑CPU；Linux6.18.44/glibc2.39，
  Python3.12.14/Clang22.1.3，SQLite3.53.1，串行本地温缓存。输入hash逐案例
  在raw；config SHA256 `a02199c4894bf47c6ea385390d2f2d8fba92776b92fcd2c2e72ff786d5b5cfe9`。

从包含冻结基线的Git checkout复现，输出使用新路径：

```sh
PYTHONPATH=. python scripts/bench_memory_retrieval.py --config agent_doc/results/memory-check03-20261016/config.json --output /FRESH_PATH/check03.json
PYTHONPATH=. python agent_doc/results/memory-check03-20261016/independent_check.py
python -m unittest tests.test_memory_check tests.test_project_memory tests.test_memory_retrieval -v
```

## 历史与边界

scope02/storage01旧list测量不改写、不挪用；ResultStore查询仅作发现，部分扫描
且61个读取错误，旧unknown信任仍保留。本次冻结证据登记也不赋予自动复用权。
[研究差异](research-delta.md)沿用12篇原始论文矩阵，补查两篇近期KV/记忆评测
与SQLite事务机制。采用常规事务局部复用，不伪称完整复刻论文或GPU算法。

无LLM/QA/token/TTFT、真实KV tensor、冷盘、RSS、部署或GPU收益。下一步仍由
主执行者先确认授权可用引擎、模型/模板/租户/精确prefix身份，再做实际bytes、
任务质量与完整请求对照；跨上下文拼接单独验收，不制造无人消费的cache接口。
