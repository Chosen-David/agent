# 跨哺乳动物麻醉：信息整合、抑制分布与局部控制的证据层次

## 问题触发

跨哺乳动物信息整合 麻醉反应性与意识不同。先核对物种、测量、状态、任务和版本，再引用论文。

## 原论文结论与条件

人、猕猴、狨猴和小鼠研究发现多数麻醉条件下 fMRI 信息整合指标下降，并在猕猴丘脑刺激后恢复；小鼠一种混合麻醉存在例外，指标不等于通用意识量。

- species: human, rhesus macaque, common marmoset and mouse
- data: resting fMRI under wakefulness and multiple anaesthetics
- metric: information decomposition Phi_R, mostly aggregated region pairs
- intervention: macaque central thalamic DBS; region-specific inhibition in computational models

## 观测、对照与推导范围

- Fig.2 中多数物种/药物条件的平均Phi_R下降；鼠 medetomidine-isoflurane 对照未得到同样显著下降，不能写成全条件成立。
- 猕猴中央丘脑刺激伴随反应性与整合恢复；PVALB/Pvalb空间对应及物种约束模型提示抑制分布参与，须区别相关、干预和模拟。

这些是来源报告的结果；本轮仅核对相关原文与图注/方法，没有生物学、训练或性能复现；没有形式化证明。

## 算得出的例子

自拟冗余例：两个模块都复制同一比特Z，联合仍只有1 bit，不能把两份各1 bit算成2 bit独立信息；这不是Phi_R的数值实现。

## 失败、反例与外推限制

- 无行为反应可来自感觉断连/运动障碍，不是无体验的充分判据；Phi_R不等于IIT全部版本的Phi。
- 小样本、跨物种采集/剂量差异与成对聚合限制推广；机制模型不是全部生理因果的直接证明。

## AI 任务映射：尚待验证的启发

区分信息冗余、协同和控制节点，筛选可恢复跨模块信息流的方案；不把该指标作为AI意识或最佳性能的代理。

- 多模块 AI 中分别检查信息互补、冗余与有效全局利用，不能只最大化相关性或广播量。
- 若借用局部控制节点，保持通信预算并比较目标节点与匹配对照；先记录目标任务指标。

生物学发现不能授权跳过目标AI验收、用户指定实验或显式复现；检索相关度与条件字符串匹配都不证明科学适用性。

## 来源定位与未验证项

- [原文/定位](https://doi.org/10.1038/s41562-025-02381-5)：Results: Integrated information; Breakdown across species (Fig.2); thalamic DBS; gene-expression/model analyses; Discussion
- [原文/定位](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13121024/fullTextXML)：Open full-text XML; corresponding Results/Methods sections as above

检索日2026-10-07；来源版本与哈希见本轮 sources.json。原文全文/缓存保留私有目录，未镜像第三方内容。
