# MEM-SCOPE-05：同状态记忆库的 scope 延迟装配

日期2026-10-16；基线main `ab8a368746233996cb39233036a1631de1d911f2`。
问题ID：MEM-SCOPE-05-EXCESS-HYDRATION。实际路径：project_memory CLI →
`MemoryLedger.list()`（agent_runtime/project_memory.py:278）→ `_get()` →
SQLite。旧 mixed-status 快路径已筛 scope，但全 active 库仍装配所有记录后
过滤。结构回归确认16条只匹配1条时，完整装配次数由16降至1；性能场景则
使用2000条/匹配20条的独立冻结输入。

本轮仅扩展进入已有快路径的条件（283–291），不改 `_get`、持久化格式、
纠错/依赖规则或模型服务。新启用分支限于内置类/状态/scope、非all，且原始
scope值存在差异。原始scope全相同则保守沿旧路径：既避免全匹配双解码，也
放弃全不匹配时可能的收益。SQL `IS NOT` 仅作分流，不替代Python成员判断。

## 固定对照与负结果

同一机器、同一输入DB SHA256、同一预算/返回语义；基线为本轮当前main，不是
更慢的早期eager版本。配置[config.json](config.json)，seed51610、21对随机
先后序，所有样本及顺序保留。完整API调用计时含路径校验、连接、事务、JSON、
读取、完整对象装配及返回；不含CLI进程启动、建库、哈希及返回比较。每臂
一次计时前正确性调用，再一次显式warmup；不测冷磁盘。两轮测量串行，未与
自有回归/独立差分重叠，不声称独占物理宿主。

初版仅放开同状态入口，全匹配控制退化15.966%，超过预设15%门槛，拒绝晋升。
保留[candidate1.patch](candidate1.patch)、[raw-primary.json](raw-primary.json)
和独立[负结果核验/第二版方案](review-v3.md)。第二版增加上述uniform分流，
不变更输入、阈值或统计规则；两版为原定候选上限，没有择优删除样本。

最终数据：[主测](raw-primary-v2.json)、[独立复测](reviewer/raw-independent-v2.json)。
时间均为中位wall ms；变化为after/before−1。两目标各需降低≥25%，五控制
各需退化≤15%，两次测量均满足；控制小差异不作为可靠提速卖点。

| 合成场景 | 主测旧→新ms | 主测变化 | 独立旧→新ms | 独立变化 |
|---|---:|---:|---:|---:|
| 2000全active/匹配20/128B内容 | 16.034304→4.058911 | −74.69% | 16.356241→4.073231 | −75.10% |
| 同上/8192B内容 | 29.320253→10.041490 | −65.75% | 31.609342→11.002417 | −65.19% |
| 2000全active/全部匹配/128B | 16.760623→16.974421 | +1.28% | 17.017209→17.154463 | +0.81% |
| 2000全active/不筛scope | 17.390157→17.596535 | +1.19% | 17.167131→17.166810 | −0.002% |
| 8条全active/全部匹配 | 0.295409→0.290242 | −1.75% | 0.296311→0.300226 | +1.32% |
| 2000混合状态/1000active/匹配10 | 3.859354→3.828789 | −0.79% | 3.801266→3.923118 | +3.21% |
| 2000混合状态/不筛scope | 11.898750→11.817468 | −0.68% | 11.338302→11.327295 | −0.10% |

两目标输入SHA256分别为
`d6ca6b3ae3569476b19c354042b1c82b3614a0a03e69cfab80f377011440e983`、
`48b44e0c6aa595a2a6189bd6f192dd0524d540b4e2255a68f2c0407a5896b1c9`；
其余输入与完整原始样本在JSON，独立重建逐项核对。没有物理I/O字节、RSS、
峰值内存、token成本、模型KV、QA、GPU/JIT或TTFT测量。

## 正确性与证据边界

修前结构测试1项含4个同状态子项失败；最终新增3项回归涵盖同状态选择、
JSON错误优先级和uniform fallback。针对性普通/`-O`均38项通过。全库1205项
运行、8项跳过，其余通过；Reader3项通过；project_docs validate通过。
实际短日志见[checks.log](checks.log)，跳过项不算通过。

独立新上下文 `memory_scope05_result_verify` 读取实际源码/参考/测量协议，
自行设计10098项完整值/错误/状态/结构与恢复检查，并复建输入、顺序和统计。
详见[independent-review.md](independent-review.md)及[独立脚本](reviewer/independent_check.py)。
六项验收仅为声明范围内usable-with-scope，不是无bug证明或受管认证回执。

合法API记录的完整对象、顺序、freshness、修正/接受与现有类型fallback不变；
全部scope/document JSON先解码，再做成员过滤。缺文档表、缺依赖表和空库等
列出的旧兼容行为单独验证。与此前scope02一样，不承诺任意手工损坏SQLite
字节/schema或注入_get错误组合的全错误顺序一致。独立探索明确观察到：
scope不匹配记录content被写成非法UTF-8时，旧版读取报错，新版跳过；这是
测试前已声明的排除边界，不计入通过的差分数，不是已修复的数据损坏。

仍O(N)元数据扫描/解码，非O(K)总查询；没有新索引/后台线程/跨调用缓存。
不同原始JSON但所有scope都匹配时仍可能进入双解码路径，未声称所有分布
恒定提速或任意负载退化≤15%。本轮只证明七个冻结合成场景的局部门槛。

## 复现、环境与研究应用

```bash
PYTHONPATH=. python scripts/bench_memory_retrieval.py --config agent_doc/results/memory-scope05-20261016/config.json --output /tmp/FRESH_scope05_measurement.json
python -m unittest tests.test_memory_retrieval tests.test_project_memory tests.test_memory_check
python -m unittest discover -s tests
python -m unittest discover -s apps/paper-reader/tests
```

环境：KVM x86_64、可见9vCPU/AMD EPYC9V74；Linux6.18.44/glibc2.39，
Python3.12.14/Clang22.1.3、SQLite3.53.1；标准库单进程，无新增线程池/依赖。
源码SHA256 `2f2b7b9c439333438be982a8200d0ed213352c76707d2b07454b113855821e98`；
runner `7de92aba6e41d3424352b586f7335faeae754a8b24d415e3a0ffb04a525d5d65`；
配置 `7d04df14f3fdccb957cc801a502a23a6418ddf99f5e96b8d4d9f3c2bda0ee550`。

沿用已核读的[12篇原始论文矩阵](../memory-storage-20261015/research.md)：
MemGPT的分层访问、A-MEM的原文与链接分离等只启发按需装配，非完整算法复刻。
本轮是常规late materialization在尚未覆盖入口的应用，不宣称新算法或新增
10篇全文精读。[SQLite官方查询规划](https://www.sqlite.org/queryplanner.html)
同时提醒索引/排序成本取决于数据；本轮不增加未经写入/迁移成本验证的新索引，
也不用SQL JSON筛选替代Python错误契约。依据实现优化技能先固定门槛，保留
负结果，再选择已验证候选；没有把研究阅读数当作升级完成。

历史结果检索scan200/partial/60读取错误，scope02已明确留下该候选；旧数据
仅作上下文，收益全部重测当前基线。知识检索segment-monoid不适用，拒用。
计划v1返修、v2通过、首版负结果、v3第二版均原样保留。未部署tmux监督或
ReviewSession/ResultValidationHandler宿主；手动独立验收不自动恢复未来信任。
结果登记仅供发现，unknown状态不提升。主AI独占实现、任务与发布，独立
角色只写独立证据；人类guide、真实用户记忆和既有实验字节未修改。

MEM-STORAGE-01仍未完成：模型KV生产/消费端、租户/模型/位置身份、取消/异步
生命周期、真实QA与完整任务延迟需要实际授权服务后另行验证。SQLite收益
不能外推为模型KV或推理提速。发布SHA及远端字节核对在实际完成后另记检查点。
