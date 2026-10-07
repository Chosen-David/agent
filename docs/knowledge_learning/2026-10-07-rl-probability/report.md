# 每小时维护与 RL / 概率论研究增量

2026-10-07 用户要求每隔 1h，优先补充 RL 与概率论。已在既有 WSL/tmux 维护配置中设置 `interval_seconds=3600`，沿原到期槽位运行，长轮次跳过已过期槽位、禁止并发追补。旧周历状态只迁移一次，保留历史；同周期重启不重置 due。单轮45分钟和来源/卡片上限保持，用户优先级保存在学习状态与维护 Prompt。聊天界面不能迁入 tmux；后台任务已独立于终端，主机关机/睡眠期间不运行，恢复见维护指南。

本轮不是完整系统综述。检索 2026 年 ICLR/ICML/COLT/ALT 官方论文集，并核对下列六篇的相关正文、设置、实验/消融、定理和附录；未证实接收的投稿/预印本不冒称正式顶会。概率方向包含学习理论与序贯推断，未声称覆盖所有纯概率前沿。完整PDF仅私有缓存，不提交全文；字节哈希、页数和定位见 [sources.json](sources.json)。本轮开始的原39条保持，新增6条；发布前整合并发 `b9d7d19` 的1张线性求解知识卡后为46条。并发修订交接和 conditioning 产物均保留。

| 知识卡 | 正式来源 | 决策用途与保留边界 |
|---|---|---|
| algo.rl-entropy-numerical-control | [Entropy-preserving reinforcement learning, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/124dde499d62b58e97e42a45b26d7369-Abstract-Conference.html) | 先检查输出精度、clip与推理/训练概率差；区分AppWorld探索与AIME已有能力，保留测试选checkpoint偏差 |
| algo.rl-spurious-reward-regimes | [Exploration vs Exploitation, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/d99e8e80a6c41e148db686918dd7eab3-Abstract-Conference.html) | 随机奖励、初始先验与难度联合判断；保留无clip梯度爆炸和低熵错误模式 |
| algo.rs-grpo-exploration-tradeoff | [Risk-Sensitive Reinforcement Learning, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/4e6d14709eae0cbc49a1d19d87fb8b21-Abstract-Conference.html) | 同时验收pass@1/pass@k；保留表2负单元格、模型数量文字不一致和不同β设置 |
| prob.conformal-policy-control | [Conformal Policy Control, ICML 2026](https://proceedings.mlr.press/v306/prinster26a.html) | 区分边际期望界、稳定性余项和实用近似权重；不冒称逐样本安全或生物湿实验 |
| prob.self-normalized-dimension-barrier | [Self-Normalized Martingales and Uniform Regret Bounds for Linear Regression, COLT 2026](https://proceedings.mlr.press/v336/chen26f.html) | 高维双重统一无正则的反例；平滑设计与噪声前提不可省略；纯理论无伪造实验 |
| prob.vector-variance-aware-concentration | [Vector-valued self-normalized concentration inequalities beyond sub-Gaussianity, ALT 2026](https://proceedings.mlr.press/v313/martinez-taboada26a.html) | 区分固定时域/混合序贯、轻尾/任意重尾；保留高方差时次高斯界更紧的实验 |

<a id="algo.rl-entropy-numerical-control"></a><a id="algo.rl-spurious-reward-regimes"></a><a id="algo.rs-grpo-exploration-tradeoff"></a><a id="prob.conformal-policy-control"></a><a id="prob.self-normalized-dimension-barrier"></a><a id="prob.vector-variance-aware-concentration"></a>

原论文的相关图表已看渲染页：RS-GRPO p.9 Table2/Fig7、ALT p.16 Fig1、CPC p.8 Fig5；其余结果结合原文和定位读取。不对未独立复核的完整证明标 derivation-reviewed/formal。所有论文卡 `local_reproduction=not-run`，代码可用性不等于固定版本实现已验收。未运行GPU训练、临床/湿实验或大规模额外探索。

先检索已安装知识，实际基础候选为 betting-test-martingale、Hoeffding、alpha-spending；对照条件均值/可预测性与停止规则后扩充。旧数学游标、工程后续 Infra 队列、历史报告和并发 EFF 工作保留。新卡以导航边关联基础及相反结果，不注入整库到全局提示。

验证与限制：

- 调度10项测试覆盖真实失败runner、锁保留、旧周历迁移、重启、固定cadence、长轮次跳槽和非法间隔。
- [新卡检索](retrieval-rl-probability.json)：6个结构问题在 files/sqlite 均 Recall@3=1、MRR=1；另有英文无关问题无命中。这是人为编写的回归，不是盲测语义能力。
- [初次失败](retrieval-initial-failed.json)完整保留：中文“火星基地土壤盐度自动灌溉”在两个后端都误匹配已有实现卡；词法公共字/词不能判断领域相关性。其余6题均命中。后续把英文无关词用于词法无命中门禁，中文语义拒答作为未解决缺口，未宣称修复。
- 旧工程回归仍 Recall@3=1；基础集 raw Recall@3≈0.9524、round2≈0.875，其有界关系全文 context recall均1。morphology仅SQLite验收，raw Recall@3=0.75、context recall=1；files词形后备仍失败，原始结果全部保留。
- [24项决策检查](decisions.json)：六卡分别检查条件缺失、匹配、不同与显式复现。显式请求始终 `run_requested_experiment`，自动跳过始终false。字符串匹配仍需主AI科学复核。
- 下列 root 检索记录对应整合前45条；最终46条语料的同组回归另存 `integrated/`，其结果以 validation.json 为准。
- 全量程序/Reader/插件检查、真实部署和发布读回收录在 [validation.json](validation.json) 与后续 [publication.json](publication.json)。原PDF检查是来源核对，软件测试不证明论文可迁移。

下一轮优先：RL长时域credit assignment、离线评估/探索；概率论异方差经验置信序列、重尾稳健序贯推断、条件校准/随机矩阵，以及正式概率期刊。先查已有卡防重复，允许有证据的零增量，不为凑数发布。

最终整合验收：46条语料，新卡与工程 Recall@3=1；旧基础 context recall=1。合并后旧round2默认3候选 raw Recall@3=0.75/context recall=0.875，morphology SQLite raw=0.5/context=0.75；原失败记录保留。使用既有 `context --limit 5`，仍限制8条/20000字符后，两组预期项 context recall恢复为1，raw指标不变。新增评测参数只公开该设置，不改变运行时默认，也不宣称语义改善。全仓548项：537通过、11跳过；Reader3/3，插件与格式通过。首轮的周历旧断言失败已保留，并按用户新要求改为明确的3600秒断言。

发布与部署收尾：功能提交 `82aa5ad615a195bc56b801b294ab1637e255df8d`，完整Git树 `b762de0937c38c1eb5af0cb7f9386dd87c3cef39` 经API读回与native Git fetch独立核对。本机15技能/273文件已同步，实际安装CLI的六主题均Top1，见 installed-retrieval.json。督导v2对80项要求可报告并停止、live=false；v1因合入并发TASK版本变更而撤销，未伪称完成。只有本轮督导停止，现有每小时知识维护继续存活。最终TASK勾选与本记录是结束后的文档修订。
