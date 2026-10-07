发布说明：下列机械证据/历史候选相对 historical-evidence.tar.gz 内 source-review/r3/ 及研究目录。正式最终结果另见 [integrated-scope-review.json](integrated-scope-review.json)。原文和哈希映射保存在归档清单。

# R3 别名与既有条目重叠的独立审查

结论：接受冻结 r3 的有界别名语义和非重复性；没有阻塞发现。完整哈希绑定见 `review-result.json`，可复验机械证据见 `alias-scope-proof.json` 和 `verify_alias_scope.py`。这不代表检索效果验收或发布完成。

## 变更边界与证据复用

- 四个候选文件均匹配 `research/candidate-freeze-3.json`。
- r1、r2、r3 两两比较：每张卡的 JSON 只改变顶层 `aliases`；该数组之外的原始 JSON 文本也完全相同，两个 Markdown 正文逐字节相同。
- r1 四个哈希同时匹配原独立来源审查及其 `reviewed-candidate` 快照。因此原正文、前提、公式、来源和强依赖审查可按身份继承，未重做或升级证明状态。
- 55 项机械断言通过。该计数包含文件哈希、字段/原始文本差异、快照一致性及固定上游核对，不能写成 55 项独立科学实验。

## 别名语义

r3 保留了有意义的机制和边界词，并加入明确的算法名称；新增的 `modified rejection sampling` 与已提供 Chen v1 原文标题、Theorem 1 用语相符。`walltime analysis`、`推测解码成本模型` 对应正文的条件成本分析，不表示已测 walltime。

少数别名是问题检索词组，并非严格同义词或独立科学断言。尤其 `greedy same seed distribution equivalence` 指向正文对三者的区分，不能读成“greedy 或 same seed 保证分布等价”。`tree MTP throughput latency boundary` 和确定性候选消元也只指向明确的适用边界。逐条理由见机器审查结果。

移除某个别名里的 residual/长度不会删除知识：剩余质量、条件尾和和 horizon 的定义仍在未变的结构词、前提和正文中。这里仅确认语义合理，不推断排名改善、无串扰或未见查询表现。

## 与既有 Infra 卡的关系

已核对上游 `infra.speculative-acceptance` 的 JSON/Markdown 与提交 `a35a102306e3aba0af1a5180390b226febe14705` 完全相同。

- 旧卡是经验案例：固定 TPU-v4、T5-XXL、batch=1、WMT/CNN-DailyMail 的论文观测，以及最小迁移检查。
- 新残差卡是正确性基础：真实提议规律、正部剩余质量、支撑/零残差、正确前缀、反例及局部候选消元。
- 新成本卡是推导工具：不要求独立的条件前缀尾和、c/v/o 分项、限定的 α>c 阈值、相关性及过长 horizon 反例。

它们在用途上互补，适合分别保留。但相同原论文、“接受率不单独决定速度”、α=0.8/γ=4 的 3.3616 例子及部分边界是重叠内容，不能算成新增独立证据、实验结果或复现。

## 导航建议

批准在新成本卡追加 `related → infra.speculative-acceptance`，保留现有 `requires → ai.speculative-sampling-residual-exactness@1` 和对应 prerequisite 导航。这个单一 related 边已经足够：成本卡直接对应旧经验案例，分布正确性基础可由现有依赖到达。残差卡再直接连旧卡可以作为可选导航，但不是必要关系。

不要把旧经验案例写成数学推导的强依赖，也不要用 corollary/application 边暗示旧测量是从新卡推导出来的。发布报告应说明“经验案例＋推导基础”的分工与共享来源。

该关系尚未在本审查中写入或读取实际整合产物。增加关系后，发布 JSON 已不同于“仅 aliases 改动”的 r3 冻结：应保留 r3、另记导航变更、冻结实际发布哈希，再校验 schema/链接及适用回归。这里的语义批准不等于对未见发布字节的验收。

## 隔离与任务归属

没有读取检索题目、gold 或结果文件；只在冻结文件内看到作者列出的反馈类别标签。没有读 reserved 目标内容，没有读取或修改 SGLang、没有修改仓库或候选文件。只写本目录，无发布动作。

本结果支撑 AIK-02 的独立别名/重叠审查，保留 AIK-01 已审查正文身份。检索与其他验收、AIK-03 的整合/回归/发布及远端读回由主 AI 继续完成。

## 实际整合版本补充验收

主 AI 随后提供实际整合文件。本次已完成独立回读，最终结论以 `final-review-result.json` 为准：

- 四个文件均与修正后的 `final-candidate-freeze.json` 匹配，最终冻结 SHA256 为 `83aec83b640aca8b75475a708783d6034dd742ba8962f6f3f9e87f8e5dcf9fce`。
- 从原始 r3 到最终文件，实际差异严格限于 status、verification.proof、verification.checks，以及成本卡新增的一个 related 边；所有别名、正文、公式、前提、来源和强依赖保持不变。
- 22 项整合范围/哈希检查通过。上述关系已实际写入并按字节核对，原“尚未验证整合字节”的限制已由本补充验收解除；整体语料快照、回归和发布仍不在此审查范围。
- 初始最终冻结把变更写成含糊的“status only”。已报告主 AI 并由其拆分原始 alias 冻结→整合、整合→本地 published 两段说明，回读关闭 R3-PROVENANCE-1；修复未改变候选字节，初始不一致证据保留在 `integrated-scope-proof-before-freeze-correction.json`。
- `published` 是本地知识检索状态，不能据此报告 Git/远端已发布。详细时间线来自 owner 记录，此审查没有独立核准其时间戳；字节及变更范围验收不依赖该时间戳。
