# 工程知识持续学习任务

用于用户已授权的 `Chosen-David/agent` 维护。真实调度器调用 CLI/模型才算运行。默认每隔 3600 秒运行一次（北京时间显示；固定周期，错过的时段不并发追补），单轮最多 45 分钟，核查 3–6 个来源、发布 0–3 条；这是上限，零发布可接受。不新增付费/API/GPU 资源。

1. 读 AGENTS.md、TASK.md、knowledge/README.md、FORMAT.md、coverage.json、learning_state.json、upstreams.json、engineering_sources.json 与最近报告。脏副本先报告、停止该轮写入；拉取最新 main、保留他人工作、不 force push、不改 SGLang、不公开私人数据/凭据。
2. 用户当前优先级（2026-10-07）：RL（强化学习）与概率论，先在二者间轮转并优先补全研究缺口；保留 AI Infra → AI 算法 → 数据结构算法的后续队列，不覆盖数学游标。优先核查 2026 年正式接收的 ICLR/ICML/NeurIPS/COLT/ALT/UAI/AISTATS 原论文；纯概率论也检索 Annals of Probability、Probability Theory and Related Fields 等原始期刊。理论工作记录定理前提、概率量词、反例和证明核验范围，不强行编造实验。先检索避免重复；兼顾历年 NeurIPS/ICML/ICLR/ACL/EMNLP/MLSys/SOSP/OSDI/ASPLOS/SC 原论文与最近 30–90 天原始发布。核查实际日期、接收状态与预印本，不能把未确认的 NeurIPS 2026 投稿称为发表。实现优先作者仓库、PyTorch/PEFT、FlashAttention/FlashInfer、Faiss、ACL 等成熟来源。
3. 阅读 observation/setup/experiments/ablation、附录和实际源码；提炼正/负结果、baseline、硬件/软件/数据版本、dtype/长度/batch、metric/unit、图表定位和限制。保留训练预算/基线混杂，不把因果推测当实测。资料不可访问则 candidate；不整库复制、不镜像全文、不从零重造实现。
4. 按 engineering_knowledge_reuse_workflow.md 维护 JSON/Markdown。论文 local_reproduction=not-run，代码固定 40 位 commit、paths、symbols/API、license、local_execution=not-run；新的本机运行证据另存真实报告。说明卡能支持哪类决策、省哪类重复探索、仍需什么迁移验证。显式复现和用户必做实验不能替代。
5. 至少一个不直接命名方法的检索问题，加条件缺失/不匹配/显式复现负例；实现检查接口与许可。不以语法校验声称 GPU 性能；说明单模型检查局限，不启动无关多 Agent 实验。
6. 发布前 validate、生成/检查插件快照、重建派生索引、运行工程和旧知识检索回归、相关 unittest 与 reader 必需回归。不删失败测试、不只公布较好指标。更新 coverage / learning_state 的 engineering 历史与 priority.next_domain（RL / probability 轮转），优先级生效时保留 engineering 后续队列；不覆盖数学游标/他人历史。实质修订递增版本并处理 refs。
7. 写 `docs/knowledge_learning/<日期>-engineering-<唯一轮次>/report.md`：来源/哈希、采用拒绝理由、ID/版本、观测/条件、真实检查、未测项与下轮缺口。对照根 TASK.md，只维护本轮工程任务，不误勾其他任务。
8. 用户授权本库升级与持续维护发布：检查通过后 commit，push 前再次 fetch/pull main、整合并发、重跑受影响检查；正常 push main 并读回 SHA。Git CLI 无写认证时，可使用本会话已连接 GitHub 的写工具，按最新 main 为 parent/base tree 创建提交，update_ref 必须 force=false 且 expected_sha=实际读回的旧 SHA；再 git fetch 核对远端内容树。不得覆盖并发、提取凭据或绕过保护。没有任何可用写认证或被保护拒绝时保留提交/补丁，报告阻塞；ChatGPT 登录本身不是 GitHub 写认证。
9. 失败不无限重试，不伪报完成；最终报告进展/零增量、验证、局限、commit 与下题。不得只抓标题/摘要就声称提炼了实验结论。定时任务属于单独主维护流程，按已有授权执行，不自行扩展权限。

本机 Windows 桥的补充契约：宿主先执行 Git fetch/fast-forward；模型保持 workspace-write，.git 只读，不尝试修改权限。发布使用已连接 GitHub 的 create_tree/create_commit/update_ref（expected_sha、force=false），不需要本地 git commit。必须读回最新 main 并整合并发，来源与报告通过后才更新引用。宿主仅在工作文件树与已发布远端树完全一致时更新本地 Git 元数据，保留工作文件；不一致或越出知识维护路径时停止并保留成果。不得把 shell/Git 拒绝说成已成功，也不能自行扩大 sandbox。
