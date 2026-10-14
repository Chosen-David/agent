# KNOWLEDGE-FENCE

目标：修正既有知识索引“fenced code is not a heading”契约，保持接口、普通段落输出和源范围。T11持续优化的局部质量维护；不认证新Agent算法、模型收益或本轮十篇论文阅读。

授权：两个knowledge_index.py镜像、知识索引回归、任务与本run证据；验收后普通推送main，无PR/强推；guide和旧实验不改。

验收：固定16案例全部符合完整段落oracle且baseline确有失配；真实知识库未受缺陷影响的输出不变；独立复核、普通/-O、旧engine拒绝/重建及全库/Reader回归。来源为CommonMark0.31.2 §4.5。先查结果的partial/errors如实保留。

## Progress

- 2026-10-14：独立计划审核通过；固定baseline2393d96，原版11/16，修正后16/16，115条真实知识记录完整sections相等。新增三个回归测试，定向14项普通/-O通过。ENGINE_VERSION v4→v5触发旧缓存重建；不新增模型/GPU/付费资源。
- 完整结果与发布状态见[报告](../../results/knowledge-fence-20261014-0705/report.md)；本局部任务完成不关闭持续优化。
