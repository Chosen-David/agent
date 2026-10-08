# 支持条件化：证据入口

主报告：[report_by_gpt.md](report_by_gpt.md)。科学验收以`manifest.json`和`independent_review_v2.json/md`为准；旧v1 invalid保留。published refs与检索/回归另行验收，不把候选旧refs静默更新。

完整原始case JSON以raw_cases.json.gz及raw_cases_v2.json.gz无损保存。每版生产者/独立重跑记录完全相同，故不提交四份重复JSON；实际汇总耗时分别保留。需要复核脚本引用的JSON文件时，在仓库根运行：

```bash
python agent_doc/results/math-conditioning-20261008/restore_raw_by_gpt.py
```

恢复脚本只写不存在文件，若现有文件不同即拒绝。冻结summary、manifest和review不变。生产者可在临时副本用verify_conditioning_by_gpt.py复现；独立脚本independent_check_by_gpt.py --v2核查完整记录和另一个算术参考，会重写自身reference/refs，故重跑须在证据的临时副本，不能覆盖冻结review后当作同一验收。

只证明有限数学/结构核验。无Lean、真实模型、GPU、e2e或token节省实测，未部署认证Engine服务。
