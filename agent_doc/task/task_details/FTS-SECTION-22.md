# FTS-SECTION-22：精确片段选择去重复分词

Task-ID: FTS-SECTION-22
Date: 2026-10-19

## Plan

基线 de05d95c725029cca53239f0eb6e0f63d4fb9c19。仅优化 indexed_search 的
正文片段选择：每节计算一次 lexical overlap，精确选择最多2节，保持按
(-overlap,start_line) 排序、零匹配过滤和全部返回字段不变。可选用 nsmallest(2)
代替全排序；不新增跨请求缓存、不改变 FTS/RRF/engine/schema/知识内容。
主AI唯一源码/TASK作者，镜像同步；不涉及 TwoLevel 或 SGLang。

DAG：prior+research → fresh-context plan review → implementation+measurement
→ independent verify_experiment_result → full regression/report → publish/readback。
仅本地有界人工执行；未配置原生 ReviewSession/tmux 宿主，不宣称已部署监督器。
预算45分钟、最多2种局部实现，CPU/SQLite，无付费API。GUIDE当前空文件只读。

既有结果搜索扫描230目录，partial=true且存在缺失record错误；命中
advice-context、combined-integration-v5、math-random-score，均非当前函数完整
检索延迟证据，不可作本次性能验收。知识搜索三个GPU/学习条目不适配该优化，拒作证明。
复用 memory-storage-20261015/research.md 的12篇既有方法阅读矩阵，不称本轮新精读。
当前研究核查 MemScope 局部修复与可复现对照原则、Python官方 heapq 精确小k选择。

验收在测量前冻结：固定PYTHONHASHSEED=0，基线完整模块从上述git SHA载入，
相同store/只读SQLite数据库、query、limit、domain、structure；计时完整indexed_search
含连接/SQL/RRF/正文/引用，语料构建和load在双方计时外。每场景1对warmup，
7对AB/BA，每个计时样本重复调用5次取每次均值；保留所有样本、输入及源码hash。
真实当前语料5查询（memory retrieval、low rank、量纲、topk、zzqxnonexistent）
各limit5；另加无词查询!!!。合成8文档，1/2/16/256节，每节固定16或512词，
正文query=memory retrieval、limit5；节重叠分数与起始行形成并列及零匹配。
合成alias-only、空正文、空结果、domain/structure过滤和limit1/20另作等价检查。
完全相同完整JSON输出才有效；冻结基线是差分oracle，不只比被测helper。
至少512词的1节/2节两场景均降低15%中位wall，其余每场景不慢于
max(基线×1.15,基线+0.5ms)，且真实5个命中/未命中查询分别报告，不混合收益。
未达到门槛则不发布性能实现，保留负结果/检查点。

测试新增一次分词契约（修前失败）和固定随机/Unicode/tie/heading/fence/alias边界。
独立验收须检查implementation、reference_boundary、data_integrity、numerical_sanity、
measurement_validity、reproducibility六项并复跑至少真实语料+合成1/2/256节。
知识专项、完整tests、Reader通过，发布前fresh fetch并处理并发差异，普通推main且回读。
结果路径 agent_doc/results/fts-section22-20261019/；复用既有benchmark模式，新增
search专用runner，因build与search计时契约不同而不改旧历史runner。

### Plan v2：测量前契约补全

7对指7个交替pair（AB、BA、AB、BA、AB、BA、AB），不是7个ABBA块。
收益=1-median(candidate)/median(baseline)，不挑最佳样本，不以配对比值均值替代。
结果契约：id=fts-section22-20261019，producer=root，consumer=report/main-publication，
独立owner=另一个fresh-context fts22_result_review；required_result_refs必须绑定本次
raw.jsonl、runner源码hash、两份生产源码hash及此冻结Plan SHA。原始状态pending；
只有六项均pass后manual usable-with-scope；不宣称原生运行时认证。
validation_plan schema=manual-result-validation/v1，scope=local SQLite whole-search
exact-output/latency；每项allow_not_applicable=false：
1. implementation：读实际源码及镜像/CLI路由；改动仅片段选择且镜像一致。
2. reference_boundary：固定基线与候选全JSON差分，含边界输入；所有比较相等。
3. data_integrity：核对全部样本、输入hash、种子DB和源码hash；不可缺样或换源。
4. numerical_sanity：所有wall有限正数，独立重算中位数及既定阈值；无统计偏差。
5. measurement_validity：核对完整调用/计时区间及顺序，无不对称预处理或缓存。
6. reproducibility：独立执行真实语料及合成1/2/256节，检验等价和阈值；不达标阻塞。
实际prior/knowledge日志存 .agent-runs/fts-section22/{prior,knowledge}.json；首次230目录，
保存时因新结果目录扫描231，候选相同且partial=true，不称穷尽。来源笔记在
agent_doc/results/fts-section22-20261019/research.md。无新的advice作为授权或算法依据。

### Frozen evidence bindings

- validation-plan.json (experiment-validation-plan/v1): ecb9e58363d3d2071c38170ded5a91a219784b6c2bb95f7a8b6760f95dbf0808
- .agent-runs/fts-section22/prior.json: 57da19383d3c7ef0e785dfd34b2a1c655c4ce1a312d0fcf2e2de4dc8ce8ff06c
- .agent-runs/fts-section22/knowledge.json: f4931bb3489edfeac35e2dda3bb542b92f3ac6ead1d904b930adc161cb80d54b
- research.md: fb73cbd44243a17ffb8531edc4d305a00f2aa9615d6311bf874f1ca004dbcb88

上述结果目录为 agent_doc/results/fts-section22-20261019/；producer、独立validator与
consumer共同绑定validation-plan的同一hash。v2内manual-result-validation/v1为记录
类型描述，不替代本实际experiment-validation-plan/v1文件。本手工流程不产生运行时认证。

## Progress

已fresh fetch并同步main，检出干净；当前所有生产文件由主AI拥有，待独立计划审核。

独立计划审核最终批准稳定Plan b1318599c07a88bc45f384c0a6dd382926fbd3e3e7fadc5dc2b117ab66d4232e。
新增分词次数测试修前失败（2 != 1），等价性参考测试通过；实现仅两份片段选择源码。
首轮benchmark启动时知识专项仍在运行，存在已知CPU争用；整轮保留为contended.jsonl，
不用于性能验收。等专项结束后顺序重测原方案，不按数值挑选结果，不修改阈值/输入。

最终主测14场景/98对与独立12场景/84对完整输出相等，均过冻结门槛；独立六项验收
usable-with-scope。1/2节×512词主测耗时下降23.22%/34.56%，独立29.19%/36.05%；
真实查询没有可靠普遍提速，量纲复测慢12.28%、无词主测慢0.040ms等负结果均保留。
256×512词波动较大，不主张稳健收益。源码镜像8eb136aa…c34d9，runner15350846…7c62。
知识专项82、独立18、全库1273（8跳过）、Reader3通过，文档validate通过；
完整证据/局限见agent_doc/results/fts-section22-20261019/report.md及independent-review.md。
剩余主控动作：fresh fetch并按普通main发布、回读；持续任务整体不因本次有界优化关闭。
