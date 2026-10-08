# ORCH-PAR-01：因果任务拆分与资源编排

这是用户2026-10-08明确要求的有界主AI规范更新，未改runtime、GPU runner或其他仓库；不算原每小时十篇/全部角色优化大批次完成。

新增共享工作流：可独立前置任务按数据集等拆分，真实资源准入后有界并发；每份数据独立验收，局部依赖可以流水，全局结论完整汇合；保留任务身份、失效范围与失败恢复，区分吞吐/延迟/算力成本。主AI、审核主AI、监督和实现入口可导航到契约，两份科研插件包含本地副本，旅行主控引用回退到仓库URL。

## 证据与范围

- 原始计划及SHA审核：plan.md、plan-review.md；实际不同宿主上下文 /root/orchestration_plan_review。人工可读审核不是ReviewSession认证回执。
- 检索：prior-search.json，27目录部分扫描、9缺record错误；旧候选不适用，无旧pass复用。源码边界直接核对core及GPU adapter，不虚构知识库定理或外部来源。
- 实现：source-freeze-v1.json固定初版19个源/生成文件，source-freeze.json固定路径纠正后的最终19文件；修改未涉及core或GPU adapter。先在fcd4f96基线上验证，再整合acf85d7；仅TASK/CODEMAP并发追加冲突，双方保留，整合未改变19个实现hash；随后因路径失败增加一条绝对项目/输出绑定规则，仅canonical与两份副本改变。
- 程序回归：regression.log、integrated-regression.log、final-regression.log分别真实执行同组68项，均通过、无跳过；main_ai_contract、plugin_reference_sync、markdown_links、project_docs_workflow、gpu_adapter、task_waiting。GPU测试含mock，只验证控制流，不是GPU实测。引用sync --check、diff --check通过。
- 自动化：automation-readback.json保存同一任务ID、保留旧prompt的增量和不变每小时配置。完整工具前后读回因含其他用户任务资料，仅留私有运行目录，独立验收者可读取核对；公开摘要不包含其私有资料。配置证据不等于该定时任务已执行新要求。

全项目文档validate在基线已失败：CONT-20261008-{01,02,03}仍为Plan v1且缺Task-ID/Date。保留这些任务原文；本轮不宣称全项目prepare/start或机器发布gate通过。后续应在所属任务版本化修复，不能用本次文档审阅绕过运行时门禁。

本次使用验证是合成资源条件下的真实模型规划，非实验数据生产；planner在v1工作流下误将相对输出解析到宿主cwd，根将原文件同字节复制至正确项目，原SHA256为920334f065c1e147461879abb408d0ef6956baeb5740b0387f152e3447402254。失败未抹去；最终规则追加绝对project_root与allowed_writes/output_root，完成程序/独立内容复核，未另跑模型证明路径行为已改善。具体方案与独立结论分别见forward-plan.md和independent-review.md。没有测量真实模型任务成功率、tokens、GPU吞吐、makespan或费用收益，不声称8倍提速。受管运行、真实异步job、资源争用及公平对照仍需获准宿主后端，本次未部署或启动该后端。

发布前状态：内容与证据准备后按用户既有授权普通发布main，再回读远端commit/tree；发布事实只以实际读回记录为准。

发布前发现并发9e23c73（数学筛选知识与TASK），非强制rebase保留；19项本轮源码hash不变，publication-regression.log再验同组68项全部通过，sync检查通过。没有把新数学知识或其结果冒领为本任务工作。
