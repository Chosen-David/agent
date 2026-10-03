# 代码阅读：覆盖核查与采用依据（2026-10-03）

基线 `a5328e4`。已读现有实现优化 SKILL、execution、workflow，以及通用/科研路由、角色注册表、伴读与讲解边界。现有实现角色已有复现/调用路径/证据规范，但主目标是修改和性能测量；没有独立只读入口、路径变体核查表或固定源码片段工具。继续往大型实现 prompt 堆规则不利于独立调用，因此新增紧凑 `code-reading`，复用原决策/权限约束；实现角色只加阅读流程路由。

检索后实际读取以下原始文件，而非仅参考 README/项目宣传。精确 commit、每个文件 SHA-256、永久链接及许可证文本位置见 [来源锁](code_reading_sources.lock.json)。这是定性源码评估，未安装或运行候选后端，没有跨工具质量/速度比较。

| 项目与实际入口 | 可取之处 | 局限与本次取舍 |
| --- | --- | --- |
| Anthropic claude-code `plugins/feature-dev/agents/code-explorer.md` | 从入口追踪到数据、按文件/行返回导航 | 阅读过的公开 prompt；根 LICENSE.md 是 Commercial Terms，不能称为开源许可证。只比较设计，不复制 prompt，不注册其工具/模型配置 |
| Trail of Bits skills `audit-context-building/SKILL.md`、`function-analyzer.md`、`workflows/audit-context.js` | 跨调用检查依赖假设；区分完整分析与紧凑记录，JS 的 RECORD_SCHEMA 约束结构输出 | 审计前置、按函数分派及专用 Workflow runtime 对一般只读问题偏重；schema 不证明语义正确。借鉴可定位的假设/未知项思想，不复制内容、schema 或分派实现；不要求逐函数启动 agent |
| Serena `symbol_tools.py` 的 FindSymbolTool/FindReferencingSymbolsTool；`repl/api/lsp_api.py:find_referencing_symbols` | 带路径约束的限定符号查找、引用位置及邻近片段；API 追到 symbol_retriever | 需要语言服务/项目同步，引用不等于可达调用；跨语言和动态分发仍需源码检查。本轮不安装，已有可用服务时可选；无服务时 rg+读函数体 |
| Aider `aider/repomap.py:get_tags_raw/get_ranked_tags` | tree-sitter definition/reference 捕获、词法回退、加权 PageRank 控制导航成本 | 名称引用图和重要性排序不是真实执行图，词法回退会丢语义；不据排名判定机制正确。不引入 parser/networkx/缓存，借鉴先定位窄切片再深入 |

新增工作流、证据脚本和合成 fixture 为本次独立编写，没有复制上游源码或大 prompt。Trail of Bits 仓库所读许可为 CC-BY-SA-4.0；Serena 根许可区分 application GPL-3.0-or-later 与 SolidLSP MIT；Aider 为 Apache-2.0。这里记录所读文件的许可信息与使用方式，不表示获得其它依赖或模型的授权。若将来复制/分发实现，须重新核对精确文件及其归属义务。

最终组合：入口/函数体/调用点导航 + 条件与状态闭合 + 默认/可选路径矩阵 + 定位证据。补充机制核查覆盖 shape、dtype、投影与选维、量化存储、预算与候选范围、强制集合、跳过范围、最终消费者，以及叙述/代码/实验冲突。脚本只固定 Git blob 证据，不声称实现通用调用图或自动事实判定。适用边界和测试见 [验证记录](code_reading_validation.md)。

## 已读原始来源永久链接

- anthropics/claude-code @ `1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528`：[plugins/feature-dev/agents/code-explorer.md](https://github.com/anthropics/claude-code/blob/1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528/plugins/feature-dev/agents/code-explorer.md) · [LICENSE.md](https://github.com/anthropics/claude-code/blob/1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528/LICENSE.md)
- oraios/serena @ `d0f7f92631c23dc4c5ed0b5ccd35bc623b19a809`：[src/serena/tools/symbol_tools.py](https://github.com/oraios/serena/blob/d0f7f92631c23dc4c5ed0b5ccd35bc623b19a809/src/serena/tools/symbol_tools.py) · [src/serena/repl/api/lsp_api.py](https://github.com/oraios/serena/blob/d0f7f92631c23dc4c5ed0b5ccd35bc623b19a809/src/serena/repl/api/lsp_api.py) · [LICENSE](https://github.com/oraios/serena/blob/d0f7f92631c23dc4c5ed0b5ccd35bc623b19a809/LICENSE)
- Aider-AI/aider @ `5dc9490bb35f9729ef2c95d00a19ccd30c26339c`：[aider/repomap.py](https://github.com/Aider-AI/aider/blob/5dc9490bb35f9729ef2c95d00a19ccd30c26339c/aider/repomap.py) · [LICENSE.txt](https://github.com/Aider-AI/aider/blob/5dc9490bb35f9729ef2c95d00a19ccd30c26339c/LICENSE.txt)
- trailofbits/skills @ `82fe8226252622fa807643bdca1710901198553a`：[plugins/audit-context-building/skills/audit-context-building/SKILL.md](https://github.com/trailofbits/skills/blob/82fe8226252622fa807643bdca1710901198553a/plugins/audit-context-building/skills/audit-context-building/SKILL.md) · [plugins/audit-context-building/agents/function-analyzer.md](https://github.com/trailofbits/skills/blob/82fe8226252622fa807643bdca1710901198553a/plugins/audit-context-building/agents/function-analyzer.md) · [plugins/audit-context-building/workflows/audit-context.js](https://github.com/trailofbits/skills/blob/82fe8226252622fa807643bdca1710901198553a/plugins/audit-context-building/workflows/audit-context.js) · [LICENSE](https://github.com/trailofbits/skills/blob/82fe8226252622fa807643bdca1710901198553a/LICENSE)
