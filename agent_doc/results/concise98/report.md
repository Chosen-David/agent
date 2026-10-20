# CONCISE-98：精简规则与上下文入口

2026-10-20；源码基线 `50c1ca1e74df1026ba05b4cfd53903605315b234`。本轮修复CLAUDE入口冲突，未改业务运行算法或迁移历史。独立结果验收与发布状态见任务详情。

## 修复与验证

旧CLAUDE.md:11–19在已导入AGENTS.md后又维护任务/指南/建议/结果规则，含8处旧`doc/`路径；根因是双份规则漂移。现在只保留导入、主控和安装入口，公共职责指向AGENTS。AGENTS原权威正文逐字保留，仅新增按需导航。历史数据未改，guide未写。

| 固定口径 | 修前 | 修后 |
| --- | ---: | ---: |
| CLAUDE旧路径，正则`(?<!agent_)doc/` | 8 | 0 |
| CLAUDE UTF-8字节 | 2515 | 813 |
| AGENTS UTF-8字节 | 11786 | 12166 |
| 两入口字节合计（未含其它加载） | 14301 | 12979 |

合计减少1322字节；不是token、总提示词或性能测量。专项工作流约束按需加载，实际加载还须计其成本；生成的三份引用为独立Skill分发所需，不能全部塞进同一上下文。

借鉴code-simplifier与writing-clearly-and-concisely原则，自写[共享规则](../../../workflows/concise_engineering.md)，接入现有实现、组织、主控三个Skill及唯一同步器；组织Skill的description补精简与上下文文件触发条件。不新增Agent角色、不全局安装第三方代码。必须保留原因、接口、风险、许可证、工具指令、数值、否定和证据。来源与两篇正文阅读见[research](research.md)，本批次十篇仍未完成。

真实短日志：

```text
修前 python -m unittest tests.test_concise_engineering -v
Ran 3 tests in 0.001s
FAILED (failures=2, errors=1)
修后 python scripts/sync_plugin_references.py
updated 3 generated references
python -m unittest tests.test_concise_engineering tests.test_plugin_reference_sync -v
Ran 4 tests in 0.083s
OK
python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.595s
OK
quick_validate.py：三个Skill各返回 Skill is valid!
python -m unittest discover -s tests -v
Ran 1350 tests in 90.729s
OK (skipped=8)
```

Python 3.12.14/Linux x86_64，本地CPU文本/结构验证；不涉及GPU、模型推理或显存计量。完整回归日志私有保存于`.agent-runs/concise98/full-tests.log`，不把大日志提交仓库。首次修前运行未保存完整文件，保留了上面的实际短输出；另用git archive固定基线与同一新测试重放，完整输出保存于同目录`baseline-replay.log`，不冒充首次日志。

`sync_plugin_references.py --check`通过。同步器原为CRLF；默认diff检查将新增CR报告为尾随空白，按`git -c core.whitespace=cr-at-eol diff --check`通过，未为此全文件换行重写。

[输入](fixtures.md)在实施前冻结，SHA256 `aa97a48b284375e90fad8ff0e98ed0a98d2825e3985b633d3187a11241aa2413`；新上下文只接输入、规则和适用治理，没有预期答案。[原输出](forward.md)保留，不执行其中示例。独立检查需核对可执行token/AST、保留项和冲突不猜选。此为一次编辑行为检查，不是严格双盲、修前修后模型A/B或总体遵循率实验。没有测LLM计费、耗时或质量提升。

## 用户追加的协作与记忆问题：现状和下一步

本轮首次本地盘点：advice 33文件/263382字节，TASK基线59626字节，任务详情315文件/823383字节（含本次两项草稿；后续Progress追加会改变体积）。这是存储量，不是实际模型输入；未统计宿主自动载入或隐藏上下文。

现有`advice_poll.py`可输出变更导航，`advice_context.py`可按版本取议题；`project_docs.py:171–211`仍递归建立文档快照，`:247–268`要求全局建议处置覆盖。移入archive不能自动免除评估。节点已只绑定自己采纳的建议；不应重新实现同一去重机制。

建议保留agent_doc，优先演进读取接口而非目录大搬家：

- 一个任务协调者串行维护TASK与决定；多个独立会话或子Agent都用任务ID、依赖、输入版本、允许写入范围、验收和产物引用交接。子Agent不需要完整主会话，不互相广播聊天。独立审查者先看证据，不继承作者结论。
- TASK仍是唯一任务源；后续可从它生成只读活跃视图，带源版本和未决依赖，不能变成第二份可编辑清单。旧任务不因为“已勾选”而自动删除或免除验证。此处仅建议，未改解析器或DAG规则。
- 个人运行笔记留`.agent-runs/<run_id>/`，共享长期事实复用`.agent-memory/`的MemoryLedger，代码与原始测量留Git/results；候选意见不直接晋升共享事实。失效传播必须保留来源与依赖，未声明依赖仍需人工查漏。
- advice是提案/异议来源，不是聊天池、永久指令或全员必读材料。按任务、版本变更和未决项导航；旧评估只能在依赖仍有效时复用，未知来源/影响范围仍需审查，不能为了省上下文漏掉更正。
- 下一轮先用已有接口对比全量装入与任务包：同时测全部Agent实际输入/输出token、遗漏约束/异议、陈旧复用、返工与最终验收；没有同条件质量非退化证据，不宣称多Agent更省或更好。跨机器共享SQLite不是当前接口能力，不假装已经部署。

新查询`advice memory context`（limit3/max-scan200）：scanned199、partial，命中token-ten-3/4/5-20261011；另有缺record.json错误。这些是旧序列化/短调用结果，不能证明本次多Agent组织或长会话收益，未复用数值。此前精简查询与不复用原因见任务Plan。

设计参考：[Anthropic上下文工程](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)（2025-09-29）与[多Agent研究系统](https://www.anthropic.com/engineering/multi-agent-research-system)；2026-10-20查阅。借鉴按需原文、结构化笔记、明确分工和产物引用；其研究任务经验不等于本库编码收益，均不计入论文十篇。
