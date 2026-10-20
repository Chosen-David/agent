# CHECK-HELPER-85：公开记忆校验读取器兼容

基线：73fc913a7750054d520c0e57cdf0b084b9d317d8。仅修改 Agent。

固定验收：先添加两个公开 check 回归（两参数读取器、节点间同连接 DDL），保存修前失败；仅给内置缓存路径补读取器身份保护；内置路径仍每次遍历一次 schema 查询，自定义路径保留逐节点读取。现有计数测试改用 profiler 旁路观测，不再替换被测函数。运行专项、-O、全库和 Reader，独立上下文复核实际代码和日志后才发布。指标为两场景正确性，不宣称速度提升或端到端任务质量提升。

历史检索：result_store search 'memory schema helper' --limit 3 --max-scan 200；扫描199且partial=true，不代表完整检索。memory-schema-20261016 是原优化证据，context-schema83 明确未覆盖 public check；历史通过不能证明此次边界正确。人类 GUIDE 为空且不修改。无可信宿主 supervisor adapter，未启动或宣称部署监督服务；本次为已授权独立本地修复。

主 AI 独占生产代码/测试/任务索引；独立 reviewer 仅写本目录 review.md。禁止修改其他仓库、人类 guide、历史实验数据。
