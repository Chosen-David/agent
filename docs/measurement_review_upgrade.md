# 测量噪声审稿升级

## 范围与已有能力

在 `da208c3` 的现有 reviewer/implementation 能力上补齐可执行检查，而非新角色。原 reviewer 已区分证据不足/错误、探索/确认、等效/非显著；原 experiment 已有 CPU fixture、GPU trusted adapter、配对计时和资源准入。本轮新增共享 measurement/evidence/redesign 契约、默认标准库检查及可选有界 SciPy CI，三角色离线同步单一脚本源。

普通使用只检查当前用户任务的证据，按需要设计补实验；**完整合成套件、盲测和模型评测仅用于开发/优化/明确评测请求**。没有新建日常自动 benchmark、GPU 任务或后台服务。可视化并发任务负责设计/渲染，本轮保留其改动，仅给图表消费者统计结论边界。

## 采用依据：实际材料与不照搬的部分

[来源锁](measurement_sources.lock.json) 给出源文件指纹/固定源码链接。只读学习上游，不复制 skill 或实现，不安装后端。

- [ASA 原始声明](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf)：统计阈值不能代替研究设计；显著性不表明效应大小或实践重要性。采用完整报告、效应/区间与上下文判断，拒绝“一个 p 值决定改进”。
- [SciPy bootstrap 官方 API](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html) 及安装的1.17 `_resampling.py`：实际读配对索引语义、BCa jackknife/resampling、退化 warning 与返回区间。使用库计算 cluster 配对均值差的 BCa，不自行实现万能统计检验。该窄分析不支持任意聚类/交叉/时间相关数据；依赖 SciPy≥1.15 的 rng 接口，缺失明确 blocked，不自动安装。
- [pyperf 官方 benchmark 规范](https://pyperf.readthedocs.io/en/latest/run_benchmark.html) 与 `_compare.py`/`_utils.py`：区分进程 runs、values、warmups、loops，保留真实层级。源码比较采用两样本 t 路径，单值/异常还有返回 significant 的分支；本轮**不采用**这些 fallback 作为科研证据，不将普通计时循环当独立模型试验，也不复制 system tune 权限修改。
- `ckorhonen/claude-skills` 的 scientific-critical-thinking SKILL 与 statistical_pitfalls：采用设计/偏差/selection/multiplicity/effect/CI 的问题框架；拒绝机械套医学 GRADE 层级、通用 n30/80% power 等阈值，以及把单侧检验限定为“反向效应不可能”的过强说法。原材料只是参考，不是自动执行命令。

pyperf 与所读 skill 根许可证 MIT；SciPy BSD-3-Clause，作为现有环境依赖使用，未 vendoring。ASA/文档链接用于归因与短篇综合，不重新分发全文。来源事实与本仓库设计取舍分别记录。

## 实现与调用

- [共享契约](../workflows/measurement_evidence_contract.md)：噪声来源、单位/配对/层级、预设效应界限、停止/precision/选择偏差、性能与准确率方案、图表尺度及 REV→CODE→复查。
- canonical 脚本：`plugins/research-assistant/skills/research-review/scripts/measurement_review.py`；sync 工具原样同步到 implementation 与主调度 skill，契约和公开合成 example 同步。
- skill 内 `python scripts/measurement_review.py references/measurement.example.json` 只检查当前材料；加 `--analyze` 才调用已有 SciPy；`--output` 拒绝覆盖。
- [开发回归测试](../tests/test_measurement_review.py)：缺原始数据、伪重复、聚类等权、选择/泄漏/事后阈值、配置缺失、派生溢出、可选停止、退化区间、真大效应和微小不确定效应。

默认状态 contract_ready_not_verified 只表示声明齐全。可选输出 conditional_interval_only、criterion_met 和 precision_met 也是依赖设计真实性的条件结果，不是模型胜负裁判。双侧95%区间的非劣/等效包含判据是预设的保守规则，不自称通用 TOST。没有 p-value；边际 CI 重叠不替代配对分析。

## 验证边界

独立代码审查发现并修复：有限输入相减溢出/巨大 JSON 整数；停止规则未强制预设。新增固定样本数与 precision 半宽字段，序贯/可选停止转交专用分析。合成例不含用户私密分数或论文数据。

开发例与留出盲测分开：`evals/noise_holdout/build.py` 固定 seed73019 生成12例，答案不发给被测角色。角色使用冻结 skill 快照实际调用宿主模型；10例 reviewer、2例 implementation CPU/mock。原始输出、输入指纹、dispatch和独立评分单独保存。它们证明本轮有限案例的实际表现，不证明普遍鲁棒或真实模型/GPU有效性。指令隔离不是 OS 访问隔离，独立人工/模型判断也不是密码学执行证明。

## 本轮实际验收结果

实现提交 `1237b28` 合并可视化 `15e633e` 后：全套 **239/239** + reader **3/3** 通过；[测试日志](measurement_evidence/tests.log)、[reader 日志](measurement_evidence/reader-tests.log)。新增测量专项11项，独立代码复审通过；offline sync 与 diff 检查通过。

真实角色盲测：固定 seed73019，**10 个 reviewer 案例 + 2 个 implementation 案例**，288 条原始 paired rows（不是288个独立实验单位），另有2个 summary/config-only 审稿输入。两个被测角色均实际读取冻结 skill 并生成 artifacts；第三个全新上下文的独立 judge 重算 paired/cluster 统计和4个BCa区间，复跑2个CPU mock。结果 **12/12 cases、48/48 判据 pass、0 fail、0 ungradable**；不是关键词或 expected 填充 actual。controller 再验证全部 output_hashes、每例四项唯一判据与证据路径。

- [分案例汇总](measurement_evidence/holdout-summary.json)
- [独立评分说明与限制](measurement_evidence/holdout-reviews/judge-notes.md)
- [角色输出](measurement_evidence/role-results/) 和 [逐项评分](measurement_evidence/holdout-reviews/)
- [完整冻结输入/输出/角色快照/dispatch/评分包](measurement_evidence/noise-holdout-v1.tar.gz)，[归档指纹](measurement_evidence/artifact-manifest.json)

案例包含真实大效应正例与零效应/配对误用/聚类相关/伪重复/混杂/缺CI/选择偏差/等效失败/漂移反例。c11 实际 mock OOM 后九个 ID、顺序、输出和种子与参考一致；c12 实际故意漏样本触发错误，没有 completed。独立评分记录了 RNG 描述和后续网格控制开销的轻微表述局限，未隐藏；这些未使预设判据失败。没有角色失败需重跑，开发阶段代码审查的两项缺陷及修复保留于上文。

该结果只支持这12例的有限识别能力，不能称全部稳健、真实GPU有效或统计覆盖率经过校准。实际模型/GPU仍 notrun；精确宿主模型版本/完整历史工具 trace 未暴露。没有启动后台 monitor；仅以前台本地 DAG 核对已有测试日志字节，独立角色评分与其分开。正常用户任务不自动触发本开发验收套件。
