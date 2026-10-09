# 全局质量区间迁移报告_by_gpt

日期2026-10-09；MATH-57；文档限定。本轮没有新执行实验、回归、模型/GPU测量或token收益，不把历史53项回归当作本轮成绩。

新增任务级候选 `candidate.softmax-event-box@1`：从完整合法全集的logit盒推导保留事件质量的准确盒极值，再有条件地连接固定value几何与局部输出误差。沿用原知识Skill，未新建Skill或published卡。学科和问题结构入口、逐项前提、一般证明、符号正例/相关约束/候选分母/独立shift反例及后续验收矩阵均在[迁移设计](../../advice/全局注意力质量区间与near_far参数证书_by_gpt.md)。

实际先查历史，prior_search.json含49目录有界扫描和缺record的partial结果；命中凸输出/FW不同目标，无实测数据复用。实际search/show固定三个相关知识卡完整内容与引用，只作已读数学前提，不声称模型自主检索或历史数据已重新验收。

近期筛选Vertex-Softmax，arXiv2605.10974v1，2026-05-08提交，2026-10-09当前abs仅列v1；正式发表未确认。阅读Sect2/3、6和AppD，未复现实验或采用通用solver实现。该论文的实数盒精确性不能自动认证普通PyTorch浮点路径。CUDA固定版13.2文档相关exp/ULP表明确是非穷尽测试、不保证；拒绝仅据该表补几个ULP就宣称严格证书。

迁移保留精确softmax事件结构；模型q/k依赖、实际dense kernel、深层传播和端到端任务精度均未认证。near/far仍按原位置语义，质量密集不是near定义；实施前必须绑定位置分区/合法全集。数值实施不仅要外包exp/sum/div，还要向外计算最终 D*(1-m_lower) 与附加误差，避免理论上界本身向内舍入后被用于ε阈值。

独立计划审核见plan_review_verdict.json/plan_review_by_gpt.md，独立完成文档审核见document_review.json/document_review_by_gpt.md；document_manifest.json绑定实际文件。两者为真实不同新上下文的本地主机调用，不宣称已部署ReviewSession服务。文档审核不是experiment-validation回执，故没有伪造实验manifest/record或usable-with-scope实验成绩。

下一步：获取真实post-RoPE trace与完整mask/分母；建立有保证的超越函数参考与独立数值验收；同预算比较逐层证书配置、最佳全层固定配置和经验mass配置，核查输出/e2e及总成本。当前尚未取得真实模型/设备运行环境和trace；因此保留候选，不改生产、SGLang或原next_topic。
