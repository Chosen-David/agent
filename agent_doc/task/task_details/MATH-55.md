# [MATH-55] 有限随机投影与打分

Task-ID: MATH-55
Date: 2026-10-09

## Plan

授权：持续基础知识建设；直接main发布。主写者root，SGLang/guide/生产行为/未用测试内容禁止修改。

方法：iid N(0,1/m)高斯矩阵，固定且独立于矩阵的Q个query、N个key；归一化后用u±v的至多2QN事件，以chi-square MGF与Chernoff给出c=epsilon²/4−epsilon³/6，再极化内积误差epsilon||q||||k||；strict margin衔接math.topk-margin。零向量、间隔等号、自适应核向量、F=diag(1,99)求逆反例。经典来源与2026 preprint v2明确分开。

验收：完整非形式化证明审核、10个有理数/维度公开检查、三条不提示定理名结构检索的file/SQLite两后端，相关知识回归与镜像检查；没有模型实测，不报告能力/e2e/token收益。旧未用测试仅固定元数据哈希，不读取内容。

DAG：独立新上下文计划审核→生产→另一独立上下文verify_experiment_result→验收消费者→fresh fetch/非强推main/远端核验。1200秒、最多2个审核cycle/2个生产attempt；无远端监督服务或GPU，不宣称已部署，真实调用生命周期本地记录。

历史检索已执行，原始partial与缺record错误保留；相关旧数据前提不一致不复用，仅复用排名间隔条目。保持其他任务与next_topic游标。

## Progress

- startup main bfb4397清洁，fresh fetch一致；原始论文限定章节已读取。

- 独立计划审核approve；另一上下文结果审核usable-with-scope，宿主观察实际完成并固定回执。
- 10公开边界、6结构检索、53回归及镜像检查通过；509绑定前后相同。没有概率覆盖、Lean、LLM或GPU/e2e/token收益测量。
- September2026距离排名preprint保留候选，最新版本未确认，不采用定量渐近迁移；失败attempt和manifest v1保留。
- main科学提交0ae64c7927bec9e8e47376d4e29de814c9d41a1f，经fresh fetch SHA/tree及独立ls-remote核验。
- 原next_topic GPU残差候选游标保留；下一步真实冻结trace的误差/gap/output/e2e与成本对照。报告：agent_doc/results/math-random-score-20261009/report_by_gpt.md。
