# MATH-25/26：归一化输出误差桥

新增能力是从固定有限 logits 误差或保留质量，带条件地推导 value 加权输出误差；不是以卡数量表示模型能力。复用 model-with-knowledge 入口，未新增 Skill/生产算法，未修改 SGLang。

## 数学与迁移

`math.softmax-barycenter-error@1` 给出可复核实数推导：输出误差≤value直径×TV，TV≤tanh(logit误差振幅/4)；剪枝误差≤D(1−p_S)，并把剪枝、保留集合上logits、value近似分成三项。硬mask不满足同支持集有限logits前提。对子空间indexer的解释：代理只用于选择集合、最终用完整logits/value时，后二项为0；不把预测器误差重复记入输出归一化。不能由此批准跨频率无损融合。

具体公开反例：α=(.45,.30,.20,.05)、v=(0,1,0,−6)，最大质量的两个token给输出误差.4，重合率只有½的另一个两token集合误差0。它说明排序/质量不决定具体value输出；不是FASA实测或端到端精度证据。跨领域实例是固定force的非负归一化混合，直径和误差单位N；signed权重和非线性执行器拒绝直接套用。Agent文本消息没有线性对应，通信省token迁移不成立，本轮不修改消息压缩。

## 来源和取舍（2026-10-07检索）

经典出处是Levin–Peres第二版作者PDF，§4.1 Proposition4.2/Remark4.3，pp48–49，核对TV恒等式；tanh和任务分解独立展示，未声称新颖。

OVAL arXiv:2610.06686v1，2026-10-05提交：读取§3与A.2及相关局部前提，采用输出敏感度/检索质量应分开的判断，不把局部均匀/isotropic谱目标当全局最优。

MC-Sparse arXiv:2610.06801v1，2026-10-05提交：读取§3–4、Algorithm1与§5相关表，保留其同密度oracle分解作为实验设计候选。式(1)最大化保留质量并非最小实际value输出误差；扩散步残差复用依赖跨步稳定性，不能直接接入自回归indexer。两篇截至本轮所见仅v1预印本，无正式接收信息；定向阅读不是全篇全附录覆盖，本机未复现作者模型/速度。版本/范围见source-checks.json。

## 验证、成本与限制

初次force样例误设取等号条件；失败保留failure-v1.json，修正为尖锐两点构造后新result/run v2。prepare脚本首次缺PYTHONPATH，修复后DAG通过。v2的416项CPU float64检查全部通过；独立角色重新运行，所有记录一致，另做12项90位Decimal参考。冻结manifest、协议、完整哈希和六项独立审查见independent/；真实collaboration开始/完成由root显式认证，host-adapter只读固定review哈希，不将JSON自报pass当授权。仅该数值范围usable-with-scope，极端极小子集概率的浮点下溢未覆盖；一般结论依据显示的数学证明，非数值证明或Lean。

4个无定理名称公开检索题，包括force跨域和错误前提，双后端Recall@3=1。错误前提的拒用是人工结构核对，不是模型实测。8个旧公开题的原始top3与召回均不变；原有平均Recall@3=0.809524、context recall=0.857143的漏检仍存在，没有掩盖。新导航关系改变少量扩展context，但正确期望命中未下降。保留未见题未打开/运行；本轮公开题不能再当未见测试。

单卡预算max_entries=1、max_chars=20000，无related扩展；上下文JSON约3710 cl100k_base token，字符预算实际5621（含外层JSON的实际计数6191）。这是开发估算，实际模型调用0、账单token未知；无实测节省/效果提升。数值脚本计时约0.026秒，仅验证duration，不是生产性能。检索耗时、索引加载范围明确写入原始JSON。已有result搜索在实验前做过，新保存查询结果不授权复用pending历史语料集成数据；其任务/度量与本数学目标不同，未替代本轮检查。

相关unittest 66/66和Reader通过；初次错误模块名以及随后README插件镜像过期的失败保留运行日志，重同步后完整相关集重跑通过。知识结构85项（82 published、3 candidate），格式校验、引用核对、插件字节同步通过。没有tmux或实际模型adapter，不声称监督部署或同模型A/B。

## 续接与发布

MATH-25完成数学、研究筛选、有限迁移和独立检查；MATH-26已完成main刷新、直接提交与远端读回；publication.json记录实现提交。下一步须固定真实indexer Q/K/V trace及输出W，按文档冻结留出，在相同索引字节/最终KV预算下对照CA/质量/输出敏感方案；再用同模型工具预算做端到端验证。未知依赖/协方差队列保留，无收益证据前不部署方案。

发布整合：远端同步发现1d516dd并发自同步修改；保留SELF-SYNC任务与CODEMAP，未更改其实现。结果目录与result_id不符的注册被正确拒绝，保留registration-blocked-layout.json；移至math-softmax-20261007-v2后重新固定哈希及独立验收，不复用过期pass。

整合后全仓unittest最终输出：

```text
----------------------------------------------------------------------
Ran 737 tests in 54.688s

OK (skipped=8)

```

实现已发布且读回：`10aa87fc2a752fbcce8f149fffd6965906512b7c`，完整树`872358594b0933b207af1e1e5021b46369431175`。注册记录本身仍是pending provenance，真实scoped使用须显式提供当前已认证host-adapter；accepted.json是这次实际独立检查，不把记录自带JSON当未来权限。
