# PROMPT-READ-67：拒绝超限提示词前的无界读取

基线 `0cb8cc1d68dd12200ec32c792b1f478e6b71339d`，2026-10-20。
路径：`scripts/prompt_context.py:17` → `compose_entries` →
`agent_runtime/prompt_context.py:12-26`。即使只选择 general，仍先读取 canonical decision。

## 根因与修复

`Path.read_bytes()` 先分配完整文件，随后才执行 1,000,000 字节检查。
超限输入最终拒绝正确，但读取/分配随文件增长。改为同一二进制句柄读取
1,000,001 字节，保留长度检查、UTF-8异常、换行和原字节哈希。
不依赖 stat，因此文件在检查后增长也不扩大这次 read 请求。
不声称解决恶意路径替换或提供 OS 沙箱。

历史搜索 `prompt context bounded read` 扫描239项、partial=true，三项词法
命中为数学/cluster旧结果，与本路径不匹配。此前 read-boundary56 针对
KnowledgeStore，不能替代本次 prompt reader 的验证。此前十篇论文阅读记录
保留于 read-boundary56/research_a.md、research_b.md；本次不计十篇新精读。
近期记忆保留/检索研究仍处于候选阶段，与本补丁无直接因果关系。

## 实测与复现

`python agent_doc/results/prompt-read67/probe.py` 在同一进程、相同输入比较
git基线与候选；输入在测量前生成，hash及源hash见 raw.json。
Python 3.12.14 / x86_64 / CPU。无GPU或模型调用，未计时。

| 输入字节 | 基线Python追踪峰值 | 候选Python追踪峰值 |
|---:|---:|---:|
| 1,000,001 | 1,005,318 | 1,005,284 |
| 8,388,608 | 8,393,624 | 1,005,284 |
| 16,777,216 | 16,782,232 | 1,005,284 |

各行均拒绝为 `prompt source exceeds byte limit`。这是一次分配诊断，
不是RSS或请求延迟基准；不外推合法小文件速度或真实模型任务质量。

新增测试修前：3项中1失败，`AssertionError: unbounded prompt read`；
修后prompt相关普通/-O各17项通过；Reader3项通过。
独立上下文检查见 independent.md：12读取边界和6完整compose输出对照一致，
独立16MiB峰值复测支持有界分配结论。全库回归原始短日志：

```text
python -m unittest discover -s tests -q
Ran 1307 tests in 89.897s
OK (skipped=8)
python -m unittest discover -s apps/paper-reader/tests -q
Ran 3 tests in 1.600s
OK
```

影响范围：无既有模型测量或实验数值需要重写；超限文件此前也未被接受。
保留所有历史数据。无新增后端、依赖或Skill安装。
