# 可检索基础知识

这里保存跨项目可复用的数学、物理知识；Skill 保存使用知识的方法。项目观测、用户偏好和执行状态仍由项目记忆、TASK.md 与运行目录负责。

当前包含 10 个经过来源核对、推导与数值检查的种子条目，不代表完整学科覆盖，也没有证明 Agent 整体性能提升。条目是本项目撰写的知识摘要与应用推导，不镜像第三方教材或 mathlib。上游来源与采用理由见 `upstreams.json` 和仓库 `docs/knowledge_upstreams.md`。

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
不要把整个知识库放进系统提示。新增条目通常不增加 Skill，也不改变主 AI 的常驻上下文。定时学习的完整可复制提示在仓库 `prompts/math_knowledge_continuous_learning.md`；本次交付没有创建定时任务。

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

related 同时返回 incoming/outgoing 边，新推论能被旧定理的使用者发现。扩库可能让新相关条目挤出固定 Top-3，故同时报告原始 Recall@3 与有预算关联上下文的召回，不能只公布较好的指标。
