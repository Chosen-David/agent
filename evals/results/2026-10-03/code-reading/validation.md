# CODE-READ-2026-10-03 验证记录

基线：`a5328e4`；实现和检查日期：2026-10-03。测试在本轮执行环境真实执行。

| 检查 | 实际结果 | 可证明范围 |
| --- | --- | --- |
| `python -m unittest discover -s tests -v` | 86 tests，OK | 全仓脚本/静态契约与已有测试；其中10项为新增源码定位/分发测试 |
| `python -m unittest discover -s apps/paper-reader/tests -v` | 3 tests，OK | 既有paper-reader单元测试未退化 |
| `python scripts/sync_plugin_references.py --check` | exit 0 | 当前包内生成引用与源文件同步 |
| `git diff --check` | exit 0 | 补丁格式检查 |
| 独立review（真实独立审阅者） | 修复后通过；其独立运行新增10项测试全通过 | 审阅增量工具、路由/离线包、证据边界；没有重跑全套86+3或sglang |
| 合成阅读输出 | [实际静态分析](synthetic-analysis.md) | 作者按skill阅读；非盲测、非性能测量 |
| 真实任务 | 指定sglang SHA的只读阅读及16个Git/AST源码锚点生成成功；工作区检查为空 | 实际使用新工具定位真实代码；没有执行sglang或修改/push该目标 |

独立review先发现：Git replacement污染固定SHA、目录被当源码、formfeed导致AST/摘录行号不一致；均先复现再修复并补回归。另修复离线协调包可选helper说明及技能数同步。初轮测试的旧技能数量断言和待写文档链接问题已修复；最终全套结果如表。

真实项目报告及原始测试日志交付到本轮任务的仓库外目录，不提交未公开论文或完整任务材料。该代码阅读入口默认只读，不替用户批准目标代码修改。来源锁和许可证采用方式见 [采用依据](../../../../docs/code_reading_sources.md)。

限制：没有对旧/新skill做多次受控LLM对比，不能从这些检查推断正确率提升；源码定位脚本不验证主张语义、实际执行可达性或模型质量；第三方后端仅阅读研究、未安装、未集成。本轮sglang结论为静态机制核查，不是GPU/e2e结果。
