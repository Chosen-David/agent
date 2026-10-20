# SYSTEM-99 正文阅读 E

2026-10-20新增1篇；同一未结束系统批次累计13篇。阅读前按ID/题名检索本库
results/docs/knowledge无命中；旧更正/恢复结果查询命中语料和通信计账记录，
不适用当前链路验收。HTML入口不可达后下载原PDF，未以搜索摘要抵数。

Cui等，[MemTxn: A Transaction Boundary for Source-Supported Updates and Complete-State Recovery in Agent Memory](https://arxiv.org/abs/2607.27834v1)，
`2607.27834v1`，2026-07-30。实际PDF9页，SHA256
`9360ef8010a9013817a28cbf929ecfa1868be1e349f422059dfcad61bb92b1c8`。
已读全部正文p1–7（Introduction、Related Work、Method、Experiments、
Discussion and Limitations、Conclusion），核对p5/7表1/4原页；参考文献p8–9
未逐项核验，图未全部视觉审读，无代码/原始trace复现。

- 方法：提案值须按顺序出现在原引文中，独立于答案模型决定写入；冲突按声明的
  时间真值契约选择版本；持久intent及完整active-map前像用于重开数据库后恢复。
- 实验：12个未见source item的60正例与179模板负例全部判对；不是普遍语义
  正确性。58个LongMemEval/10个LoCoMo历史的多键故障中，完整map恢复优于
  单键undo；需外部detector实际调用。matched-top8控制保留部分QA增益，不能
  混用默认检索深度24的eligibility分母。
- 消融/成本：移除组件影响检测/旧任务保留，降低门禁可靠率亦退化；表4中完整
  map更大且有写入/恢复开销。成本边界排除共享抽取/检索/答案调用，非请求提速。
- 局限：词序不证明来源真相或主客体关系；最新断言只在应用明确允许时胜出。
  完整intent/快照与被调用controller为可信前提，并发、重复故障及物理损失未保证。
- 本库adapt：阶段G实际观察“更正→受影响消费者→旧报告拒用→新版本复验”的
  全链，保留原始观测和旧回执；reject：直接引入词序授信、最新时间覆盖或整库
  回滚。原实现探针通过时只报告验收证据，不制造新生产修复或模型收益。
