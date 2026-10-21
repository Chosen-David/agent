# RESULT-TIME-97 结果记录

日期：2026-10-21。原始基线：`27195c7d791f21d491097249ff1154fe6a55da24`；
最终复核基线：`011547708922bf65d603d9d7f5fdcbad60e2a13b`。

## 问题与实际修复

`agent_runtime/result_store.py:_timestamp` 接受带时区的合法 ISO-8601 文本后，
会把它换算为 UTC。`0001-01-01T00:00:00+01:00` 与
`9999-12-31T23:59:59-01:00` 能被 `datetime.fromisoformat` 解析，但 UTC
换算越出 CPython `datetime` 范围。旧代码让 `OverflowError` 穿过
`show -> search -> CLI`，因此一个损坏的持久化记录会中断整个检索；注册路径也暴露
非领域异常。

本任务先在旧基线完成修前复现并形成窄来源修复候选。发布前同步发现并发提交
`b928a253` 已在同一 `astimezone` 调用处把 `ValueError/OverflowError` 转成带 cause 的
`ResultStoreError`，随后由 `01154770` 记录远端发布。主控丢弃自己的重复生产补丁，
保留并新增五项公开回归：

- 上下 UTC 极值拒绝、cause 类型及两个相邻可表示值；
- API 搜索隔离 `measured_at`/`registered_at` 坏记录，正常邻居仍可返回且记录字节不变；
- 真实 CLI 搜索仍退出 0 并返回结构化 `errors`；
- 注册在创建结果目录前拒绝越界测量时间；
- 自定义 `show` 抛出的无关 `OverflowError` 继续传播，防止以后用宽泛捕获掩盖缺陷。

生产实现位于 `agent_runtime/result_store.py:166-179`；加强回归位于
`tests/test_result_store.py:128-224`。本任务没有更改 JSON、排序、配额、时间裁剪或
可信复用语义。

## 修前失败与修后验证

在 `27195c7d` 上加入五项测试、尚未修改生产代码时，普通专项实际结果为
`FAILED (failures=1, errors=5)`：两个直接边界、API 搜索、CLI、两次注册子例均暴露
未隔离的 `OverflowError`；“无关 OverflowError 必须传播”负控通过。修前失败保留为
本记录中的短日志，不把后续并发实现误写成本任务原创。

在最终 `01154770` 源码和本任务五项测试上实际执行：

| 检查 | 结果 |
| --- | --- |
| 新增五项，普通模式 | 5/5 通过，0.187s |
| 新增五项，`python -O` | 5/5 通过，0.200s |
| 并发 R21-R25 回归 | 6/6 通过，0.011s |
| 完整 `tests/` | 1638 项执行成功，12 项能力型跳过，111.222s |
| Paper Reader | 3/3 通过，1.592s |
| `test_result_store.py`，`python -O` | 39/39 通过，2.047s |
| 插件引用同步、`compileall`、`git diff --check` | 全部退出 0 |

命令口径为 `PYTHONPATH=.:tests python [或 python -O] -m unittest ...`；全量发现使用
`python -m unittest discover -s tests -v`。12 项跳过包含真实 tmux/Unix socket 与
可选依赖等既有显式能力门禁；本次专项没有跳过。

## 环境、绑定与边界

- CPython `3.12.14`；Linux `6.18.55`，x86_64。
- 最终 `agent_runtime/result_store.py` SHA-256：
  `a37069546d927cc8682b5d2584ef855f6766d30ca88d89909b4686f6e87a25bc`。
- 加强后的 `tests/test_result_store.py` SHA-256（独立验收前候选）：
  `3055f1aca440fd8401599dedbda967ba0472ee7ae5a25f214522be8338ded53d`。
- 旧生产源码 SHA-256：
  `8e9cebfcf4a5e204899ca407984e8e01abf77eb7da2c2002cdad34276b371efe`。
- 测试均使用临时 CPU 文件和标准库；无模型 API、GPU、付费资源或私密数据。

结论仅覆盖 CPython 3.12 本地结果库的时间边界拒绝、坏记录隔离与上述调用链。
未测其它 Python 实现/平台、真实生产数据分布、吞吐、延迟、token 或模型质量；没有性能收益
主张。SYSTEM-99 系统批次仍保持 open，本有界结果不代表整轮完成。
