# [ART-BOUND-01] 文本比较序列化大小下界剪枝

Task-ID: ART-BOUND-01
Date: 2026-10-12

## Plan

持续优化 Agent 的既有授权，同接口局部优化、验收后推 main。基线 f8c92dc15bd948f0b50f748991cac782a913af0a；只改 artifact_context 现有路径，不新增平行生产版本、模型调用或服务器服务。空人类 GUIDE 保留。

实际先查 `artifact comparison multiline splice`：189 个目录，有缺失 record、partial=true；词法候选与本题不匹配。手工读取已有 artifact unique/equality 记录，仅用作旧方案与失败经验，不复用收益。历史连续优化 ledger 记录十篇全文阅读批次已完成；本轮未新增全文精读计数。近期 HDSO 的条件对照思想只作研究启发，不把论文数字当本库实测。Python 官方 difflib 文档核对了 matcher 最坏二次复杂度。

方法：在现有 len(JSON) 选择口径下，同 ref/sha 的假设单空 edit 是任意合法 edits 表示的下界。当前 target 长度 <= 下界时不可能被严格击败，安全跳过 matcher；token counter 模式不剪枝。否则保留原唯一单行守卫及 matcher。

验收：至少1000完整入口差分案例，普通字符、UTF8计数、偏好edit计数三种模式packet精确一致并恢复；artifact回归全过；2048重复行删除两行，warmup后7对交替入口计时，中位数至少降低50%。CPU预算90秒，无模型/GPU。DAG：历史查询→独立计划审读→补丁/生产测试→独立代码数据验证→报告/发布。宿主实际独立agent调用，未部署ManagedEngine/监督器，不称受管运行时回执已安装。

## Progress

- 独立新上下文计划审读 approve，特别限定为序列化字符口径，非UTF8字节最小化。
- 生产差分1229案例、3模式共3687检查，无packet/恢复差异；42项定向首次1FAIL是旧fixture预期调用matcher，调整长插入后复跑。
- 独立复测、全库回归与发布回读待完成，未提前标完成。
- 结果验收完成：生产3687精确packet检查；独立复跑3687及另2704独立oracle检查；42定向全过，全库1175项1167通过/8跳过，reader3通过。独立合成入口中位386.892123ms→0.592301ms，只有已测CPU场景收益。
- 未改变模型、token、账单与GPU结论；新全文阅读0，不将历史十篇计作本轮新增。完整证据见 `agent_doc/results/artifact-bound-20261012-2221/`。发布前核对main仍为f8c92dc；普通main发布与远端SHA/字节回读由主控收尾，未推前不称远端完成。
