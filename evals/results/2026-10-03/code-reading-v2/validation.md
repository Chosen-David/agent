# CODE-READ-v2 实际验收记录

2026-10-03；实现基线 `4439900`，保留已合入的并发handoff任务。最终发布commit由Git历史定位，本记录不把未完成push预写为成功。

| 验收 | 实际结果 | 边界 |
| --- | --- | --- |
| 全仓 `python -m unittest discover -s tests -v` | 105 tests，OK | 包含并发基线测试；新增覆盖契约测试12项 |
| `python -m unittest discover -s apps/paper-reader/tests -v` | 3 tests，OK | 既有应用单元回归 |
| code-reading focused suite | 22 tests，OK | 首版10项＋新增12项 |
| 独立代码review | 4项发现修复后通过；审阅者重跑新增12项通过 | 不声称该reviewer运行了全套或sglang |
| 六题独立阅读＋独立匿名评分 | baseline 18/18，candidate 18/18 | 每臂一次，强提示任务，不能证明质量提升或统计显著差异 |
| 真实只读SGLang复核 | 固定SHA追加6锚点，总22；5行覆盖报告、3条主张；checker contract_valid，2行unresolved | 不执行目标、未加载校准基、未验证GPU/runtime；报告只交原任务 |

独立review修复项：schema_version布尔值被当1、JSON重复键被静默覆盖、无命令的测试却声称验证不执行命令、oracle将模型属性配置写成实际“使用旋转”。增加严格类型/重复键拒绝，测试加入不应执行的touch哨兵命令；模型措辞改为declares/configures。**评分前**修正oracle，由未读packet答案的独立代码reviewer提出；任务输入和18项计分数量未改。评分者明确两份答案均识别没有旋转实现。

## 阅读对比的可审查材料

- [固定任务](../../../code_reading_v2/taskset.json) 与 [18项rubric](../../../code_reading_v2/oracle.json)。输入四文件在同目录fixtures。
- [baseline输出](baseline-answer.md)、[candidate输出](candidate-answer.md)、[独立逐项评分](independent-grading.json)。匿名评分映射X=candidate，Y=baseline；评分时不提供映射或skills。
- [运行与哈希清单](run_manifest.json)，记录各packet输入/skill文件hash和实际读动作；[冻结skill文本](skill_snapshots/)，不把随后完成的checker算进该A/B处理条件。
- [全仓测试日志](unit-tests.log)、[reader日志](reader-tests.log)、[focused日志](focused-tests.log)。

执行后对两份原packet的所有冻结文件重新计算hash，全部未变。工具调用次数来自执行者的读取记录，没有另采宿主telemetry。每个执行者最多12次读/搜索，执行者自述baseline4次成功、candidate4次尝试/3次成功，最后复读受服务断连影响；没有目标代码执行。两臂未显式切换模型或推理参数，宿主实际模型未独立核验。两份已达到任务上限；无法排除题目提示和模型已有能力导致相同结果，也不能据文本长短或引用数量排名。

## 采用与限制

接受的是可核查的工程增量：覆盖卡及消费者/跨模型条件变为明确交接契约；检查器可拒绝版本不一致、悬空引用、未读路径上的确定结论、单入口run冒充跨入口执行、重复键。它不解析调用图、不推导tensor shape、不发现未声明入口、不校验源码文本或日志真实性。未知行仍能产生contract_valid；这是诚实报告可交付，不是研究问题已解决。

真实案例两项未决为跨模型旋转维/布局适用性、投影基实际文件与per-rank Hkv/D/r匹配。报告留在任务私有输出目录，没有把论文材料写入本库。所有sglang分析为源码事实/条件静态推断；未修改或push它。

最终结果再经独立review复核：17个可对应的冻结输入/技能文件hash、评分JSON的74处答案引用及105/3/22测试日志一致；建议发布。工具次数和复读断连标为执行者自述，独立评分/结果审阅未持有原始工具telemetry。
