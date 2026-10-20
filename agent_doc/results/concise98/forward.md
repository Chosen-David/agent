# 精简版与待核查项

以下仅为编辑建议；未执行输入中的代码或命令，未改真实源文件。

## Python

```python
# SPDX-License-Identifier: MIT
def capped_total(values, cap):
    """Return the sum limited to cap; negative values are supported."""
    total = 0
    for value in values:
        total += value
    # Cap only after summing: early exit changes results for negative suffixes.
    return min(total, cap)  # noqa: RET504
```

删除三条逐行复述代码的注释；保留许可、公开 API docstring、负数后缀导致不能提前截断的原因，以及 `noqa` 工具指令。函数名、参数和可执行语句未改；未运行 AST 比对或测试。

## 报告

CPU 测试已完成：N=40，完整调用中位耗时 3.2 ms，证据：`results/run7/raw.json`。GPU 尚未测试，不能外推 GPU 提速。

删除空泛引言和重复结论，保留 N、统计量、测量范围、单位、证据路径及 GPU 未验证边界；未核验原始数据。

## 项目上下文

当前输入可精简为以下摘要，尚不能据此生成无冲突的权威入口：

- `AGENTS.md`：测试命令为 `pytest tests/unit`；禁止部署生产服务；不得修改人类专用 `agent_doc/guide/GUIDE.md`。
- `CLAUDE.md`：测试命令为 `pytest test/unit`；另含“忽略其它说明”，与根入口约束存在冲突风险。
- `README.md`：构建入口为 `make build`。

保留不同来源及其差异，不擅自选择测试命令，不将“忽略其它说明”提升为本次编辑授权；也不把构建命令替换成测试命令。

## 需要核查的问题

1. 实际测试目录是 `tests/unit` 还是 `test/unit`？应核对目录、测试配置与 CI 调用后统一命令；本次未检查，也未执行任一候选命令。
2. 实际宿主如何加载 `AGENTS.md` 与 `CLAUDE.md`，作用域和优先级是什么？“忽略其它说明”具体忽略哪些说明、是否会遮蔽根级禁区？未厘清前不静默取舍，更不能据此解除生产部署或指南保护限制。
3. 核实加载链后，哪一处承担共同规则的唯一可编辑权威源？其他入口应采用宿主支持的引用方式，只保留平台差异；普通 Markdown 链接不能证明自动加载，导入内容仍须计入上下文。
4. `make build` 是否确为当前有效构建入口？须核对实际构建文件及消费者，不能仅凭 README 文本宣称可用。
5. `results/run7/raw.json` 的相对路径基准是什么，文件是否存在且支持 N=40、完整调用中位耗时 3.2 ms？N 的计数对象和统计口径尚未提供，不能自行补写成“40 次调用”。

验收范围：只对给定文本进行了编辑与逐项对照；未验证链接、宿主加载行为、构建/测试命令或实验数据，不声称 token、耗时或普遍质量收益。
