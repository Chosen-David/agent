# TOKEN-TOTAL-18：拒绝累计 token 计数中的等值非整数

基线 main `91d7545b75b090a9eea977af185a6f8d13b5a736`。
`agent_runtime/token_usage.py:44–52` 的 app-server 单轮计数接口仅对 `last` 验证精确整数，
`total` 只比较数值相等；Python 中 `False == 0`、`True == 1` 和等值浮点数可绕过该门禁。
真实使用入口包括 `agent_doc/results/token-001b-control-20261009/producer.py:165`；
`scripts/token_probe.py` 使用另一 JSONL 接口，本次不修改。

修复在同一 guard 中同时检查两桶的五个计数为精确非负 int，之后仍执行累计相等及原算术检查。
合法返回继续来自 last，不减去 cached tokens、不累计中间快照。非法 total 错误可能从
cumulative history 改为 noninteger；不声称所有非法输入诊断不变。

## 实际验证

- 正式14项方法运行，修前14个 subtest 失败（5浮点、9布尔），修后普通/-O各14项通过。
- 独立新上下文从git加载原实现，普通/-O各复现14项接受→拒绝、70项合法完整返回不变、
  108项既有非法仍拒绝；案例数不是模型任务样本或unittest方法数。
- 全库1256项运行、8跳过、0失败/错误；Reader3项通过。源码hash前后相同。
  207.324秒为共享机器测试耗时，不是性能基准。原始日志和独立审核均保留。

本修复只提高遥测输入契约可靠性；没有发现历史账单或实验数值受污染的证据，不修改历史数据。
新增五字段类型检查开销未测速，无token节省、模型KV、QA、TTFT或吞吐改善结论。
先前12篇方法矩阵及后续定向研究保留，不用论文数量证明本次语言类型机制。
Python官方依据：https://docs.python.org/3.12/library/json.html ，
https://github.com/python/cpython/blob/main/Doc/reference/datamodel.rst （2026-10-18查询）。
不引入JSONschema依赖；采用现有精确类型检查，时间/辅助空间为固定字段数量，不是新性能算法。

## 复现与边界

在仓库根执行 `python agent_doc/results/token-total18-20261018/independent_checks.py`，
可加 `-O`；脚本要求基线git对象存在。`independent_checks_original.py`保留原私有层级脚本，
可移植版本仅改ROOT定位，迁移后的独立复验及发布检查见final-review.md。
专项命令为 `python [-O] -m unittest discover -s tests -p test_prompt_context.py -v`。
全库由regression_runner.py串行运行，日志绑定环境/输入与候选hash见manifest.json和environment.json。

过程使用手工独立上下文审查，不宣称受管ReviewSession或常驻监控已部署；未申请新资源。
TOKEN-TOTAL-18的输入类型修复有界完成，整体Agent持续优化及MEM-STORAGE-01真实模型目标仍开放。
发布以远端SHA、tree和明确文件字节实际回读为准。
