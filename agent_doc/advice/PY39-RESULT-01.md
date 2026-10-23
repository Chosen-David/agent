# PY39-RESULT-01：恢复3.9历史结果检索

基线4fa6a474568247f139e3673467bf1a316d804ec1；源码agent_runtime/result_store.py:17,493–503。此前STATE-UTF8-01扩大回归发现的3.9失败根因在结果库：insort(key=...)仅3.10+支持，3.9每个匹配结果都抛TypeError，被search按单条错误保留，结果列表为空而status=incomplete。不是合法no_hits；调用者不能忽略errors后宣称无历史证据。真实登记→检索最小输出：

```text
status=incomplete, results=[]
errors=[{'run_id':'earlier','error':"'key' is an invalid keyword argument for insort_right()"}]
```

修复只替换排名插入API：在最多20个现有命中的(-score,run_id)键上bisect_right定位，再插入原始记录。不改分词、分数、exact-context加分、limit/max_scan、partial标志、证据/污染/独立验收门禁；无新缓存、依赖或算法近似。键提取有有界额外工作，不主张性能收益。

## 验证

Linux CPU，实际Python3.9.25／3.12.14，无模型/GPU/kernel参与。固定25历史记录，summary三档alpha beta／alpha／unrelated，limit7；由独立全排序预期检查分数与run_id，覆盖并列、截断和无命中；tests/test_result_search_compat.py。修前真实3.9测试1failure，原错误逐条保存。修后：

```text
PYTHONPATH=tests /root/.local/bin/python3.9 -m unittest tests.test_result_search_compat tests.test_result_store tests.test_result_store_fd tests.test_result_search_depth tests.test_prior_search_drift tests.test_task_manifest
Ran 113 tests in 6.696s — OK
PYTHONPATH=tests python -m unittest [同上六模块]
Ran 113 tests in 6.928s — OK
python -O -m unittest tests.test_result_search_compat
Ran 1 test in 0.065s — OK
```

首次两解释器扩大测试各75项含1导入error：test_result_store依赖tests目录顶层fixture test_result_validation；补PYTHONPATH后重跑113通过，保留原result-py{39,312}-after-1900.log，不将入口错误称生产缺陷。修前/修后和最终日志在私有检查点result-*-1900.log。git diff --check通过。按普通低风险兼容修复轻量回归由主AI核对，不宣称新独立模型验收。

历史影响：3.9搜索报告中的incomplete/errors须重查，不能据空results判定没有先前结果。3.12原语义回归通过；相关task_manifest的旧失败已恢复。不代表全库支持3.9，不涵盖真实模型/多机/任务质量、总usage或吞吐；SYSTEM-99整体批次及原协议/真实后端缺口继续open。未改历史数据、未修改其他执行者新增的memory reconcile或reference去重。
