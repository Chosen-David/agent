# 独立最终代码、数据与发布前验收

Task: RP-T-20261008-1515。Reviewer: `/root/mixture_final`。结论：**usable-with-scope**。这是实际候选与原始数据的验收，不是沿用计划 approve；远端发布和 CI 不在此结论内。

审查了 AGENTS、decision/project-document 协议、本轮计划/任务、FORMAT、公开 holdout 元数据、最终完整正文及元数据、开发和独立验证代码、原始结果、来源审查、运行命令和并发整合。独立重算与哈希证据在 `final_review.json`，可由 `final_verify.py` 重复审计。本次 235 项检查通过，当前无阻塞项。

## 科学与证据范围

逐式检查固定 λ 的非负指数超鞅、全实轴固定高斯混合、条件 Tonelli、平方配方、有限截断停止及递增事件极限，闭式与双侧边界反演相符。q 为可预测条件 MGF 代理，不能只用真实/经验方差；ρ 和 δ 必须预定。随机有限 q 不保证无条件 L1 的措辞问题已修复，最终正文与修订后独立审读正文相同。原始候选及修复记录保留。自包含证明支持 requires=[]，related 不冒充强依赖。

原文核对由独立 source-review 与 unseen reviewer 完成并保留具体 v9/式14/式51定位；本审查核对其证据及最终正文边界。公开来源许可标签可见，但独立许可全文/PDF 字节获取失败仍明确记录；不声称 PDF 哈希或正式刊物字节身份。14 项开发检查及独立 9 科学情形、9 机器检查、6 条双语检索与 canonical run3 均有原始数据和源码哈希。冻结 case 哈希未变。首次独立评审未发现 L1 问题的事实也保留，后续修订不冒充全新未见用例。

## 原始回归与命令

直接阅读 `scripts/eval_knowledge.py`、实际 runner 和比较脚本后，重新从 actual/expected/context_ids 计算每条 Recall@3、MRR、context recall、no-hit。原、round2、morphology 默认设置和原/round2 context8 共 **76 个 suite/backend/query 组合，四指标全部无退化**；query/expected 与原 fixture 完全一致。该计数包含重叠组合，不是 76 个独立任务。

基线和候选各 12 条命令收据的真实退出码及原始日志 SHA256 全部匹配。各全套 unittest 852 项，851 通过、1 skipped；Reader 各 3/3。validate/sync/sync-check/index/diff-check 均 exit 0。**五个旧检索评估命令在两个阶段均 exit 1，仍是绝对门槛失败；无退化并不将它们改为通过。** 本轮 original raw Recall@3=.8095238095、round2=.75，morphology files=0/sqlite=.75；历史 .95238 不是本轮数据。没有性能或模型效果推断。

## 整合、保护与修复历史

开始版本 b93e66c6f65cbc3a82c14472b9f657d8a38279d2；整合远端 31e6b94dc47d034eb4dabd1076cbd610e5883540 的 MATH-51 完成文档和 learning_state。分别核对 start→integrated 远端五个路径、integrated→worktree 本轮元数据，避免把合法并发变化混同本轮越界。旧 learning_state 所有历史项及非 history 字段均保留。

独立逐字节核对 215 个 protected 路径（包括原全部知识条目、运行时/检索脚本、fixture、holdout、guide），与 start 相同；旧 neuro 阻塞、T19–T23、SGLang 和历史失败未被本轮改写。完整 knowledge 镜像逐文件一致。当前 canonical ref 与 independent run3 和 postintegration 相同：math.normal-mixture-boundary v1 / `918e3c4c11706109d08a36c4bedec42ed25774285aa0a7db19f76078d25d730e`；snapshot `d43e482d0207eb792941eb07c8b39203d6de93fcc049f8c36e74a26a2f97073f`。

首次审计真实 blocked：一是将新合入的远端 MATH-51 路径计入 start 以来的本轮白名单，二是 coverage 正在修改时镜像暂不一致。完整首次结果保留在 final_review.json.prior_audits。后续按实际整合边界审查且镜像同步，235 项全通过。postintegration 的 sync-check/validate/index/diff-check exit 0，源码及 corpus snapshot 不变，故无需重复无关全套测试。

验收仅支持此知识卡及指定检索无退化；不证明形式化正确、真实流 MGF 成立、最优功效或 GPU/模型收益。主控仍须完成受授权的最终 fetch、提交、普通 push、远端 SHA/内容读回和 CI 可见性记录。后续若正文、元数据语义、运行代码、fixtures 或引用改变，应重新核查受影响证据。
