# CONCISE-98 阅读与取舍（2026-10-20）

本次新增正文精读2篇；本批次10篇门槛尚未完成。历史read-boundary56十篇不重复计数；全文访问失败的2608.11095与2606.15828不计入。下轮继续本批次，不以重复唤醒或重复旧记录凑数量。

## 2602.11988v1：Evaluating AGENTS.md

[原文](https://arxiv.org/html/2602.11988v1)，2026-02-12。实际读§1–6、附录A文字与表1–3；未核验图中逐点数据，HTML附录B未显示提示词正文，不声称全附录精读。
问题：额外仓库说明是否提高任务完成率？方法：四种agent/model组合，SWE-bench Lite的300任务及AGENTbench的138任务，比较无说明、模型生成说明和人工说明。新基准的说明/测试借助gold patch生成，并人工检查部分泄题和过拟合风险。
核心证据：§4.2模型生成说明在8种设置中的5种降低完成率；表2显示成本增加。删除其余文档的消融方向改变，说明“信息是否重复”比“是否存在说明”更重要。§4.3发现工具说明确实被遵循，不能把负结果简单归因于模型不读规则。
局限：主要Python、每任务单次采样、测试覆盖不等于安全/长期可维护性；不能据此删除本库权限和证据门禁。采用：只删已证明重复/错误的入口文字，保留公共约束，按需载入专项流程。拒绝：把更短直接称为更快或更正确。

## 2601.20404v1：On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents

[原文](https://arxiv.org/html/2601.20404v1)，2026-01-28。实际读正文§1–5、表1及研究路线；外部在线补充未复现，不据占位DOI宣称正式发表。
方法：10仓库124个PR，单一Codex配置，同任务/快照成对比较有无根说明；PR限定≤100行且≤5文件。表1报告中位wall时间98.57→70.34秒、输出token2925→2440，但输入token中位数略增。
关键限制：§3.1.8明确未做完整功能正确性评测，仅人工抽查50任务是否非退化。§5把正确性和跨模型验证留作未来工作。因此它与前篇不构成简单矛盾：任务选择、说明来源和验收目标不同。
采用：未来性能实验使用同输入配对，并同时检查任务质量；本轮保留真实规则，先修失效路径。拒绝：把论文节省比例套到本仓库；本次只报告实际字节/路径/有限前向样例。

## Skill与官方规范

| 来源（读取于2026-10-20） | 处理 |
| --- | --- |
| [Anthropic code-simplifier](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md) | adapt：只清理当前范围，保持行为、可读性优先；不采用其React/JS偏好或自动扩大重构范围。 |
| [obra writing-clearly-and-concisely](https://github.com/obra/the-elements-of-style/blob/main/skills/writing-clearly-and-concisely/SKILL.md) | adapt：具体表达、删空话；不导入约12k-token英文教材，不套英语语法到中文。 |
| [Claude memory](https://code.claude.com/docs/en/memory#write-effective-instructions) | adapt：平台入口与按需技能分离；@import仍计加载成本。当前宿主Claude版本/实际加载未实测，不依赖新版本特性。 |
| [AGENTS.md规范](https://agents.md/) | adapt：正确文件名与子目录作用域；不未经许可改名、建symlink或删除既有指令。 |

上游默认分支未固定commit，仅作为已读取的设计参考；未复制/安装上游代码或正文，中文规则为本库独立编写。以后直接引入源码需另核许可与固定版本。
