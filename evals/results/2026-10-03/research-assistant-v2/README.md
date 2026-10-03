# v2 科研项目交付

本轮目录：run-v2-20261003/

- project_state.md：结论、输入更新影响、保留工作与下一步。
- results.md：可使用的中文结果段落、图注与指标定义。
- figure_v2.png / .svg / .pdf：现有四行测量的两面板图；实际检查了 PNG。
- task_chain.yaml：10 项任务的依赖、负责人、输入、动作、产物、验收、恢复条件与预算；7 done，3 blocked。
- retention_check.md：历史背景的适用性与缺失产物说明。
- derived_metrics.csv、input_manifest.json、claim_evidence_ledger.yaml：数值、输入哈希和主张证据。
- analyze.py：实际执行的 CPU 分析和绘图脚本。
- build_records.py、validation.json、artifact_hashes.json、qa.md：任务图检查、交付哈希和实际检查边界。

端到端 small / medium 延迟分别减少 20.0% / 16.7%，large 增加 10.0%；kernel 的 2.00× 速度比只适用于 kernel_only。保留候选，优先补齐已有资料以诊断 large；本轮没有新实验、代码优化、GPU、外部服务或独立审阅。
