# [MATH-40] 独立验收与按需检索/main发布

Task-ID: MATH-40
Date: 2026-10-08

## Plan

单条有限softmaxKL知识，复用已有TV条目，不更改生产行为。公开64组CPU开发输入→独立verify_experiment_result→检索/回归/main。主AI唯一TASK/知识写者，独立owner由真实宿主协作指派。预算单卡、64组/一次重跑、六检索、一完整包；无SGLang/付费/GPU/模型。tmux不可用，有界直接宿主，不宣称ManagedEngine或ReviewSession部署。

## Progress

已同步main b327113；读取空只读GUIDE、15角色和持续状态，旧数学任务均completed；实际先查prior-results，旧TV已存在，新KL数据不可由旧数据替代。

独立六项验收usable-with-scope，实际host inspect_result通过；当前manifest6c74f665…/validation-v2 c6ef5da4…已核对。64组/10边界/4饱和，905断言；Decimal参考最大KL误差2.88e−16，raw/summary重跑一致，188语料/六检索/3625token复核。并发main0347d0e保留，74回归合并后通过。普通main发布读回待完成，无模型/GPU/未见测试/savings。

普通main实现提交`730bfb344c1636285e9cea87c0f51dda31fa149e`已fetch读回，树7104c1b28c6cd29ed49196436c37aa06cf1b34b5与本地一致；未force，并发修改保留。后续模型/真实trace留出仍未完成。
