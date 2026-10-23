# PY39-RESULT-01

## Plan

同SYSTEM-99，基线4fa6a474568247f139e3673467bf1a316d804ec1。实际3.9结果搜索在insort(key=...)失败，命中变errors并遗漏。改用3.9支持的bisect_right在最多20个命中排名键上定位，再插入原记录。保持(-score, run_id)并列顺序、limit/max_scan、partial、错误与证据门禁，无新依赖/缓存/检索算法。

验收先保存真实3.9失败；25历史记录、分数并列、limit7截断和无命中，独立全排序作预期；同条件3.9/3.12结果库/深度/FD/先验搜索与task_manifest回归及-O。低风险本地API兼容修复按轻量回归，不主张吞吐/总token/模型质量或整个批次完成。发布前fetch，重放并发改动，普通推送及远端回读。

## Progress

- 真实3.9最小登记→search返回incomplete、结果空、错误key invalid keyword for insort_right；新测试1项修前failure，原日志result-py39-before-1900.log保留。不是STATE-UTF8补丁导致。

- 修后3.9/3.12各113项通过(6.696/6.928s)，-O专项1通过；原task_manifest历史检索失败恢复。首次各75项含顶层fixture导入error，补PYTHONPATH=tests重跑，失败日志保留。见[简报](../../advice/PY39-RESULT-01.md)。普通轻量兼容修复由主AI核对，无新模型/性能/整批完成声明；发布回读另核。
