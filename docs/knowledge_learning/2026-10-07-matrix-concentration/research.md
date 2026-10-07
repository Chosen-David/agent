# 本轮研究筛选：2026-10-07

主题有界为二阶矩谱误差、样本独立性与校准方向。固定版本/日期/PDF哈希见sources.json，3篇一手来源；相关页核对，不宣称完整读完/复现。Tropp经典原文Theorem6.1.1及proof路径支持基础卡。

## 近期1：cross-covariance

Chen与Sanz-Alonso，arXiv2605.16733v1，2026-05-16，检索日最新版本仍v1；预印本，未核实正式发表。阅读Theorem2.1、Remark2.2、Theorem3.1与从后者到前者的归约。均值为0的iid向量对(X_i,Y_i)；X、Y各自sub-Gaussian，可在同一对中任意相关；两个非零边际协方差的有效秩和共同决定界。不能把“对内相关允许”解释成“沿时间的向量对可以相关”。隐藏常数及sub-Gaussian参数未认证，故保留为研究候选，不制成可部署数值阈值。

迁移候选：独立文档内按预设位置生成一对query/key，研究其cross moment；真实token pair的分布、跨文档独立与中心化必须核对。该研究估计二阶交叉矩，不自动给indexer平方score loss的四阶联合矩分解。本轮不更改NoPE白化假设或生产行为。

## 近期2：data-dependent subsets

Liu、Wang、Balzano，arXiv2606.24766v1，2026-06-23，检索日最新版本仍v1；预印本，未核实正式发表。阅读§2.1 Theorem1/2声明与选样依赖/非空概率解释。标准Gaussian独立原始向量，Theorem1对所有满足最小比例的子集同时给谱下界；upper结果有相应比例条件。其保证是原始总样本规模与比例相关的谱包络，不等于任意选样后仍无偏或接近原协方差。证明/常数及一般化未全面审计。

本轮拒用迁移：把选择后的高分token或cluster成员视为新的iid calibration样本。特殊Gaussian/比例/同时界未获数据证据；一般embedding不由热图证明Gaussian。精确合成反例保留选择造成目标改变，不能用此近期定理免除审查。

## 采用边界

采用经典有界固定样本矩阵界与明确方差推导；两个近期结果保留条件、机制、不成立迁移和下一阅读位置。没有新Skill、没有声称“最新论文证明当前Agent更好”。后续优先验证document-level采样协议与跨文档依赖，再考虑effective-rank和dependent/heavy-tail工具，不无限扩展文献。
