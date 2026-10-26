# CONTEXT-WIRE-01 v3 独立静态复核

Verdict: **approve**，限 v3 的两处 fixture/oracle 修正及原 v2 生产范围。没有批准额外执行次数或修改生产范围；尚无通过结果。

本次仅静态读取方案、生产七文件 diff、fixture-v2 与新 fixture 的完整 diff、旧 artifact 测试变更、baseline/result-v1 元数据及相关失败原始日志。唯一写入本文件；未运行测试/模型/论文示例，未派发任务。

## 修订判断

1. **dispatch schema 修正合理。** 新 fixture 相对已冻结 fixture-v2.py 只有将公共 `value['project_root']` 断言限定到非 dispatch 输出。`prepare_dispatch` 原生返回没有顶层 project_root；根绑定在 params.cwd 以及 input_text 内 project_root。新 fixture 仍严格检查完整 params（含 cwd/config/reasoning/approval/sandbox/thread IDs）、完整 inner packet、documents 与 source_dependencies。没有删除合法 dispatch 合同字段或放宽父设置/依赖/取消内容检查。result-v1 两处 KeyError 与此一致。上次方案审核未发现这处 fixture schema 误判，本次予以纠正；不能把该两处报错误作生产缺陷证据。

2. **旧 artifact 预算测试更新合理。** 已批准方案从 v1 即声明新显示预算错误 exit2/stderr、空stdout。旧测试仍要求 `--max-chars 2` 预算拒绝 exit1/stdout，是旧 oracle 与本次新 CLI 合同冲突。新断言严格检查 exit2、stdout为空、stderr为 JSON 且含 budget，并新增输入字节快照；不是将失败忽略、skip 或放宽为任意非零。输入/数据错误保持原 exit1/stdout JSON，由新 fixture 的 missing ref/stale hash 和原 API 测试覆盖。

3. **生产七文件与已运行 result-v1 绑定字节完全一致。** 对 result-v1.json 的全部七个生产 code_refs 实际重算 SHA-256 均相等；fixture-v2.py 与 result-v1 的 fixture hash 相等。生产未借 oracle 修正再次改动。ContextBudgetError 继承 ValueError，artifact 只替换两处 comparison-budget 的 `_need` 为同文案子类；候选枚举/比较、counter入参、API预算及其它数据错误类型未改。CLI 先捕获 typed budget 返回2/stderr，再由原 OSError/ValueError 等分支保留1/stdout；没有按字符串分类错误。

4. **v2 实现边界满足静态要求。** 五 CLI 启动配置 stdout/stderr UTF8，成功完整输出经过共享 render_cli_context 并只 print 一次。source/dispatch 用原100000 API上限构建，advice/grid用原1M构建，再执行最终显示预算；artifact保留 LIMIT=16MiB，token候选筛选预扣 os.linesep，最终再次共享渲染检查。helper默认1M、显式 ceiling最大16MiB，不复制 serializer、不放宽其它消费者。dispatch 脚本及 prepare_dispatch 未新增 backend/RPC/进程派发或文件写入。

## 七域

| 域 | 结论 | 理由 |
| --- | --- | --- |
| intent | pass | 两处修正使 oracle 对齐已声明合同，不改变真实 wire/内容保真目标。 |
| guide | pass | 人类 guide 只读、唯一 SYSTEM-99、旧未决/限制继续保留。 |
| assumptions | pass | dispatch 实际 schema 明确核对；artifact显示错误与数据错误分开。 |
| prior_results | pass | baseline 7方法21fail14error 与 result-v1 119方法1fail2error 原件保留；不能把 schema/helper新参数引起的 fixture错误全算作生产反例。无已有失败被覆盖或改称通过。 |
| acceptance | pass | 精确预算、cp936、完整JSON、原文/依赖/父配置、只读、counter换行及helper上限判据保持；旧测试更新反而增加 stdout/stderr/只读约束。 |
| risk | pass | 生产 diff 在 v2 已授权边界，typed错误 ValueError兼容；未知宿主/Windows及全库未验限制保留。 |
| resources | pass | 主控已用2/3，剩余仅1次相同15模块suite且<=120s；独审仍未运行，后续仅1次同冻结suite<=120s。失败/超时保持blocked，不能重置。 |

主控可用最后一次固定 suite 执行；失败保留并报告 blocked，通过仍须明确请求独立结果验收。本文不是 usable-with-scope 结果记录，不是发布批准或 SYSTEM-99 完成。

## SHA-256 绑定

| 路径 | SHA-256 |
| --- | --- |
| `agent_doc/results/context-wire-20261026/plan-v3.md` | `eaf1b7f20b909f87eb0781527348f3a9759afc35d62c0f46efee289bd7cec791` |
| `agent_doc/results/context-wire-20261026/plan-review-v2.md` | `87ea542f8bc13a7689a2ea4dc1fd0b82e8f39beeeb3470dfb9bbd3fc02942c4b` |
| `agent_doc/results/context-wire-20261026/fixture-v2.py` | `423baacb7177c642bf0a69af3adb0452f77c00578abfe870b291ab7266b1ea0c` |
| `tests/test_context_cli_wire.py` | `9be90cda92adc5c68d238d1e778f7d45e0fc170ca378196b66c396e6667904fb` |
| `tests/test_artifact_context.py` | `763f888f18b36795006bc712d27a43fe0030d89636fb73287f2c7e8ccddaabf6` |
| `agent_doc/results/context-wire-20261026/run_checks.py` | `80565f43d01e48cd6304ec5eb11323243fe06dc9dd421aaca5f0ba57f80d9c53` |
| `agent_doc/results/context-wire-20261026/baseline.json` | `22cf0aebb3593a4729aa4fa99c605708b60e64b1435bd98c7961518331800fcf` |
| `agent_doc/results/context-wire-20261026/baseline.log` | `e2378f517777581639237cd5eba6d3a8a89b8529266d7f56019cb99c23445abc` |
| `agent_doc/results/context-wire-20261026/result-v1.json` | `322e6fbfe96e737e041bcd9753bde34c938305cfc7677eb2f76ad9b67c62a54e` |
| `agent_doc/results/context-wire-20261026/result-v1.log` | `25197ed4c5a6d3d26cb4a96917b0fd8b95817e2bc99db851dac0c72f68c22db0` |
| `agent_runtime/context_serialization.py` | `2606666cf723af13cb2b8a4a0934848f233ffb16c50728fc4a43da01ff26453d` |
| `agent_runtime/artifact_context.py` | `e38f36b6a5a0a4f8b115b2ff478069ae938b30d046674b9d8e9e85b91a3fc40e` |
| `scripts/source_context.py` | `fb53f5da1d1b0b9452ceb04c54e4f83674691685d335cc718568fc3902c7f181` |
| `scripts/dispatch_context.py` | `086e711f8cd5852215a6198cce78938ca9d7f55d3fcbeb853e82730ab7ec2ed5` |
| `scripts/artifact_context.py` | `031dc82e22a3374bd0748a1e57ca2dba929335ba9846cd019d837b2b56842ded` |
| `scripts/advice_context.py` | `3efd2d4269f8e671b5ce4d38fa66e79236210da86aa41c0377e8aa2ba8f92a9e` |
| `scripts/grid_context.py` | `cc51674bde2261c8faa073bb00e8d75fad4b17ae54f099a51256bd0c15b707bd` |
