# CONCISE-98 独立结果验收

结论：**usable-with-scope**。本轮入口去重、三个既有 Skill 的按需规则接入及一次独立编辑样例通过；十篇阅读批次仍为 **2/10，未完成**。本文件不是 ManagedEngine/ReviewSession 回执、发布许可或模型质量/速度验收。

## 实际核验

基线：`50c1ca1e74df1026ba05b4cfd53903605315b234`。独立读取实际 diff、源工作流、同步器、三份 Skill、专项测试、fixture、forward、research、report 与 Plan/Progress。

| 核验项 | 观察与判定 |
| --- | --- |
| AGENTS 原文 | 程序移除新增导航段后与基线原始字节完全相同；原 11786 字节完整保留，新增 380 字节。不是重写或删权限。 |
| CLAUDE 责任 | 保留 `@AGENTS.md`、主控及首次安装入口；补不支持 import 时显式读取的后备。删除的任务所有权/tmux、唯一 TASK、产物交接、人类指南、建议处置、独立结果验收及历史检索职责，均在 AGENTS 原文对应节保留，路径已是 canonical `agent_doc/`。 |
| 入口计量 | 独立重算 CLAUDE 2515→813 字节，`(?<!agent_)doc/` 8→0；AGENTS 11786→12166 字节；两入口合计减少 1322 字节。该口径不含其他加载内容，更不是实际 token/计费/推理耗时。 |
| 触发与镜像 | code-organization 的 description 明确精简/AGENTS/CLAUDE；三个既有 Skill 均有按需本地 reference。MAPPINGS 仅增加这三个目标，无新角色；同步检查通过，源与生成格式一致，本地入口存在且链接闭合。未验证用户本地安装或真实宿主自动加载。 |
| Python fixture | 从两个 Markdown 提取 Python 块，逐项比较可执行 token（忽略 COMMENT、NL、ENCODING）、`ast.dump` 及公开 docstring，全部相等；SPDX、noqa 与负数后缀/截断顺序原因逐字保留。只删除三条直译注释，未执行示例函数。 |
| 报告 fixture | CPU、N=40、完整调用中位耗时、3.2 ms、证据路径、GPU 未测试及不能外推均保留；未把 N 解释成未经给定的调用次数，未自称验证原始数据。 |
| 上下文 fixture | 两个不同 pytest 命令及来源、`make build`、禁止生产部署、人类 guide 只读均保留；“忽略其它说明”标为冲突风险，没有被执行或升级成授权。待核查宿主/目录/证据问题明确，无静默择一。 |
| 范围保护 | 实际差异无 guide、历史报告、SGLang 或 runtime 算法修改，无活跃路径迁移。RESULT-TIME-97 保持未完成，不由本轮验收冒领。 |

## 测试证据

独立重新执行：

```text
python -m unittest tests.test_concise_engineering tests.test_plugin_reference_sync -v
Ran 4 tests in 0.100s — OK
python scripts/sync_plugin_references.py --check
exit 0
python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.578s — OK
git -c core.whitespace=cr-at-eol diff --check
exit 0
```

读取完整回归日志 `/tmp/concise98-tests.log`：1350 项、90.729s、OK (skipped=8)，即 1342 执行通过、8 跳过；7 项缺可视化依赖，1 项 tmux 宿主 opt-in。日志 SHA-256 `c643a28b92d001b1a4503e52ab206d0d729cf83ec204a67460949d422ae6cde6`。本审阅没有重新执行全套，不能把跳过项称通过或把该测试耗时称模型耗时。修前失败目前仅在 report 摘录可见，未独立复现或查得原始失败日志，不据此作额外收益结论。

## 阅读与追加建议边界

独立打开两篇原始 HTML，核对 research 中主要方法、样本/表格数值及限制：[2602.11988v1](https://arxiv.org/html/2602.11988v1) 的 §3–5 支持不同说明来源/冗余条件需区分；[2601.20404v1](https://arxiv.org/html/2601.20404v1) 的 §3.1.8、表1和 §5 明确完整正确性验收缺失。笔记的关键事实及“不外推本仓库收益”取舍合理。审阅不替代作者真实阅读过程证明，也未独立逐点读取图像；缺附录 B 提示词和外部补充未复现的限制保留。新增阅读计 2，不重计旧十篇；本批十篇尚缺 8。

追加多 AI/advice/memory 内容是建议而非已实施架构。已读 `advice_poll.py`、`advice_context.py`、`project_docs.py` 的递归快照/全局处置/节点采纳过滤及 `project_memory.py` 的 MemoryLedger：与报告所述接口范围一致。MemoryLedger 是本地审计账本，不是模型记忆 API、科学验证器或跨机共享服务；不能推断已部署。advice 33 文件/263382 字节和 TASK 基线 59626 字节可复核；任务详情随 Progress 写入变化，当前 315 文件/823918 字节，报告旧 823383 字节应标盘点时点或更新，不影响此处代码验收。

## 收尾条件与冻结输入

发布报告须补全已结束的全库回归，建议把临时日志按原字节保存到本 run 并核对上述哈希；不要保留“完整回归待收尾”而同时汇报完成。后续文档进度追加不等于源码重新验收；任何实际规则/样例变动需重查相关项。所有实际部署、发布、十篇阅读及性能收益均不在本次已通过范围。

| 输入 | SHA-256 |
| --- | --- |
| fixtures.md | `aa97a48b284375e90fad8ff0e98ed0a98d2825e3985b633d3187a11241aa2413` |
| forward.md | `ebd2df7515a1a61fc116788d18abe3b875b233e31d24834107f238c6b92b8d2c` |
| workflows/concise_engineering.md | `6d342d49dd782b837407ecfe29e1eb972e7b0ce937a76c550284dc3ed06223c9` |
| research.md | `f4a4f6b87cade4a45d26cff9cd11bdd0faa6080d324facb3ba5efed2dcafcefa` |
| report.md（审阅时，待上述收尾） | `9c843afa69a6a510e821b65ba0c034e2b03c82e6e421a9344acc504f41ac6e2a` |
| tests/test_concise_engineering.py | `825c5235ffced43424ab79ec3b2359493899432957409d8267c6c59b46e662ee` |

本次仅写本验收文件，未改源或代主控更新 TASK。

## 收尾复核

主控已补全 report 的全套结果与 Python/Linux/CPU 环境说明，删除“完整回归待收尾”；现 report SHA-256 为 `f294115e9e2949d9c57053a4b1958651e18e49c1385f8391ba1c7b6f3beac776`。实际完整日志已保存到 `.agent-runs/concise98/full-tests.log`，哈希与以上临时原件一致。

另读取 `.agent-runs/concise98/baseline-replay.log`（SHA-256 `8647e6131e7a04f9aff9e41b50bd8d00567497d907ea61f1886976bfe45f7e30`），确认为 3 项中 2 fail、1 error：旧路径、缺 Skill 引用、缺新工作流。独立比较重放目录 `/tmp/concise98-before.yRz9M3` 中 CLAUDE、AGENTS、三个 Skill 与固定基线的字节，全部一致；所用新测试亦与当前测试字节一致。该记录验证的是结构回归在旧源码的预期失败，明确不是第一次执行的原始日志，也不是旧模型行为失败。此收尾满足日志归档与回归记录要求；总体结论仍为上述有范围通过，2/10 阅读未完成。
