# 斑马鱼脑干：模块化回路与眼位记忆的受约束前向模型

## 问题触发

模块化眼位记忆 生理约束前向模型 斑马鱼。先核对物种、测量、状态、任务和版本，再引用论文。

## 原论文结论与条件

幼体斑马鱼脑干连接组可分出眼动与身体运动相关模块；在符号、归一化及动力学尺度等约束下，模型预测眼位敏感性与慢动力学的群体分布。

- species: larval zebrafish brainstem; separate EM and physiology animals
- task: body-fixed spontaneous ocular fixation
- model: linear rate network; known signs; normalized synapse counts; fitted beta and tau
- comparison: population distributions; actual versus potential synapses and shuffled blocks

## 观测、对照与推导范围

- Fig.2–4 的循环连接与两个弱耦合眼动子模块，提供低维慢动力学的结构解释。
- Fig.5 用实际突触构建的模型能匹配群体眼位敏感性和衰减特征；仅用邻近的潜在突触不能同样匹配。
- 慢尺度观测下，两块与七块打乱模型都能匹配主要动态特征；现有实验不能仅凭该特征辨别所有细粒度机制。

这些是来源报告的结果；本轮仅核对相关原文与图注/方法，没有生物学、训练或性能复现；没有形式化证明。

## 算得出的例子

自拟线性例：离散状态 x[t+1]=0.9x[t]，10步后为初值的0.9^10≈0.349；特征值靠近1延长保持，但不是动物的实测参数。

## 失败、反例与外推限制

- 不是无参数的结构→功能证明：连接符号、输入归一化、整体增益及时间常数使用生理约束或拟合。
- EM与钙成像来自不同鱼，比较是群体分布；身体固定、线性化及忽略调制限制迁移。

## AI 任务映射：尚待验证的启发

研究分模块递归记忆与不同时间尺度；先问细节是否能被目标任务辨识，再决定增加模型复杂度。

- 区分直接测到的结构、已知生理约束和拟合参数；设计记忆模型时逐项记录。
- 先选能区分候选机制的观测尺度；只看慢动态可能无法辨别更细模块。

生物学发现不能授权跳过目标AI验收、用户指定实验或显式复现；检索相关度与条件字符串匹配都不证明科学适用性。

## 来源定位与未验证项

- [原文/定位](https://doi.org/10.1038/s41593-024-01784-3)：Results: Axial and oculomotor modules; three-block cycle; Predicting neural coding and dynamics; Figs.2–5; Discussion
- [原文/定位](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11614741/fullTextXML)：Open full-text XML; corresponding Results/Methods sections as above

检索日2026-10-07；来源版本与哈希见本轮 sources.json。原文全文/缓存保留私有目录，未镜像第三方内容。
