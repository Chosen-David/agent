# MEM-SCOPE-02：只装配当前 scope 的有效记忆

## 目的与实际结果

2026-10-16；优化 Chosen-David/agent 的记忆存储入口，基线为当时最新 main
`f872166a7ce4c61e21353dad83a83729d44440ca`，不是第一阶段旧 eager 基线。
稳定问题 ID：**MEM-SCOPE-02-EXCESS-HYDRATION**，confirmed 性能浪费。
独立新上下文 `memory_scope02_review` 完成方案检查、代码阅读、1366 个差分
场景及串行复测，结论 **usable-with-scope**。完整持续记忆/KV任务未完成。

真实入口 `python -m agent_runtime.project_memory --root PROJECT list --scope T1`
→ `MemoryLedger.list()` → `_get()` → SQLite。当前 mixed-status 快路径虽已
跳过非请求状态，仍装配该状态下所有 scope 的 content/source、文档和父依赖，
最后才剔除 scope 不匹配者。本轮先用现有元数据精确筛 ID，仅装配匹配项。

适用范围为规范API写入的有效记录及所测元数据异常。返回完整对象、顺序、
纠错/接受及依赖语义不变；全部 scope/document JSON 仍先 Python 解码，
然后执行原 Python 成员检查，避免 null 的成员错误盖住后续 JSON 错误。
只对已进入 mixed-status 路径且 scope 为内置 str 启用；None、非str、子类、
all、全请求状态沿原路径。无schema、索引、长期连接、内容缓存或外部依赖。

仍 O(N) 解码及元数据暂存，绝非 O(K) 总查询。与上一阶段同样不承诺任意
人为损坏SQLite字节的错误可见性完全不变：新跳过的 scope 不匹配 content/
source 若被手工破坏为非法UTF-8，不保证再读取和报错。未加强并发快照保证。

## 固定对照与可复现数据

预设门槛：两种scope稀疏历史场景耗时降低≥25%，四类控制退化≤15%。
固定 seed1610、21对随机先后序，同一DB字节，双方各warmup一次；全入口
计时包括路径校验、连接/事务、读取/JSON/完整装配/筛选/列表返回。建库、
完整结果比较、哈希及统计在计时外。主测与独立测量串行且不与测试重叠。

| 合成场景 | 主测旧→新 ms | 耗时变化 | 独立旧→新 ms | 耗时变化 |
|---|---:|---:|---:|---:|
| 2000条/1000 active/匹配10，128B内容 | 13.357964→4.361570 | -67.35% | 11.919134→4.216343 | -64.63% |
| 同上，8192B内容 | 23.419538→9.146568 | -60.94% | 23.322374→8.861323 | -62.01% |
| 2000条/1000 active/全部scope匹配 | 12.527621→13.354509 | +6.60% | 12.720506→13.102424 | +3.00% |
| 2000条/1000 active/无scope过滤 | 12.489305→12.325581 | -1.31% | 13.693241→13.714854 | +0.16% |
| 8条全部active小库 | 0.337110→0.336760 | -0.10% | 0.349559→0.321928 | -7.90% |
| 400条全部active/匹配4 | 3.378850→3.394963 | +0.48% | 3.983418→4.037138 | +1.35% |

全部样本/配对顺序、DB输入SHA256与软件环境见
[raw-primary.json](raw-primary.json)、[independent-raw.json](independent-raw.json)，
六类固定输入见[config.json](config.json)。没有丢弃样本或事后调整门槛。
tiny控制差异不作可靠提速卖点；主测和独立控制退化均在预设上限内。

```bash
PYTHONPATH=. python scripts/bench_memory_retrieval.py --config agent_doc/results/memory-scope02-20261016/config.json --output /tmp/FRESH_MEMORY_MEASUREMENT.json
PYTHONPATH=. python agent_doc/results/memory-scope02-20261016/independent_check.py
python -m unittest tests.test_memory_retrieval tests.test_project_memory
```

benchmark按固定Git SHA读当前基线、校验源哈希再载入独立namespace；不是
把较慢的旧eager算法当对手。输出文件独占创建以保留原始结果。脚本以显式
配置运行受信任的本仓库Git源码，不应对不可信仓库/commit执行。

## 正确性与回归

先红后绿的结构用例：基线为只返回m15仍 `_get` m03/m07/m11/m15，候选
只 `_get` m15；错误在修前实际出现，非用自身输出作正确性参考。其余测试
对照完整packets/顺序及异常。新增4项，检索12项/连同project_memory共27项通过。
独立[1366场景](independent_check.py)与当前f872的完整值或异常类型/消息比较，
覆盖scope的list/dict/string/null/数字、空/无命中、状态短路、先解码后成员错误、
老schema/缺依赖表、排序、子类及保留traceback后立即写入，全部通过。

```text
baseline structural test: FAILED (failures=1)
candidate memory/project-memory: Ran 27 tests in 0.668s, OK
python -m unittest discover -s tests
Ran 1194 tests in 68.029s
OK (skipped=8)
python -m unittest discover -s apps/paper-reader/tests
Ran 3 tests in 1.580s
OK
project_docs validate: exit 0, canonical layout
```

8项跳过不算通过。独立结果与代码/数据范围见
[independent-review.md](independent-review.md)。手动宿主实际独立上下文，不是
受管ReviewSession/ResultValidationHandler认证回执；没有tmux/动作adapter，
未启动新的后台监督器。结果登记只用于发现，不能自动批准以后复用。

环境：KVM x86_64，可见9 vCPU，AMD EPYC9V74；Linux6.18.44/glibc2.39，
Python3.12.14/Clang22.1.3，SQLite3.53.1。本机局部温缓存合成数据，不包含
真实用户记忆，无GPU/JIT/模型/冷磁盘/峰值RSS/计费token或QA质量测量。
虚拟宿主噪声保留在原始数据，未声称独占物理机。
最终源码SHA256=`914229446d705343ef71d81c79b20b7119652a376aa180e9eff54e83a7d1d450`；
基线源码=`5ae35f1dcad87ab759fe4aab5f7deb522c9a3ea1d01ef8118c4ca65547ef7b19`。

## 研究应用与余项

沿用已核对的[12篇机制/实验矩阵](../memory-storage-20261015/research.md)，
本次补读EfficientAgent、CacheScout及Persistent Memory负结果的关键方法/实验，
见[研究增量与取舍](research-delta.md)。不是10篇新全文通读或新算法复刻；
实际应用是原文保留、先确定相关记录再分层装配，按实现优化技能先比较后验收。

已有结果查询首位命中memory-storage-20261015；扫描200/partial=true/61错误，
不推断全历史完整。仅复用研究/实验结构，本轮收益全部重新比较当前基线。
QLoRA/HNSW/FlashAttention知识卡与此SQLite结构不匹配，未作为方法依据。
没有覆盖历史结果、真实记忆或人类guide，不要求重算既有模型质量数据。

真实模型KV仍缺已配置服务、模型/格式/租户身份、缓存tensor消费者及资源合同。
下一步应在这些条件存在后比较exact-prefix原生HBM/CPU tier/无缓存，记录
实际token/byte命中、重算、TTFT与完整任务质量；不以Python命中或本轮60%+
数据库耗时下降声称模型推理同等加速。全active scope优化保持后续待评估，
本轮没有放宽错误边界来扩展适用域。
