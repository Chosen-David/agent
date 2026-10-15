# MEM-STORAGE-01：减少历史记忆的无关装配

2026-10-15；基线 `408af9e8975eb2bc8db6c97a81db7743bc587ecd`。本轮用户目标为 Chosen-David/agent 的记忆及 KV 存储；授权在验证后直推 main。未修改其他仓库、人类 guide、私有记忆或历史实验。

## 问题及修复

稳定 ID：**MEM-STORAGE-01-HYDRATION**，confirmed 性能浪费，非论文新算法。

真实调用入口：`python -m agent_runtime.project_memory --root <project> list` → `agent_runtime/project_memory.py:362` → `MemoryLedger.list:263` → `_get:121`。旧版列出全部 ID，再为每条记录读取 content/source、解码 JSON、查文档依赖、查父依赖，最后才判断状态。历史条目越多，即使只要少量 active，也需付出全部对象和关联查询成本。scope 为精确 Python 成员检查，不能安全改成字符串 LIKE。

修复：仅在内置 MemoryLedger / 普通 str 状态 / 非 all 且存在其他状态时使用延迟装配。先以 Python 预检全部 scope 与 document snapshot JSON，再由 SQL 筛出请求状态并装配完整对象。无历史时、子类、all 查询保持原路径；依赖表缺失回到原路径报错。预检 fetchall 后才解码，避免捕获并保留异常 traceback 时 SQLite cursor 持续持有读锁。

没有新增 schema、索引、长期连接、缓存副本或外部依赖；返回顺序和完整对象保持不变。元数据预检仍 O(N)，没有宣称总成本 O(K)。复杂度收益来自避免无关内容复制和每条历史的多次关联查询。独立 100 条/5 active fixture：SELECT **401→25**，仅作为结构佐证。

等价范围是规范 API 写入的有效记录及已测元数据损坏情况；不保证任意损坏 SQLite 字节下的异常次序完全相同，例如手工 SQL 制造被排除 content 的非法 UTF-8。读取期间外部并发写入的快照保证未加强；这也是后续需要单独设计的边界。

## 失败、复现和正确性

新增 `tests/test_memory_retrieval.py` 用基线 eager 算法差分验证完整对象，而非只比较数量。覆盖五种状态、精确 scope、排序、空库、状态非法、修正/接受/依赖、旧 schema、子类、坏 JSON/UTF-8/深度及保留异常后立即写入。独立上下文另构造 **68** 个边界场景。二者均通过。

候选阶段失败保留，不包装成历史生产 bug：

- 简单 SQL 筛选会隐藏被排除条目的坏 JSON；SQLite json_valid 对部分 UTF-8 BLOB 与 Python 解码不一致，拒用该替代。
- 第一版元数据预检：主测全 active 退化 16.09%，独立 19.27%，超过预设 15%；`negative-v1.json` 和独立诊断保留，未采用。增加无历史原路径后重测。
- 后续发现空选择会隐藏缺 dependencies 表错误，以及流式 cursor 的异常 traceback 读锁；均先复现、修正，再独立重查。
- 最初深度用例假定必抛异常，在当前 Python 构建不成立；改为新旧输出或异常一致性，没有将错误测试预期算作 bug。

最小复现及同输入全入口计时：

```bash
python -m unittest discover -s tests -p test_memory_retrieval.py -v
PYTHONPATH=. python agent_doc/results/memory-storage-20261015/measure.py /tmp/memory-result.json
```

`measure.py` 内含冻结的旧 eager 检索基线；SQL 生成临时合成数据库，建库不计时，原始数据库字节 SHA256 在每个结果中。双方 warmup、21 对随机先后序、计时包含连接/读取/解码/筛选/完整列表返回，计时外核对完整内容及数据库未变。不保存真实用户记忆。

## 性能与环境

预设门槛：两种历史密集场景中位耗时至少降低 25%，small/all-active 退化不超过 15%。最终主测和独立测量均在彼此及全库测试停止后串行进行；前期重叠计时只作诊断。

| 合成场景 | 最终主测：旧→新 ms | 耗时降低 | 独立：旧→新 ms | 耗时降低 |
| --- | ---: | ---: | ---: | ---: |
| 8 条/全部 active，128 B content | 0.330300→0.292965 | 11.30% | 0.288378→0.265865 | 7.81% |
| 400 条/全部 active，128 B | 3.568269→3.664602 | -2.70% | 3.345856→3.414558 | -2.05% |
| 2000 条/20 active，128 B | 17.968795→3.556071 | 80.21% | 16.063734→3.383062 | 78.94% |
| 2000 条/20 active，8192 B | 27.010483→9.445347 | 65.03% | 26.076417→8.999378 | 65.49% |

设备为 KVM x86_64、可见 9 vCPU、AMD EPYC 9V74；Linux 6.18.44/glibc2.39；Python 3.12.14，构建编译器 Clang22.1.3；SQLite3.53.1。seed=1510；无 GPU kernel、驱动或框架参与，无 JIT。原始 21 对样本和输入 hash 见 [raw-accepted.json](raw-accepted.json)、[independent-raw.json](independent-raw.json)。small 的微秒差异不作可靠加速卖点，仅为退化控制。

冻结最终源码 SHA256：`5ae35f1dcad87ab759fe4aab5f7deb522c9a3ea1d01ef8118c4ca65547ef7b19`。最终完整回归：

```text
python -m unittest discover -s tests
Ran 1190 tests in 72.644s
OK (skipped=8)
python -m unittest discover -s apps/paper-reader/tests
Ran 3 tests in 1.561s
OK
```

8 个跳过仍未验证，不记作通过。独立结果为 usable-with-scope；这是真实独立工具上下文审查，不是受管运行时认证 receipt。源码/数据/研究与任务绑定见 manifest。未运行模型、GPU、真实用户数据、冷缓存磁盘基准、峰值 RSS 测量；没有 token、问答或模型 KV 提速声明。

## 研究应用、影响及下一步

[12 篇原文阅读及适配决策](research.md)覆盖 LongMemEval、A-MEM、Mem0、MemGPT、Zep、PagedAttention、SGLang、CacheBlend、KVFlow、LMCache、RAGCache、ObjectCache。本轮是保留原文的分层读取适配及已登记 CO-017 的局部实现；没有冒称完整实现任何论文的学习记忆或 tensor 缓存算法。

既有结果检索使用 `scripts/result_store.py search`、query=`memory scope status cache`、limit8/max-scan200：partial=true，扫描200，解析错误62；命中主要为通信历史。本轮不复用旧性能数字。此次优化不改变历史原始记录/事实语义，不要求重算旧模型质量数据；若需要量化旧 Agent 运行耗时影响，须在相同任务上重测，不能从合成 SQLite 推算。

后续优先确认实际模型服务，并接入原生 exact-prefix 缓存观测/存取，评估 HBM-only、CPU tier 和无缓存强基线。需模型/格式/租户身份、失效及 ready/free 协议；缺服务资源仅阻塞真实 KV 实验。当前研究建议不安装新服务、不占未知 GPU。整个持续优化仍进行中。
