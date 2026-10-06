# 2026-10-06：意图纠错、证据记忆与科研产物

状态：实现与全部角色代表任务验收完成；发布状态以根 TASK 的 T11 读回记录为准。基线 `d208d1c3cd2f1d8d6f6659e8db6fb95e8db2298a`，候选 `2bc1fc5`。本轮对应根 TASK 的 T6–T11；所有证据区分论文报告、工程验证、模型任务和线上集成。

## 11 篇论文怎样组合成改进

不是逐篇堆 Prompt。按 arXiv ID 去重，11篇都是本台账新增；实际阅读原始全文的方法、实验和相关局限，必要关键图表另行渲染查看。各篇作者、固定版本/日期、章节和未读范围见 [记忆](research/memory-papers.json)、[科研/作图](research/research-viz-papers.json)、[推理](research/reasoning-papers.json)。不声称逐页审读全部附录或复现作者模型榜单。

| 原文 | 机制/成立前提 | 实验与失效边界 | 成本/取舍 | 本库决定 |
| --- | --- | --- | --- | --- |
| [LongMemEval v2](https://arxiv.org/html/2410.10813v2) | 分开检索/阅读；测知识更新、时序和拒答 | 正确召回不保证答对，错误时间过滤会丢正确来源 | 索引压缩省上下文但丢细节 | 采用纠错/未知验收维度；大规模模型准确率待测 |
| [A-Mem v1](https://arxiv.org/html/2502.12110v1) | 原子笔记、自动链接与邻居演化 | 效果依赖模型/类别，生成链接不是因果依赖 | 多次模型写入与索引维护 | 不直接采用自动改写事实；生成索引待冻结集验证 |
| [MemGPT v2](https://arxiv.org/html/2310.08560v2) | 上下文分页、外部档案、按需检索 | 早停/函数调用失败；有损摘要基线限制对比 | 检索次数/延迟需预算 | 采用短上下文+来源入口规则；不引入新后端 |
| [Zep v1](https://arxiv.org/html/2501.13956v1) | 原始episode与派生事实分开，保留失效历史 | 作者未直接评测来源关联，也未测试科研依赖级联 | 图抽取/模型调用有成本 | 借来源与失效思想，用小型SQLite显式依赖；不复制整套图服务 |
| [The AI Scientist v1](https://arxiv.org/pdf/2408.06292v1) | 从可运行baseline生成idea、实验、写作 | 指标方向误读、泄漏、幻觉实验，评分不证明科学贡献 | 实验/评审资源有界 | 保留强baseline、负结果和参数化脚本，拒绝靠自评宣布科研成功 |
| [Agent Laboratory v1](https://arxiv.org/pdf/2501.04227v1) | 阶段交接与用户反馈 | 自动评分6.1、人评3.8，研究质量并不等同自动评分 | 用户协作提高可控性但占注意力 | 采用反馈→版本化更正→依赖复查，不增每阶段强制等待 |
| [MatPlotAgent v1](https://arxiv.org/pdf/2402.11453v1) | 分开代码调试与渲染图反馈 | GPT-4改善、部分代码模型退化；领域覆盖有限 | 最多有限轮视觉调用 | 采用数值硬门+具体视觉反馈+回退；美观收益待独立配对评测 |
| [ChartMimic v1](https://arxiv.org/html/2406.09961v1) | 图像高层与可执行低层指标组合 | SelfRevision总分68.3低于Direct71.4；趋势相似不等于数值准确 | 评图/执行双成本 | 不用单VLM总分验收；保留before/after与数值保真 |
| [Cannot Self-Correct v2](https://arxiv.org/html/2310.01798v2) | 公平初始要求、无oracle停止、统计对改错 | 当时模型的反思会退化，不能泛化为所有现有模型能力 | 额外调用也可能降质量 | 采用correct_to_wrong/wrong_to_correct独立统计 |
| [Let's Verify Step by Step v1](https://arxiv.org/html/2305.20050v1) | 中间步骤验证与候选选择 | 78.2%为best-of-1860，非单次提示；需训练数据/成本 | 大量采样和训练不可直接移植 | 借可核验中间产物；不声称训练PRM或读取私密思维链 |
| [CRITIC v4](https://arxiv.org/html/2305.11738v4) | 用实际工具核查再修订 | 工具反馈仍可改错；oracle结果不代表部署 | 搜索/执行/修订增加延迟 | 采用证据绑定、最后版本验收和回归统计，不无限反思 |

综合取舍：用显式来源和依赖解决“这条结论还能否使用”，用参数化runner与不可变记录解决复现和文件散落，用独立验收约束反思。自动语义图重组、PRM训练、大规模盲评暂不采用，原因是本轮尚无公平本地效果证据，并非认定论文方法无效。

## 实际改动

- `agent_runtime/project_memory.py`：私有项目SQLite账本，候选/当前/失效/替代状态，来源、scope、不可变ID和传递依赖；事务纠错、显式接受、历史与影响查询。新意图不自动把旧派生结论变正确。
- `agent_runtime/task_manifest.py`：声明 `memory_refs` 的任务，在执行、结果读取和验收时必须检查当前有效性；已经done的旧报告会显示needs_review。没有声明的隐式依赖不能自动发现。
- `scripts/publish_report.py`：通用参数化报告发布器。原始产物按路径/哈希引用，每轮快照不可覆盖；稳定latest原子更新；读取时复查数据哈希和记忆。不是实验执行器或科学裁判。
- 复用既有 `agent_eval_pipeline.py`，不复制每轮runner；扩展首轮→末轮语义回归/修复计数，阻塞、未评分、不可评分不计成语义错误。
- 三个相关Skill按需引入同源记忆流程，插件副本自动同步。主AI/科研/实现/文件管理交接当前意图、数据版本与消费者；现有角色注册数保持14。
- 先完成全部授权TASK基线，再在既有真实监督/预算/权限门禁内采用 `agent/<task-id>/<run-id>` 独立分支，旧 `agent-explore-*` 可继续使用；有界实验不自动合并/发布。

## 用户如何存任务与文件

`AGENTS.md`（复数）记录稳定规则，`TASK.md` 固定根目录保存项目目标、验收与结果索引；可继续让用户手写结果摘要，详细数据链接到唯一记录。`CLAUDE.md` 只负责接入这些规则，不再复制一份任务列表。

| 内容 | 路径/维护方式 |
| --- | --- |
| 通用实验/测试脚本 | 现有src/scripts；变体传参数或配置，保留代码/配置hash |
| 原始观测与输入 | data/raw或原项目位置，保留字节和采集条件 |
| 每轮测量/图与日志 | results/<task>/<run>、figures或既有目录，来源与消费者登记 |
| 每轮报告 | reports/<task>/runs/<run>/report.json + report.md，不可覆盖 |
| 用户当前入口 | TASK/CODEMAP指向reports/<task>/latest.json；读取时重验来源 |
| 私有记忆/高频状态 | .agent-memory/ 与 .agent-runs/，不自动提交公共Git |

不能为了“都在一个文件夹”把运行脚本、原始数据、缓存和交付混放。先沿用项目布局；文件管理Agent给生产者分配位置、接收清单、检查引用，主AI串行改总任务；不批量搬正在运行或归属未知文件。

## 云端记忆是否使本地管理失去意义

不是。要区分模型权重、当前上下文、产品记忆与可审计项目状态。官方文档在2026-10-06核查：

- [OpenAI Memories](https://learn.chatgpt.com/docs/customization/memories)：ChatGPT Web/Work记忆与本地Codex客户端存储/控制不同；持久团队要求应放AGENTS.md或受版本控制文档，不能只依赖记忆。本文不推定用户账号已启用任何选项。
- [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)：提供项目指令发现；TASK不是默认指令文件，本库入口显式要求读取它。
- [Claude Code memory](https://code.claude.com/docs/en/memory)：CLAUDE.md与自动记忆不同；自动记忆是机器本地、不会自动跨机器/云环境共享，主会话自动记忆也不默认传给普通子Agent。

所以本库保留可跨宿主交接的项目证据/更正及最小有效摘要。只对实际可访问且获授权的产品记忆入口执行修改；没有入口就给出纠错事实/引用并在项目验收拦截，不能声称清掉所有云端副本或改了模型参数。账本不能保证模型永不误解，独立验收仍必要。

## 本轮验证

程序回归：340项，332通过、8跳过；独立paper-reader测试3/3通过。7项跳过要求当前缺少的CJK字体/作图依赖组合，另1项是真实tmux/Unix socket集成；不将跳过算通过。同步检查与3个修改Skill的quick_validate通过。原始日志见 `evidence/unit-tests.log`、`evidence/reader-tests.log`。14角色及主AI、实际协调→写作交接共17项最新全部通过；首次收集15/17，19个真实新上下文。两次首轮失败分别为产物目录错误、文件重组缺少可执行回滚，均保留后由新上下文恢复。首次收集指标包含有界视觉QA修复，不是无干预首稿成功率。语义对改错0、错改对1，交付失败恢复另计1；单轮不能估计稳定发生率。归档恢复及完整性复验通过，见 [模型证据](evidence/model-eval/README.md)。公平模型A/B未完成，不能用程序测试替代。已执行的确定性对照见 [memory-gate-comparison.json](evidence/memory-gate-comparison.json)：固定8个合成报告验收情境，旧门禁匹配3/8，新门禁8/8；五种不该接收的旧/候选/未知记忆被拦截，三种有效情况保留，原始CSV字节保持。这里的“8/8”只是精确构造的程序状态检查，不是模型准确率提升。

复现脚本 `evidence/compare_memory_gate.py` 接收 --repo/--baseline/--candidate/--out，可换固定版本复跑，不复制不同参数版本。比较时两边读同一个候选账本状态，比较对象仅ReportingHandler；旧版本本来未实现该门禁，不能用这个结果推断整个旧Agent科研表现。

### 新的意图纠错交接样例

另有一项 fresh-context `code-organization` 实际执行：主控制器仅给原项目、用户纠正和写入范围，没有给标准答案。旧mean报告被撤销为当前p95证据；旧意图superseded、报告stale、原样本和无关inventory保持active。Agent复算mean20 ms、最近秩p95=71 ms、线性p95=58.6 ms，并因分位数口径/真实采集证据缺失保持LAT未完成。

主控制器独立检查原文件字节、8项产物hash、当前账本与旧报告拒绝；记录见 [independent-review.json](evidence/correction-handoff/independent-review.json)，可读交接见 [report.md](evidence/correction-handoff/report.md)。一次误建空输出目录已报告并由主控制器只删除该空目录，未删输入；进程检查失败，因此仅依据running声明保护活跃路径。该样例不是盲式配对A/B，也不是用户真实系统实验。

### 运行环境边界

本轮使用当前宿主真实子Agent执行机制和CPU/渲染工具，不是Claude CLI线上调用。现环境不能提供已验证的tmux/Unix socket监督会话，本轮没有声称启动或部署目标服务器的监督器；沿用已有阻塞记录并推进独立实现/验证。tmux真实SSH断链、目标服务器接入和公平固定模型/预算的重复A/B仍未验证。程序与单轮合成任务的通过不能证明整体科研准确率、图表美观或线上稳定性提升。

## 持续优化

已将本轮范围合并到原有每3小时任务（ID `6ac49448fab08190a825f0db4a6f3ca9`），保持原调度/启用与main发布门禁，不创建重复定时任务。继续累计新论文、未测候选、负结果和逐角色证据。下一优先：真实意图纠错保留任务与图表独立配对评测；本轮不宣称“优化到极致”。

## 发布与复现版本

验证使用本地候选 `2bc1fc5d41920d4c82edc6233c31956b37f6a2b8`；GitHub 可达候选 `2f0398c4d27b9ad2a1ce1d81230bdc56ca0928f9` 的文件树完全相同（`6803cefca363c97c07798231826c38ceaaebae21`）。两者仅提交元数据不同。证据发布提交以该远端候选为父提交；复现脚本可以使用远端候选。原始执行回执不改写，映射见 [publication.json](evidence/publication.json)。发布完成以根 TASK 的远端提交读回为准。
