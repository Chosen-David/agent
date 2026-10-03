# Ten-paper research phase (2026-10-03)

Research preceded implementation at 4439900. New main e72e0cf adds code-reading coverage and paper-delivery contracts: these are reread before implementation; literature mechanisms remain relevant. Statements below of no repository modification/model runs refer to the research phase. Implementation and new execution results are in round.md; do not treat these notes as those results.


## 跨论文机制对照与实施取舍

| 原文 | 机制 | 成立条件 / 成本与限制 | 本轮决定 |
|---|---|---|---|
| [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/html/2308.03688v3) | 执行终态与正确性分离 | 多环境与指定历史模型；环境完成不等于任务正确 | 采用到 pipeline 状态与固定分母；不迁移历史排名 |
| [AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents](https://proceedings.neurips.cc/paper_files/paper/2024/file/877b40688e330a0e2a3fc24084208dfa-Paper-Datasets_and_Benchmarks_Track.pdf) | 子目标进度/失败归因 | 细粒度标注有成本；最高历史进度不能代替最终成功 | 采用逐项诊断；自动进度分数暂不实现 |
| [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/html/2310.06770v3) | 独立执行测试/非退化 | 真实issue与测试可验证范围；测试不涵盖所有语义 | 采用独立程序检查；模型修复成功率需另做配对实验 |
| [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/html/2405.15793v3) | 工具反馈与可观察轨迹 | ACI收益依具体模型/工具；额外轨迹有存储成本 | 采用宿主工具证据；固定last-5策略不直接照搬 |
| [AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents](https://arxiv.org/html/2406.13352v3) | 效用与过程安全分别验收 | 注入任务/工具权限设定决定可迁移性 | 空评分不能过关已实现；注入双轴任务仍为CO-009待测 |
| [τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment](https://arxiv.org/html/2506.07982v1) | 共享环境终态与必要过程约束 | 双控制模拟器和通信设定；模拟器失败不能混算模型错误 | 采用必要过程证据与真实文件交接；不声称双控制后端集成 |
| [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/html/2303.11366v4) | 外部反馈驱动有界恢复 | 反馈质量与额外预算重要；可污染后续记忆 | 保留有界新attempt和旧失败；角色反思策略CO-006待测 |
| [Self-Refine: Iterative Refinement with Self-Feedback](https://arxiv.org/html/2303.17651v2) | 具体反馈与反复改写 | 修改可能错改；成本随轮次增加 | 采用first/final分离；不以模型自评作正确性证明 |
| [Agentless: Demystifying LLM-based Software Engineering Agents](https://arxiv.org/html/2407.01489v1) | 定位→修复→验证分阶段 | 软件仓库分布限定；简单结构也需同预算基线 | 保持小型stdlib recorder；不自动增加多Agent层级 |
| [Agent Workflow Memory](https://arxiv.org/html/2409.07429v1) | 从成功轨迹归纳流程 | 错误成功标签污染；步骤指标可升而整任务下降 | CO-008待测；不自动将当前轨迹写回Skill |

组合方式：先以终态与完整分母建立可信验收，再以真实工具观察补过程约束；恢复仅追加尝试，不重写失败。与之冲突的做法是用触发率/历史最大进度代替完成、把自评当oracle或让未经验证的工作流记忆影响冻结验收。Skill加载优化必须先测实际读取与约束遗漏，不能仅凭镜像文件重复推断浪费。各篇具体证据位置、实验设置与最小判别实验见下文；论文报告不等于本仓库已验证效果。

---

# AgentBench / AgentBoard：只读论文与评测实现核查

读取日期：2026-10-03。目标仓库只读基线：`4439900212b3733936bf13f1478709b1b109cb4e`。本文件是研究中间材料，不是本库执行效果报告；没有修改目标仓库、安装外部 runtime 或执行付费模型评测。

## 1. AgentBench: Evaluating LLMs as Agents

- ID / DOI：2308.03688 / 10.48550/arXiv.2308.03688。
- 作者：Xiao Liu、Hao Yu、Hanchen Zhang 等（完整名单见 JSON）。
- 实际全文版本：[arXiv v3，2025-10-04](https://arxiv.org/html/2308.03688v3)；初稿 2023-08-07。
- 阅读范围：主文 §1–6；表 1–4；附录 A 的调度/恢复、B 的 OS 检查流程、C 的 DB 状态验收与偏差分析；J.1、J.2.1、J.2.4–6，J.2.2 的案例开头。打开图 5 框架图。其余环境的完整 prompt 示例和所有长轨迹没有逐项精读，不声称逐页全覆盖。

**论文报告。** 研究问题是多轮、交互环境中的执行能力如何评测。八类环境使用任务特定指标，模型通过观察—动作循环完成任务。§2 和附录 J 区分正常结束、格式错误、非法动作、上下文超限、步数超限；“正常结束”不代表答案正确。主文表 3 比较 29 个模型，GPT-4-0613 的 OS 成功率 42.4%、HH 78.0%，不同任务差异很大；这些历史排名不能说明今天模型优劣。表 2/§4.1 给出 dev/test 269/1014 项和估计约 3k/11k 调用，无完整统一美元成本。附录 C 用更新后数据库状态校验操作，C.4 做小批次重标注偏差检查；不是严格框架因果消融。代码训练影响来自模型比较，不能直接推成“加代码 Skill 必然提高能力”。

**实际源码。** 官方库目前 main 已转 FC 版本，因此读取论文相关 `v0.2` 分支，并固定到 `ed013ff9887b0c3d7864c56ae54d41eba54a99d8`（2026-02-08）。[`src/assigner.py`](https://github.com/THUDM/AgentBench/blob/ed013ff9887b0c3d7864c56ae54d41eba54a99d8/src/assigner.py) 调用 `run_sample`，分别写 runs/error JSONL，按 agent-task 容量调度；[`src/server/tasks/os_interaction/task.py`](https://github.com/THUDM/AgentBench/blob/ed013ff9887b0c3d7864c56ae54d41eba54a99d8/src/server/tasks/os_interaction/task.py) 先执行，再独立检查，返回 completed 与 result 两个维度。静态阅读也发现恢复只看文件/索引、可选错误重试无显式总预算；这两点不能原样复制。

**本库候选（待验证）。** 把现有 prepare 的输入隔离保留，外接 runner adapter 和独立 scorer；运行状态用 completed/timeout/infra_error，质量用 passed/failed/ungraded。第二，恢复键绑定 commit、Skill 依赖哈希、输入、模型/工具/预算和评分器版本；旧终态不得直接复用。第三，用有限重试及追加日志做中断恢复。最小实验：同一旅行或代码任务分别注入错误答案、缺输出、断线和预算耗尽，评分器必须正确区分，恢复后不能重复外部动作。当前 13 角色规模先用有界队列即可，不必搬 HTTP 集群或最大流。

## 2. AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents

- ID / DOI：2401.13178 / 10.48550/arXiv.2401.13178。
- 作者：Chang Ma、Junlei Zhang、Zhihao Zhu、Cheng Yang、Yujiu Yang、Yaohui Jin、Zhenzhong Lan、Lingpeng Kong、Junxian He。
- 实际全文：[NeurIPS 2024 官方 38 页 PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/877b40688e330a0e2a3fc24084208dfa-Paper-Datasets_and_Benchmarks_Track.pdf)。arXiv 页面记录 v2 为 2024-12-23；未把会议 PDF 假定为与 v2 字节相同。
- 阅读范围：主文 §1–7；表 1–5；附录 B、D、F、G、I、J、K 的表 14、L.9–10 与 M；N 统一模板/AlfWorld 示例。请求查看 PDF 页 7、16（从 1 计），其余 38 页没有逐页视觉验收；未逐项读完 N 的各领域长 prompt。

**论文报告。** 针对最终成功率无法解释“卡在哪一步”，把任务拆成可验证子目标或直接状态匹配，记录逐步 progress 与合法动作率。公式 2 的进度是历史最大值，不会因后续破坏产物而下降。表 3 GPT-4 平均进度 70.0%、成功率 47.9%，两者不可互换。附录 F 表 9：GPT-3.5 的 ReAct 在不同任务表现不一致；表 10 的摘要记忆也不总胜过滑窗。因此不能把“反思更多/提示更长”当可靠优化。附录 J 做三轮标注检查；附录 B 承认人工子目标劳动量与真实世界动态标签问题。附录 M 估计整套 GPT-4 5.5 小时，不能迁移为本项目预算。

**实际源码。** 固定 [`bb7255e2daf1989069a186dad9e53f70680961db`](https://github.com/hkust-nlp/AgentBoard/commit/bb7255e2daf1989069a186dad9e53f70680961db)（2024-04-23）。[`agentboard/tasks/alfworld.py`](https://github.com/hkust-nlp/AgentBoard/blob/bb7255e2daf1989069a186dad9e53f70680961db/agentboard/tasks/alfworld.py) 真正循环 agent.run→env.step→agent.update，记录轨迹；[`environment/alfworld/alfworld_env.py`](https://github.com/hkust-nlp/AgentBoard/blob/bb7255e2daf1989069a186dad9e53f70680961db/agentboard/environment/alfworld/alfworld_env.py) 用正则匹配环境观察，子目标标志只增不减；logger 保存样本/汇总。静态发现 [`eval_main.py`](https://github.com/hkust-nlp/AgentBoard/blob/bb7255e2daf1989069a186dad9e53f70680961db/agentboard/eval_main.py) 第 133–155 行只按 task_name 恢复，并重复把 hard_sr 传入 easy_sr；未经执行复现，不称已确认运行故障。官方发布代码早于会议最终论文，两者指标范围不默认完全一致。

**本库候选（待验证）。** 保留 hard-pass 终态门禁，再加“来源核对/产物生成/产物验收”过程事件定位卡点；不拿 regex 命中代替证据正确。增加“先满足午休再被新交通覆盖”“图表先正确后被改错”的回退案例，终态失败必须压过历史峰值。展示每角色成功率、进度、合法调用率、成本、缺测分母及失败轨迹。最小实验由评分者先冻结 rubric、执行者只看任务与输入，另一上下文评最终文件；比较两版同模型、工具、输入与预算。研究与写作开放任务不强制唯一操作顺序，避免惩罚同样有效的替代路径。

## 合并后的 pipeline 设计建议

1. prepare（冻结输入与 Skill 闭包）→ execute（宿主 runner adapter）→ collect（输出与工具事件）→ score（只读评分进程）→ compare（成对差异）→ report（逐角色与跨角色）。
2. 一个 case 分开记录执行退出原因、产物完整性、硬约束、内容正确性、可读性、时间/调用数；这些维度不能合成一个“通过率”后隐藏失败。
3. 对 prepare_agent_eval.py 的只读核查确认它仅复制 Skill/fixtures/prompt、创建 outputs，没有模型运行或打分。应新增明确接口，避免把 prepare 成功叫执行成功。
4. 跨角色交接案例必须读取真实上一阶段产物。修改输入或 Skill 后按依赖图局部失效；缓存须验证评分器版本与产物哈希。AgentBoard/AgentBench 的历史恢复实现是反例，不照搬。
5. 对评分器先用人工构造的正负/回退产物检查，再跑真实模型。缺可执行宿主 adapter 的项目记 blocked；评分未运行记 ungraded；不得转成通过。

所有候选均未在 Chosen-David/agent 上验证，当前决定是进入 pipeline 设计候选，不主张性能已提升。



---

# 代码类论文与评测实现只读研究

读取日期：2026-10-03。仅调研与设计；未执行上游 benchmark、未修改或发布 Chosen-David/agent。下述效果数字均属论文；本库效果尚未测量。实际读取原始全文 HTML 的核心章节和下列关键附录，并非仅摘要；不声称逐页完整视觉审读。

## 1. SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

Carlos E. Jimenez、John Yang、Alexander Wettig、Shunyu Yao、Kexin Pei、Ofir Press、Karthik Narasimhan。[原文 v3，2024-11-11](https://arxiv.org/html/2310.06770v3)。研究问题是模型能否在真实仓库快照上修复 issue，而非只生成独立函数。方法将参考修改拆成实现补丁和测试补丁，先证明基线失败、参考修复成功，再用失败转通过与原有通过测试共同验收。实验来自 12 个 Python 仓库、2,294 个任务；v3 表 5 的 BM25+Claude 3 Opus 为 3.79%。表 2—3 的上下文对照显示更多检索内容不必然更有效；Oracle 设置用到了参考答案文件位置，不能当真实部署条件。附录 A.3—A.4 明确缺失测试不是通过；C.5 区分修复后回归与真正解决。成本上，§2.4 引入 300 题 Lite 降低负担；附录 C.3 的部分 GPT-4 实验仅覆盖 25% 子集。§7 承认测试通过不能保证全面性、效率与可读性。

**本库适配推断：** 对 `research-implement-optimize` 的首选改进是把现有“先复现、再修复”的文字流程接到可执行裁判。每题固定源码 SHA、公开输入及独立裁判包；agent 在干净副本提交补丁，裁判在另一个副本从相同 SHA 重建，只导入允许路径的实现补丁，再加载裁判测试。开发中写的新测试可以保留为产物，但不能由 agent 自己更改最终分母。对 `code-reading` 则不要求修复：交付入口到输出的调用链、默认/可选分支、可复核行号；独立检查反例配置与代码实际分支是否一致。任务需要包含名字相似但不被调用的函数，防止只凭检索命中得分。

**最小判别实验：** 冻结 8 个跨文件任务，含正常修复、只修示例、删测试、伪造通过输出、异常退出、缺依赖等；同模型工具预算分别跑旧/候选 skill。主要指标为隔离裁判全通过率，附报误接受率与环境失败率；不因缺依赖删分母。成本低至中；暂列候选，优先实现评测隔离而非引入整个 SWE-bench runtime。

证据阅读范围：§§2—5、7；表 1—8、18—23；附录 A.2—A.4、B.1、C.1—C.5；图 1、2、8 的流程说明；§5.1 具体失败案例。本文未复核每一张附录图片。

## 2. SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering

John Yang、Carlos E. Jimenez、Alexander Wettig、Kilian Lieret、Shunyu Yao、Karthik Narasimhan、Ofir Press。[原文 v3，2024-11-11](https://arxiv.org/html/2405.15793v3)。研究固定模型下，搜索、查看、编辑与反馈接口如何影响任务完成。ACI 合并常用操作，编辑后显示当前内容并对新增语法错误反馈；原实验压缩旧观察。表 1：GPT-4 Turbo 全集解决率 12.47%，Lite 18%，同表 shell-only Lite 为 11%；每题预算上限 4 美元，成功任务平均成本不是所有尝试总成本。表 3 的编辑器及 lint 消融为 10.3%、15%、18%；参数选择在 37 个开发实例上进行。附录 B.5 的六次运行揭示单题结果会变化；D 的通过案例仍可能存在测试未覆盖差异。范围局限于程序任务，不能外推旅行或论文写作效果。

**本库适配推断：** 最值得先借的是运行轨迹与工具反馈的结构化记录，而非重写宿主工具。当前 `code-reading` 已有固定 SHA 的 `source_evidence.py`，实现角色已有复现要求，可在轻量 pipeline 中记录 `task_id/run_id/attempt_id`、工具名、参数、实际退出码、耗时、输出摘要和完整日志引用、输入/输出哈希。只保存可见执行事件与简短决策摘要，不要求隐藏推理。失败后复跑沿用任务 ID、产生新 attempt，禁止覆盖初次失败。只读角色继续禁止修改目标；实现角色交付 patch 加复现日志，路由器不因 agent 自报完成而跳过裁判。

**最小判别实验：** 同一 6 题保留输入，各重复 3 次，比较旧版反馈与候选结构化反馈；控制模型、工具权限、步数和预算。关注最终正确率、首次失败后恢复率、无效重复命令数、token/时间成本。另做离线 action replay 来诊断工具行为，但它不重新调用模型，不能计入模型成功率样本。现代宿主已有可靠编辑器时，额外包装可能增加成本，所以编辑器重建暂拒绝；轨迹与失败归因进入优先候选。

证据阅读范围：§§2—5、7；表 1—3、5、9—10、13；附录 A.2—A.3、B.1、B.3—B.5、B.7—B.9、C、D 的案例文字、E.1—E.3；图 5、6 原始界面图已打开，其余涉及图的结论以正文与表格为依据。

## 3. 官方代码核查（当前实现不等于论文实验版本）

固定读取以下官方 SHA，未安装或运行其 runtime。

| 仓库与 SHA | 实际读取文件与发现 | 本库取舍 |
|---|---|---|
| [SWE-bench `02e7a74`](https://github.com/SWE-bench/SWE-bench/tree/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e) | [run_evaluation.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/run_evaluation.py)：独立实例容器、补丁、超时、原始输出、report；metadata 记录数据集与任务库。 | 借分层与指纹，不抄其 `SYS_ADMIN` 权限；本库先用受宿主限制的独立副本，无法强隔离时如实标注。 |
| 同上 | [grading.py](https://github.com/SWE-bench/SWE-bench/blob/02e7a74ffd0b707aab73d203fe87bdc7c76afc8e/swebench/harness/grading.py)：核对实跑迹象、测试退出码；环境错误保持 unresolved。但当前 P2P skipped 可算 maintained，XFAIL 可算 passed，空 F2P 分母返回 1。 | 本库必需检查用更严格合同：缺失/skip/未运行均不得通过；不能原样搬评分语义。 |
| [SWE-agent `3ea751c`](https://github.com/SWE-agent/SWE-agent/tree/3ea751c087f32b16e039a2233dd6eefecef325d5) | [agents.py](https://github.com/SWE-agent/SWE-agent/blob/3ea751c087f32b16e039a2233dd6eefecef325d5/sweagent/agent/agents.py)：每步轨迹与最终 patch 分开记录；[run_replay.py](https://github.com/SWE-agent/SWE-agent/blob/3ea751c087f32b16e039a2233dd6eefecef325d5/sweagent/run/run_replay.py) 将历史动作交 ReplayModel 执行。 | 借事件记录与确定动作重放；明确 replay 只是工具/环境回归，不是新模型评测。 |
| 同上 | [07.yaml](https://github.com/SWE-agent/SWE-agent/blob/3ea751c087f32b16e039a2233dd6eefecef325d5/config/sweagent_0_7/07.yaml)、[edit 配置](https://github.com/SWE-agent/SWE-agent/blob/3ea751c087f32b16e039a2233dd6eefecef325d5/tools/windowed_edit_linting/config.yaml)、[edit 实现](https://github.com/SWE-agent/SWE-agent/blob/3ea751c087f32b16e039a2233dd6eefecef325d5/tools/windowed_edit_linting/bin/edit)、[flake8_utils.py](https://github.com/SWE-agent/SWE-agent/blob/3ea751c087f32b16e039a2233dd6eefecef325d5/tools/windowed/lib/flake8_utils.py) 与 windowed_file.py：工具文档、实现、undo 相联。 | 此项目不是 SKILL.md 体系，真实对应物为配置+工具实现；不虚构有对应 skill。只对新增语法错误判定的思想可借，但本库无需复制完整窗口编辑器。 |
| 同上 | [history_processors.py](https://github.com/SWE-agent/SWE-agent/blob/3ea751c087f32b16e039a2233dd6eefecef325d5/sweagent/agent/history_processors.py) 明示 last-N 会影响 prompt caching，现代模型未必需要；保留标签支持例外。 | 拒绝直接固定 last-5；先量测本宿主上下文成本与证据遗失率。 |

## 4. 轻量 pipeline 的代码角色合同建议（尚未实现）

- **输入与隔离：** manifest 指向固定源码 SHA、技能文件哈希、公开任务和外部裁判 ID。执行器只收到公开任务；最终答案和裁判测试由另一个上下文/目录持有。目录分离只是防误读，若同一 shell 能访问两者，不能宣称安全隔离。
- **失败复现：** buggy baseline 必须触发预期业务失败，而非 import error；reference patch 必须解决它且不引入回归。环境预检失败标 `blocked_environment`；不能把它当“没有 bug”。
- **补丁验收：** 新干净副本应用 agent patch；拒绝裁判/runner/清单修改；裁判在执行后注入测试并运行。对恶意补丁的隔离需要宿主 sandbox/container，普通 venv 不提供安全边界。正常测试与隐藏测试都保留完整 stdout/stderr、退出码、测试身份和已执行数。
- **代码阅读验收：** 输出 `claims.json`，每条含 commit、path、symbol、range、claim、condition、source_fact/static_inference/runtime_evidence。裁判核对随机抽取的符号和反例配置，检查调用链是否闭合、未知是否明确；文本存在与行号有效只是结构检查，不能冒充语义正确率。
- **重放：** 先支持裁判重放（固定 patch+fixture+environment）及动作重放（固定可见工具调用）；恢复必须校验输入/技能/工具版本指纹，不复用失效输出。真实 agent 重跑单独记录新的模型采样。
- **对照：** baseline/candidate 同模型、输入、工具、预算；至少报告题级配对结果、重复次数、失败、缺测、耗时及总调用量。API 费用未知时填 null；不能填零。初期小样本给描述性结果，不宣称普遍提升。

本轮本地直接联网失败，已改用可用的官方 GitHub 连接读取文本；未因此降低研究范围。首次误定位 flake8_utils.py 后通过仓库树找到并阅读正确依赖。以上均为研究与设计记录，没有上游安装、账户写入或用户仓库修改。


---

# 安全、状态与交互评测：两篇原始论文及实现核对

阅读日期：2026-10-03。范围：只读研究与 pipeline 设计；未安装上游 runtime、未执行攻击、未修改用户仓库。以下迁移建议均为**本库仅设计、未验证**。论文版本与当前源码 commit 分别固定，不能把当前源码视为论文实验时的同一版本。

## AgentDojo — arXiv:2406.13352v3

[原文](https://arxiv.org/html/2406.13352v3)，2024-11-24，Edoardo Debenedetti、Jie Zhang、Mislav Balunovic、Luca Beurer-Kellner、Marc Fischer、Florian Tramèr。已读正文 §1–5、附录 A 的任务/管线接口、C 的完整结果、D 的成本与攻击位置分析；核对 PDF 第9页图9、第20页表3–5。未逐段阅读数据卡 F，也未执行论文实验。

**研究问题与机制。** 正常任务完成率不能说明遇到网页、文档等不可信内容时仍可靠。§3 将用户任务、攻击目标、可变环境和工具分开，用执行前后状态与输出检查两种目标；§3.4 分别报告正常效用、攻击下效用、攻击目标成功率，避免“全部拒绝”冒充安全且有用。§4 覆盖97项用户任务及629项安全组合；表5显示检测器虽降低攻击成功，却明显损伤正常效用。工具过滤也不是通用答案：正常任务本身所需工具可能足以完成攻击，选择结果也可能被污染。表2消融和图8表明攻击措辞与先验知识影响结果，单一注入模板不足以证明鲁棒。附录D的35美元/629例、4美元/97例是当时GPT-4o成本，不能当作本轮报价。原文§4.3“7.5%”与表5“6.84%”不同，不混用。

**源码与本库对照。** 固定 [089ed468](https://github.com/ethz-spylab/agentdojo/tree/089ed468cf3ed0322acc66b0211f26d9d90dbf60)：`base_tasks.py` 把 `utility` 与 `security` 分开，后者 True 实际表示攻击成功；另有 `*_from_traces`，可检查不留终态痕迹的动作。`task_suite/task_suite.py::run_task_with_pipeline` 深拷贝初态、真正调用管线再判定；`default_suites/v1/travel/user_tasks.py::UserTask0` 同时检查预订日期、目标及额外副作用。当前任务检查不是可直接照搬的答案匹配器。

**适配候选。** 在本库 `scripts/prepare_agent_eval.py` 的执行后阶段增加独立评分：成果正确、硬约束、禁止副作用分别列项；旅行与代码阅读各做干净/污染来源配对任务，保留同一事实只改变不可信指令，真实跑宿主角色，核对最终产物和工具轨迹。预计可识别过度拒绝与暗中越界，成本是小型状态夹具和隔离评分器。最小实验固定模型/预算，各3组保留输入，与现有入口配对；任一禁止副作用失败即不发布。不能从论文攻击率推断本库安全，也不能把通过固定攻击集称为安全保证。

## τ²-bench — arXiv:2506.07982v1

[原文](https://arxiv.org/html/2506.07982v1)，2025-06-09，Victor Barres、Honghua Dong、Soham Ray、Xujie Si、Karthik Narasimhan。已读正文 §1–5、附录 A 任务/轨迹实例、B 验证过程、E 全部模拟器故障；核对 PDF 第8页图4/5、第10页表2。附录 C/D 按接口与工作流对比所需定位，未声称逐条读完全部业务政策。

**研究问题与机制。** 用户也能改变世界状态时，单主体测试会漏掉沟通与协作失败。§3 用共享状态、两侧工具和可见性约束模拟协作；任务由初始化、解法、断言组成，组合后先验证可解性。§3.3把终态、沟通、动作与自然语言断言区分，telecom主实验仅使用状态断言。§4.1四次重复、温度0、固定GPT-4.1用户模拟器；图4中GPT-4.1由no-user 0.52降至default 0.34，给oracle-plan为0.73，说明应把协调故障与求解故障分开诊断。更长流程文档并非总有益，oracle设置反而下降。表2数据及正文显示telecom 3/50=6%关键模拟器错误，表注“没有关键错误”与之冲突；不沿用表注。附录E列出提前结束、漏约束等错误。论文一次全域约40美元仅是历史设置。

**源码与本库对照。** 固定 [5bfa7e37](https://github.com/sierra-research/tau2-bench/tree/5bfa7e37b36656b37dc6d022156be6563c1007f3)：`runner/simulation.py` 实跑orchestrator后调evaluator；`evaluator_env.py` 由轨迹重放状态、对照gold环境并逐项执行断言；`evaluator.py` 按reward_basis聚合。需拒绝照搬其“无验收条件返回1”和`checkpoint.py`自动恢复时接受配置变化、排除policy的选择；本库要求缺测不算通过且版本可追溯。

**适配候选。** 第一，给13角色统一 `task→isolated execution→artifact/trace→independent grader` 外壳，空验收判invalid；每次保存技能、输入、评分器、模型配置hash，变更不得复用旧成功。第二，旅行改约与科研反馈各做固定脚本用户和有界LLM用户两层，单列simulator_error；失败后用无用户/已知计划诊断，不能用诊断分数代替原任务结果。最小实验用2个新组合任务×4次配对，报告每次成功及成本，保留模拟器错误与无效分母。跨主体差异不自动等于因果证明；客服模拟得分、专家新手差距及严格科研判断不可直接迁移。本库仅设计、未验证。

## 固定源码阅读清单

两个官方树中均未发现 `SKILL.md`；它们提供测试框架和接口，不能称为已接入的Skill。另实际读取本库 `AGENTS.md`、`prompts/decision_review.md`、`config/role_registry.json`、`travel-planner/SKILL.md`、`code-reading/SKILL.md`，确认13角色及只读/不自动预订边界。

| 官方仓库及commit | 实际读取文件 | 用途 |
|---|---|---|
| AgentDojo `089ed468cf3ed0322acc66b0211f26d9d90dbf60` | `src/agentdojo/base_tasks.py`；`src/agentdojo/task_suite/task_suite.py`；`src/agentdojo/benchmark.py`；`src/agentdojo/default_suites/v1/travel/user_tasks.py`（重点UserTask0/1） | 状态与轨迹双检查、独立效用/攻击结果、真实任务及副作用 |
| τ² `5bfa7e37b36656b37dc6d022156be6563c1007f3` | `src/tau2/evaluator/evaluator.py`；`evaluator_env.py`；`src/tau2/runner/simulation.py`；`runner/checkpoint.py`（恢复兼容性部分）；`src/tau2/run.py`（run_task）；`src/tau2/domains/telecom/tasks/create_tasks.py` | 分离执行与评分、重放和断言、任务抽样、版本恢复边界 |

其他下载的action/communicate/metrics/data-model/batch文件只作定位，未计入上述精读清单。源码仅作阅读，没有导入或执行。


---

# 反馈迭代论文精读与 Pipeline 候选

研究日期：2026-10-03。只读仓库基线：`4439900212b3733936bf13f1478709b1b109cb4e`。本文是研究与设计证据，不是模型任务运行结果；未安装第三方 runtime，未修改或发布仓库。

## 1. Reflexion: Language Agents with Verbal Reinforcement Learning

原文：[arXiv:2303.11366v4](https://arxiv.org/html/2303.11366v4)，2023-10-10；Noah Shinn、Federico Cassano、Edward Berman、Ashwin Gopinath、Karthik Narasimhan、Shunyu Yao。实际阅读正文§1–8、算法1、图2–4、表1–5、附录A、B、C及D的错误反馈示例与提示。打开PDF并请求第6页截图核查图4。没有把参考文献列表视为已精读其引用论文。

论文研究不更新权重时，如何利用一次失败帮助下一次执行。Actor生成行动，Evaluator给出成功/失败或测试结果，反思模块将轨迹与反馈压缩为可用于下次尝试的建议；记忆通常只向模型提供最近1–3条。它不是靠“再想一想”自动获得真值：HotpotQA的反馈来自答案精确匹配，编程反馈来自生成测试的实际执行，ALFWorld有环境成功信号与卡住检测。§4.1在134个环境、多达12次尝试上报告130个完成；不能与一次调用的成功率等同。表1 HumanEval Python为80.1→91.0%，但MBPP Python为80.1→77.1%；表2将误接收错误程序与不可靠自生测试联系起来。表3在50道困难Rust题上，完整机制60→68%，仅反思而无测试降到52%，有测试无反思为60%。附录B.1的WebShop四轮无明显改善，附录A较弱模型也无收益。因而可迁移的是“有来源的失败反馈＋小范围修订”，不能迁移其绝对收益或无限反思有效的结论。额外试次、反思和更长上下文有成本；论文未提供跨任务统一token/延迟预算下的胜率。

源码固定至 [`218cf0ef1df84b05ce379dd4a8e47f17766733a0`](https://github.com/noahshinn/reflexion/commit/218cf0ef1df84b05ce379dd4a8e47f17766733a0)。实读 `programming_runs/reflexion.py`、`programming_runs/executors/py_executor.py`、`alfworld_runs/main.py`、`alfworld_runs/generate_reflections.py`：编程循环保留实现、反馈及反思，内部测试触发修订，最终测试评分单独调用；环境记忆写回JSON，但给反思的上下文截断到最近3条。算法1写成“未通过 OR 未达上限”，不能直接照抄为停止逻辑；实际代码使用有界循环。Python执行器使用进程内exec，不能原样当安全执行沙箱。

候选R1：让所有角色的修复记录绑定失败证据、产物hash、输入修订号及允许修改范围，保留最后一次验收通过的产物；预期减少重复失败与错改，成本为共享记录结构和角色适配。先以相同模型/输入/调用预算比较“仅重试”“结构化反馈修复”，用独立终态验收计修复率及正确→错误率。拒绝默认给13个角色全部增加多轮反思：上文负结果不支持这种做法。

## 2. Self-Refine: Iterative Refinement with Self-Feedback

原文：[arXiv:2303.17651v2](https://arxiv.org/html/2303.17651v2)，2023-05-25；Aman Madaan等16位作者，完整名单见配套JSON。实际阅读正文§1–6、算法1、图1–5、表1–2，附录A/C/D/G/H/J/N/O/S相关内容，重点核查反馈消融、数学oracle、偏好评分和代码优化。PDF共54页，不声称逐页视觉审读；请求第6页截图核查分析图表。

同一个模型先生成初稿，再按任务维度给具体反馈，随后结合反馈修订；§2允许按反馈或轮数停止，§3最多4轮。这里的内部自评是修改建议，不是外部正确性证明。七类任务使用GPT-3.5、ChatGPT、GPT-4等，既有运行指标，也有人类盲评/GPT-4偏好分，不能把不同指标平均值解释为真实Agent成功率。表1中GPT-4代码优化比例27.3→36.0%，数学92.9→93.1%；表2具体反馈优于泛泛要求，图4显示边际收益递减。附录H指出多维品质可能非单调，修订可引入新问题；oracle反馈改善数学，不能当部署时可得信息。§4的70例定性分析将大部分失败归于错误反馈，而非修订未执行；Vicuna-13B不能稳定反馈/遵循修订。§6还限定英语与闭源模型，因此不能直接外推到中文旅行和论文生产。每轮新增反馈与修订调用，历史增长增加token；论文未证明等token预算普遍优于重采样。

源码固定至 [`9a206d41e5d2d0c241bb441f41eeadb945afaa55`](https://github.com/madaan/self-refine/commit/9a206d41e5d2d0c241bb441f41eeadb945afaa55)。实读 `src/pie/run.py`、`feedback.py`、`src/acronym/run.py`、`src/gsm/gsm_selfref_eval.py`、`src/utils.py`、`docs/pie_eval.md`。PIE以模型声称代码不慢的字符串提前停止；批处理会吞异常，不能照搬。GSM评分一旦某轮正确，就把后续轮都记正确，是累计oracle视角，不是每轮最终输出准确率。acronym的条件是分数非负而不是胜过best，不能仅凭变量名声称保留最好版本。

候选S1：将反馈来源分成程序/外部事实/独立审阅/同模型自评；仅前三者合格证据可支持硬约束通过，自评只支持修改提案。候选S2：保留first/final/best-by-development-check三版及每步评分；隐藏验收只在最终运行后评分，不反馈给执行者。预期避免错把累计最好成绩当交付能力，适配成本低于引入新runtime。拒绝用自评分选优后再用同一自评分证明进步；先做配对、盲序、固定预算的模型任务对照。

## 3. 对当前仓库的具体对照

已读实际 `config/role_registry.json`（13角色）、`AGENTS.md`、`prompts/decision_review.md`、持续优化状态，以及 implement/write/travel 三个 `SKILL.md` 和 `references/execution.md`。现有规范已经要求基线、硬约束、证据、预算、回退和反思；继续堆叠同义Prompt价值有限。应把这些要求接到运行记录、独立评分和恢复状态上。当前 `state.json` 明确此前未做角色质量A/B，故本报告只提出待验证方案。

拟增共享运行层（路径为设计候选，尚未创建）：`evals/pipeline/runner.py`、`feedback.py`、`metrics.py`；13个Skill继续由registry加载角色相关契约与验收，不复制三套迭代控制Prompt。建议反馈最小字段为 `case_id, attempt_id, input_revision, artifact_hash, source_kind, checker_version, observed_failure, allowed_repair_scope, evidence_refs`。这是我们的适配设计，不是两篇论文已有的schema。

| 角色 | 反馈依据与最终检查 | 失败恢复限制 |
|---|---|---|
| research-assistant | 依赖、输入版本、真实产物及任务终态 | 只重跑失效节点，不能把skip算验收 |
| research-explore | 原文证据、替代解释、可判别实验 | 不靠新增“创新”形容词提高分数 |
| research-implement-optimize | 独立reference、真实测试、实际计时 | 正确性先于速度；无GPU明确缺测 |
| research-figures | 数据与结构输入、合成整图视觉检查 | 修改版重新渲染，防文字反馈脱离实际图 |
| research-write | claim→evidence与稿件渲染 | 文风反馈不能扩大科学结论 |
| research-review | finding的源位置与反证 | 可撤销误报，不能要求原稿迎合审阅者 |
| research-read-pdf | 逐页渲染与定位记录 | 渲染器故障单列，不当内容缺陷 |
| paper-reading-companion | 原页锚点、段落与阅读状态 | 新版本使相关解释失效 |
| explain-research-concepts | 权威事实与可检查推导 | 反馈表达清晰度不等于数学正确 |
| travel-planner | 服务窗口、午休、通勤、报价单位、事实日期 | 改交通重算关联节点，保留预约与必选项目 |
| research-data-visualization | 数据数值、单位、统计口径与实际图 | 布局修复不得改变数值/误差定义 |
| research-diagrams | 节点/边/图例与实际渲染 | 美观改进不得引入未给定机制 |
| code-reading | 入口→调用→数据→输出的源码锚点 | 新commit触发相关证据复核，不凭函数名推断 |

## 4. 最小判别实验与停止设计

先固定开发反馈集和执行者不可见的保留验收集。三臂使用同一模型版本、工具、任务和总调用/token/时间预算：A当前流程，B同预算直接重试，C证据驱动修复；保留first输出，报告最终通过率、错误→正确、正确→错误、未执行/超时数、token、wall-clock和外部调用数。单个代表任务只能查链路可用，不能估计某角色通用成功率；每角色至少纳入正常、边界、恢复、对抗任务后再逐步扩大。

停止须由控制器决定：预算耗尽、必要资源缺失、同一失败签名连续出现且无新证据、硬约束冲突或验收通过即退出；实验可先设最多2次修复（属于待验证默认，不冒充论文最优）。同模型说“足够好了”仅终止自评建议环节，不能把任务标passed。异常/缺测计入固定任务分母并单列原因，不删行。保留集的结果不作为该次修复反馈；若用于开发，则将该输入移出保留集。

负对照：已正确答案＋错误审阅意见；模拟测试全绿但保留输入失败；反馈要求删午休/换指定店；图表视觉变美但数值变化；已过期source hash；空反馈/畸形JSON；重复动作；模型自称已完成而产物缺失。候选必须在独立终态评分上有证据并保持硬约束非退化，才进入实施/发布阶段。

证据边界：上游代码仅静态阅读，上述风险未对上游运行复现；未运行付费模型、没有本仓库效果数字。git clone遇到宿主网络代理不可用后改用已连接GitHub只读接口，不绕过权限。


---

# Agent 组织与可验证 pipeline：两篇精读记录

日期：2026-10-03。只读研究；没有安装或运行外部 runtime，没有修改目标仓库。现有仓库阅读基线 `4439900212b3733936bf13f1478709b1b109cb4e`。备选题名 AgentSCoRE 未核实；候选 ID 2502.09376 实际为 LoRA 理论论文，因此替换为 Agent Workflow Memory（不是把错误 ID 计为完成）。

## 1. Agentless: Demystifying LLM-based Software Engineering Agents

Xia、Deng、Dunn、Zhang；arXiv:2407.01489v1，2024-07-01。[原文](https://arxiv.org/html/2407.01489v1)。阅读正文 §1–7、表1–4、图1–6的对应说明；另查看 PDF 第3页图1、第10页表4；v1没有独立附录。

**论文报告。** 研究问题是复杂自主规划是否为代码修复的必要条件。§2用“目录→类/函数骨架→编辑位置”逐级收缩上下文，再生成、语法/回归过滤和重排补丁；并非增设更多角色。§3实验为300题 SWE-bench Lite、GPT-4o-2024-05-13，每题42个候选。表1报告82/300、均价0.34美元；这是当时模型和计价，不能当本库预算。表2显示压缩上下文同时损失正确定位覆盖。表3单候选70题、多候选78题、加测试82题，说明应分别测定位、候选生成和筛选，不能只看最终总分。§5识别缺信息和含答案任务，表4另报252题过滤集；公平评测要预先分类并保留原始全量结果。

**源码核对。** 官方仓库固定 `5ce5888b9f149beaace393957a55ea8ee46c9f71`，晚于v1且README已描述三阶段实现，不能把当前代码等同v1实验。`agentless/fl/localize.py`保存每阶段定位及轨迹，`--start_file`可续跑；`compress_file.py:get_skeleton`通过LibCST省略函数体，解析失败退回原文；`rerank.py:majority_voting`存在复现测试全失败后退回回归候选、甚至最终对所有补丁投票的路径。这是生成候选策略，绝不能迁移为本库“失败也可发布”的验收规则。

**本库推断与候选。** 现有code-reading已经要求入口到输出闭环，无需重复增加读码角色。建议在`evals/`拟议模型pipeline增加定位产物阶段：固定SHA、候选文件、已读函数、未闭合调用、输入token，后续角色只按需展开，成本中等。最小实验用未见过的多文件/动态分发任务，比较现有读取与分层读取的终态正确率、主张证据覆盖和token；保留“找错文件但自信输出”对抗项。另以单角色固定流程作为多角色路由的同预算基线；若独立评审没有减少错误，不增加常驻角色。均为待测设计，不能由论文排名推出本库收益。

## 2. Agent Workflow Memory（AWM）

Zora Zhiruo Wang、Jiayuan Mao、Daniel Fried、Graham Neubig；arXiv:2409.07429v1，2024-09-11。[原文](https://arxiv.org/html/2409.07429v1)。阅读正文 §1–7、表1–11、附录A–C；查看PDF第3页图2/3、第10页表9/图7。图表与正文冲突已保留。

**论文报告。** §2把成功轨迹抽成参数化子流程，作为上下文建议，支持离线或在线归纳。WebArena用GPT-4-0613，表1任务成功率35.5%；Mind2Web表3分别报告步骤与整任务指标，二者不能混用。最值得借鉴的是负结果：表9宏动作版本步骤成功率提高，整任务却由4.8降到3.6；正文误写“相同3.2”，PDF亦矛盾，故不用该句主张收益。图7显示机场输入后的候选弹窗需重新观察，固定宏不能盲走。附录C表11也不支持离线与在线记忆直接相加必然更好；§3.2指出误判成功可污染记忆。步数减少不等于token、金额、延迟都减少；文中不足以给本库成本承诺。

**源码核对。** 官方commit `8c0ff8cd11d648c8fceb99e4e42f37e3b75381b1`。`webarena/pipeline.py`串行执行推理、评价、归纳，只有`Popen.wait()`而不检查返回码；`induce_prompt.py`依据auto-eval记录筛选并覆盖workflow文件，日志解析含`eval`。`prompt/instruction.txt`要求子程序去重和变量化，但也保留假定不变的页面ID。`agents/legacy/agent.py:get_action`先裁剪主prompt再附加workflow；`mind2web/memory.py`另外检查总token，并使用历史gold actions做离线逐步评价。因此不能把其Mind2Web分数当真实自由运行成功率，也不能照搬日志解析、原地覆盖或页面ID假设。

**本库推断与候选。** 将13个skill组织成“稳定职责入口＋可选小型流程卡＋工具适配”，从独立终态验收通过的训练轨迹提取流程，卡片写适用前提、参数、观察点、失效条件、来源run；先进入候选目录，经保留任务后才启用。最小实验固定skill版本、模型、工具和总预算，对比无流程卡/经筛选流程卡；按任务模板划分训练与测试，至少测错误成功标签、旧输入、工具接口改变三类污染。pipeline需按阶段return code和产物hash阻断，不允许验收失败仍更新记忆。收益假设是减少重复步骤和提示词重复，成本中等，当前决定待测。禁止从“用过该卡”直接计成功，也不将抽取的工作流扩大为新权限。

## 适合本库的设计原则（研究者建议，尚未实测）

1. `prepare_agent_eval.py`目前只准备隔离输入，继续保持这个职责；新增runner、observer、grader、aggregator作为不同接口，不能把准备输入称为跑过Agent。
2. executor只见任务、技能快照及公开输入；grader可见封存验收条件和实际产物。共同记录`task_id / attempt_id / code_sha / skill_digest / input_digest / model / budget / tool_schema_digest`。
3. 所有角色均有代表任务；受影响角色做配对A/B，多角色组合另有终态测试。报告失败、基础设施错误、超时、缺测，不合并为一个success数字。
4. 冻结回归集内禁止边测边修改skill/记忆；在线学习另设按时间顺序的实验，固定顺序和重置点，不能与冻结集比较混称。
5. workflow候选合并需检查语义重叠、前置条件与总token；错误和负例可以进入诊断记录，未经验收的成功轨迹不能成为执行建议。

## Additional implementation sources (read 2026-10-03)

- Inspect AI commit `93f7182cf2ce9be22724b05e499cd1358d7ed41d`: actually read [`src/inspect_ai/_eval/task/task.py`](https://github.com/UKGovernmentBEIS/inspect_ai/blob/93f7182cf2ce9be22724b05e499cd1358d7ed41d/src/inspect_ai/_eval/task/task.py), `_eval/evalset.py`, `scorer/_scorer.py`, and official [eval-set](https://inspect.aisi.org.uk/eval-sets.html)/[scorer](https://inspect.aisi.org.uk/scorers.html) documentation. Adopt task/execution/scoring separation and bounded retries; preserve failure records rather than following retry cleanup defaults. Bind source, inputs, rubric and runner bytes in addition to configuration identity. No Inspect runtime installed.
- Anthropic skills commit `8a1541c4a3ffa5a20a5a91de0dcf3f0bab1d1ef4`: actually read [`skills/skill-creator/SKILL.md`](https://github.com/anthropics/skills/blob/8a1541c4a3ffa5a20a5a91de0dcf3f0bab1d1ef4/skills/skill-creator/SKILL.md), its `scripts/run_eval.py`, `scripts/aggregate_benchmark.py`, `agents/grader.md`, and `agents/comparator.md`. Borrow independent direct artifact review and matched-version comparison as a future experiment. Reject skipping missing grades, treating trigger activation as task success, characters as tokens, and forced winners. No external skill package installed or copied.

These sources motivate the mechanism; the round's program and host-task evidence, not upstream popularity or benchmark ranking, determine acceptance. The implemented snapshot uses an explicit dependency allowlist rather than claiming a full transitive resolver; host invocation remains outside the portable Python recorder.
