# 供主 AI 串行合并（根文件尚未修改）

TASK.md：保留原 LAT p95 目标及未完成状态，不写成用户更换目标。增加本轮 report.md 索引及 memory_refs=[LAT-intent-v2,samples-v1]；DOC 保留 inventory-v1。把 impact.json 的 LAT-RECONCILE、LAT-METHOD、LAT-EVIDENCE、LAT-REPORT 编入现有任务链，other-work 独立继续。不要另建总 TASK。

合并前核对监督状态与源哈希绑定；若有绑定，按既有机制版本化并保存旧快照，避免在跑任务源版本漂移。原 TASK 哈希见 source-hashes.json。

CODEMAP 建议增量行：

| Task | Path | Status | Producer | Data / memory refs | Consumers |
|---|---|---|---|---|---|
| DOC | inventory.md | 原 verified 标签保留；纠错不影响合成环境描述 | 原作者未记录 | inventory-v1 | DOC负责人 |
| LAT | reports/old.md | stale；历史均值报告，不能作为p95完成证据 | 原作者未记录 | LAT-report-v1 / LAT-intent-v1 superseded | 写作/复核者 |
| LAT | data/samples.csv | reusable synthetic raw；五条ms值 | 原作者未记录 | samples-v1；source-hashes.json | 实验负责人 |
| LAT | outputs/p95-correction-20261006/report.md | 已生成纠错交接；非科学验收 | code-organization | LAT-intent-v2、samples-v1；artifact-manifest.json | 主AI/实验/写作/复核者 |

未找到项目内实验脚本，脚本覆盖率不适用，不虚构脚本路径。results/live.log 不搬动、不归档、不改写，负责人不变。旧报告直接打开不会自动显示账本失效状态，故主 AI 需要合并上述显式标记。
