# ResultStore：查询 context 不变量的有界优化

## 问题和行为

`ResultStore.search` 在每个读取成功、未被撤销的记录上，重复扫描同一查询 context，判断字段是否齐全及递归 `_unknown`。实际结果库的有效 context 达105,460个JSON字符。扫描223个目录时，这些输入检查重复143次；记录读取、内容校验和撤销检查仍各有必要。

最终v5在第一个实际进入匹配的记录内，识别普通内置JSON数据并缓存输入资格。每条记录仍读取/校验、检查污染撤销、计算词法分数、精确比较context、收集错误并排序。迭代类型检查保留深层结构；特殊容器、键/值子类、tuple、自定义show实例和ResultStore子类回退原逻辑。缺少/空结果库不会提前触发原本未执行的递归检查。没有缓存记录或答案，也没有降低验收标准；检索依然不授信。

源码改动仅`agent_runtime/result_store.py`的私有分类助手与现有search；无新增生产后端。基线`9c071f7c735eed861244951a150d456ffe27a4ef`。调用期间context不能被外部并发修改，这是原同步API没有保证的情境，不宣称这一优化提供快照隔离。

## 测量与独立验收

Linux6.18.44 x86_64、Python3.12.14，共享CPU、温OS文件缓存；`perf_counter_ns`计时完整search（包含文件读取、检查及撤销门），固定query=`result source context`、limit3/max_scan250。六个实际context场景，各一次warmup、11对串行交替次序计时。143个record.json前后哈希一致；223目录中的80个无效/缺record错误全部保留，partial标记未删除。完整返回JSON逐次相等，不以top3相似冒充等价。

先验门槛为两个大context中位延迟降低至少10%，控制场景不退化超过10%；近噪声的小变化不称收益。

| 场景 | 独立基线ms | 独立v5 ms | 降低 |
|---|---:|---:|---:|
| combined-corpus-v4 context | 159.341 | 93.721 | 41.18% |
| math-inverse-update context | 149.296 | 91.497 | 38.71% |
| comm-batch context | 95.126 | 90.664 | 4.69%（仅观察） |
| None | 94.462 | 93.583 | 0.93%（噪声内） |
| 不完整context | 97.180 | 97.128 | 0.05%（噪声内） |
| 含unknown context | 92.106 | 91.114 | 1.08%（噪声内） |

生产者v5的大context降低41.93%/38.53%；整合后的实际生产方法对冻结基线再次测量，降低41.55%/37.45%（164.030→95.881ms、153.304→95.894ms），各完整返回相等。原始66对/每轮见raw-v5-serial.json、independent-v5.json、native-v5.json。只支持本机已测文件检索入口；没有模型token、费用、真实任务质量、冷缓存或完整Agent请求收益。

发布前并发main更新到`66c88cd60dc4a7bf064d835f2e3c50b822f8b2cd`，只增加数学记录/知识镜像/TASK，无运行时或测试代码变化。保留MATH-113和本任务条目，已有本任务暂存快照保留。扩展至144个record后重新串行对拍实际生产方法和冻结基线：主执行者大context降低42.23%/38.69%；独立新语料复跑为 **170.844→96.965ms（43.24%）**、**151.709→91.958ms（39.39%）**，全部返回相等；控制项没有超过10%退化。最新原始数据为native-integrated-66c.json、independent-integrated-66c.json，后者是最终发布主数据，前表保留原143-record历史条件，二者不混算。

独立审读及复跑覆盖18个接口边界：空/缺库、known/None/incomplete/nested unknown、tuple、dict/scalar/key子类、非法set/NaN、深层early-unknown、自定义show修改输入、子类回退、真实撤销/损坏记录及无成功记录。见review.md、reviewer-boundaries.py和独立输出；生产集成/全库结果的最终复核另见final-review.md。这是宿主实际独立审读/运行，不宣称已部署受管ReviewSession、ResultValidationHandler或tmux。

## 失败证据和取舍

无条件提前计算会改变自定义容器异常和空库行为，故拒绝；反例见reviewer-empty-subclass.json。进一步审读发现特殊键哈希、自定义show、未知值短路后的深嵌套及回退开销，最终引入纯内置路径、懒求值、一次分类与迭代遍历。早期源码提取anchor不匹配的调用未产生有效计时；一次v4/独立v3计时重叠排除出验收。中间迭代保留在本地检查点，不用其较好数字替代最终v5串行结果。

权衡：增加25行兼容性路径。每次查询多一次普通数据类型扫描，换取大context免重复递归；小输入没有已证明的显著收益。保持简单JSON原样、错误/撤销门原样；不引入持久索引、缓存失效协议或新依赖。

## 研究与现有结果

本持续批次已有`docs/continuous_optimization/papers.json`登记的52条去重阅读及对应原文分析，前十篇覆盖τ-bench、AgentBench、AgentBoard、SWE-bench、SWE-agent、AgentDojo、τ²-bench、Reflexion、Self-Refine、Agentless；具体范围与排除见既有rounds文档。本次不把旧数量当十篇新精读，不重新认证全部历史阅读，也不把循环不变量称为论文创新算法。近期Atomix/UndoBench/AgentChaos/VP-Control的源检查继续支持一个采用约束：相同元数据/检索命中不等于可信验收，此优化保持现有证据门。

2026-10-14新检索发现REMORY(arXiv2610.11287)、LAM(2609.32256)等线索；仅检索元数据，未精读/采用，不用其摘要宣传支持本库收益。优先采用本库可独立实测的精确局部改进；有损记忆/学习检索仍需实际质量与成本对照。

ResultStore先查scanned222/partialtrue，combined-corpus历史结果为语料检索或发布证据，与本次完整ResultStore性能不等同，拒绝直接复用；原返回prior-search.json。首轮143记录仅为本次检索输入，没有重新验收其中历史实验。

## 状态与复现

原基线整合全库运行1179项：1171通过、8跳过；Reader3项通过，基线定向ResultStore21项通过。最终生产源码/助手与冻结候选逐字匹配，独立18个接口边界普通/-O均通过；日志与最终独立审核见full-tests.log、reader-tests.log和final-review.md。并发66c新基线重新全库运行1179项，同为1171通过/8跳过，Reader3通过；新日志为full-integrated-tests.log、reader-integrated-tests.log，由delta-review.md独立验收，不凭旧pass继承新文件条件。8项跳过不计通过。只暂存明确列出的源码、此run交付与TASK详情；不带其他未提交研究检查点，不写guide。不建PR/额外升级分支，不强推。最终commit/远端回读以对话给出的实际SHA为准；本报告自身不自证发布。

基线与候选完整方法/助手字节已冻结在raw-v5-serial.json。`python agent_doc/results/result-search-invariant-20261014-0304/measure.py agent_doc/results/result-search-invariant-20261014-0304/raw-v5-serial.json`可在整合版本对冻结基线和当前实际方法重新配对；实际语料路径固定于本次本地环境，迁移需按源码ROOT重绑定输入，不把更换语料的数字混入旧测量。
