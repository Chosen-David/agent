说明：以下保留初版独立审查结论，路径说明已适配发布目录；未修改原始数学审查结果。原文在历史归档 `source-review/source-review.md`。当前整合状态见 [report.md](report.md)。

# 独立来源与逻辑审查

结论：accepted-for-bounded-knowledge-claims。接受两条候选的限定知识声明；不认证上游运行时、GPU 性能或真实模型实现。冻结审查对象及 SHA256 见 `review-result.json`，候选快照保存在本目录 `historical-evidence.tar.gz` 的 `source-review/reviewed-candidate/`。

## 已纠正问题

- SR-1，`ai.speculative-decoding-cost-bound.md` 算例1：v=4 的速度比原写 0.763…，正确值是 191/250=0.764。已回读修订。
- SR-2，`ai.speculative-sampling-residual-exactness.md` 的 Chen 来源定位：原写 §2；原文使用未编号小标题。已改 Algorithm 2 (PDF p.3)、Modified Rejection Sampling (pp.4–5)、Theorem 1 (pp.10–11)，JSON 同步。
- 当前被冻结的候选未发现阻塞知识层面接受的问题。若后续改动正文/前提/公式/来源，需比较差异后更新审查，不能沿用这次 SHA 接受任意新版。

## 固定来源及实际阅读

1. [Leviathan / Kalman / Matias, ICML 2023](https://proceedings.mlr.press/v202/leviathan23a.html)：PMLR 202:19274–19286。独立下载正式13页PDF，重点读 §2.1–3.5、A.1、A.3。§2.2–2.3 与 Algorithm 1 在 PDF pp.2–3；精确性证明 p.11；接受数近似和成本假设 pp.3–5。
2. [Chen 等, arXiv:2302.01318v1](https://arxiv.org/abs/2302.01318v1)：v1 2023-02-02 18:44:11 UTC。独立下载11页PDF，读 Algorithm 2、Modified Rejection Sampling、Theorem 1。原文 p=draft、q=target，与候选符号相反，不能按字母机械搬运比值。
3. [Li 等, EAGLE-3, NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/c7b5a35ea98b62512a869c19ea7b03cb-Abstract-Conference.html)：正式20页PDF，DOI 10.52202/085713-4562，独立下载并重点读 §2–3、§4.3、Table 3、Appendix A。§2.2 (p.4) 说明继承动态树；§4.3 (pp.8–9) 的特定吞吐实验反而使用长度3的链。论文实验设置不能当成本恒等式或本地测量。未读取全部附录或复现所有实验。
4. [SafeAILab/EAGLE 官方库](https://github.com/SafeAILab/EAGLE) 固定 `cb7e0841fe0c206c6ed74a197ad5e2a1f13f5a2b`，提交日期 2026-02-20T02:53:29Z。通过 GitHub API 独立解析 main，再按提交下载 LICENSE、README、utils.py、ea_model.py、cnets.py；没有执行这些文件。

全部原始来源文件的实际字节数、SHA256、代码 git blob SHA1 在 `source-manifest.json`；其中 file 仅是历史本地缓存名，文件本身不随仓库分发，可按 URL 重新获取核对。保留原始网页和源码仅供本地复核，不能把原始缓存整体当成应提交/公开的知识交付。

## 许可范围

- Chen v1 页面自身指向 CC BY 4.0。
- Leviathan 的正式 PDF 显示作者版权，PMLR 的[通用出版协议](https://proceedings.mlr.press/pmlr-license-agreement.html)列 CC BY 4.0；没有看到本篇签署合同或本篇独立许可声明。研究者锁中“正式PDF特定许可未独立确认”是合适的保守表述。
- EAGLE-3 的正式页/PDF中未确定具体复用许可。OpenReview 页面出现浏览器验证，没有完成验证码或绕过限制；无需依赖该页面完成论文身份和内容核查。
- EAGLE 固定提交的 LICENSE 明确 Apache-2.0、Copyright 2025 SafeAI Lab。不能由代码许可推出论文、权重或训练数据许可。
- 候选交付是原创中文解释、公式推导和算例，引用原源，不包含长段转载、上游实现或模型权重。

## 公式与适用条件审查

- 残差公式需要共同输出空间、归一化的实际 p/q、按 q 取候选、合法接受随机数与正确历史条件。候选明确处理 q(X)>0、p/q 支撑不包含关系及 Z=0 的不可达残差分支。
- top-k/top-p/temperature 后的目标分布是保证对象；不能拿原 logits 的概率做比值而另用 argmax 提议。greedy 是确定 tie-break 后的点质量问题。相同分布不推出同 seed 相同文本或不同 kernel 位级一致。
- 逐步条件分布与共同前缀、拒绝后的后缀丢弃、位置/KV 状态一致性是序列结论的前提。终止规则必须保持同一输出序列语义；长度公式明确排除了 EOS/max-length 截断。
- 尾和公式使用连续接受事件的联合概率；条件概率乘积成立不需独立。恒定条件接受率才给几何和，不能用无条件平均接受率替代。
- 串行固定草拟成本、固定/稳定轮成本、足够长序列及同基线口径限制均保留。v=1/o=0 下 alpha>c 的“存在正 horizon 严格获益”充要条件是候选自己的正确推导；不外推到真实验证成本。
- 任意树整轮接受数和 MTP 命中率不等于单提议 1−TV。局部确定性候选消元可映射 q=delta_c；其合法性取决于更新剩余分布与新接受随机数条件，不能认证任意树构造或核验器。

## 官方代码静态对应与不能据此断言的事项

固定提交的定位：
- `eagle/model/utils.py` L38–54：温度及 top-p/top-k 预处理；L360–373：greedy 分支；L383–415：按前缀筛选、候选去重、qx=1、拒绝后清零归一化；L458–464：后续抽样/argmax。
- `eagle/model/cnets.py` L762–827：top-score 节点选择、树 mask、路径索引。置信分数用于树选择，不能不加证明当作单链的独立 q 样本。
- `eagle/model/ea_model.py` L215–218：temperature>1e-5 才创建随机分支的 processor；L275–303：更新后再检查停止/长度并返回；L322–325、L367–380：基线的对应分支。该静态检查没有证明两者所有返回长度、EOS截断、batch、缓存和数值语义相同。
- `utils.py` 的 Python random 与 torch 抽样、有限精度 softmax、残差归一化，都没有被本轮跑通或做分布检验。不能把局部数学解释升级为“该固定版本已证明无损”。候选没有这样越界。

## 独立有限检查

实际执行 `python independent_math_check.py`，输出 `independent_math_result.json`：
- 225 对三元有理分布：恢复质量、零残差和 1−TV 恒等式。
- 240 个分布/确定性候选顺序组合：逐候选消元与最终剩余抽样恢复目标。
- 一个含不同历史条件和不重叠支持的二步输出例：9个联合概率坐标与目标链一致。
- 1620 个理想成本网格点：alpha≤c 不严格获益；gamma=1 的 alpha>c 充要比较。
- 修正算例精确值 191/250=0.764。

这是 reviewer 自写的有限代数语义检查，与 owner 的 verify.py 独立；不是模型性能测量、形式化证明或上游 sampler 单测。

## 隔离与剩余项

先读取并遵守 `knowledge/evaluation_holdouts.json`，没有查询/读取四个 reserved 目标论文、答案或结果；没有读取 SGLang 私稿，没有变更主库，没有使用 GPU、模型权重或上游运行时。知识接受之外的系统测试、检索评估和发布验收仍由相应 owner 负责。
