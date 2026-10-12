# 最新 main 合入后的独立发布复核

审查者 `/root/artifact_equal_review`。状态：**usable-with-scope**。

实际核对当前 HEAD `edab6b496e4f26be4e70ed3d3eeacd8288e44a29`。相较固定测量基线 `bd65a2348e32d8a70af9e003cbc309064363dd9e`，最新 main 没有改变 `agent_runtime/`、`scripts/artifact_context.py` 或既有 artifact 测试；新增规范及同步元数据不属于测量执行路径。候选 `agent_runtime/artifact_context.py` SHA-256 仍为 `e533244e68e698cb95f298bd04ce5e63727dd2cf485e4f731805883191b3e30f`，与已独立复测字节一致。故受影响的测量执行路径为空，复用原 7 对 CPU 原始样本与独立验收，无需重复性能测量。

当前 tracked working diff 仅：正式 `artifact_context.py` 4 行补丁（删除 1 行，添加等值条件和 2 行注释），任务索引新增 2 行。另有本任务新回归文件，恰好 3 个 test 方法；本任务详情和结果目录为计划/验收证据。两份 generated metadata 已由最新 main 提供，本轮没有重复 metadata 工作树差异。两个其他研究 untracked 目录属于既存无关工作，不建议纳入提交。

最新原地整合规范已经阅读。实现直接修改正式模块及原入口，未新增 fast/v2/optimized 平行运行时实现。测量脚本从固定 Git 源加载基线，是独立 correctness/性能复现所需证据，不被生产消费者导入，也不构成常驻旧实现副本；原版通过 Git 恢复。新增回归验证相等输入不匹配、不同输入正常匹配、hash 不绕过磁盘检查，覆盖实际契约。没有需清理的本轮冗余替代源码。

报告已核对：`report.md` 的独立证据链接现在为真实 `independent_review.md`，错误连字符版本已不存在。此次结论承接原有 CPU synthetic 范围，不能扩展为一般任务、模型质量、token、账单或端到端收益。正式发布后仍需由主任务执行普通 push、回读远端 SHA 和对应内容核对。
