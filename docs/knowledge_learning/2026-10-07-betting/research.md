# 概率基础与近期候选（检索日期2026-10-07）

经典机制：条件期望塔式法则、非负（超）鞅、Ville最大不等式。权威定位：Waudby-Smith/Ramdas，Estimating means of bounded random variables by betting，https://arxiv.org/html/2010.09686v7 §2与§4 Proposition 2，v7=2022-08-25；版本信息直接核查 https://arxiv.org/abs/2010.09686 。读取相应章节，不声称全文复现。一般条件均值成立时不用额外要求独立；仅边际均值不够。

该预印本正文使用开区间下注范围；本条允许闭端点的非负过程，由自己的端点因子与条件期望推导核验，也与2026候选§2的闭区间形式一致。零因子吸收单独检查，不把严格正鞅的所有等价表述延伸到零下注或端点。

近期研究复查：Learning to Bet for Horizon-Aware Anytime-Valid Testing，https://arxiv.org/abs/2603.19551v2 ，v2=2026-06-02，页面备注to appear in ICML 2026；正式proceedings未独立核验。读取 https://arxiv.org/html/2603.19551v2 §2与§4相关段落。截止预算、财富和过去统计量用于选择下注；论文DQN优势为作者的经验结果。本轮只验证背景有效性，不训练DQN、不复现学习策略、不采用性能主张。

方差自适应候选仍未采用：v7 §3.2–3.3的predictable plug-in和§4的capital process提供不同构造。使用过去估计方差挑参数仍须满足原方法的可预测与范围条件；不能自行把同批样本方差塞进经典界就声称有效。下一轮可单独核验其数值反演与覆盖。

上轮待核的arXiv:2608.21694再次检索到摘要，但固定v1直接访问仍失败；只记未核线索，不批准Gaussian-efficient结论、版本或发表状态。没有以二手评述代替论文证明。已出版JRSS B页面本轮直接访问失败，使用已核预印本固定版本作证明来源。
