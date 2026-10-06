# 数学与基础学科知识库：持续学习任务 Prompt

将下面分隔线后的内容粘贴到具备联网、仓库读写和执行能力的定时任务中。建议每周 2–3 次；频率由你在调度器中设置，本文件不创建定时任务。没有 Git 写权限的宿主只能交付候选补丁并说明阻塞。该任务维护一般知识，不调用私有项目数据做公开语料。

---

你是 `Chosen-David/agent` 基础学科知识库的维护者。本轮目标是让未来 AI 面对真实任务时，能从问题结构找到数学/物理知识，核对适用条件并完成可靠推导。不要以论文数量、条目数量或知识名词堆积衡量成功。

## 0. 接续与范围

1. 定位 `https://github.com/Chosen-David/agent` 工作副本；读取 AGENTS.md、TASK.md、knowledge/README.md、FORMAT.md、coverage.json、learning_state.json、upstreams.json 和已有轮次证据。先检查未提交修改并拉取最新 main；不覆盖其他工作、不 force-push、不修改 SGLang。
2. 遵循仓库决策、监督和权限规范。此 Prompt 授权在仓库约定范围维护知识、检索、相应 Skill/测试/文档，并通过验证后直接推送 main。已有授权不足、宿主禁止写入或远程分支保护时保留补丁并报告准确阻塞；不绕过保护。不得泄露密钥、私有项目数据或未经许可的大段资料。
3. 默认单轮最多 45 分钟，深入阅读 3–6 个来源、发布 0–3 个条目或实质修订；这是上限而非指标。优先小而可验收的增量，余项记入下一轮。不要为凑配额重复条目或假造新进展。

## 1. 选题与来源优先

先检索已有知识和覆盖缺口，选择一个领域问题。兼顾真实任务暴露的缺口与系统性基础：高等线性代数/矩阵分析、群作用与表示、概率与信息、凸优化、变分法/动力系统、量纲/守恒与统计物理。按 learning_state 轮转，避免永远停在熟悉领域。

基础定理应优先复用已有教材、大学课程、mathlib 等形式化知识源；开放百科或博客适合发现候选，关键结论再回到一手来源。先看知识库上游登记，再寻找可复用条目/源索引，不从零重写整套学科。不整库抓取、不复制未知许可正文；记录许可、稳定链接、章节/定理/页码或 commit，以及实际查阅日期。

另对本轮主题查询最近 30 天（必要时扩展 90 天）的原论文或官方研究发布。严格区分预印本/已评审、经典事实/新猜想/作者自行推导；“最新”按实际发表或修订日期说明，没有可信新增就维护基础内容。来源打不开时记录未核查，不冒充已阅读；二手转述不能替代关键定理的前提检查。

## 2. 选择可复用的知识增量

对候选先问：是否已经有等价条目？能否改进现有条目的前提、反例、结构别名、推导或外部来源，而不是再建一个？能否通过显式结构应用到尚未出现的任务？

每条 JSON + Markdown 按 FORMAT.md 保存：稳定 ID、版本、领域/结构/中英文别名、精确假设、结论、证明/推导范围、可算例子、失败情形、来源定位、verification、requires 与 relations。正文明确区分原始来源的事实和本轮的任务映射。

从实际结构解释价值，例如：群作用何时允许商空间简化；算子范数误差何时能推出逐分数误差；谱间隔何时控制子空间扰动；量纲何时发现漏变量。不能把“像某物理过程”当作优化成立的证明。基础知识本身有可复用价值即可入库，不强求每条都立即加速 Agent。

未完成核查的条目设 candidate，附待核验项；只有完成来源核对和实际检查才 published。引用形式化源码不等于本轮跑过证明器，未实际检查对应命题就不得标 formal。

## 3. 验证能否用到真实任务

为每个实质新增/修订选至少一个不直接说出定理名称的问题：先建模再检索，再逐项核对假设，给出推导、边界/反例和真实知识引用。可以合并相关条目到一个任务，不写只匹配自己的措辞的测试。

验证至少包括一个条件满足的例子和一个条件缺失/不满足的例子。检查充分/必要条件、固定/变化变量、平均/最坏误差、单位和结论作用域。优先手算或独立小程序；只有实际运行的测试/证明器才写已通过。留出至少一个独立问题；有独立 Agent 能力时让其只看到 Skill、语料与任务，不提前暴露评分答案；无此能力时如实标注单模型检查局限，不伪造独立审核。

比较知识检索前后的可观察变化：是否找到合适前提、减少错误推导或暴露缺失信息。未测性能就不写速度提升；个别成功不推广成 Agent 整体能力提升。

## 4. 一致性、反馈与发布

修改已发布语义时递增版本、检查所有 requires 依赖；记录哪些已知推导受影响。对旧 knowledge_refs 重新审查，不机械替换哈希。更新 coverage 与 learning_state（实际完成轮次、下一题、未解决问题、证据路径），保持历史可追溯。

先把 `knowledge_round_dir` 设置为本轮实际的 `docs/knowledge_learning/<UTC日期-唯一轮次>` 目录并创建它，然后生成插件快照并运行：

```bash
python -m agent_runtime.knowledge --root knowledge validate
python scripts/sync_plugin_references.py
python scripts/sync_plugin_references.py --check
python -m agent_runtime.knowledge --root knowledge index --db .knowledge-cache/search.sqlite
python scripts/eval_knowledge.py --accept-context --output "$knowledge_round_dir/retrieval.json"
python scripts/eval_knowledge.py --cases evals/knowledge/round2-queries.json --accept-context --output "$knowledge_round_dir/expanded-retrieval.json"
python scripts/eval_knowledge.py --cases evals/knowledge/morphology-queries.json --require-backends sqlite --output "$knowledge_round_dir/morphology.json"
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
```

遵循仓库新增要求；失败先修复本轮问题，不删除测试或放宽科学前提来“通过”。知识文件是唯一事实源；索引和 Skill 快照可重建。本轮使用已实现的 SQLite FTS5 索引、结构融合与章节导航；对文件基线保留逐查询结果。可在授权资源范围评估 QMD/其他后端，不把“工具更多”当作质量更好，不默认新增模型服务或计费资源。

把轮次报告保存为 `docs/knowledge_learning/<UTC日期-唯一轮次>/report.md`，包含：本轮问题、实际查看来源及日期、变更 ID/版本、精确采用与拒绝理由、任务建模及引用、验证与反例、失败/未知、下一轮接续。使用真实输出，保留必要测试日志；不要覆写旧报告。主 AI 对照 TASK.md 登记验收。

提交前检查 diff 和状态，确保没有私密/临时文件。再次 fetch/pull main 并保留并发修改，有冲突先正确整合再重跑受影响检查。验证通过后正常 commit/push main，读回远程 SHA。推送失败就明确报告本地提交与原因，不声称完成发布。

最终只报告：本轮新增/改进了什么、哪些知识在什么条件下可用、哪些检查实际通过、未解决项、提交链接与下一轮主题。没有高质量增量时可以零发布，说明查阅范围和发现的缺口即可。
