# CONTEXT-SCHEMA-83：事务内 schema 查询复用

基线 `fad3bd48ba108b90a8e36ecafd5bf2462207c8bd`。生产位置 `agent_runtime/project_memory.py:315–342,417`；候选文件 SHA256 见 review.md。依赖闭包逐项读取时重复查询 document_dependencies 表存在性，固定的事务内 schema 元数据可复用。仅对原始读取器及普通 SQLite 事务/行/文本工厂开启局部缓存；不缓存条目、有效性或文档校验，不跨调用保留状态。保留既有所有路由守卫。

此前 context81 私有探索发现直接传缓存会破坏两参自定义读取器，并在自定义读取器同事务 DROP TABLE 后使用过期状态。本次新增读取器身份守卫和三项回归，保留自定义路径原调用行为。SQLite 官方说明同连接修改可见，不能把普通读事务等同于禁止同连接 DDL：https://www.sqlite.org/isolation.html （2026-10-20 核查）。这是一项工程优化，不宣称提出新算法。十篇论文既有正文阅读记录见 ../read-boundary56/research_a.md、research_b.md；本次未新增十篇阅读。

## 验证与测量

冻结计划见 plan.md，复现：`PYTHONPATH=. python agent_doc/results/context-schema83/measure.py`。使用固定基线方法与候选，完整 basis_context 输出一致；合成线性依赖链，每条内容128字符，max_chars200000，预热3次，随机21组AB/BA，每样本5次调用。输入hash、Python/SQLite/平台、全部原始样本在JSON中；不涉及GPU/kernel/驱动。指标是 wall CPU装配时间，包含文件、数据库和校验路径；建库在计时之外。未测峰值内存、LLM质量或真实请求TTFT。

| 节点 | 串行主测修前ms | 修后ms | 降幅 | 独立串行降幅 |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.5844 | 0.6002 | -2.71% | 1.48% |
| 32 | 1.4799 | 1.4026 | 5.22% | -1.24% |
| 256 | 5.2303 | 4.9129 | 6.07% | 7.15% |
| 512 | 10.1396 | 9.3667 | 7.62% | 6.44% |

主测 serial.json，独立 independent.json，均通过原门槛：256/512至少改善5%，1/32回退不超过10%。1节点不调用闭包，为噪声控制。原主测 raw.json 保留；初次独立计时与全库测试可能重叠，independent-concurrent.json 排除验收，明确串行复测排除已知干扰。未删除不利样本，不声称统计显著性或生产负载保证。

原始短日志：全库 `Ran 1321 tests in 83.719s; OK (skipped=8)`；Reader `Ran 3 tests in 1.578s; OK`；优化模式 memory `Ran 60 tests in 2.048s; OK`。独立80项memory/handoff及10组精确输出/异常差分记录见 independent*。跳过的外部集成未验证。历史context81探索不作为生产加速证据；其他历史实验数据不修改。真实业务分布及模型任务质量需另行重测。

独立宿主审查见 review.md，不声称已安装ManagedEngine监督服务。发布前再次fetch、普通main更新及远端树回读由主执行者完成；具体远端提交在交付中确认。
