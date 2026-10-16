# MEM-REVISION-11 独立结果审查

Verdict: usable-with-scope / ACCEPT，限当前冻结源码的公共 Python 记忆修正输入校验，不是模型/GPU/KV 性能验收，也不是受管 ReviewSession。

## 实际独立检查

- 源码 diff 仅 `_revise` 集合检查之前新增既有 `_ids(deps, 'deps')` 校验及注释，无广泛异常捕获，原事务生命周期不变。
- 独立运行 `independent_verify.py`：30组通过，其中15组非法deps覆盖None、数值、bool、嵌套list/dict、混合、错误容器/ID/重复；7组基线TypeError转为MemoryError。所有拒绝路径均比较entries/dependencies/events/document_dependencies完整原始行，事务未变。
- 10组合法/拒绝控制与基线一致，包含list/tuple、空依赖、正常raw依赖、missing/self/旧节点/直接及间接后代/candidate依赖；接受候选仍保留内容、依赖、verified新版本，旧版本superseded。reason/source/unknown-old及superseded先行诊断不变。
- 内部_insert注入TypeError且先执行一条写入：内部异常仍原样暴露，完整事务回滚。没有通过catch掩盖内部失败。
- 独立运行新增专项4测试通过；复核生产者普通及-O专项4测试日志。
- 读取实际磁盘入口regression_runner.py与final-regression.json：全库1239项，8跳过，无errors/failures；Reader3项通过。执行前后生产源哈希一致。该入口将unittest结果直接汇入JSON，并未把退出码当唯一证据。

## 证据边界及负结果

首次独立有效输入比较失败日志 `independent-attempt1.log` 原样保留：两个自造数据库的生成时间不同且毫秒碰撞导致list排序不同，属于比较器错误。最终有效输入比较仅剔除生成created_at并将条目集合按ID排序；不声称有效输出逐字节相等。无效路径的单库事务比较保持完整原始行，不剔除时间戳。

当new_id/content和deps同时非法时，deps现在先于_insert中的字段校验，诊断字段优先级可改变；仍为MemoryError，未承诺所有多非法参数错误文字完全一致。已有reason/source/旧节点状态/后代读取优先级保留。未检验自定义list/str恶意子类、GPU/模型推理、跨进程部署或LLM行为，不推导速度/任务质量收益。

Source SHA256: 9da1501aca98ad326f23d20482160519e817fba4945b080b99513aa9b4c88dd3
