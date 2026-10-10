# [MATH-73] 分块 softmax 合并的代数与边界

Task-ID: MATH-73
Date: 2026-10-10

## Plan

EXECUTE 用户持续建设2/4/5/6/7/8/9/10；复用research-explore。独立有界文档研究，1200秒，至多两次普通独立审核session；主AI唯一作者。非受管实验DAG，没有可信ReviewSession或result_verifier，不做CPU/model/GPU/Lean/未见实验。仅自足推导和公开解析开发例，普通文档审查不能升级为实验验收。MATH65保持blocked，不续跑/改预算。

candidate.softmax-block-merge@1：非空有限实logits、同一query/head/model/cache version/mask/temperature/value坐标，互斥完整分片。三元state(m,l,u)合并，实数结合/交换律，自足证明；显式empty identity，all-empty输出undefined，拒NaN/+Inf与直接-inf减-inf；局部均值必须带LSE，exp2与自然对数单位匹配。重复/遗漏/版本混用与浮点重排不受精确代数保证。near/far完整质量与代理质量、层参数优化分开。

公开无定理名开发题：两worker给均值0/10及权重9/1，期望1而等权平均5；缺块/重复块/empty sentinel/极小权重巨大value拒用；三项等logit value(1e16,-1e16,1)展示浮点结合律失败；跨域离散Gibbs能量分片保留exp加权统计而不保证采样/物理相变。普通文档审核核对证明、例子与边界，非模型检索/拒用实测。保留真正未见测试不使用。

读取经典1805.02867v2 §3/Theorem1/§3.1；近期2606.01502v1 §3.2/3.3/4，仅筛选通信代价与数值相等边界，核对日期/版本/发表状态，禁止移植速度主张。已有检索partial有缺记录错误，相关输出卡只作前提参照不复用旧CPU数据。方案只写advice/results/detail与TASK/coverage/state，不动canonical/Skill/runtime/guide/SGLang；更新候选双索引、不改110/5/67计数与旧游标。

验收保存来源/knowledge_refs/公开开发题与审核hash、实际成本/限制；发布前同步main处理并发，直接main并核对远端SHA/父/树。后续实际kernel/多机实验需要固定源码、GPU、合法分片与数值协议，不由此宣称已有bug或提升。

## Progress

- 已同步main至934da4b，工作区干净；读取AGENTS/唯一TASK/角色/知识索引与持续状态/指南（GUIDE空），无同主题登记。候选检索记录已保存。

- 普通独立计划审核approve；补binary64舍入前提与candidate精确hash。文档完成待不同上下文证明复核，无CPU/GPU实验。

- 不同上下文普通独立文档复核初次revise仅hash来源措辞，已修并原记录保留；最终精确advice SHA approve，数学/解析例/跨域/拒用边界核对，无模型或数值实测。候选双索引、coverage gap、history追加；canonical计数与既有游标未改。
- 284受保护文件与934da4b基线字节一致；JSON/hash/CRLF感知diff检查为文档结构检查。直接main发布前同步与远端SHA/父/树核验；后续真实kernel与分片数值/总开销实验待资源，不启动生产。
