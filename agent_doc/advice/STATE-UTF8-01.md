# STATE-UTF8-01：检查点固定UTF-8写入

基线 `653b1f7d1670208be951fdf22159d588a8381c90`。`agent_runtime/task_manifest.py:48` 的atomic_json使用默认locale编码；其ensure_ascii=False会直接输出中文，非UTF-8系统因此报UnicodeEncodeError。实际入口包括task_supervisor的plan/progress/live/final-report/monitor/source-snapshot及crash_restart状态。修复仅给fdopen补encoding=utf-8，保留临时文件、fsync、守卫和replace，不改变JSON字段/格式与权限。

## 复现及回归

Linux，本地真实Python3.12.14／3.9.25子进程；`-X utf8=0`、`PYTHONUTF8=0 PYTHONCOERCECLOCALE=0 LC_ALL=C`，ASCII-only命令argv中使用Unicode转义产生中文和emoji。无GPU/模型/kernel。新增`tests/test_atomic_json_encoding.py`固定输入reason=任务恢复、symbol=🚀；成功后UTF-8解码JSON并比对值。创建/覆盖，以及序列化NaN失败时保留旧文件和清理临时文件均覆盖。

```text
修前：Ran 2 tests in 0.157s; FAILED(failures=3)
UnicodeEncodeError: 'ascii' codec can't encode characters ...
修后 python -m unittest tests.test_atomic_json_encoding tests.test_task_manifest tests.test_crash_restart
Ran 47 tests in 1.091s; OK
python -O -m unittest tests.test_atomic_json_encoding
Ran 2 tests in 0.158s; OK
python -m unittest tests.test_managed_supervisor tests.test_supervisor_lock_files
Ran 16 tests in 18.936s; OK(skipped=1)
/root/.local/bin/python3.9 -m unittest tests.test_atomic_json_encoding tests.test_crash_restart
Ran 5 tests in 0.189s; OK
```

3.9扩大回归47项出现1 error：`test_prepare_and_live_dispatch_perform_prior_result_lookup_before_data_work`在结果检索后索引空列表。单独将task_manifest模块替换为基线git show原字节后仍复现1 error，故不能报3.9全绿；失败原日志保留，不改断言或数据掩盖。与当前单行编码修复无因果证据，根因仍待查。

原始短日志存本次私有检查点atomic-utf8-{before,after,optimized,supervisor,py39,py39-focused,py39-baseline}-1803.log。最初非ASCII argv在ASCII宿主解码失败的探针不是函数复现，已纠正为转义命令并执行到真实fdopen。git diff --check通过。普通低风险编码修复按现有轻量回归边界由主AI复核，不宣称新增独立模型验收。

历史影响：非UTF-8宿主中含中文的计划/恢复报告可能根本未落盘或旧状态未更新，不能据此声称任务恢复成功；需在受影响宿主重跑保存和回读。当前Linux ASCII子进程可复现并通过，不等于Windows/tmux/真实后台恢复已验。无吞吐、总token或模型质量收益主张；SYSTEM-99原协议冲突、真实宿主/输入暴露/全部actor usage与质量缺口继续open。

发布前并发main新增5e2415b7共享引用去重；本次补丁已重放，未覆盖其154文件改动。合并后同组63项17.745s通过(1skip)，日志atomic-utf8-rebased-1803.log；发布父提交为5e2415b7c870dda1221ade0c750c5f2607c85b42。
