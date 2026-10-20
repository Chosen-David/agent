# RESULT-FD-95：结果读取、哈希与登记的描述符释放

日期2026-10-20，基线 `e30dfce8424f7912a3716dd6ef035f648808e2f7`。独立结果验收为 usable-with-scope；发布状态以远端回读另核。

## 真实链路和问题

`scripts/result_store.py` → `ResultStore.show/search` → `_read`，以及 `register_history/decide_run` → `_check_ref`、`register/register_history` → `_save`。原实现分别在 `result_store.py:72,112,272` 把已获得的fd交给fdopen；构造失败时尚未进入with，无法由流释放。Linux把record.json误建成目录即可在读取路径真实触发；存储路径通过故障注入触发构造/进入失败。重复搜索虽返回结构化错误，进程资源仍会累积。未证明真实线上实例已经耗尽fd。

现在 `_read:72–80`、`_check_ref:116–127` 显式保持原始fd所有权，流用closefd=False借用，finally关闭；哈希对象先于open构造。`_save:279–286` 嵌套finally确保关闭后才原子link，外层仍清理临时名。未改变搜索排名、信任门禁、JSON深度隔离、路径限制、读取上限、哈希或不可变登记规则。没有抽新框架、重试或依赖。

## 实际验证

先运行新增 `tests/test_result_store_fd.py` 再修复。修前日志 `before.log`：9方法中出现12个失败子场景，均为异常后fstat仍成功；其中重复搜索方法在第一次泄漏即停止，不能把计划4次算作4个已测失败。

```text
python -m unittest discover -s tests -p test_result_store_fd.py -v
Ran 9 tests in 0.027s
FAILED (failures=12)
python -m unittest discover -s tests -p 'test_result*.py' -v
Ran 103 tests in 4.747s
OK
python -O -m unittest discover -s tests -p 'test_result*.py' -v
Ran 103 tests in 4.759s
OK
python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.124s
OK
```

测试总耗时不是性能对照。具体资源收益以独立故障矩阵的修前/修后每fd观察为准；不从失败子场景数直接推断泄漏总数。测试检查真实目录、构造/进入/中断、读取/stat、写入/flush/fsync/link错误、成功登记和重复登记不覆盖；测试清理只回收本次获得的基线fd，观察先于清理，避免后续污染。

源码SHA256 `6ef04bd8497e196dd728bc480afba11f192c29c43282b663aa410db3afdfefaf`，新增测试SHA256 `564940de12e0e1cf3a5912c76cc427f5f9ce54cb10b4e18f5f8e6d0e4f851701`。环境Linux6.18.55 x86_64/glibc2.39、CPython3.12.14/Clang22.1.3；标准库本地CPU与合成临时文件，无GPU/模型/API请求。

全库 `python -m unittest discover -s tests`：1347项完成，1339通过、8跳过；原始末尾为 `Ran 1347 tests in 93.130s / OK (skipped=8)`。完整私有日志 `.agent-runs/result-fd95/full.log` SHA256 `0d0262cfd63e31bc820ef7f12c8d7976d7ba6fac9707df9db518aca7e6c8ce4b`，不把跳过计为通过。

[独立验收](independent-result.md)已完成六项检查，并独立重跑普通/-O各103项回归。独立矩阵每种模式、每个版本各38场景：修前12个实际fd泄漏，修后0；候选33次成功获取与33次原始关闭逐一对应。两种模式合计152条观察，不是152个不同场景。真实目录错误、注入失败、并发目标存在、关闭先于link以及异常身份/字节保持均检查通过。输入SHA256为 `e45b1b0032dd6b489d0be35f9d3244e8506269bec28175f9cff2dc5b4669f6fc`；原始证据及复现脚本见同目录 independent*。全库与Reader日志为复核者检查的主控证据，不称独立全库重跑。

## 研究、限制及复测范围

[计划](plan.md)、[研究取舍](research.md)记录真实历史查询、已有十篇阅读和本轮新论文定向阅读。实现与优化技能要求把状态不变量、错误语义和资源指标分开；本轮落实为实际fd检查，未把“发生预期异常”冒充资源安全。

仅主张本机已覆盖路径的资源可靠性；没有wall吞吐、RSS、token、模型质量或真实任务成功率数据，不把无泄漏称普遍提速。不保证任意同权限并发关闭/替换fd、OS崩溃、所有平台或其他模块无泄漏。原始close本身失败的异常策略未新增保障。历史结果内容无需因本补丁重算；仍应独立验证具体结果的适用性。无tmux/受管宿主，不声称部署监督服务。
