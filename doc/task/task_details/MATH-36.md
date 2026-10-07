# [MATH-36] 局部扰动传播知识维护

Task-ID: MATH-36
Date: 2026-10-08

## Plan

独立owner=/root/propagation_verifier；冻结数据合同后核对实际代码/输入/证明与六项验收，再同步插件/检索/回归和普通main发布。 主AI唯一知识/TASK写入者；无生产更改、模型/GPU/付费/SGLang写入；公开开发样例不算未见。有界直接宿主，不宣称tmux或受管ReviewSession部署。

## Progress

已同步main 2e77b77；读取指南（空/只读）、角色、知识/持续状态，旧运行均completed；实际先查doc/results，旧局部几何与DP不能替代传播证据。

独立验收usable-with-scope，manifest 5dc9adee81f059ce1014bbfcba3931cbf532d8c1868885b2a4180789850368e2；验证SHA43fdcb9a592777e664e233a4e35d023ea5768451c8b7747b1ee7a127c724deff。实际宿主核对协作身份与完整冻结绑定后inspect_result通过。56案例/168步/28收缩/255断言，独立反例与原raw复现；180语料文件/6检索/3943编码token复核。74回归与同步通过；公开开发/非形式化，无模型/GPU或token节省。main发布待远端读回。

普通main实现提交 `8d8bcdb43f0bd67adf8f2f83361e4849121bc252` 已fetch读回，远端tree `f69069d135ab2c133029ab9cf1d5d2a61b2cb60f` 与本地验收树一致；无PR/强推。收尾只补发布证据。
