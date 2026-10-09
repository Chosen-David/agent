# [MATH-64] value 运输耦合与输出误差证书

Task-ID: MATH-64
Date: 2026-10-09

## Plan

### 目标与方法

按用户持续知识建设要求补充有限运输与value输出界，原目标为按需建模/核对前提而非追求条目数量。EXECUTE；仅agent知识、索引/coverage/state、当前任务与本轮证据，不改SGLang、人类guide或生产行为。原指南缺失则保持缺失；无远端/GPU/模型假设。复用现有research-explore和知识入口。

经典对象：有限非负归一化α,β，固定values和线性W，π≥0行/列边际α/β。令Cij=||W(vi-vj)||，L_C=min<π,C>；||WΣ(α−β)v||≤L_C≤D·TV。任意可行π给输出上界；可行f_i+g_j≤Cij给最优运输成本下界，下界不是输出误差下界；相等认证运输最优。重复values的token间成本可零，此为value推前测度的W1而非token身份度量。自己的耦合/TV/近似value/Lipschitz扩展证明；经典LP来源Peyré/Cuturi 1803.00567v4，§2.3式2.10–2.11，§2.5命题2.4式2.20–2.21、页23，2020-03-18修订、2019出版。无需以强对偶替代弱对偶可复核证书。

近期：OTPrune 2602.20205v3（2026-04-01修订；原摘要Accepted CVPR2026，自报接收与正式来源区分）选择性读§3及A2；视觉feature的W2/second-order surrogate不能不核验映射便作为真实attention-V证书。AttSVD 2610.06927v1（2026-10-03），预印本，§3.2和附录B query/value metrics：非零ridge增加λ||E||F²，不能将正则化metric等同无正则logit误差；per-key diag mass是替代PᵀP的代理，不是相同目标。作者实验不作本库复现/收益。

### 冻结验收与资源

本轮fixtures.json冻结T1–T8及精确值：重复value无重合、二点等号、抵消、局部移动优于全局DTV、错误feature度量、近似value另计、非法质量/边际、非零ridge反例。检索三条无定理名问题见retrieval_protocol.json，两后端实际文件/FTS5-RRF、Top3六命中、Fano无关不加载，仅新卡+softmax前置两个条目≤16000字符；aliases精确命中只是公开结构测试。34知识/index回归。公开案例不当未见测试；holdout只哈希，不读内容。8-case proof/general informal proof非Lean，CPU Fraction不代替一般证明；时间/字符不是tokens。force mixture跨域例同量纲N；真实LLM token文本无该线性映射，仅保留探索建议。

预算1800秒，最多2次计划审核/返修，producer→独立verify_experiment_result→publish；独立计划调用approve后生产，另一个fresh owner独立结果回执后主AI钉定实际完成事件与receipt执行native gate。没有后台部署/ReviewSession身份认证声明。推送前重新同步，保留并发变更，非force直接main读回提交/树；保留原GPU和其他领域游标。

## Progress

- main同步0a532bf，角色/索引/状态/前置已读取；没有同主题本地运行状态目录（不推断远端无任务）。旧结果查询及KB查询取舍已保存。来源读取完成必要经典章节及近期限定段落；不宣称整篇审稿或复现。
