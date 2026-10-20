# CHECK-HELPER-85

Task-ID: CHECK-HELPER-85
Date: 2026-10-20

## Plan

用户授权 Agent 改进及验证后直推 main。基线73fc913a7750054d520c0e57cdf0b084b9d317d8，独立检出及排他锁；人类 GUIDE 为空且只读。范围为公开 MemoryLedger.check 的自定义读取器兼容，不改变算法、权限或其他仓库。

冻结验收和历史检索见 [plan](../../results/check-helper85/plan.md)。两个最小回归先失败后通过，内置schema复用保持一次查询，专项/-O/全库/Reader及独立结果复核通过才发布。无可信宿主监督适配器，不声称已部署服务。

## Progress

已保留修前两项错误；补一个读取器身份保护，计数测试采用不替换被测函数的 profiler。专项及 -O 各62项通过；全库与独立复核进行中。研究取舍见 [research](../../results/check-helper85/research.md)。下一步主 AI 汇总独立验收、再次fetch、普通发布及远端回读。收益限定兼容性，不宣称生产速度或 LLM 任务质量提升。

最终验收：全库1323项（8skip）和Reader3通过；独立reviewer从基线重新复现两项错误，并验证反向CREATE表、损坏绑定拒绝、异常原样传播、回滚及内置schema一次查询，结论usable-with-scope。见 [报告](../../results/check-helper85/report.md)及 [独立复核](../../results/check-helper85/review.md)。再次fetch main仍为基线SHA。CLI dry-run缺GitHub用户名凭据，采用已连接GitHub接口原子CAS发布，实际远端SHA/树在发布后回读；未完成前不宣称已推送。
