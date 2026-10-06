# 来源筛选（2026-10-06）

经典：Gregory W. Thomas 作者讲义 https://ai.stanford.edu/~gwthomas/notes/concentration.html ，页面无版本日期；核查 Hoeffding 引理与独立求和证明，不复制讲义。当前条目补充端点、零范围、配对差值与自己的逐次预算推导。

近期候选：Taga/Oymak/Shekhar, Learning to Bet for Horizon-Aware Anytime-Valid Testing，https://arxiv.org/abs/2603.19551v2 ，v2 2026-06-02；页面备注 to appear in ICML 2026，未另核正式 proceedings。已读HTML §1–2；未声称全文审稿或复现。
https://arxiv.org/html/2603.19551v2 §2式(6)–(9)要求下注量由过去决定并落在合法范围，使财富非负且零假设下为鞅；这是停止有效性的基础。§1把截止预算加入目标。学习策略的经验优势是作者主张，本仓库未验证，不能把策略学得好当成统计有效性证明。
迁移候选：冻结Agent评测的有界分数与剩余预算可对应论文对象；实际任务复用、模型修订、非独立样本会破坏前提。先对冻结评价流比较误判率、区间宽度、评测次数与推理成本，再考虑接入；不训练DQN、不安装作者代码。

另一近期检索结果：Martinez-Taboada/Ramdas, Gaussian-efficient testing by betting on the mean of bounded data，arXiv:2608.21694。检索返回摘要但直接页面读取失败；未核版本/出版状态或正文，仅保留下一轮查证线索，不用其结论批准条目或行为。

已出版背景：Waudby-Smith/Ramdas, Estimating means of bounded random variables by betting，JRSS B 86(1), 2024, 1–27，doi:10.1093/jrsssb/qkad009（在线2023-02-16）；核查出版页面与概述。其方差自适应方法未复现，不称本条联合界为该论文算法。
