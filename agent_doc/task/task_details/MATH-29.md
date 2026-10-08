# [MATH-29] 加权双线性低秩知识与迁移

Task-ID: MATH-29
Date: 2026-10-07

## Plan

在既有持续数学授权下完成一个有界主题，保留其他任务与人类guide；只维护知识/证据，不改SGLang或生产attention。验证条件为显示推导、CPU产品分布/反例、两个后端结构检索、独立验收、插件同步与相关回归；main发布须先刷新、无force推送并读回。模型A/B、GPU和未见留出不在本轮验收范围。

## Progress

- main已同步到4d3751d，开始时工作树干净，上一数学状态completed；空的人类GUIDE.md已读且不改。
- 复用SVD/输出几何，无新Skill。冻结协议与producer→independent verify→consumer合同见`doc/results/math-weighted-bilinear-20261007/`。
- 初步CPU生产2698项有限断言、224条产品分布记录；未充当一般证明或模型实测。独立结果仍待读回，尚不报告通过。
- 无新自动化/后台服务；有界宿主调用去重状态在.agent-runs/，没有声称部署双主ReviewSession或tmux。
- 下一步：独立核验后同步相关回归，刷新main发布并核对远端。

- 独立验收v2 usable-with-scope：原始数据重跑一致、非零均值矩形Cholesky交叉检查、检索/引用与成本核对通过。代码绑定缺项与旧回执失效均保留并版本化修正。
- 74项相关知识单测通过；格式87项有效、插件镜像与knowledge refs通过。当前仍无模型/GPU/未见验收。MATH-30等待实际main推送和远端SHA。

- main知识提交8430d377e9329b220bbeb721d0df820919b82fff已实际发布并通过git fetch/ls-remote核对；远端tree fa4eeb68c46ed363b0e6ce3a1e95c512089ff098与本地验证树一致。HTTPS缺凭据，使用既有GitHub接口；未force更新，无SGLang写入。
