# [MATH-27] 核验固定value输出Gram几何、局部Jacobian余项及线性margin，筛选Prism v2并验证跨域与失效条件

Task-ID: MATH-27
Date: 2026-10-07

## Plan

核验固定value输出Gram几何、局部Jacobian余项及线性margin，筛选Prism v2并验证跨域与失效条件。本轮只支持显示推导与有限CPU开发验证；无模型A/B、无GPU或生产行为修改，SGLang排除。独立验收先于消费/发布；预设协议与DAG见 `doc/results/math-geometry-20261007/`。

## Progress

- 同步最新main 4d9a6a7，工作树干净；无同任务活动agent，本地唯一run目录已登记。tmux不可用，不声称部署监控。指南目录不存在，按当前明确授权继续。
- 先检索已有结果：14个目录、5个词法候选；旧softmax数据不含新Gram/Jacobian测试，其他候选目标不匹配，均不作为新主张验收。
- 保留未见测试协议但未生成或运行；开发题公开后不得称未见题。

- 完成：568项数值与2项人工前提检查；独立Fraction/162项60位Decimal/625项分类扰动检查通过，正式验收usable-with-scope。无形式化证明或模型性能结论。
