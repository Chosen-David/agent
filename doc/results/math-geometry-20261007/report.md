# MATH-27/28：输出几何与局部敏感度

本轮补入 `math.attention-output-geometry@1`，复用 model-with-knowledge，没有新建Skill或修改SGLang/生产attention/通信。经典数学内容是固定线性映射的Gram半范数、softmax的局部Jacobian、显示证明的Taylor余项，以及固定线性分类器的严格margin条件；不是新颖性或实际模型收益声明。

## 真正增加的推导能力

从实际概率权重差δ、value V和输出投影W，得到精确输出误差平方 δᵀVWᵀWVᵀδ；利用归一化去掉共同value偏移；局部logits目标由G=J C J给出，并有D·osc(e)²/8的一阶输出余项界。对应条目区分有限精确权重比较、固定有限logits局部比较及下游固定线性margin。查询改变、value变化、硬mask或非线性下游不能无条件套用。

公开迁移实例：同二范数的两组权重扰动，固定values=(0,1,100)时输出变化分别.01和1；固定线性浓度传感器乘2后变化.02。相同概率误差不能唯一确定输出质量。公开失效实例：非线性化学反应拒用、hardmask拒用局部Taylor但可用实际概率Gram、Agent文字压缩无固定线性混合对应。未对真实模型trace或LongBench作质量结论。

## 来源、研究对照与负结果

2026-10-07核对Petersen–Pedersen Matrix Cookbook 2012-11-15版，§2.4.2 Eq81和§2.4.4 Eqs96–98，印刷页11–12；只作为二次型/微分参考，attention专用公式在条目中独立推导。

Prism最新可见arXiv版本v2，2026-05-25修订，arXiv作者comments标ICML2026；本轮未独立核对会议proceedings，故不额外认证发表状态。定向读取§3.2–3.4、§4.1/4.4与附录§6，并核对作者仓库YaRN说明，不称全文所有实验精读。来源 https://arxiv.org/html/2602.08426v2 。

采用固定内容/固定频率的几何级数池化等式及其前提；保留双频段温度校准作为实际trace上的候选。频段能量与pooling解释不构成value输出或e2e最优证明。B=8、θ=2π/8、固定内容时平均旋转为零，有限温度无法恢复零信息；反向随位置旋转的内容则池化为1，说明固定内容公式不能外推任意内容。Prism附录残差项应保留，不能把其均值项衰减解读为整个信号必然消失。未复现作者GPU/模型性能。

## 结果、检索与成本

`verify.py`执行570项：568项有限数值检查，2项显式人工前提检查，不是570个模型验收任务。随机seed2707，80组固定shape/float64构造，n=1、共同偏移、PSD/局部null方向、严格margin和pooling边界均覆盖。独立验证见independent/；一般数学结论依赖条目显示证明，不依赖随机数值样例，不是Lean形式化证明。

4个公开、未点名定理的开发检索题，包含浓度跨域和不适用反例，文件/SQLite两后端Recall@3均为1。拒用由人工前提核对，不是模型实测。8个旧开发题两后端原始平均Recall@3仍.809524、关联context recall仍.857143；baseline来自删去新卡的隔离旧语料副本，旧卡字节未改，原有漏检未隐藏。默认关联包部分请求仍partial；相关度和命中不认证应用正确。

只加载新条目与必要softmax前置两卡，无related扩展，max_entries=2、max_chars=20000。完整JSON实际cl100k_base编码6867 token、10905字符；这是本地编码，不是实际模型tokenizer/账单、效果或节省实测。真实模型调用0；CPU执行duration只是开发验证计时，不是GPU/生产性能。正式模型评测须记录真实工具、token预算和质量对照。

验收前冻结validation-plan和producer→independent verify→consumer DAG，manifest绑定实际代码、输入/config、原始输出与环境。既有结果先检索14目录、5个候选，旧softmax数据没有本轮Gram/Jacobian主张，其他目标不匹配，所以未把旧pending数据当新验收。无tmux/持久模型adapter，不声称后台部署；当前本地run目录用于同任务去重和接续。没有人类guide目录，未创建或修改它。

相关unittest 92/92通过；知识结构86项（83 published、3 candidate）、知识refs和插件镜像通过。只更新知识与接续记录，不改变生产选择器。未生成/未运行的独立留出题只有协议，实际未见模型测试仍缺；公开开发题不可再次称未见。

## 下一步和采用门禁

取得真实Q/K/V与W的固定trace，按文档ID冻结未用于选择的留出；在相同索引字节/最终KV预算下比较FC选择、FC+low-rank残差、实际输出目标。离线Gram/Jacobian用于诊断或训练候选，不在线形成n²矩阵；输出差可直接O(nh)计算。随后同模型/权限/可比预算验证任务质量和实际延迟，必要时记录概率误差较小但output/e2e更差的负结果。没有可靠收益前不部署。未知依赖/协方差队列保持。

发布状态见publication.json；实现提交号在远端核对后写入独立发布记录，报告本身不冒充推送成功。

独立验收完成：568项数值复现及2项人工前提记录核查；额外162项60位Decimal导数/余项检查、625项Fraction分类器扰动检查，以及精确Gram/平移/null方向检查通过。既有验收入口返回 `usable-with-scope`，仅限固定有限value的数学结构与公开CPU验证；详见accepted.json与independent/review.md。
