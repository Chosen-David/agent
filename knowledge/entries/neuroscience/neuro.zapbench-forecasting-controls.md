# ZAPBench：全脑预测先校准基线、上下文长度与分布外刺激

## 问题触发

全脑预测基线 长上下文非总是更好 跨神经元信息利用。先核对物种、测量、状态、任务和版本，再引用论文。

## 原论文结论与条件

ICLR2025的单幼鱼全脑预测比较显示：长上下文多有利于远期预测，却非所有设置更好；简单刺激基线有竞争力，跨神经元混合与空间信息的收益需按设置核对。

- species: one larval zebrafish; 6 days post fertilization
- data: 71721 putative neurons; about 2 hours; 9 visual conditions; calcium traces/video
- evaluation: C=4 or 256, horizon H=32; MAE; 3 seeds; held-out TAXIS
- models: Linear, TiDE, TSMixer, Time-Mix and volumetric U-Net; mean/stimulus baselines

## 观测、对照与推导范围

- §4：长上下文通常改善较远预测，但U-Net单步预测有反例；长上下文的若干非线性模型表现接近。
- 短上下文32步时只有53/120运行优于刺激基线；TAXIS中的TiDE受未见刺激协变量影响，不能只报告训练条件平均。
- 跨神经元混合未显示稳定优势；短上下文U-Net较好，但不能从误差降低推断已恢复因果生理机制。

这些是来源报告的结果；本轮仅核对相关原文与图注/方法，没有生物学、训练或性能复现；没有形式化证明。

## 算得出的例子

来源设置核算：32×0.914s=29.248s；4步上下文约3.656s，256步约233.984s。该算术解释采样尺度，不是本机MAE测量。

## 失败、反例与外推限制

- 单个体、时间切片和钙信号限制跨鱼/真实电活动迁移；MAE不覆盖生成分布或因果解释。
- 本版全脑连接组仍在重建中；无需据此假定截至当前最新版已完成，使用前另查数据版本。

## AI 任务映射：尚待验证的启发

利用成熟全脑数据/基线筛选预测架构；迁移到 Agent 长程记忆先区分远期与近期指标及未知协变量，不重造该基准。

- 预测模型先复用公开均值/刺激基线及冻结切分，分别报告条件、步长、种子与OOD。
- 研究上下文或图结构时保持预算，保留单步退化和简单模型强基线；代码下载/训练未在本轮执行。

生物学发现不能授权跳过目标AI验收、用户指定实验或显式复现；检索相关度与条件字符串匹配都不证明科学适用性。

## 来源定位与未验证项

- [原文/定位](https://proceedings.iclr.cc/paper_files/paper/2025/file/668563ef18fbfef0b66af491ea334d5f-Paper-Conference.pdf)：§2–4; Figs.3–5; Appendix B/C and Figs.S3/S4/S7; official ICLR2025 PDF pp.4–9
- [作者技术博客](https://research.google/blog/improving-brain-models-with-zapbench/)：Institution/author blog: context and resource pointers only; empirical claims checked against primary paper

检索日2026-10-07；来源版本与哈希见本轮 sources.json。原文全文/缓存保留私有目录，未镜像第三方内容。
