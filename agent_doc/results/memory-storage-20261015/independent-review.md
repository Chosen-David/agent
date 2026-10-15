# MemoryLedger 检索优化独立核验

结论：**usable-with-scope**。最终候选通过本次固定性能门槛及所列边界核验；不是模型质量、真实 memory QA 或模型 KV cache 的验收。

## 版本与独立性

- 独立执行上下文：memory_scope_review；只读实现与测试，独立创建临时 SQLite 数据库。
- 核验源码：agent_runtime/project_memory.py，SHA256 `5ae35f1dcad87ab759fe4aab5f7deb522c9a3ea1d01ef8118c4ca65547ef7b19`。
- 原始独立测量与诊断记录：[independent-raw.json](independent-raw.json)。
- 此审查未创建或声称宿主认证的 ReviewSession，也不授予用户权限。

## 先前候选被否决及修正

1. 仅 SQL status 下推会忽略被排除条目的损坏 JSON。独立复现：candidate 的 scope='not-json' 时，旧版 list(active) 抛 JSONDecodeError，简单 WHERE status 后却成功。已改为 Python 元数据预检。
2. SQLite json_valid 不能替代 Python 解码：非法 UTF-8 BLOB `b'"\\xff"'` 的 json_valid=1，但 json.loads 抛 UnicodeDecodeError；转为 TEXT 后 sqlite 取值也会失败。最终实现不依赖 json_valid。
3. 初版元数据预检使 all-active 独立测量退化 19.27%，超出 15% 上限。该版未接受，新增无历史时的原路径。
4. 缺 dependencies 表、且所选状态无命中时，第二版返回空列表，旧版抛 MemoryError。独立复现后已补 schema 查询与原路径回退。
5. 流式元数据 cursor 在 JSON 解码异常 traceback 被调用者保留时，会保留 SQLite 读锁，导致后续 writer 报 database is locked。独立复现后改为 fetchall，再解码。最终验证保留异常对象期间即可立即写入。

以上失败保留为诊断，不混入最终验收数据。第一次深层 JSON 用例的固定失败预期不适用于当前 Python 构建；生产者已修正为新旧结果/异常一致性，未将其计作实现错误。

## 最终正确性核验

独立生成 68 个边界场景，均通过：

- 五种状态，精确 scope 成员匹配（T1/T10/T）、空和非字符串 scope 参数。
- 相同 created_at、倒序 ID 插入下的固定排序。
- 完整字典、dependency 排序与 document_refs 内容。
- 覆盖 _get 的子类，以及 str 状态子类使用旧路径。
- scope/snapshot 的损坏 JSON、非法 UTF-8 BLOB 和 TEXT 均拒绝；捕获并保留异常后立刻写同一数据库成功。
- 缺 document_dependencies 的旧 schema、缺 dependencies 且无所选状态命中时与旧路径一致。
- 独立重跑新增 8 个 unittest 方法全部通过。

查询数量独立 fixture：100 条记录、5 条 active，完整返回一致；SELECT 数量 **401 → 25**。这只是结构性佐证，不替代全入口计时。

## 最终独立性能

基准：固定 4 组数据库字节与 hash、21 次配对、随机顺序、双方 warmup、全 list() 入口，返回完整对象后核对一致。最终计时期间主执行者暂停其他 CPU 工作；先前同时跑全库测试的数字只保留为诊断。

| 场景 | 修前中位 ms | 修后中位 ms | 变化 |
| --- | ---: | ---: | ---: |
| small：8/8 active | 0.288378 | 0.265865 | 耗时降低 7.81% |
| all-active：400/400 | 3.345856 | 3.414558 | 耗时增加 2.05% |
| history-small：2000/20 active，128 B content | 16.063734 | 3.383062 | 耗时降低 78.94% |
| history-large：2000/20 active，8192 B content | 26.076417 | 8.999378 | 耗时降低 65.49% |

两种历史密集场景均超过 25% 降低门槛；small/all-active 均未超过 15% 退化上限。输入 hash、全部原始样本、Python/SQLite/平台版本见独立 JSON。

## 结论边界

收益限于已测本地温缓存 SQLite 合成场景。等价范围为规范 API 写入的有效记录与明确测试的元数据损坏情况。没有证明所有任意损坏 SQLite 字节上的异常类型、次序或信息完全不变；例如直接 SQL 制造的非所选 content/source 非法 UTF-8 不再保证被读取。仓库 runtime 未控制真实模型 KV tensor，不能将这项存储检索优化表述为 KV 推理提速或记忆回答质量提高。

## 发布前文档与最终数据复核

再次读取最终源码，SHA256 与上文一致。独立复算主执行者串行 raw-accepted.json：small 耗时降低 11.30%，all-active 增加 2.70%，history-small/large 分别降低 80.21%/65.03%；通过固定性能门槛。实际最终测试日志为 1190 项运行、8 项跳过、其余通过；Reader 3 项通过。该全库记录由主执行者执行，本审查实际回读日志，未冒充独立重跑全库。

研究和任务详情将 12 篇原文的定向方法/实验核对与新增全文阅读数量分开，明确部分页及附录未新近完整读完；也区分本地 SQLite 改进与后续 KV 接入。此处只核验研究叙述与实现/数据的一致性，未独立重读远端全部论文，不能作为每项文献主张的独立科学验证。研究文件初稿中的不存在 scripts/project_memory.py 已反馈给主执行者，真实入口为 python -m agent_runtime.project_memory。

最终 report.md 已读取：四行主测/独立数字与原始 JSON 一致，测试数与实际日志一致，源码入口/行号正确；研究文件已纠正 CLI 模块路径。报告明确保留元数据 O(N) 预检、全 active 小幅退化、候选失败、任意损坏数据库不保证异常次序，以及缺真实模型/GPU/冷缓存/RSS 验证。任务详情保持整项记忆/KV 优化未完成，没有把本轮局部收益当长期目标完成。当前无新增发布阻断；发布仍由主执行者核对最新远端、冻结 manifest 和逐文件读回。本独立文件到此冻结。
