# RESULT-FD-95 有界计划与验收

2026-10-20。基线 e30dfce8424f7912a3716dd6ef035f648808e2f7，干净独立检出；任务为用户授权的 Agent 可靠性/效率提升及 main 发布。guide 为既有空文件，禁止修改。其他工作树 DISPLAY91 负结果及 TwoLevel 补丁不纳入。

## 决策与历史检索

EXECUTE：检查 result_store 的三个 fdopen 所有权交接点，维持接口和数据策略。搜索 `result search JSON reliability scan memory`（limit5/max_scan200）实际扫描199、partial=true；返回词法候选不能证明可复用。直接读取 search93/report.md 和 artifact-fd77/report.md：前者已解决 JSON 深度，不重复；后者在 result_validation 中修复同类泄漏，但未覆盖 result_store 的 _read/_check_ref/_save。本轮必须新复现，不能沿用其13→0计数。

知识查询 `file descriptor ownership closefd` 的三个命中为推测解码/采样/CAR-LoRA，前提不匹配，不采用。已有十篇研究全文记录 read-boundary56/research_a.md、research_b.md 已重新阅读；采纳故障注入必须真实触发且保留正常对照的评测原则，不把记忆压缩算法强加到文件I/O。Python3.12官方 os.fdopen/open 文档2026-10-20重新核对；采用closefd=False借用描述符、finally由原始owner关闭的既有仓库模式。

## DAG、资源与边界

独立计划审查 → 生产者修前复现/局部修复/回归 → 独立 verify_experiment_result → 文档/发布消费者。当前无 tmux 和受管任务宿主 adapter，不能声称部署 ManagedEngine 或后台监督；本会话工具执行和真实独立新上下文审查，人工维护同一依赖门禁。仅本地标准库CPU、临时合成文件，无模型/GPU/新服务/付费资源。主控唯一维护源码、测试、TASK及报告；独立审查者只写 independent* 文件。

## 候选与停止条件

A：三个创建后借用fd的 try/finally；成功与异常都恰好关闭一次。_save仍先关闭/flush/fsync后原子link，finally清理临时名；不覆盖现有record。B：抽公共helper或先检查目录，额外重构/竞态不能替代所有权保障，本轮不采用。最多一次候选返修；无法保持语义则留检查点不发布。

## 固定验收（结果须独立核验）

- implementation：完整检查三处源码及public show/search/register_history；仅改变描述符所有权，拒绝/异常类别与记录字节语义保留。
- reference_boundary：真实目录输入与注入fdopen构造失败，在修前能测到泄漏；正常、fstat/read/write/flush/fsync/link失败、open失败、重复注册对照。真实成功open的fd必须可用fstat确认最终关闭；每个场景测试自行清理基线泄漏。
- data_integrity：源码/测试/输入哈希、固定基线、原始失败日志；记录/临时文件保留策略不可被修复改变。
- numerical_sanity：泄漏计数为非负整数，目标所有已触发故障/正常场景修后0泄漏；正常内容及异常身份可复核。
- measurement_validity：只主张泄漏fd减少，不以测试总耗时作提速。wall/RSS/token/模型质量未测，允许不适用。
- reproducibility：专项普通/-O、全库、Reader，独立审查并复跑冻结基线/候选故障对照；全部适用检查通过才消费/发布。

发布前fetch并复核并发改动，只暂存本次明确文件，普通非force更新main，回读远端SHA和树。缺验证保留待发布，不空提交。
