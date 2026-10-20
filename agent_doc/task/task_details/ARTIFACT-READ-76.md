# ARTIFACT-READ-76 小文件读取分配

Task-ID: ARTIFACT-READ-76
Date: 2026-10-20

## Plan

主控唯一作者。用户已授权优化与验证后main直推；guide只读。
冻结方法、DAG、接口和验收：[v1](../../results/artifact-read76/plan.md)、
[v2](../../results/artifact-read76/plan-v2.md)。沿续未合入read74负结果，
只允许无损读取实现，不改变内容/预算/hash或使用外部模型资源。
发布前独立审核、fetch并回读；无可信长期运行适配器，不宣称监督器已部署。

## Progress

- 干净独立clone a55a3d1，已持有本机Agent锁。历史候选与负结果已读。
  主控冻结v2后等待独立计划审核，尚未开始测量或修改生产源码。
- 后续计划审核通过，实施单一候选：小于64KiB且seekable的文件探测size+1，
  填满时释放探测结果并从同一句柄有界重读；大文件/不可seek路径不变。
- 修前小文件峰值回归失败，修后41项通过；完整派发16,787,810→10,612 bytes，
  主控17个分配场景满足冻结门槛；全库1314项（8跳过），Reader3项通过。
- 独立结果审核usable-with-scope：15项精确语义对照、23个分配场景和41项测试通过。
  [完整证据](../../results/artifact-read76/report.md)；不外推wall/RSS/模型质量。
- 待办ARTIFACT-FD-77：独立复现基线及候选在目录os.fdopen拒绝路径泄漏fd，
  两次错误fd数4→6；本项未修复，需独立最小复现、修复和验收。
- 实现验收完成，发布前仍需刷新main、核对候选树并实际发布回读。保留旧read74负结果。
