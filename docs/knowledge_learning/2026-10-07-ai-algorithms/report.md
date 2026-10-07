# AI 算法知识补充：推测采样正确性与成本边界

## 结论与交付范围

在上游 `a35a102306e3aba0af1a5180390b226febe14705` 的39条知识上增加2条可复算推导卡，现为41条。既有39条的 JSON/Markdown 不变；未带入旧会话取消的 runtime 批次，没有修改 SGLang、训练模型或执行上游推理代码。

- `ai.speculative-sampling-residual-exactness@1`：接受质量与正部剩余质量恢复目标分布；明确实际提议、共同输出空间、正确条件前缀、零支撑/零残差及树/MTP边界。
- `ai.speculative-decoding-cost-bound@1`：条件前缀尾和、不要求独立的产出计算、分项成本与限定的盈亏阈值；包含相关事件、长草稿及验证成本逆转反例。强依赖第一条。

最终知识快照为 `820007a073af71c4479f04cc28f3c3708b3cca5d0c97dac80612bd6701e5ad8f`，四文件字节哈希见 [final-candidate-freeze.json](final-candidate-freeze.json)。这里的 `published` 是本地知识 schema 的可检索状态，不代表已经推送远端。Git 发布与读回由主维护者另行记录。

结论是可在现有工作流中使用，并保留已知检索缺口。默认文件检索的12题全文上下文全部命中；SQLite默认仍漏2题。使用现有明确领域筛选后，两后端均在原预算内恢复12/12。没有把这种恢复写成默认检索成功或未见任务泛化。

## 与上游已有案例的分工

`infra.speculative-acceptance@1` 已保存 ICML 2023 在 TPU-v4/T5-XXL/batch=1 上的作者实验与迁移条件，不能把这些旧观测算成本轮新增实验。两条新增卡补充可逐步使用的正确性证明、条件事件尾和、成本阈值和反例；它们不是两项新的经验结果。

共同原论文、α=0.8/γ=4 的3.3616期望长度例子、“接受率不足以决定速度”及部分采样边界存在重叠，明确不重复计为独立证据。新增成本卡以 `related` 指向既有经验卡，并保留到正确性卡的强依赖；不把旧硬件测量当成一般定理的前提。旧卡未修改，无需改其版本。

独立语义审查核对15个别名及55项身份/范围断言；最终集成补充核对22项允许改动。这些计数是机械与语义检查，不是科学实验数。报告见历史归档的 `source-review/r3/` 与 [alias-review.md](alias-review.md)、[integrated-scope-review.json](integrated-scope-review.json)。

## 来源、数学与适用性

原论文与固定源码的身份、定位、日期、许可边界见 [source-lock.json](source-lock.json)、[source-review.md](source-review.md)。包括 Leviathan 等 ICML 2023、Chen 等 arXiv v1、EAGLE-3 NeurIPS 2025，以及固定 EAGLE commit 的相关分支静态阅读。原始PDF、上游源码、模型权重不随本交付分发；[source-manifest.json](source-manifest.json) 中 file 是历史缓存名，URL/字节哈希供重新获取核对。阅读范围不是完整文献普查，也未声称读完所有附录。

- 研究者13组有限有理数自检，包括784对三元分布与成本正负例。
- 独立来源审查另写程序：225对分布、240个候选消元配置、9个二步联合概率坐标、1620个理想成本网格点。
- 独立数学/适用性验收：12个检查族，包括784对分布、729对二步条件表与一个非对称三token条件表；追加4个候选特有检查族明确为见候选后的补充。
- 冻结12题的逐题适用/拒用/信息不足审阅12/12。这里是有限数学/人工论证与程序检索，未把它写成12次独立模型实验。

不同检查可能复用同样数学问题，不能把网格点总数相加当独立统计样本。`derivation-reviewed` 不等于形式化证明。初版0.763小数错误已更正为191/250=0.764，Chen的章节定位已更正；历史审查记录保留。

## 冻结、失败与修复轨迹

冻结题SHA256为 `f9af50f1e1381f33f41348e00f4ea78059a15d05c4b92c71ca8d598bc4496061`。题目先于首版候选阅读冻结；r2/r3复跑都属于开发/回归，不再是盲题。没有改查询、gold、ranking或预算。

1. r1：16→18旧语料上，新题文件Top-3 12/12、SQLite11/12，关联全文均12/12；但旧物理建模和线性残差题出现排序/召回退化，未通过旧题门槛。
2. r2：只保留论文/算法名式别名，旧题恢复；新题文件Top-3 9/12、上下文10/12，SQLite10/12、上下文11/12。另一次因并发同ID导入失败而产生的无效续跑明确作废，不能算通过。
3. r3：恢复合法的问题/机制检索描述，仅去除歧义的裸 `residual` 与物理“长度”别名，并添加规范算法名称。正文、前提、来源未改。旧16→18逐题零新增退化；新题文件Top-3 11/12、SQLite10/12，全文上下文均12/12。不把缺少Top-3命中掩盖为排名成功。
4. 最新main先有独立39条基线，再比较41条候选。上游已有排名变化单独保留，未归因于本轮。添加与既有经验卡的正常关联后，默认SQLite两个目标包仍因预算不足而被显式跳过；该失败保留。
5. 新知识与保留策略文件未同步到插件时，第一次知识测试60项有1项快照失败；全局同步后60/60通过，原失败日志保留。

独立语义审查的初步哈希/别名/互补性接受消息于主维护者观察的01:36:48 UTC收到（消息无独立工具时间戳，不把该秒值当外部审计时间），本地可检索状态于01:38:01 UTC切换；正式r3报告完成于01:39:38 UTC。后续最终字节/元数据补充审查另行关闭。没有声称正式报告早于状态切换；远端发布仍须最终集成审查。

## 最终检索结果与实际恢复

使用原查询、原gold、Top-3和默认8条/20,000序列化字符预算。全部条目正文与强依赖保持完整，`applicability=unchecked` 仍由使用者审查。

| 12题开发/回归 | 文件Top-3 | 文件全文上下文 | SQLite Top-3 | SQLite全文上下文 |
|---|---:|---:|---:|---:|
| 默认全库 | 10/12 | 12/12 | 8/12 | 10/12 |
| 显式 `domain=ai-algorithms` | 11/12 | 12/12 | 11/12 | 12/12 |

默认SQLite缺口是A03零剩余质量与A12终止/剩余token预算。相关旧卡被召回，但新成本＋正确性完整包在其他种子及其依赖之后超过预算，正常拒绝装入；没有截断前提或放大预算。现有工作流允许在确认问题领域后筛选候选再读取全文。限定领域后24个后端×题组合全部恢复，最大包18,253字符，refs闭包与正文一致性均通过。[默认结果](evaluation/default-current.json)、[领域恢复](evaluation/domain-recovery-final.json)。这不是新增自动路由器或默认检索优化。

四套旧catalog共36题×2后端，39→41的Recall@3、context recall、MRR及无命中判断逐题零新增退化。工程15题两后端全部原样保持。旧缺口也保留：original平均Recall@3为20/21；morphology文件召回0、SQLite原始召回3/4但context为1，不能说整个旧评测全满分。历史16→18及最终39→41证据分别见 [旧基线比较](evaluation/legacy-original-comparison.json)、[当前比较](evaluation/legacy-current-comparison.json)。

## 程序、快照与边界

最终程序回归：全仓501项，500通过/1跳过；Reader3/3；知识专项60/60；插件引用/语料字节同步检查通过。唯一跳过项是需要可用宿主tmux/Unix sockets的显式opt-in测试。全仓结果包含同轮其他已授权变动，不能把501项全部说成新增知识测试。

日志见 `evaluation/tests-final.log`、`reader-tests-final.log`、`knowledge-tests-final.log`，结构化摘要见 [tests.json](tests.json)。没有新增真实GPU/模型分布实验、生产吞吐、自动horizon控制或用户服务器部署验证。另有一次真实独立角色使用，单独登记如下，不混入有限数学与开发检索计数。

## 一次真实独立角色使用

独立上下文回答“8个草稿token、90%平均接受率、draft0.2T、验证4T是否至少快4倍，draft用temperature/top-p而目标argmax是否无损”。该角色未读本轮验证题/gold，实际执行search、context、show和check-refs，并独立查原论文；[完整回答](live-use/response.md)、[适用性与工具记录](live-use/knowledge-use.json)、[检查摘要](live-use/evidence-summary.md)。

它分别计算每token与整批draft成本的1.094×/1.459×条件估计，用一轮至多9token的上界否定4倍；区分边际、条件、实际提交比率口径，给出argmax相对随机目标的反例。58/58有限有理数检查通过，主维护者审读回答及边界接受。不能把这些条件值写成设备实测。

首次两条知识仍为candidate，普通show被拒；角色保留失败，未绕过门禁。只读观察到本地状态变为published后，重新按正常show读取、冻结引用并验证。其实际上下文设置为26,000字符，与上文固定回归的20,000预算不同，不能拿这次使用证明原预算默认召回成功。结论仅覆盖一个真实角色实例，不是泛化A/B或模型性能实验。

## 证据包与复现

历史证据包（本次未上传，原始归档与SHA256保留在本地检查点；此处仅描述历史归档）保留r1/r2/r3候选、首次失败、无效装配诊断、完整上下文和独立审查的公开副本；不含第三方PDF/源码或派生SQLite。为避免发布私有工作区路径，副本统一替换路径前缀，原始字节仍保留在私有工作区。[归档清单](historical-evidence-manifest.json) 逐文件记录原始SHA256、公开副本SHA256和是否路径规范化。数值、查询、gold、候选正文与失败状态未改。历史日志中的 `<repo>`、`<evidence>` 是来源标记，不是可直接执行的路径。

从仓库根复现当前结果：

```bash
ROUND=docs/knowledge_learning/2026-10-07-ai-algorithms
python "$ROUND/verify.py"
python "$ROUND/independent_math_check.py"
python "$ROUND/evaluation/check_math.py" --output /tmp/aik-math.json
python "$ROUND/check_domain_recovery.py" --repo "$PWD" --corpus knowledge --cases "$ROUND/evaluation/frozen_tasks.json" --output /tmp/aik-default.json --unscoped
# 上一条按保留的2个默认缺口退出1；不是执行错误。
python "$ROUND/check_domain_recovery.py" --repo "$PWD" --corpus knowledge --cases "$ROUND/evaluation/frozen_tasks.json" --output /tmp/aik-domain.json
python -m unittest discover -s tests -p 'test_knowledge*.py' -v
python scripts/sync_plugin_references.py --check
```

重放39→41比较时，先将 `git archive a35a102306e3aba0af1a5180390b226febe14705 knowledge` 解到新的隔离目录，再用 `compare_retrieval.py --repo "$PWD" --baseline 隔离目录/knowledge --candidate knowledge --out 一个尚不存在的输出目录`。不要覆盖历史输出或把新的结果改写成首次盲测。
