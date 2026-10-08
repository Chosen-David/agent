# [MATH-55] 有限随机投影与打分

## Plan

授权：持续基础知识建设；直接main发布。主写者root，SGLang/guide/生产行为/未用测试内容禁止修改。

方法：iid N(0,1/m)高斯矩阵，固定且独立于矩阵的Q个query、N个key；归一化后用u±v的至多2QN事件，以chi-square MGF与Chernoff给出c=epsilon²/4−epsilon³/6，再极化内积误差epsilon||q||||k||；strict margin衔接math.topk-margin。零向量、间隔等号、自适应核向量、F=diag(1,99)求逆反例。经典来源与2026 preprint v2明确分开。

验收：完整非形式化证明审核、10个有理数/维度公开检查、三条不提示定理名结构检索的file/SQLite两后端，相关知识回归与镜像检查；没有模型实测，不报告能力/e2e/token收益。旧未用测试仅固定元数据哈希，不读取内容。

DAG：独立新上下文计划审核→生产→另一独立上下文verify_experiment_result→验收消费者→fresh fetch/非强推main/远端核验。1200秒、最多2个审核cycle/2个生产attempt；无远端监督服务或GPU，不宣称已部署，真实调用生命周期本地记录。

历史检索已执行，原始partial与缺record错误保留；相关旧数据前提不一致不复用，仅复用排名间隔条目。保持其他任务与next_topic游标。

## Progress

- startup main bfb4397清洁，fresh fetch一致；原始论文限定章节已读取。
