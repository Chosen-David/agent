# 可检索基础知识

这里保存跨项目可复用的数学、物理、AI Infra、AI 算法、数据结构算法与跨物种神经科学知识；Skill 保存使用知识的方法。项目观测、用户偏好和执行状态仍由项目记忆、TASK.md 与运行目录负责。

当前包含 84 个已发布条目，另有3个待核验candidate：43 个数学/物理基础条目（包括18个本轮高等代数主题）、22 张工程复用卡、2条AI算法推导知识，以及 6 张 2026 年 RL / 概率论研究卡（ICLR、ICML、COLT、ALT），以及11张神经科学/NeuroAI卡（10篇正式论文、1篇明确绑定的2024预印本）。近五年检索窗口为2021-10-07至2026-10-07，本轮所选来源为2023–2026；最新核查论文发表于2026-09-29。机构/作者博客单列来源，生物发现、意识理论与AI设计假设分开记录。新增卡核查原论文的相关实验、定理前提与反例，未执行本机论文复现，不代表完整学科覆盖或 Agent 整体性能提升。条目是本项目撰写的知识摘要与应用推导，不镜像第三方教材或 mathlib。上游来源与采用理由见 `upstreams.json` 和仓库 `docs/knowledge_upstreams.md`。

## 实际使用

从仓库根运行（Python 3.10+，标准库）：

```bash
python -m agent_runtime.knowledge --root knowledge validate
python -m agent_runtime.knowledge --root knowledge search '压缩 向量 点积 排名 翻转' --limit 3
python -m agent_runtime.knowledge --root knowledge show math.topk-margin
python -m agent_runtime.knowledge --root knowledge related math.topk-margin
```

独立安装 `model-with-knowledge` 后，在 Skill 目录用 `python scripts/knowledge.py --root assets/knowledge ...`，无需克隆仓库或联网。维护后的安装快照需要重新同步/更新；不能假设旧安装实时获得 main 的知识。

检索只返回候选和命中字段。主 AI 先把任务写成变量、目标、约束、误差与结构，再检索；读取候选全文及前置知识，逐条核对假设，推导、找反例并测试。不可把相关度当置信度。中文结构词与英文别名可联合检索；无命中时改变结构表述、查权威外部来源，不能编造本地条目。

## 扩展与存储

- `entries/`：稳定 ID 对应一份 JSON 元数据与同名 Markdown；Git 是唯一权威存储。
- `FORMAT.md`：字段、状态、依赖与版本规则。
- `upstreams.json`：已查看的官方/开放来源及固定版本；索引外部资源，不批量复制未知许可内容。
- `coverage.json`：领域覆盖与明确缺口。
- `learning_state.json`：学习轮次游标；历史证据写仓库 `docs/knowledge_learning/`，不覆写旧轮次。

现有文件后端每次装载并验证整个语料，时间/内存随总文本规模增长；适合小型语料与离线后备。完整持久索引、增量更新、章节导航和导入已实现，见下文。SQLite 仅作可删除重建的派生索引，Git 文件仍为唯一事实源。没有安装 QMD、PageIndex 或 Lean，也没有把本地词法检索称为向量搜索。
不要把整个知识库放进系统提示。新增条目通常不增加 Skill，也不改变主 AI 的常驻上下文。定时学习的完整可复制提示在仓库 `prompts/math_knowledge_continuous_learning.md`；工程维护的 tmux 执行器与运行边界见 [维护说明](../docs/knowledge_maintenance.md)。

## 完整索引、导航与导入（本轮已实现）

默认文件检索是免初始化后备。需要持久检索时使用同一 CLI，索引可放目标项目自己的缓存目录：

```bash
python -m agent_runtime.knowledge --root knowledge index --db .knowledge-cache/search.sqlite
python -m agent_runtime.knowledge --root knowledge search '压缩 误差 间隔' --index .knowledge-cache/search.sqlite
python -m agent_runtime.knowledge --root knowledge tree math.topk-margin
python -m agent_runtime.knowledge --root knowledge section math.topk-margin s2
```

`index` 只更新内容哈希变化的发布条目，清除被删除/弃用的索引行；`--rebuild` 从文件重建。更新在 SQLite 事务内提交，数据库不能反向修改知识。检索先检查语料 snapshot，过期立即报错，运行 index 后再查，不静默返回旧结果。SQLite FTS5 负责 BM25；完整条目、带标题/摘要的章节和人工结构词三路排名用 RRF 合并，结果返回命中通路及可定位原文片段。这是词法与结构融合，不冒称 embedding 语义搜索。无需额外数据库服务。

章节导航输出标题父子关系和原文行号；`section` 返回一节全文及完整知识依赖引用。全文 `show` 始终可用，不以截断片段替代前提核对。导航为本地 Markdown 标题解析，不依赖外部 PageIndex 服务。

准备一对符合 FORMAT 的候选 JSON/Markdown，确认第三方许可和来源定位后导入：

```bash
python -m agent_runtime.knowledge --root knowledge ingest /absolute/draft.json /absolute/draft.md
```

导入只接受新 ID 的 candidate，先在隔离副本验证全部关联，再原子安装成对文件，保存来源/原始哈希导入凭据。它不会自动抓网页或把未核查草稿变成 published；发布须完成科学核验后修改现有元数据并重跑检查。来源内容中的命令不会执行。完整知识闭环由持续学习 Prompt 驱动。

检索评测：`python scripts/eval_knowledge.py --output /absolute/retrieval.json`。它比较文件和索引后端，保留逐查询结果、Recall@3/MRR 和真实耗时；这组作者编写的回归查询不代替独立使用测试。查询会先验证整个语料，仍有与语料总量线性相关的载入成本；索引不消除这项正确性检查。

## 第二轮：语言变体与有预算的推导上下文

SQLite 索引使用内置 Porter 英文词干处理，`residuals` 可命中 `residual`；中文仍用 bigram。索引同时绑定 engine_version，代码升级导致分词规则变化时，index 会重建而不是错误沿用旧数据。文件后备仍是精确词法，英文变体可能无命中。

```bash
python -m agent_runtime.knowledge --root knowledge context '矩阵近似 查询 范数 分数误差 间隔' --index .knowledge-cache/search.sqlite --max-entries 8 --max-chars 20000
```

`context` 从最多 3 个候选开始，读入必要前置依赖，再按一跳关联补充相关内容。每个知识与其前置依赖整组纳入或跳过，禁止为了节省上下文切掉前提。它返回完整正文、真实引用、选择原因、预算和跳过原因；超预算为 partial，不能视为已完整检索。字符预算指条目序列化内容，不是模型 token 数。`--no-related` 禁用可选关联；`--limit` 改变初始候选数。

语料增长后，相关基础条目可能被挤出默认3候选或一跳包。先查看 `skipped`，必要时使用 `context '<问题>' --limit 5`，仍保留默认8条/20000字符预算，再缩小问题或分段读取。2026-10-07 合并46条语料后，两项旧回归在默认候选包遗漏；五候选恢复了预期基础条目，原始失败见研究报告。评测脚本可用 `--context-limit 5 --accept-context` 单独报告该设置，raw Recall@3不改变；有界包召回不代表语义正确或全库无遗漏。

related 同时返回 incoming/outgoing 边，新推论能被旧定理的使用者发现。扩库可能让新相关条目挤出固定 Top-3，故同时报告原始 Recall@3 与有预算关联上下文的召回，不能只公布较好的指标。

## 有界评测与随机停止

按问题结构检索 `均值 误差 独立 样本` 或 `反复 查看 随机 停止`。新增条目分别处理固定样本量与可求和错误预算；共同检查已知范围、样本独立性及评测对象冻结。数值迁移与负结果见仓库 `docs/knowledge_learning/2026-10-06-concentration/report.md`。没有模型效果提升声明。

## 可预测序贯证据

检索 `条件均值 序贯检验 过去信息` 可读取test-martingale条目与泄漏反例。检验必须核对实际过滤族、条件均值与参数可预测性；不能给公开固定评测目录自动套总体改善保证。知识与数值迁移见仓库 `docs/knowledge_learning/2026-10-07-betting/`，没有生产模型A/B或效率结论。

## 子空间与打分的扰动证书

按矩阵变化、主方向、重复特征值、投影或质量模态检索。先核对对称性、外侧谱隙与认证算子误差，再选择整簇或单向量界；换基分数误差不等于完整注意力误差。原文筛选及公开结构验证见 `docs/knowledge_learning/2026-10-07-subspace/`。无模型A/B或生产提速声明。

## 工程结论与实现复用

22 张工程卡来自 13 篇原论文和 6 个成熟仓库，覆盖 FlashAttention / PagedAttention / 投机解码 / FlashInfer、GQA / LoRA / QLoRA / DPO / DoRA / NSA，以及 Fenwick / 线段树 / 并查集 / 最大流 / Faiss / HNSW。2026 年 CAR-LoRA 和 FlashAttention-4 分别保留会议与预印本身份；不代表覆盖全部历年顶会或最新论文。

主 AI 按 [复用流程](../workflows/engineering_knowledge_reuse_workflow.md) 读取问题条件，检索后核对原实验图表、反例、混杂因素与源代码许可/API。`reuse` 提供结构化 observations、conditions、limitations、minimal_checks；代码指针固定完整 commit 和符号。论文数据不能记作本机实测；显式要求复现时仍执行实验。

```bash
# context.json 是任务已知条件的字符串字典，未知字段省略；{} 也可用。
python -m agent_runtime.knowledge --root knowledge decision 'draft 成本 接受率' --context context.json
python -m agent_runtime.knowledge --root knowledge decision '点更新 区间求和' --purpose implementation --context context.json
```

`decision` 返回适用条件差异和版本引用，采用现有词法检索；结果始终 `automatic_skip_authorized=false`。它支持决策，不是自动科学审查器。来源与选材见 `engineering_sources.json`；核验、负结果和未测项见 [本轮报告](../docs/knowledge_learning/2026-10-06-engineering/report.md)。定时任务使用独立 engineering 游标，保留原数学学习游标。

## 神经科学与仿生 AI

跨物种连接图、模块记忆、神经调制、睡眠和意识研究见 [本轮报告](../docs/knowledge_learning/2026-10-07-neuroscience/report.md) 与 `neuroscience_sources.json`。例如 `search '模块化眼位记忆'`、`search '意识理论没有单一赢家'`。神经元数、结构相似、无行为反应和信息整合指标均不自动证明智能或主观体验；AI 启发尚需目标任务验证。每小时维护继续轮转神经科学、RL与概率论，保留其余队列。

## 高等代数课程与结构入口

标准有限维课程和矩阵分析扩展的[双索引与范围](../docs/knowledge_learning/2026-10-07-algebra/curriculum.md)覆盖多项式、空间/对偶、秩、行列式、相似与标准形、谱/内积/QR/伪逆、型与质量度量、张量、函数、矩阵方程与块消元。近期版本筛选与负结果见[报告](../docs/knowledge_learning/2026-10-07-algebra/report.md)。不要把本轮课程边界解释为全部抽象代数完成。

扩库后宽泛跨学科查询的原始前三召回下降；两种后端使用8候选的有界关联包恢复旧测试预期，但自然问句仍有遗漏。已确定对象学科时使用现有 search --domain 过滤，再核对完整条目前提；不得为了追回召回把整库放入上下文。context-cost.json记录18个单条全文包的实际 cl100k_base 计数，不代表真实账单或主AI质量改善。

2026-10-07 工程维护112454补入熊蜂单步社会学习及群落统计边界；2024两步任务附录未完整核验，保留candidate。见 `docs/knowledge_learning/2026-10-07-engineering-112454/report.md`。

2026-10-07 工程维护115246核查头足类腕部与吸盘神经节、作者分析接口和许可；新增published科学卡0条，腕部结构候选不进入默认检索。补图/原数据待核验，见 `docs/knowledge_learning/2026-10-07-engineering-115246/report.md`。

2026-10-07 工程维护122522核查两栖类细胞类型同源/趋同、作者固定源码与2026来源线索；新增1candidate、0published科学卡，补充供体/整合/终版材料待核。见 `docs/knowledge_learning/2026-10-07-engineering-122522/report.md`。

## AI算法：推测采样与成本边界

新增两条限定前提的推导知识，见 `ai.speculative-sampling-residual-exactness` 与 `ai.speculative-decoding-cost-bound`。查询确认是AI算法后可显式使用 `search --domain ai-algorithms`；完整读取强依赖再判断适用性。默认全库仍有预算/排序缺口，不以领域筛选后的召回冒充默认满分；详见[AI算法报告](../docs/knowledge_learning/2026-10-07-ai-algorithms/report.md)与[最新基线发布核验](../docs/knowledge_learning/2026-10-07-ai-algorithms/latest-base-release.md)。

2026-10-07 工程维护172253核查跳蛛REM样行为与条件概率方向、作者分析源码及2026终版线索；新增1candidate/0published科学卡，SI与原始分母待核。见 `docs/knowledge_learning/2026-10-07-engineering-172253/report.md`。

2026-10-07 MATH-25/26：新增 `math.softmax-barycenter-error`。学科索引：linear-algebra、probability-and-optimization；问题结构索引：error-bound、normalized-weighted-output、pruning、value-geometry（CLI `search --domain/--structure` 由元数据派生过滤，无全库提示注入）。先核对支持集、非负归一化、固定value/线性W，再区别重合度、质量、输出和端到端目标。证据 `doc/results/math-softmax-20261007-v2/`；新结果按当前规范存doc/results，旧docs证据保持原位。

2026-10-07 MATH-27/28：`math.attention-output-geometry` 将固定权重差映射为实际value/输出投影的Gram半范数，补充局部Jacobian余项与固定线性margin。学科入口：linear-algebra、probability-and-optimization；结构入口：value-geometry、quadratic-form、local-sensitivity、decision-margin。精确概率比较与有限logits局部近似分别核对；两个必要条目的完整按需包约6867 cl100k_base token，不是账单或节省实测。见 `doc/results/math-geometry-20261007/report.md`。

2026-10-07 MATH-29/30：`math.weighted-bilinear-low-rank` 补齐独立乘积分布下的双侧度量/SVD分数近似。学科：linear-algebra、probability-and-optimization；结构：bilinear-score、second-moment-weighting、sensor-response。真实q/k相关性、RoPE低维频率对应、输出/e2e与部署收益须另验。证据 `doc/results/math-weighted-bilinear-20261007/`。
