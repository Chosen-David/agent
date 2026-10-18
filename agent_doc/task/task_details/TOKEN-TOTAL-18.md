# TOKEN-TOTAL-18：app-server累计用量的严格类型检查

Task-ID: TOKEN-TOTAL-18
Date: 2026-10-18

## Plan

在Agent已有授权范围修复short_appserver_usage累计total字段的等值非整数绕过。
保留合法完整返回、最终快照、事件/累计/算术拒绝及JSONL接口；不作模型或性能收益承诺。
执行链：独立计划审核→修前失败→最小guard→专项→独立结果复核→全库/Reader→发布复核。
证据在[结果目录](../../results/token-total18-20261018/report.md)。

## Progress

2026-10-18：修前14个非法数值子场景被接受；修后普通/-O专项14项通过。
独立各14项复现、70合法完整输出差分、108既有非法检查通过；全库1256运行/8跳过、Reader3通过。
只恢复遥测输入契约，无历史账单/实验污染证据；新增检查成本未测。发布以远端读回闭环为准。
MEM-STORAGE-01真实模型KV、QA与完整TTFT仍未完成，本项不关闭整体持续任务。
