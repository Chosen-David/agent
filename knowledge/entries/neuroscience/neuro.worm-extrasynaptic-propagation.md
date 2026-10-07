# 线虫：静态突触图不足以预测信号传播，需考虑突触外通信

## 问题触发

连接图无法预测活动 拓扑之外的通信 神经肽。先核对物种、测量、状态、任务和版本，再引用论文。

## 原论文结论与条件

线虫单细胞光遗传扰动与全脑钙成像显示，解剖约束模型与实测传播存在差异；UNC-31 突变对照支持致密核心囊泡依赖的突触外信号参与快速动力学。

- species: C. elegans head neurons
- method: single-neuron optogenetic activation and whole-brain calcium imaging
- comparison: wild type versus unc-31 mutant; anatomy-constrained model
- scope: evoked pairwise signal propagation; not freely behaving cognition

## 观测、对照与推导范围

- 测量23,433对头部神经元；Fig.3 的解剖模型即使拟合有线边的符号和权重，仍不能完整解释传播。
- Fig.4–5 的 unc-31 对照与候选神经肽/受体表达支持突触外通信；部分响应发生于亚秒尺度，不能把这类调制一概视为慢过程。

这些是来源报告的结果；本轮仅核对相关原文与图注/方法，没有生物学、训练或性能复现；没有形式化证明。

## 算得出的例子

自拟通信例：A 没有直接调用 B，但 A 写共享变量 g、B 读取 g，仍存在 A→g→B 的影响路径。该例不模拟神经肽扩散。

## 失败、反例与外推限制

- 钙信号、单细胞刺激及实验状态不等于膜电位或自然行为；未显著响应不等于永远不存在功能连接。
- UNC-31 影响致密核心囊泡释放，不能据此把每条响应都归因于某一个肽；结果不说明解剖信息无用。

## AI 任务映射：尚待验证的启发

将固定路由与状态相关广播分开建模，检查被静态调用图遗漏的通道；不据此新增无约束的全局共享状态。

- 若设计 Agent 通信，分别列出直接调用、共享状态和广播信号，核对间接路径与时延。
- 比较固定拓扑与增加状态调制的最小对照，保持通信预算和任务相同；仍需目标 AI 实测。

生物学发现不能授权跳过目标AI验收、用户指定实验或显式复现；检索相关度与条件字符串匹配都不证明科学适用性。

## 来源定位与未验证项

- [原文/定位](https://doi.org/10.1038/s41586-023-06683-4)：Results: Functional measurements differ from anatomy; Extrasynaptic signalling; Figs.3–6; Discussion; Methods
- [原文/定位](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10632145/fullTextXML)：Open full-text XML; corresponding Results/Methods sections as above

检索日2026-10-07；来源版本与哈希见本轮 sources.json。原文全文/缓存保留私有目录，未镜像第三方内容。
