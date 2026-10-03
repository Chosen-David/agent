# 第二轮代码阅读升级：来源、缺口与验收

起点为 `4439900`（包含首版 `dbfc901` 与并发handoff改良），2026-10-03。先前Claude/Trail of Bits/Serena/Aider调研保留，不重复声称新发现；本轮针对遗漏的图解析实现、专用探索/PDG技能及研究评测开展补充。主工作流仅加按需入口，具体矩阵放短引用卡；不新建角色、不重写通用调度、不安装索引数据库。

## 为什么再改

首版已有默认/可选和shape要求，但交付主要依赖自由叙述。缺少具体的消费者覆盖矩阵、跨模型适用行、图索引版本/分析层/截断检查；没有程序检查“已支持主张覆盖了未读消费者”或“单条运行被写成多入口执行证据”。真实只读应用中，状态更新只在一个selector入口、其他入口仅消费，以及模型旋转维/布局不同，都是必须显式保留的边界。

改动：新增按需覆盖卡，区分调用表达式、已解析目标、观察到的运行；反向核查关键值消费者和函数外初始化；按入口/模型/配置限制shape与机制结论；不从过期或未建层的空图结果推断不存在。新增标准库 `check_coverage.py` 拒绝未决范围上的确定结论、陈旧commit、悬空证据引用和未观察入口的executed声明。它只检查声明契约，不负责发现所有漏项、解释源码或鉴真日志；旧证据抽取工具保持独立。

## 新来源的真实实现对照

每个已读文件的精确SHA、原始URL、文件hash及许可证见 [新来源锁](code_reading_v2_sources.lock.json)。以下为源码定性分析，不是后端性能实测。

| 来源与阅读位置 | 采用的能力/思想 | 限制与没有采用的部分 |
| --- | --- | --- |
| GitNexus `gitnexus-exploring/SKILL.md`、`gitnexus-pdg-query/SKILL.md`；`local-backend.ts:_pdgQueryImpl`；`evidence-weights.ts` | 索引绑定repo与commit；查询从入口到上下游；区分未建立PDG、未知层和真实空结果；控制依赖与数据依赖分开 | 当前根许可PolyForm Noncommercial，不称开源。只读比较，未复制skill/源码。原skill建议stale时重建索引，但本任务只读不能自动执行。工具的process、静态边与人工加权confidence均不等于运行trace或校准概率；PDG所读入口是函数内分析 |
| CodeGraphContext `indexing/resolution/calls.py:resolve_function_call`；`test_calls_resolution_tiers.py` | 解析策略/证据标签要随边返回；将歧义作为显式待核对项 | Tier8会选多个候选中的first，Tier9可回退caller文件；源码/测试明确这些是低置信启发式。其“EXTRACTED”标签也不直接证明动态调用。MIT；不接数据库，只采用保留策略与歧义的输出要求 |
| Codebase-Memory `lsp_resolve.h`、`pass_calls.c`、`mcp.c:handle_trace_call_path` | 调用点source occurrence与绑定证据；反向/正向遍历；显式截断、generation与cursor过期；可选择输出edge evidence | 当前源码与论文评测release不同，不能用论文数值证明当前实现。CLI/索引/监控会增加状态，未安装；MIT根许可不代表所有vendored grammar一致。查到图边仍需读调用点和消费者 |
| RepoQA `compute_score.py:needle_evaluator`、`metric.py:compute_function_similarity` 与研究论文 | 用含语义判别的函数定位任务，评分与输入隔离；报告作者与独立执行者分开 | 实现按函数代码相似度寻找best target并按阈值统计；适合定位，不足以验证张量机制、配置覆盖、状态更新或最终消费者。Apache-2.0；本轮新写6题机制任务/18项rubric，未复制其数据集或运行模型provider |

[Codebase-Memory论文](https://arxiv.org/html/2603.27277v1)区分图结构检索与文件阅读任务；本轮据此保留“图导航＋源码核查”，没有把其测量移植到本skill。[RepoQA论文](https://arxiv.org/abs/2406.06025)评估自然语言描述到函数的检索，本轮任务另检查机制链和未覆盖条件，二者分数不互换。

检索同时遇到RepoGraph等面向修复的研究线索，未深入其实现、未采用，不列为已验证集成。尝试读取PyTorch shape-propagation官方实现遇访问失败，不据未读源码引入FX能力。科学代码shape部分由已读真实源码和自建任务验证，不声称通用静态shape推理器。

## 新增任务与比较设计

[taskset](../evals/code_reading_v2/taskset.json)冻结6题：注册分发/动态target、状态生产消费、tensor前后处理、跨模型RoPE条件、配置与实验叙述冲突、空图与消费者覆盖。[oracle](../evals/code_reading_v2/oracle.json)固定18项按语义与定位评分。输入是原创synthetic engine/config/experiment/notes，不包含用户论文。

同轮两名独立执行者分别读取首版skill快照和新增覆盖卡快照；同样输入、6题、最多12次读/搜索调用、禁止执行输入/联网/读oracle。没有模型/推理档位切换；独立评分者仅见匿名X/Y输出及oracle。每臂仅一次，且任务问题本身给出较强提示，不能估计泛化正确率或把任务通过归因于skill。候选packet冻结后补充的契约检查器不计入这次文本阅读A/B处理条件；它单独做程序测试。

真实SGLang案例继续只读，不跑runtime，不公开私密论文：复核状态消费者、模型旋转维/布局和可选投影形状；用覆盖报告明确限制“所有decode路径/所有模型”等主张。完整报告交原任务，不加入公开taskset。

验收结果、实际输出、独立review及限制见 [第二轮结果](../evals/results/2026-10-03/code-reading-v2/validation.md)。本轮只按可证明范围接受改良；没有证明的整体读码质量收益不作宣称。

## 源码永久链接

- abhigyanpatwari/GitNexus @ `f99dde8aa386cf6720d5b8e8ec43a0e365f04e4e`：[gitnexus-claude-plugin/skills/gitnexus-exploring/SKILL.md](https://github.com/abhigyanpatwari/GitNexus/blob/f99dde8aa386cf6720d5b8e8ec43a0e365f04e4e/gitnexus-claude-plugin/skills/gitnexus-exploring/SKILL.md) · [gitnexus-claude-plugin/skills/gitnexus-pdg-query/SKILL.md](https://github.com/abhigyanpatwari/GitNexus/blob/f99dde8aa386cf6720d5b8e8ec43a0e365f04e4e/gitnexus-claude-plugin/skills/gitnexus-pdg-query/SKILL.md) · [gitnexus-shared/src/scope-resolution/evidence-weights.ts](https://github.com/abhigyanpatwari/GitNexus/blob/f99dde8aa386cf6720d5b8e8ec43a0e365f04e4e/gitnexus-shared/src/scope-resolution/evidence-weights.ts) · [gitnexus/src/mcp/local/local-backend.ts](https://github.com/abhigyanpatwari/GitNexus/blob/f99dde8aa386cf6720d5b8e8ec43a0e365f04e4e/gitnexus/src/mcp/local/local-backend.ts) · [LICENSE](https://github.com/abhigyanpatwari/GitNexus/blob/f99dde8aa386cf6720d5b8e8ec43a0e365f04e4e/LICENSE)
- CodeGraphContext/CodeGraphContext @ `642c3215f8ef87fba03bc5dea6dbcb28d655fbd8`：[src/codegraphcontext/tools/indexing/resolution/calls.py](https://github.com/CodeGraphContext/CodeGraphContext/blob/642c3215f8ef87fba03bc5dea6dbcb28d655fbd8/src/codegraphcontext/tools/indexing/resolution/calls.py) · [tests/unit/tools/test_calls_resolution_tiers.py](https://github.com/CodeGraphContext/CodeGraphContext/blob/642c3215f8ef87fba03bc5dea6dbcb28d655fbd8/tests/unit/tools/test_calls_resolution_tiers.py) · [LICENSE](https://github.com/CodeGraphContext/CodeGraphContext/blob/642c3215f8ef87fba03bc5dea6dbcb28d655fbd8/LICENSE)
- DeusData/codebase-memory-mcp @ `96c3f41cf334d87670cb085f1fcf16f637293222`：[src/pipeline/lsp_resolve.h](https://github.com/DeusData/codebase-memory-mcp/blob/96c3f41cf334d87670cb085f1fcf16f637293222/src/pipeline/lsp_resolve.h) · [src/pipeline/pass_calls.c](https://github.com/DeusData/codebase-memory-mcp/blob/96c3f41cf334d87670cb085f1fcf16f637293222/src/pipeline/pass_calls.c) · [src/mcp/mcp.c](https://github.com/DeusData/codebase-memory-mcp/blob/96c3f41cf334d87670cb085f1fcf16f637293222/src/mcp/mcp.c) · [LICENSE](https://github.com/DeusData/codebase-memory-mcp/blob/96c3f41cf334d87670cb085f1fcf16f637293222/LICENSE)
- evalplus/repoqa @ `ae876deb1365dbf5a15b0533723c8ed123eee586`：[repoqa/compute_score.py](https://github.com/evalplus/repoqa/blob/ae876deb1365dbf5a15b0533723c8ed123eee586/repoqa/compute_score.py) · [repoqa/metric.py](https://github.com/evalplus/repoqa/blob/ae876deb1365dbf5a15b0533723c8ed123eee586/repoqa/metric.py) · [README.md](https://github.com/evalplus/repoqa/blob/ae876deb1365dbf5a15b0533723c8ed123eee586/README.md) · [LICENSE](https://github.com/evalplus/repoqa/blob/ae876deb1365dbf5a15b0533723c8ed123eee586/LICENSE)
