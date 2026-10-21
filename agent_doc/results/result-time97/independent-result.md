# RESULT-TIME-97 独立结果验收

日期：2026-10-21
审查者：可信宿主独立上下文 `/root/result_time97_independent_result_review`；不是实现者，也未采用主执行者的通过声明替代复测。

## 结论

**accepted / usable-with-scope**。

允许发布的对象仅为最新 `origin/main` 已有生产实现，加上
`tests/test_result_store.py` 的五项加强回归测试。不得再次发布或叠加旧候选
`agent_runtime/result_store.py` 补丁。

- 修前 SHA：`27195c7d791f21d491097249ff1154fe6a55da24`。
- 最新验收 SHA：`011547708922bf65d603d9d7f5fdcbad60e2a13b`。
- 同类生产修复进入主线的提交：`b928a253da2586255bceedd0bb1a32fb71eb0f51`。

## 实现与调用范围判断

最新主线仅在 `_timestamp` 的 `instant.astimezone(dt.timezone.utc)` 调用处捕获
`(ValueError, OverflowError)`，并转换为 `ResultStoreError`，保留异常 cause。
捕获边界没有扩大到 `show`、`search` 或 CLI 顶层，因此自定义 `show` 抛出的
无关 `OverflowError` 仍会传播。虽然主线比原计划多列出 `ValueError`，它仍只包围
UTC 转换这一明确来源；`ResultStoreError` 本身也是 `ValueError` 子类，不改变搜索
既有的单记录错误隔离边界。

实际调用链检查覆盖：

- `_timestamp -> show -> search -> scripts/result_store.py search`；
- `register/register_history -> _timestamp -> _save`；
- `decide_run` 的 freshness 路径仍复用 `_timestamp`。

## 独立复测证据

测试均在临时归档或独立 worktree 中运行，未修改共享候选。新测试叠加到指定
SHA 后执行。

### 修前复现

在 `27195c7d` 上执行五项新增测试：

```bash
PYTHONPATH=.. python -m unittest -v \
  test_result_store.ResultStoreTests.test_timestamp_rejects_utc_conversion_overflow_as_domain_error \
  test_result_store.ResultStoreTests.test_search_isolates_timestamp_utc_overflow_without_changing_records \
  test_result_store.ResultStoreTests.test_search_cli_isolates_timestamp_utc_overflow \
  test_result_store.ResultStoreTests.test_timestamp_overflow_is_rejected_before_history_registration \
  test_result_store.ResultStoreTests.test_search_does_not_hide_unrelated_overflow_from_custom_show
```

结果：`Ran 5 tests`，`FAILED (failures=1, errors=5)`。两个直接边界子测试、API
搜索及两个注册子测试均出现裸 `OverflowError`；CLI 搜索退出码为 1 并输出
traceback。自定义 `show` 的无关 `OverflowError` 传播测试通过。该结果重现了修复前
单条坏记录可中断整批 API/CLI 搜索的问题。

### 最新主线专项测试

在 `01154770` 上执行同五项测试，并加入上游
`tests.test_reflect50_g05.Results.test_R21_overflow_is_record_error`，所以以下计数为
“上游 R21 一项 + 本任务新增五项”：

```bash
PYTHONPATH=.. python -m unittest -v <R21及五项测试>
PYTHONPATH=.. python -O -m unittest -v <R21及五项测试>
```

- 普通模式：`Ran 6 tests`，6/6 通过。
- `python -O`：`Ran 6 tests`，6/6 通过。

这些测试验证：上下 UTC 溢出均转为带 `OverflowError` cause 的领域错误；可表示的
上下相邻边界及普通日期保持标准库结果；API 同时隔离坏 `registered_at` 与坏
`measured_at` 并保留好记录；CLI 返回码为 0 并返回好记录；检查范围内所有记录
字节不变；`register_history` 在写入前拒绝；自定义 `show` 的无关溢出不被吞掉。

完整 result-store 优化模式回归：

```bash
python -O -m unittest discover -s tests -p 'test_result_store.py' -v
```

结果：`Ran 39 tests`，39/39 通过。

原生 `register` 另外使用真实 `ResultStoreTests` fixture 检查两个边界，断言调用前后
均不存在 `agent_doc/results/cpu-run-1/record.json`：

```text
native-register-before-save: 2/2 ok
```

Reader 回归：

```bash
python -m unittest discover -s apps/paper-reader/tests -v
```

结果：`Ran 3 tests`，3/3 通过。

`git diff --check` 通过；最新主线独立 worktree 中仅
`tests/test_result_store.py` 有 95 行加强测试增量，没有重复生产补丁。

## 全库结果、限制与适用范围

独立执行：

```bash
python -m unittest discover -s tests
```

结果：`Ran 1638 tests in 106.036s`，12 skipped，1 failure。唯一失败为
`test_managed_supervisor.WorkerTests.test_status_verifies_worker_process_identity_against_pid_reuse`：
该 unified-exec 环境中的 unittest 进程读取自身 `/proc/<pid>/stat` 得到 `None`；单独
重跑同一测试仍为相同失败，而独立 `python -c` 探针可读取 starttime。该测试与
result-store 时间解析、搜索、注册、CLI 及本次改动文件没有调用或文件交集，因此不
阻断本次 scoped acceptance，但不能把这次独立全库运行表述为全绿。

本验收仅支持 CPython 3.12、本地固定偏移 ISO-8601 输入、上述 API/CLI 故障隔离、
写前拒绝和字节不变结论；不构成跨 Python 实现、所有时区实现、性能提升或全仓库无
缺陷保证。后续若更改 `_timestamp`、搜索异常边界、注册写入顺序或 CLI 错误处理，
需重新执行相应专项验收。
