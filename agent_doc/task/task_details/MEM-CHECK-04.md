# MEM-CHECK-04

Task-ID: MEM-CHECK-04
Date: 2026-10-16

## Plan

延续 MEM-STORAGE-01，基线 main 2d7ddc46b13b24ecc0c3611b1d8dcb63df7e6b10。
以显式依赖迭代器栈替换递归 DFS，只保留请求根内容，释放祖先内容；不改变
逐次状态/来源文档检查、依赖遍历顺序、事务和返回值。主AI独占实现、任务与报告；
独立新上下文 memory_check04_verify 审查方案和实际代码/数据，仅写复核证据。
人类指南不编辑，其他仓库不在范围；没有受管宿主/tmux接口，不宣称部署后台服务。

冻结协议：[config.json](../../results/memory-check04-20261016/config.json)。
一版候选/30分钟CPU探测；256层×16KiB链的完整check Python traced峰值下降
至少70%，七场景21对随机AB未tracing wall中位数各退化不超过15%；另7对trace。
正确性差分、首次异常顺序、新鲜度、1024/1200层可靠性单独验证；模型KV/QA/TTFT
未接入，不能从本地SQLite推断。失败保留，不调门槛或扩大实验直到碰出收益。

## Progress

- 检索历史结果和知识条目，旧结果仅复用方法；部分历史读取失败如实保留。
  独立方案v1要求修订固定fixture/计时/内存规则，冻结后v2 adopt，才开始源码改动。
- 新增1200层链最小回归在基线出现RecursionError（8项运行/1错误），候选通过。
  采用迭代器帧避免宽图预先展开，显式del非返回entry避免内容驻留；checked标记
  时机和DFS先后不变，包含脏库已有cycle行为。8项定向check及20项memory回归通过。
- 主测七场景门槛通过：深内容链Python峰值4522288→119862 bytes（下降97.35%），
  最大wall退化4.65%。原始数据及待完成独立/全回归均绑定同一冻结源码。
  [报告](../../results/memory-check04-20261016/report.md)。本项当前等待独立结果和发布。

- 独立7733普通差分、4文档事件顺序、7fixture/hash/随机顺序复核与1024/1200层
  可靠性通过；同协议独立峰值下降97.35%，wall最差退化2.33%，局部usable-with-scope。
  主执行者全库1202项运行/8跳过，-O memory20项及Reader3项通过。已再次fetch，
  main仍2d7ddc4；允许发布本有界修复，总体模型KV/任务质量目标仍未完成。
