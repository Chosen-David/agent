# 本轮增量代码与产物地图

ADOPT-01–04：`scripts/setup_codex.py` 从已提交快照安装/同步 Codex 用户技能；`templates/codex_global_instructions.md` 为简短受管入口；`tests/test_codex_setup.py` 验证冲突、更新、备份和中断保护；`docs/codex_adoption/` 为接入/迭代及验收记录。主 AI 单一生产者；本机 Codex 和用户是消费者，私有部署记录在 `.agent-runs/codex-adoption/` 与 `CODEX_HOME/chosen-agent/`。

现有入口：`setup.py` 安装主 AI/Skills；`config/role_registry.json` 注册角色；`prompts/orchestrator.md` 路由；`agent_runtime/` 执行与验收；`scripts/sync_plugin_references.py` 生成独立插件资源。本文件是知识库升级的增量地图，不宣称已盘点全部历史产物。

| TASK | 实际锚点 | 生产者 → 消费者 | 用途 |
|---|---|---|---|
| T19 | `knowledge/entries/`, `knowledge/FORMAT.md` | 知识维护者 → 建模 Skill | 一般知识、来源、前提、版本与关系 |
| T19 | `agent_runtime/knowledge.py` | 主 AI 实现 → CLI/ReportingHandler | 校验、检索、引用身份与依赖闭包 |
| T19 | `agent_runtime/knowledge_index.py` | 主 AI 实现 → CLI/建模 Skill | SQLite FTS5 增量索引、排名融合、章节导航 |
| T19 | `agent_runtime/knowledge_ingest.py` | 主 AI 实现 → 学习流程 | 候选原子导入、来源哈希凭据 |
| T20 | `plugins/research-assistant/skills/model-with-knowledge/` | sync 脚本/主 AI → 独立 Skill 宿主 | 流程、脚本和字节一致的语料快照 |
| T20 | `agent_runtime/task_manifest.py` | 任务执行者 → 独立验收/主 AI | 已声明知识在执行前后与验收时复查 |
| T21 | `prompts/math_knowledge_continuous_learning.md` | 主 AI → 用户选择的调度器 | 有界学习、证据验收、更新发布 Prompt |
| T21 | `evals/knowledge/queries.json`, `scripts/eval_knowledge.py` | 主 AI/维护者 → 验证流程 | 可重复文件/索引检索比较 |
| T21 | `docs/knowledge_validation/`, `tests/test_knowledge*.py` | 主 AI/独立测试 Agent → 用户/维护者 | 程序、检索与真实使用证据；不混为部署证明 |
| T22 | `TASK.md` | 主 AI → 用户/后续维护者 | 本轮授权、验收与 main 发布读回 |
| COMM-02 | `agent_runtime/communication.py` | 可信 host adapter → 按任务订阅的消费者 | 事务投递、幂等事件、版本隔离、回执与现有 handoff 消费 |
| COMM-01/03 | `workflows/agent_communication_workflow.md`, `docs/communication_research.md` | 主 AI → 科研角色/持续优化任务 | 有证据的通信设计、定向反馈、研究候选与验收边界 |

`.knowledge-cache/` 是可重建索引；`.agent-runs/knowledge-v1/` 是当前运行临时状态，均不提交。未移动历史目录或活跃作业路径。

T23 增量：`knowledge/entries/math.linear-system-stability.*` 等5条、`agent_runtime/knowledge.py` 的context/双向related、`knowledge_index.py` 的Porter/engine_version/事务重建、`evals/knowledge/*queries.json` 与 `docs/knowledge_learning/2026-10-06-round2/`。生产者主AI与独立使用D/E/F；消费者为建模Skill、维护者与最终验收。

本轮知识学习增量：

| TASK | 实际锚点 | 生产者 → 消费者 | 用途 |
|---|---|---|---|
| MATH-11 | `knowledge/entries/math.eigenspace-gap-perturbation.*`, `docs/knowledge_learning/2026-10-07-subspace/verify.py` | 主 AI/知识维护者 → 建模 Skill/科学验收 | 谱隙、投影打分、物理模态、采样边界及近期原文审查；有限验证非模型收益 |
| MATH-12 | `docs/knowledge_learning/2026-10-07-subspace/report.md`, `tests.json`, `retrieval.json`, `publication.json` | 主 AI/现有eval与sync脚本 → 用户/下轮维护者/独立插件消费者 | 程序与结构检索验收、版本固定及main发布读回 |
| KB-ACCESS-01/02 | `workflows/knowledge_access_workflow.md`, `agent_runtime/knowledge.py::check_handoff_knowledge`, `agent_runtime/communication.py` | 主 AI/知识生产角色 → 可信消费者 | 按需工具入口、适用性记录、知识引用随通信交接校验 |
| KB-ACCESS-03 | `docs/knowledge_access_validation/`, `tests/test_knowledge_handoff.py` | 独立模型角色/程序测试 → 主 AI验收 | 真实知识使用与交接证据、拒收边界和调度读回 |


T24–T28 增量：`knowledge/entries/{ai-infra,ai-algorithms,data-structures}/`（22 张复用卡），`knowledge/engineering_sources.json`（原论文与固定源码来源），`agent_runtime/knowledge_reuse.py`（条件化决策 CLI），`workflows/engineering_knowledge_reuse_workflow.md` 与三类 Skill 引用（主 AI/建模/实现路由），`prompts/engineering_knowledge_continuous_learning.md`（有界轮转学习），`scripts/knowledge_maintenance.py` / `run_knowledge_windows.py`（WSL tmux 日历与原生 Windows 登录桥），`tests/{test_knowledge_reuse,test_knowledge_maintenance,test_knowledge_windows_runner}.py`、`evals/knowledge/engineering-queries.json`、`docs/knowledge_learning/2026-10-06-engineering/`（检查与来源）。生产者为主 AI/定时维护，消费者为主 AI、代码 Agent 与独立 Skill；私有运行状态在 `.agent-runs/engineering-kb/`，不提交登录信息、PDF 或下载的源码。

| 任务 | 实现/证据 | 生产者 → 消费者 | 用途/限制 |
|---|---|---|---|
| BASIS-01/02 | `agent_runtime/handoff_basis.py`, `agent_runtime/communication.py`, `tests/test_handoff_basis.py` | 主 AI/生产角色 → 可信消费 host | 统一知识/记忆门禁、结论 DAG、已校验交接的更正影响和预算上下文；科学适用仍独立验收 |
| BASIS-03 | `docs/communication_basis_validation/verify_upgrade.py`, `verification.json`, `report.md` | 程序/合成公开 fixture → 主 AI验收 | 冷/热上下文精确字符/字节与失效拒用；没有 tokenizer 或模型 A/B 收益 |

| EFF-01/02 | `agent_runtime/handoff_basis.py`, `tests/test_selective_context.py`, `workflows/agent_communication_workflow.md` | 主 AI/消费者可信request → Mailbox/模型host | 消费者结论依据闭包、候选/拒用保留、可选命名编码与硬限；语义适用仍独立检查 |
| EFF-03 | `docs/communication_efficiency/2026-10-07-selective/` | 公开合成fixture/实际tokenizer → 主 AI验收/下轮维护 | 同输入编码成本、包壳/无收益控制与本地pack延迟；无真实模型质量/账单收益声明 |
| ADOPT-01–04 / SYNC-01–03 | `scripts/setup_codex.py`, `tests/test_codex_setup.py`, `templates/codex_global_instructions.md`, `docs/codex_adoption/` | 主 AI/已验证发布 → 本机 Codex/后续维护 | 技能归属、字节快照、备份与目标布局冲突预检；安装成功不等于模型行为改善 |
| MATH-13/14 | `knowledge/entries/math.linear-solve-backward-error.*`, `docs/knowledge_learning/2026-10-07-conditioning/` | 主 AI知识维护 → 按需建模入口/科研工程任务 | 后向误差、逆界、排序及接地电路证书；近期低秩更新仅有限候选，未做模型A/B |
| RLP-01–03 | `scripts/knowledge_maintenance.py`, `tests/test_knowledge_maintenance.py`, `knowledge/entries/{ai-algorithms,probability}/`, `evals/knowledge/rl-probability-queries.json`, `docs/knowledge_learning/2026-10-07-rl-probability/` | 原论文/主 AI → 检索与实验前决策/已部署 WSL tmux | 每3600秒固定周期、旧状态迁移、6张2026研究卡；保留失败检索和适用边界，无本机RL复现 |

NEURO-01–03：`knowledge/entries/neuroscience/` 与 `knowledge/neuroscience_sources.json` 保存版本化研究摘要与来源层级；`evals/knowledge/neuroscience-queries.json` 是人工回归集；`docs/knowledge_learning/2026-10-07-neuroscience/` 保存研究、边界与检索验证。主AI维护→建模/研究技能按条件消费；`.agent-runs/neuroscience/` 是私有缓存、tmux验收与发布凭据。既有每小时学习任务读取更新后的priority与Prompt，不新增调度器。

| MATH-15/16，ALG-01–05 | knowledge/entries/math.*（18新主题），docs/knowledge_learning/2026-10-07-algebra/ | 主AI知识维护 → 建模Skill、科研任务与下轮维护者 | 标准代数双索引、来源版本、76项有限检查、自然检索负结果、token成本与main发布证据；非模型收益 |

2026-10-07 AIK / VEX 增量：

| TASK | 实际锚点 | 生产者 → 消费者 | 用途 |
|---|---|---|---|
| AIK-01/02 | `knowledge/entries/ai-algorithms/ai.speculative-*`, `docs/knowledge_learning/2026-10-07-ai-algorithms/` | 知识维护/独立核验 → 建模与实现角色 | 推测采样残差校正、条件接受事件与成本边界，保留新旧检索失败及有界恢复 |
| AIK-03 | `plugins/research-assistant/skills/model-with-knowledge/`, `knowledge/evaluation_holdouts.json` | 同步与发布验收 → 独立技能宿主/后续学习 | 版本语料快照及评测目标隔离；隔离元数据不是权限系统 |
| VEX-01/02 | `workflows/visual_explanation_workflow.md`, `tests/test_visual_explanation.py`, `docs/visual_explanations/` | 知识解释 → 作图 → 解释消费/审查 | 网页轻量图解、步序对应、真实图像检查与已有交接完整性验证 |
| VEX-03 | `scripts/sync_plugin_references.py` 与六个角色的生成引用 | 同步/主 AI → 分发技能与目标宿主 | 保持单包引用闭合；仓库发布与网页个人技能更新分开核验 |

项目文档新架构：唯一活跃清单位于 `doc/task/TASK.md`，根 `TASK.md` 仅跳转；逐任务方法/进度/验收位于 `doc/task/task_details/`。人类专用 `doc/guide/` 只读，建议在 `doc/advice/` 评估后按任务采用。

| TASK | 实际锚点 | 用途与边界 |
|---|---|---|
| DOC-01/02 | `agent_runtime/project_docs.py`, `scripts/project_docs.py` | 路径解析、可恢复迁移、稳定计划/可变进度、guide 依赖与应用内写入保护；不是 OS 沙箱 |
| DOC-03/04 | `workflows/project_document_workflow.md`, `tests/test_project_docs_acceptance.py`, `tests/test_project_docs_workflow.py` | 主 AI/运行时/安装/独立技能接线、对照复验和统一发布 |
| DATA-01/02/03 | `agent_runtime/result_validation.py`, `scripts/validate_experiment_result.py`, `workflows/result_validation_workflow.md`, `tests/test_result_validation.py`, `tests/test_result_gate_acceptance.py` | 每轮数据后的代码/数据版本与实际独立校验门禁；不承诺绝对无 bug 或未测性能 |
| REUSE-01/02/03 | `agent_runtime/result_store.py`, `scripts/result_store.py`, `workflows/result_reuse_workflow.md`, `doc/results/`, `tests/test_result_reuse_acceptance.py` | 新命令先查历史结果，完整条件/时效/独立校验匹配后复用；不跳过显式复现和新主张验证 |

| EK-112454-01–03 | `knowledge/entries/neuroscience/neuro.bumblebee-social-diffusion.*`, `evals/knowledge/bee-learning-queries.json`, `docs/knowledge_learning/2026-10-07-engineering-112454/` | 主AI/真实小时维护调用 → 知识检索、研究决策与下轮维护 | 3来源、1待发布复用卡，附表模型/计数限制；两步附录候选；全仓Windows回归阻塞，未推送；本机复现与AI收益未测 |

| EK-115246-01–03 | `knowledge/entries/neuroscience/neuro.cephalopod-arm-segmentation.*`, `docs/knowledge_learning/2026-10-07-engineering-115246/verify.py`, `report.md`, `sources.json` | 主AI/既有真实小时桥 → 按需检索、研究决策与下轮维护 | 4来源、1candidate/0新增published；接口许可与重复单位诊断；旧检索非退化、相关13单测与Reader3通过；补图、数据和AI迁移未验收 |

| EK-122522-01–03 | `knowledge/entries/neuroscience/neuro.salamander-cell-type-homology.*`, `docs/knowledge_learning/2026-10-07-engineering-122522/verify.py`, `report.md`, `sources.json` | 主AI/既有小时桥 → 按需检索、研究决策与下轮维护 | 5来源、1candidate/0新增published；同源/趋同和源码许可边界；7目录双后端非退化、13单测/Reader3通过；补充材料与AI迁移未验收 |

AIK-01/02：`knowledge/entries/ai-algorithms/ai.speculative-*`及`docs/knowledge_learning/2026-10-07-ai-algorithms/`提供条件化采样/成本推导与独立验证；AIK-03通过既有知识技能同步和实际Git发布核验，不新增runtime。

| MATH-17/18 | `knowledge/entries/math.matrix-bernstein-covariance.*`, `docs/knowledge_learning/2026-10-07-matrix-concentration/` | model-with-knowledge / 主AI → 按需知识与校准前提审查 | 经典矩阵界、2近期候选、有限检查/拒用；模型与真实trace收益未测 |

| MATH-19/20 | `knowledge/entries/math.centered-covariance-merge.*`, `docs/knowledge_learning/2026-10-07-centering/` | model-with-knowledge / 主AI → 中心化、分块合并、数值/统计前提审查 | 经典原页与2近期候选；有限开发检查，模型/网络收益未知 |

| MATH-21/22 | `knowledge/entries/math.dependent-mean-variance.*`, `docs/knowledge_learning/2026-10-07-dependence/` | model-with-knowledge / 主AI → 依赖校准、目标方差与拒用前提审查 | 固定n推导与2篇2026候选；模型收益未知 |

| EK-172253-01?03 | `knowledge/entries/neuroscience/neuro.spider-rem-like-state.*`, `docs/knowledge_learning/2026-10-07-engineering-172253/` | ?AI/????? ? ?????????????? | 4???1candidate/0published???????/???/???????14????????13???Reader3?SI/???/2026???AI???? |

| MATH-23/24 | `knowledge/entries/math.gaussian-quadratic-energy.*`, `docs/knowledge_learning/2026-10-07-quadratic/` | model-with-knowledge / 主AI → 二阶矩目标、谱尾/依赖条件检查 | 经典ECP最终版、2近期候选；实际模型收益未知 |

SELF-SYNC-01–03：scripts/run_knowledge_windows.py 的 prepare_host / sync_host_skills 在 verified pull 后、模型启动前同步并复查；模板维护持久入口，tests/test_knowledge_windows_runner.py 核对顺序、失败与阶段证据；docs/codex_adoption/pull-sync/ 为本轮记录。生产者为主 AI，消费者为 Codex 与原每小时维护桥；私有检查点 .agent-runs/codex-pull-sync/。
| MATH-25/26 | `knowledge/entries/math.softmax-barycenter-error.*`, `doc/results/math-softmax-20261007-v2/` | 主AI producer → 独立数学验收 → 建模Skill/维护者 | 分布/剪枝/value输出误差与有限开发验证；不含生产模型收益 |

| MATH-27/28 | `knowledge/entries/math.attention-output-geometry.*`, `doc/results/math-geometry-20261007/` | 主AI producer → 独立数学/代码数据验收 → model-with-knowledge | 固定value几何/局部余项/线性margin；无生产模型或GPU收益 |

| DUAL-01–03 | `agent_runtime/plan_review.py`, `prompts/planner_main.md`, `prompts/review_main.md`, `workflows/dual_main_workflow.md` | planner-main → 独立 review-main → protected Engine / publication → 原有独立结果 gate | 完整 DAG/身份/回执/有界返修；宿主适配器必须真实提供，CPU 测试不是模型质量收益 |

| MATH-29/30 | `knowledge/entries/math.weighted-bilinear-low-rank.*`, `doc/results/math-weighted-bilinear-20261007/` | 数学producer → 独立验收 → 按需建模Skill | SPD乘积分布的分数目标；不含真实模型/RoPE/e2e最优 |

- `doc/results/math-allocation-20261008/`: MATH-31/32 finite discrete-budget proof, exact CPU fixtures, independent review and retrieval/cost evidence; not production solver.

| MATH-33/34 | `knowledge/entries/math.finite-menu-selection.*`, `doc/results/math-selection-20261008/` | 主AI producer → 独立统计/代码验收 → 按需建模Skill | 冻结菜单选择后风险与期望成本；无真实模型或省token收益 |

| MATH-35/36 | `knowledge/entries/math.perturbation-propagation.*`, `doc/results/math-propagation-20261008/` | 主AI producer → 独立数学/代码数据验收 → 建模Skill | 有条件复合误差传播；teacher缺陷失配与有限增益拒用，无生产e2e收益 |

| MATH-37/38 | `knowledge/entries/math.sequence-tv-coupling.*`, `doc/results/math-sequence-tv-20261008/` | 主AI producer → 独立概率/代码数据验收 → 建模Skill | 有限生成分布TV与seed/greedy拒用；无模型e2e测量 |

| MATH-39/40 | `knowledge/entries/math.softmax-kl-fisher.*`, `doc/results/math-softmax-kl-20261008/` | 主AI producer → 独立数学/代码数据验收 → model-with-knowledge | KL中心化/Fisher路径曲率与饱和拒用；无生产模型收益 |
CONT-20261008-01–03: RL/SFT trajectory and horizon-aware testing cards → model-with-knowledge; existing engineering prompt obeys saved rotation cursor; scoped producer/verifier records in `doc/results/rl-probability-20261008/`; report in `docs/knowledge_learning/2026-10-08-rl-probability/`. Private canceled batch and machine service state remain `.agent-runs/` only.
