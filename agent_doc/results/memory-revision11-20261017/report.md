# MEM-REVISION-11：修正接口先验证依赖，再执行集合检查

基线 main `38d84ccddec9a820c0e0da2fee4dd511aa346abd`。
`agent_runtime/project_memory.py:255–275` 的 `_revise` 在 `_insert` 的共享 `_ids` 校验前
调用 `set(deps)`；None、整数及包含list/dict的列表会抛出未约定的TypeError。
依赖输入可能来自API调用者，捕获MemoryError的调用方因此不能按既有失败契约处理。

在旧条目读取、状态和后代检查之后，紧邻集合操作前使用已有 `_ids(deps, 'deps')`。
不宽泛捕获TypeError、不吞掉内部损坏；新版本写入/后代失效/事件记录仍在原事务内。
这是存储接口可靠性修复，不是新的缓存算法。源码/环境/固定复现脚本hash见environment.json。

## 实际证据

修前5个输入场景均TypeError，修后5个均MemoryError；每个调用前后entries、dependencies、
events、document_dependencies四张业务表逐行完全相同。修前本来已经回滚，本轮不声称新增
回滚能力。正式4项测试修前5个subtest错误；修后普通及-O均4项通过。
list/tuple有效依赖、后代stale、candidate接受，以及重复/缺失/失效谱系拒绝均保留。
独立30组检查通过，其中15类非法deps有7类从TypeError修为MemoryError；有效输入/失效谱系/
先行诊断控制保留，注入内部TypeError仍原样暴露且回滚。首次独立双库比较因生成时间戳
排序不同失败，修正oracle仅忽略created_at并按ID排序；原始失败日志保留，未改生产代码。
最终全库1239项运行（8跳过）、Reader3项通过，源码hash前后一致。
独立验收见result-review.md；原始结果见final-regression.json。

诊断边界：仍保留reason/source、旧条目读取/状态/后代等先行校验，但同时多个参数非法时，
deps现在可能先于new_id/content报告错误，不声称所有无效输入诊断文本和顺序逐字节一致。
异常类别统一为约定MemoryError，业务语义未放宽。没有新性能计时或峰值内存数据；一次额外
依赖校验有线性输入扫描成本，不声称无开销。未修改历史实验结果，也不需要重跑旧KV实验。

## 范围和后续

仅真实Python/SQLite修正API。无模型KV tensor、任务QA、TTFT或吞吐收益证据。
既有12论文方法矩阵与近期定向研究继续保留，未把阅读数或本可靠性修复冒称模型性能创新。
本轮另初读PCR2610.02766v1的TTL闭包模型，只作后续线索，不把离线块时间目标当GPU延迟。
父任务MEM-STORAGE-01仍未完成，实际模型存储适配、质量/总成本实验仍待可用消费者。
所有独立复核为可信新上下文人工有界检查，未声称运行受管ReviewSession或常驻supervisor。
复现脚本按实际私有run层级定位ROOT；复制至仓库.agent-runs/<run>/后运行，勿直接在结果目录运行。
