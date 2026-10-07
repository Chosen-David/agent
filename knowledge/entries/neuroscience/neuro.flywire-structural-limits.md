# 果蝇 FlyWire：全脑结构图的版本、阈值与缺失边界

## 问题触发

果蝇全脑结构图 阈值改变连接统计 电突触。先核对物种、测量、状态、任务和版本，再引用论文。

## 原论文结论与条件

成体雌性果蝇 FlyWire 提供可导航的神经元与化学突触图；论文分析绑定版本783，连接阈值与突触附着完整度会改变图统计，结构图不提供完整动力学。

- species: adult female Drosophila melanogaster; single specimen
- data_version: FlyWire materialization 783 as analysed in paper
- measurement: EM reconstruction; chemical synapses
- graph_rule: default analysed connection threshold at least 5 synapses

## 观测、对照与推导范围

- 重建约139,000神经元；正文区分自动检测的约1.3亿突触与成功连接到校对神经元的子集，不能混为同一计数。
- 论文报告突触前附着约93.7%、突触后约44.7%；≥5突触阈值下有2,700,513条连接，弱边与不同脑区分析需单独定阈值。

这些是来源报告的结果；本轮仅核对相关原文与图注/方法，没有生物学、训练或性能复现；没有形式化证明。

## 算得出的例子

自拟计数例：A→B有4个突触，A→C有6个；阈值5只保留一条连接。换阈值后图不同，不代表生物连接瞬间改变。

## 失败、反例与外推限制

- 仅化学突触；电突触、受体、调制与活动状态未被完整捕获，脑不包含全部腹神经索。
- 单雌性个体与重建误差限制跨性别/跨个体外推；突触数不自动等于有效权重或符号。

## AI 任务映射：尚待验证的启发

作为稀疏计算图、局部反馈和类型化节点的候选来源；成熟数据门户可用于定位结构，不复制整个连接组到系统提示。

- 检索/下载图前固定 materialization、神经元ID、脑区和边阈值，分清 synapse 与 connection。
- 若借用稀疏图或局部反馈结构，先与相同边数/度分布的对照比较；结构相似不构成性能证据。

生物学发现不能授权跳过目标AI验收、用户指定实验或显式复现；检索相关度与条件字符串匹配都不证明科学适用性。

## 来源定位与未验证项

- [原文/定位](https://doi.org/10.1038/s41586-024-07558-y)：Reconstruction of a whole fly brain; Synapses and connections; Discussion; Extended Data Fig.2; data release v783
- [原文/定位](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11446842/fullTextXML)：Open full-text XML; corresponding Results/Methods sections as above
- [机构博客（解释性来源）](https://alleninstitute.org/news/how-far-are-we-from-a-human-brain-simulation-and-what-does-that-mean-for-science)：Institution/author blog: context and resource pointers only; empirical claims checked against primary paper

检索日2026-10-07；来源版本与哈希见本轮 sources.json。原文全文/缓存保留私有目录，未镜像第三方内容。
