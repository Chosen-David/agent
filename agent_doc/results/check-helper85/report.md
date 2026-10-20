# CHECK-HELPER-85：公开 check 缓存边界修复

2026-10-20；基线 `73fc913a7750054d520c0e57cdf0b084b9d317d8`。入口 `agent_runtime/project_memory.py:299-314`，修复在308行添加 `_read_entry is _BUILTIN_READ_ENTRY`；其余生产代码未变。

## 原因与修复

public check 的 schema 复用绕过 `_get`，直接给读取器传第三个缓存参数。原有扩展路径只要求两个参数；自定义读取器也可能在同一连接内变更可选表结构。于是两参数包装器 TypeError，DROP TABLE 后继续按缓存的存在性读表导致 MemoryError。上下文入口已有对应保护，公开入口遗漏。

只在内置读取器身份未变时缓存 schema；其余走原 `_check → _walk → _get`，两参数及逐节点 schema 读取均恢复。不缓存条目有效性，不改变依赖顺序、预算或权限。计数测试用 profiler 观察真实内置函数，避免测试包装器本身触发新回退；依旧要求内置每遍历一次schema查询、自定义_get四次。

## 实测与范围

- 最小两场景：修前2项均错误（before.txt），修后均通过；输入是测试文件中的临时合成 leaf→parent SQLite，哈希见environment.txt。
- memory 专项62项通过；`python -O` 同62项通过，日志为targeted.txt、optimized.txt。
- 全库1323项通过、8skip；Reader3通过，见full-summary.txt、reader.txt。完整全库原日志本地 `/tmp/check-helper85-full.log`，SHA256 `696c1c5807b1bd9a89b0d36900d2dd643eceb523dd85f0b27d0a693955f99abd`；仓库保留短尾日志，不冒充全量记录。
- 独立复核记录见review.md：直接从基线Git源码重现，并扩展检查新增表/损坏依赖绑定、异常传播及内置缓存未退化。验收以该记录的范围和限制为准。

这是可靠性修复，非新的性能提速。自定义扩展需要逐节点查询的开销是恢复既有契约；未测wall、模型准确率、生产请求延迟。普通内置路径仍一次schema查询不等于实测速率不变。无GPU、模型API、训练或付费资源。环境Python3.12.14/SQLite3.53.1/Linux x86_64。

历史 memory-schema-20261016 的内置场景证据不作废，但不支持自定义读取器兼容保证；context-schema83 未修改公开check，其已记录范围不扩张。无需重写旧数据。后续如扩大任意猴子补丁兼容承诺，需独立明确接口范围和新增回归。

研究来源与采用边界见research.md；不把外部论文分数、历史十篇阅读或本轮单行修复包装成新算法或端到端性能提升。发布前重新fetch，远端提交与树在实际发布后另行回读。
