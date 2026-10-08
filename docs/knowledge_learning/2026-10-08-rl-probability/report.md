# 2026-10-08 RL／概率论知识维护

本轮以已授权的持续维护为范围；先保留取消发布的 engineering-192521 全部工作，再拉取并核对 main `b327113958124f2025a35f8cf15965cdc898c01c`，同步 15 个角色、436 个文件并通过安装检查。未恢复或发布旧取消批次，未写入人类专用 `doc/guide/`。

## 来源与采用

新增两张 published/source-checked、version 1 的论文结果卡。正式会议信息由 ICLR/PMLR 原始目录确认；原始 PDF 与固定源码的实际哈希见 [sources.json](sources.json)，上游全文与代码没有镜像到本库。

- `algo.rl-sft-trajectory-concentration`：[RL Squeezes, SFT Expands，ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/e52554a70e0df57a0bea11d1eca0c9b5-Abstract-Conference.html)。已读 Table 1、§3、B.1/B.2、C.4/C.5 对应方法/结果与负例；联合检查成功率、路径代理与预算。既有 checkpoint 对照、字符串聚类和有限采样不足以证明潜在能力或普适因果。
- `prob.horizon-aware-betting`：[Learning to Bet for Horizon-Aware Anytime-Valid Testing，ICML 2026](https://proceedings.mlr.press/v306/taga26a.html)。已读 §3、§4 及 E.2–E.6、F.4 对应设置；区分安全可预测下注的误报保证、附加条件下的有限时域功效、DQN 实证表现。拒绝将经验优势当作全局最优。E.6 的网格反演是近似；正文与训练表的 episodes 数不一致，保持未解决。

作者源码 `egetaga/learning-to-bet@9bf1b5e6caf4dc1ced5aabbbd69e849f265c73de` 的 README、MIT 许可、dp.py、dqn_entrypoint.py 与 dqn/env.py 已读，属于可追溯线索，不声明源码已执行或训练已复现。已有 COLT 2026 自归一化维度障碍卡不重复新增；既有精度/熵与测试鞅卡用于前提定位，真实检索引用见 prior-knowledge.json。

## 轮转修正

既有工程维护 prompt 每轮都把神经科学排在首位，尽管 `priority.next_domain` 已为 RL。现在显式以保存的游标作为本轮入口，只有缺失游标才初始化，记录已覆盖领域后推进。本轮覆盖 RL 和概率论，下轮为神经科学；3600 秒周期、数学游标和其他队列保留。这是指令契约修正，不是模型遵从率测量。

## 本机验证及独立验收

完整证据在 [doc/results/rl-probability-20261008](../../../doc/results/rl-probability-20261008/)。预先固定 DAG、六域验收协议与合同；生产者运行在 WSL/tmux 的冻结 LF checkout。实际结果为：

- 七套既有检索集共 116 条 file/SQLite 记录，逐题与 b327113 基线比较未退化；两条新问题在两个后端共4条记录均命中目标 top-3。
- 两张卡各4种决策情境，共8条：条件相同、条件缺失、环境不匹配、显式复现；没有任何情境自动批准跳过实验。
- 仓库 783 tests：772 通过、11 因可视化依赖缺失跳过；Reader 3/3；插件快照与知识格式检查通过。不是绝对无 bug 或真实模型质量证明。
- 单独的宿主进程 `host-retrieval-2576` 重建 SQLite、重放新查询与决策、核对完整输入/代码清单和原始分母，实际门禁为 `usable-with-scope`。这是独立确定性宿主验收，不冒充第二个 AI 或科学复核。无可信 provider 的同一合同保持 pending。

第一次宿主检查因既有 Windows PDF checkout 换行与 Linux Git 字节不一致而保持 pending，原 manifest、verifier 和结果留在 failed-first-host-review。修正后仅对 Git 确认无修改、且 canonical Git 字节恰等于冻结执行字节的历史文件允许核对；不放行脏文件，不改历史 PDF。最终门禁的 limitations 保留差异数量。

所有论文卡 `local_reproduction=not-run`。没有新模型训练、论文数值复现、未见题评测或 GPU 性能数据；检索是公开编写的开发回归。文献结论只支持筛选与最小迁移检查，用户指定复现和必做验收仍执行。

## 发布和持续任务

发布前再次 fetch/整合 main；以正常非强制方式发布并独立核对 SHA 和完整树，随后同步本机技能。具体回读与原小时 tmux 会话恢复证据在 publication-readback.md；此前本轮发布状态为待回读。WSL/tmux 可跨终端断连持续运行，Windows 关机/重启不保证会话存活。
