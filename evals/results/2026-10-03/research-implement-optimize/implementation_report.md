# moving_average 修复与现有测量分析

运行 ID：`CODE-20261003-moving-average`。仅使用本任务目录的输入；原始文件未修改，修复版为 `outputs/buggy.py`，补丁为 `fix.diff`。

## 修复及契约

调用路径：调用 `moving_average(values, window)` 后直接构造窗口均值列表。原实现使用 `range(n-window)`，遗漏起点 `n-window`，即最后一个完整窗口。最小复现 `[1,2,3], window=2`：实际 `[1.5]`，应为 `[1.5,2.5]`；实际执行记录见 `minimal_reproduction.log`。窗口恰等于输入长度时也错误返回空列表。

修复为 `range(n-window+1)`，保留函数名称、双参数签名、列表返回值、切片求和与除法语义。正整数窗口超过输入长度或空输入返回 `[]`；不修改输入。新增窗口验证：非正整数值抛 `ValueError`，非整数类型抛 `TypeError`。采用整数 `__index__` 协议；将布尔值明确视为无效窗口。原说明未指定异常类型及布尔行为，这是本轮明确的边界约定。

## 已执行正确性检查

`check_moving_average.py` 使用独立端点枚举和 `Fraction` 精确有理数累加作为参照；浮点比较误差预设为相对/绝对 `1e-12`，未因失败调整。检查最后窗口、空输入、单元素、窗口为 1、等于或大于长度、零/负数、浮点输入、负数数据、元组、非法参数、整数协议以及列表输入不变。固定种子 `20261003` 的 200 个随机整数案例也通过。

- 原始实现：7 组测试执行，14 个失败、3 个错误，退出码 1；详见 `baseline_checks.log`。同一组内有多个子案例，因此失败数可大于测试组数。
- 修复实现：7 组测试全部通过，退出码 0；详见 `fixed_checks.log`。
- CSV 分析脚本：退出码 0；可复算结果见 `measurement_analysis.log`。

复现命令（实际已通过 Python 子进程执行；完整解释器路径、参数、版本和文件 SHA-256 见 `execution_evidence.json`）：

```bash
python /tmp/agent-forward-v1/research-implement-optimize/outputs/check_moving_average.py /tmp/agent-forward-v1/research-implement-optimize/inputs/buggy.py
python /tmp/agent-forward-v1/research-implement-optimize/outputs/check_moving_average.py
python /tmp/agent-forward-v1/research-implement-optimize/outputs/analyze_measurements.py
```

第一条命令预期失败，用于确认检查能抓住原始缺陷。还实际执行了目录内文件读取、`rg --files` 枚举、`mkdir -p`、Python 最小复现及 `difflib` 补丁生成。没有执行 GPU、性能基准或 profiler；测试框架报告的用时不作为性能证据。

## measurements.csv 支持的结论

定义：加速比 = baseline/candidate；延迟降幅 = (baseline-candidate)/baseline。以下只是所给 CSV 的描述性算术结果，不是本轮测量。

| 工作负载 | 范围 | baseline ms | candidate ms | 加速比 | 延迟降幅 |
| --- | --- | ---: | ---: | ---: | ---: |
| small | 端到端 | 100 | 80 | 1.25× | 20.00% |
| medium | 端到端 | 120 | 100 | 1.20× | 16.67% |
| large | 端到端 | 200 | 220 | 0.9091× | -10.00% |
| kernel | 仅 kernel | 20 | 10 | 2.00× | 50.00% |

候选在 small/medium 的记录值较低，在 large 退化。只有额外假定 small、medium、large 各运行一次并且可串行相加，端到端总计才是 420→400 ms，即 1.05×、延迟下降 4.76%；这不是已知生产负载混合的整体收益。kernel 行必须单独解读，不能与端到端相加或用其 2× 结果推断系统收益。

数据没有重复样本、方差、硬件、工作负载细节、计时边界、版本、正确性或与此函数的关联。不能推断显著性、稳定提升、因果瓶颈、跨规模泛化或本次修复的性能。原实现还少算一个窗口，未来计时必须先保证两版输出语义一致。

## 方案取舍、能力与限制

本轮已有终端和 Python 标准库足以完成有界修复；按“仅任务目录输入”约束使用本地能力路线（`offline_fallback`），未联网选型或安装新技能，没有宣称找到当前最先进或最快实现。加载的技能与输入版本已用 SHA-256 锁定。

设输入长度 n、窗口 w、输出数 k=max(n-w+1,0)。所选逐窗求和在有效窗口下为 O(k·w) 算术操作、O(w) 临时切片空间、O(k) 输出空间；Python 大整数运算成本还取决于位数。与原实现算法相同，只修复语义。窗口增量和可做到 O(n) 操作及 O(1) 辅助空间，但改变浮点累加顺序且遇到非有限数时需要特别处理；前缀和也可做到 O(n)，代价是 O(n) 辅助空间及数值差分风险。本次无性能实测支持这些改动，因此没有引入。算法模式为固定长度滑窗区间求和；无需外部库、低层 ISA 或 GPU。

未验证极端浮点数、所有第三方数值类型、自定义可变序列、生产集成或实际性能；本次保留原有 `sum` 数值行为，不新增精度保证。若要将 CSV 用于修复版的性能结论，下一步需先补齐数据来源、代码版本、相同输出的基线及计时契约，再执行经过授权的重复测量；当前修复交付不依赖此后续工作。
