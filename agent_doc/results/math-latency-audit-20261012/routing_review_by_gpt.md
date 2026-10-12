# Three public-query structure audit

这是parent对已固定CLI输出的解释，不是模型检索/拒用实测；查询已经公开，不是未见测试。三个问题与实际成本、排名和完整输出见queries.json。没有修改检索器、摘要或候选。

| 问题结构 | 实际top3 | 有条件的应用和拒用 |
| --- | --- | --- |
| 局部模块变快但整体没提升：对象为组件、整体时间与开销；固定工作和串行分解未知 | MATH95 first score4；两条无关历史结果各1 | MATH95只有互不重叠I/R、其余R不变且同质量/计时口径时给S=1/(1-p+p/s+h)；题干本身不足以证明前提，FLOP占比不能当p。 |
| 两条并行分支一样慢：对象为两条必须完成的分支；是否争用/是否必须都完成未知 | MATH95 first score1，MATH96 second score1 | MATH95相关但没有并列路径一般敏感性式；继续核对MATH96。在固定图/无限资源/最早就绪模型中A=B使仅缩短一节点节省0；共用有限执行器时拒绝此零收益结论。 |
| 无依赖但共用一个执行器：对象为多个必做任务，明确资源有限 | MATH96 only hit score3 | MATH96明确拒绝把span当实际makespan；既有两个各10单位任务的公开例子，单执行器总20而span10。拒用无限资源等式不等于无法建立有限资源模型。 |

按现有双索引，MATH95属于performance-modeling/ai-infra及serial exclusive time结构；MATH96属于discrete mathematics/performance-modeling与fixed DAG/parallel join结构。导航按需加载，最多读这两个完整候选及必要前提，不将整个库送入上下文。排名是词法相关度，不是适用性证明；第二题必须避免first-hit-only。

具体迁移复核：多AI会议中每位必须提交报告的调用对应节点，真实先后依赖对应边；若两位独立且同耗时的必做报告能同时开始并无资源争用，MATH96并列路径预测单独加速一位不改变会议结束时间。必须全完成、固定输出质量、固定图/其他耗时和无争用关系才被保留；真实API限流、动态停止、资源与报告内容影响均未知。GPUindexer→组件的MATH95映射仍须实际exclusive trace与不变R；并行kernel/PP不能凭名字套串行式。本轮没有采集trace或验证性能，只复核原候选的成立/拒用条件。

可证伪的最小实际验证仍是记录就绪/开始/结束/资源等待与输出质量，然后在固定请求和计时边界下只改变一个节点。如果前提成立，耗时应符合相应公式；否则补建资源模型或拒绝应用。没有同模型、同工具、可比预算的新问题实测，不能声称主AI会做出上述判断。

canonical查询top3为GQA、FA2、speculative costbound：完整costbound和residual prerequisite已读，但其每轮submitted-token回报/串行draft及随机轮成本要求不同，未用于固定DAG结论。源库已发布并不自动保证可迁移；未复用其中作者GPU测量。

决定：这三条固定问题已经能发现相关候选，没有证据支持新增导航、重复advice或代码修改。保留已有结构入口。未证明全库召回正确、排序最优或模型能力提升；60个记录读取错误使prior screen不完整，属于单独待处理问题。
