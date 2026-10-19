# ATX-BOUNDARY-62 局部正确性修复计划

基线 b69b4150e41492183433b1061add742aaa44510b；用户授权 Agent 持续优化及验证后 main 发布。guide/GUIDE.md 为空，guide 全目录只读。独立 clone 的唯一既有未跟踪归档临时文件保留，不暂存。主控拥有源码、测试、TASK、报告；独立审查者只写本目录审查文件。flock /tmp/agent-audit.lock 串行维护。

只读发现：knowledge_index.sections 的标题正则末尾 `\s*#*\s*` 不要求闭合井号前有空格；可能删掉 C# / foo# 的正文字符；`\s+` 也误用 Unicode 空白作开头分隔，非空捕获遗漏空标题。追踪入口 knowledge CLI → navigate / indexed_search / build_index → sections → chunks.heading / 分段和摘录。修复仅 top-level ATX 原始标题边界，不实现完整 CommonMark 容器、HTML 或 inline rendering；保持现有 splitlines 行约定、fence、原文和层次算法。

依据：2026-10-19 核验 CommonMark 0.31.2 (2024-01-28) §4.2、例75/76/79：开头1–6个#后是ASCII空格/tab或行尾；可选闭合#串前后只能是规定空白；允许空标题，原始inline源码不解码。https://spec.commonmark.org/0.31.2/#atx-headings 。这是规范修复，不称论文算法创新或模型收益。read-boundary56/research_a.md 与 research_b.md 已有十篇定向精读，本轮读其记录作背景，不冒充十篇新读。

历史实际查询：result_store search 'knowledge dependency recursion deep chain' --limit 5 --max-scan 300：238扫描、partial=true、缺record错误；命中 memory-check04 等是不同模块，不能复用验收。源码已迭代且已有1100层测试，放弃重复深链修复。rg 定位 knowledge-fence-20261014-0705：旧修复明确未改标题正则，沿用其真实旧引擎重建验证方法，拒将旧通过当新证据。knowledge search 'parsing token boundary heading' 返回数学/推测解码候选，与解析语法不符，knowledge_refs=[]。

方法：仅改 sections 的ATX识别/原始标题去尾，保留body源字节；同步独立Skill镜像；ENGINE_VERSION v5→v6，旧缓存拒绝并公开重建。不改语料或检索预算。

DAG：独立计划审查 → 冻结表驱动测试/修前失败 → 局部实现/修后测试与真实115语料sections差分 → 独立结果检查 → 全库/Reader回归及独立发布复核 → 主控fetch/显式暂存/普通push回读。无可信managed adapter，不伪造ReviewSession或tmux部署；按允许的有界人工维护执行。

验收固定：不少于16个期望独立于实现的case覆盖粘连#、合法闭合、escaped#、空标题、ASCII/tab与NBSP、1–6/7井号、缩进、LF/CRLF/EOF、fence与parent/range；候选全通过且基线实际有失败。完整节点字典/原文拼接检查，真实语料差异逐项解释，不静默放宽。旧v5源码实际建库→新引擎拒绝→无源变化重建→二次no-op。canonical/mirror逐字节一致。全库和Reader通过；独立验收批准后发布。无速度主张，measurement_validity N/A，主指标为固定输入解析正确率，不外推LLM任务质量。CPU标准库测试，无付费/模型/GPU；单个检查最多60s轮询，全库依既有规模。失败保留、无收益不制造提交。

## 审核前版本绑定

- TASK SHA256 c35ebef5bbf28b5231a5be607cd497a13108d22b6b59d35240d6d278ad95d436；详情初始完整文件 SHA256 5fefea286d9e8c2bcc292c51acce468ff732c6aba3c3b0855788526986e798ac（后续仅追加Progress，收尾索引另核）。
- GUIDE.md SHA256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855；guide/README.md SHA256 f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261。README是既有目录治理说明，不新增人为授权假设。
- 未执行的固定测试 tests/test_knowledge_atx.py SHA256 253ad42cb0cf8a22155d508e09935fe5e472641ce8e3b8f2e148a20273cb112d：24输入×3行尾=72完整字典对照，另1层次案例。
- 追加实际更具体历史查询 'knowledge heading ATX sections'：239扫描、partial=true、70缺record错误；五候选 advice-context、cluster-planning、codex-pull-sync、combined-corpus-delta-v2、combined-corpus-v3 均不提供本ATX修复的验证，拒复用为新数据。该查询不证明穷尽历史。
