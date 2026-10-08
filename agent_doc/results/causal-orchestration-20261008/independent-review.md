# ORCH-PAR-01 独立结果验收

结论：**usable-with-scope；本次有界规范及合成规划语义无未解决阻断。** 可用于原生宿主文档发布；不认证 ReviewSession 机器接入、全项目受管启动、真实 GPU 调度、模型质量或性能收益。远端发布读回是主控尚须完成的独立交付步骤，本报告不将本地验收当成已发布。

审核者为实际独立宿主上下文 `/root/causal_result_review`，只写本文件，未修改源码、TASK、人类指南或规划。已读 AGENTS、决策/项目文档约束、ORCH-PAR-01 详情、固定计划、新工作流、实际源码、相对 `origin/main` 的补丁、原始及整合后回归日志和新上下文规划。审核时整合基线为 `acf85d7`，本地实现提交为 `f7604ac`；并发 CODEMAP/TASK 追加均保留。审核没有使用关键词计数代替规划判断。

## 固定对象与核验结果

| 对象 | 独立核验 |
|---|---|
| `plan.md` | 实际 SHA-256 `817bd087fb8f0ffaf93b733c17326e2f34333d4740cfddfc393f9c289fd4236e`，与原计划审核绑定一致。 |
| `source-freeze.json` | 最终19个源/生成文件逐字节重算 hash，零失配；manifest自身 SHA-256 `e3f2a205d01013a9375f64a3df85097c7b8ae0a455fa35e1359aedbce0e8cc7a`。原始及整合后回归对应的19项旧冻结保留于 `source-freeze-v1.json`，其SHA-256为 `36f5fcdf1b9da834678b32289c05c796e4dc2c9b1544229b1068dba0046df0d8`。 |
| 实际 Engine | `agent_runtime/core.py:339–448` 每 tick 至多 claim 一个节点，循环 claim 后 break，持久 cursor 后调用同步 `handler.run`。工作流所述短 submit/poll 才可能让外部长作业重叠，符合当前实现；并未新增资源 schema 或改变引擎。 |
| 实际 GPU adapter | `request/plan/run` 的 accuracy 按 `sample_ids[i::N]` 分片、每设备 worker；performance 强制单设备、外部排他认证、同步后串行交错 baseline/candidate。CLI/计划不能替代可信 runner，也不是本案例八数据集资源调度器。源码未改，相关回归是 mock/程序边界证据。 |
| 入口与生成引用 | 新规范可从 AGENTS、通用/科研/planner/review 入口、监督与实现工作流发现；两份研究插件新规范实际生成。独立运行 `python scripts/sync_plugin_references.py --check` 返回 0，18 份 Markdown 源/生成文件本地导航实际解析，无缺失或越界。旅行 planner/review 为同步产生的仓库 URL 回退，不能声称该新增规范在旅行包离线内置；相应目标在待发布源码中存在。 |
| 回归 | 原 `regression.log`、整合后 `integrated-regression.log`、最终 `final-regression.log` 均为相同68条测试记录且全部ok，无skip/error/failure；分别0.307s、0.295s、0.241s。涉及 main-ai contract、reference sync、Markdown、project docs、GPU adapter、task waiting；不等于全套测试或真实模型/设备执行。最终同步检查也独立重跑返回0。 |

原日志 SHA-256：`06b6c73d41465b30a4de7271dddc2251f068f431f753af75ce866f7d3fdeb936`；整合后日志：`5add455981fc67582950589c0b6a71483a613cac5263b83cf517233899a968a6`。本审核读取日志并检查实际测试及实现范围，没有另造一次 68 项运行记录。

最终日志 SHA-256：`76f174a30638ec22cb98363916a9944d298b7737b95d10bfa6828f465ab512ad`。最终代码冻结相较v1仅改变因果工作流与其两份生成副本，新增派发必须给出绝对 project_root 和 allowed_writes/output_root、消费者核对项目范围的要求；审核实际三份diff后确认修复与路径缺陷对应，未扩大本轮范围。

独立执行 `python scripts/project_docs.py --root /workspace/scratch/4f9639d1bad2/agent validate` 仍 exit 2，原始错误为 `detail requires one stable ## Plan section before ## Progress`。三份既有 CONT-20261008 详情仍为 `## Plan v1` 且缺标准 Task-ID/Date；本补丁未改这些文件。该既有失败限制全项目机器接入结论，但不阻断本次原生宿主有界文档内容验收。不得报告“全项目 validate 已通过”或“受管监督已启动”。

## 八数据集方案实质验收

正确路径内的 `forward-plan.md` 实际 SHA-256 为 `920334f065c1e147461879abb408d0ef6956baeb5740b0387f152e3447402254`。以下判定仅针对题设合成案例的规划能力，不是实机结果。

| 原始要求 | 实际方案及判定 |
|---|---|
| 固定只读 M/P；D1…D8 全集 | PREP/VPREP 先冻结共享只读输入、样本身份、协议与验收，八个评测仅依赖 VPREP；无共享训练状态伪并行。每份结果均由不同实际 owner 独立验收，消费者绑定准确契约。通过。 |
| A/B 24GiB、C 48GiB；每卡≤1；D1…6 16GiB、D7/8 32GiB | D8 首先占 C、D1 占 A；D2 在加载槽释放且 B 获准后启动。D7 等 C 释放，A/B 拉取剩余小任务；未把 A+B 显存相加，未同时派 D7/D8 到 C。此排队没有被伪写成科学因果边。通过。 |
| 加载≤2、CPU验收≤2 | 初始只加载 D8/D1，加载完成释放槽后才准入 D2；总 GPU 在途≤3、每卡≤1、验收队列≤2。验收若需 GPU，必须重新按设备准入，不能计成免费 CPU 检查；绘图也受总体 CPU/RAM 限制。通过。 |
| 时长未知，D8 可能最长 | D8/C 早开是有限启发，明确 unknown、无 ETA/最优/加速声明；C 专用大作业、D1早图、等待年龄及不抢占规则相容。通过。 |
| D1验收后先图 | V1→A1→VA1→SHOW1 仅消费 C1/Cplot，可与其他评测并行；图明确 D1 局部范围，未抢跑八项总排名。通过。 |
| D3首试失败、其他继续 | 保留 a01 失败证据，V3/JOIN8/FINAL 阻塞，独立作业及D1图继续；不确定作业状态先 poll/reconcile，终止确认后才重试；初次+一次重试为建议上限，实际预算仍须冻结授权。新尝试新结果与计划版本，不覆盖或重置预算。通过。 |
| macro、micro及完整结论 | JOIN8 等全部八份验证契约，检查唯一性、分母、版本和样本覆盖；macro=Σ(ci/ni)/8，micro=Σci/Σni，汇总再独立验收。7/8不完成、失败分片不改可选、空分母不静默丢弃。通过。 |
| 可变模型 D1→D8 连续微调 | 明确 checkpoint/优化器/RNG 状态依赖必须顺序推进；独立从M0训练八副本属于不同实验，不能替换目标。通过。 |
| 准确率并发计时作为单卡延迟 | 明确共享 CPU/I/O/加载污染，即使每卡一作业也不能据此称单卡无干扰延迟；单独性能链需要匹配硬件/协议、排他与共享瓶颈控制。通过。 |

该方案保留真实 UUID、job ID、资源租约、预算及接口均尚未取得的事实，执行前仍 blocked。计划中的 hash、路径、owner、重试字段是设计记录，不是现有 runtime 可直接接收的机器请求。

## 已发生的缺陷与恢复

**输出路径失配，已恢复。** planner 首次将相对路径写到宿主 cwd 的 `/workspace/scratch/4f9639d1bad2/agent_doc/results/causal-orchestration-20261008/forward-plan.md`，在指定仓库路径读取时实际报 `No such file or directory`。因此首次文件交付不合格，不能描述成首次即成功。主控随后逐字节复制到 `/workspace/scratch/4f9639d1bad2/agent/agent_doc/results/causal-orchestration-20261008/forward-plan.md`；本审核重新从该正确路径读取并计算上列 hash，与原件一致，恢复成立。后续派发应显式携带 PROJECT_ROOT 及绝对 allowed_writes，并在完成时回读绝对路径。本次语义规划验收与该路径错误分别记录，不抹去失败历史。

该防错要求已进入最终规范与两份同步副本，并通过最后68项程序回归。本例 planner 实际读取的是v1规范（其文件所记旧workflow hash保持原样），本轮没有在修正后重新启动新上下文模型测试。因此不能把补充指令及程序回归说成“已实证模型不再写错目录”；最终可用范围仅包括针对实际缺陷的规范修正、同步一致性与原案例语义核验。

## 既有小时任务配置

独立读取私有 `.agent-runs/causal-orchestration-20261008/automation-before.json` 与 `automation-after.json`，未公开完整 prompt。实际比对确认同一任务 ID `6ac49448fab08190a825f0db4a6f3ca9`、schedule 字节相同、旧 prompt 为新 prompt 的完整精确前缀、新增725字符、enabled=true。旧/新 prompt SHA-256 分别为 `38e924e9e998b63a01134c5ae93639d29aa8b0367ded46c984c8cac7616afce5`、`c66e5ec5a32c5d7ba16a9138c94471d8af7e0a3d9648f174f3141dc36080a693`。这支持“原小时任务增量配置已保存并读回”，不支持“该小时批次已执行完成”。

最终可用 scope：规范导航及生成同步、实际实现边界说明、上述有限案例规划语义、所列局部回归及既有自动化配置更新。无尚未解决的本 scope 阻断；项目全量 validate 缺陷、真实资源/adapter/预算补齐、GPU测量与远端发布读回不在本报告已完成结论内。

## 发布前并发整合 delta 复核

远端更新至 `9e23c73` 后再次进行有界只读复核；本地重放提交为 `7307cce`、`e47b27c`。相对 `origin/main` 的文件清单仍仅本轮规范、入口/生成引用及 ORCH-PAR-01 证据；CODEMAP/TASK差异仅追加本轮条目，没有删除上游数学筛选知识或其任务。当前 `source-freeze.json` 的19项再次重算零失配，前述最终内容验收继续适用。

实际 `publication-regression.log` 记录同一68项测试全部ok、0跳过，0.235s；测试名称及状态与 `final-regression.log` 完全一致，包括实际调用 `sync_plugin_references.py --check` 的生成同步检查。该日志 SHA-256 为 `2ae219cd2d0378b902d6383ada640517e372cce948678e55c4bdd3e2130156fa`。本delta没有另外执行扩展测试或新数学知识验收，也不将上游知识结果计成本任务成果。**无新增本范围阻断**；原可用scope与全部限制保持，远端发布事实仍由后续实际读回证明。
