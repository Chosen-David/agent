# 一次独立静态审核原反馈

Reviewer: /root/sentry_reading_review_1958。以下保留返回正文；主控随后采纳两条非阻断编辑建议，无第二次审核。

结论：**accept，限本次冻结材料的手工静态复核**。未发现必须阻断的科学解读或源码适用性错误；不构成可信 ReviewSession、结果认证、生产放行或 SYSTEM-99 完成证据。

- **科学核对通过**：正确区分 online-from-scratch、持续更新的 held-out、冻结 playbook 的曝光对照；200 同检查点分叉保留 74 gain／101 tie／25 harm，未当成 200 独立任务，且限定 detector 选择范围。19.01M／12.32M＝约1.54倍是额外 token 用量；same-backbone verifier 不是独立验收；Replay 是 annotation-conditioned 环境。未将 playbook 准入解释为 MemoryLedger.correct／accept 授权或终态放行。
- **源码解读通过**：MaintenanceGate 仅在明确 handled、前后指纹相同且时间有效时记录 ACK；mailbox 索引与分页不提供全局闭包或语义验收，consume_handoff 与 ACK 分离；MemoryLedger.index 绑定完整 selected snapshot，但不证明语义相关集合完整；correct／accept 的实际用户来源或可信验收仍由宿主承担；basis_impact 不改写历史 ACK、不自动重跑。
- **prior 不可复用判断合理**：raw 为 scanned=334、partial=true、25 errors、3候选，均为 corpus 集成记录，任务／输入／指标不能支持恢复经验收益。知识候选及前提只按 inputs／reading 的手工记录审阅，未追认原检索或 corpus snapshot 的执行真实性。

实际完整读取：

- AGENTS.md；review-1958 的 checkpoint.json、reading.md、inputs.json。
- paper.txt：[0,14000)、[14000,28000)、[28000,37600)、[43354,57354)、[57354,71354)、[71354,85354)、[85354,99354)、[99354,100022)。合计94,268字符，覆盖§1–6、A.1–A.8、Eq1–2、Tables1–19及Fig1–4文字图注；未读中间 References 或 PDF。
- maintenance_gate.py 1–132全文件；communication.py 1–135、271–430；project_memory.py 284–345、439–511；handoff_basis.py 218–269。未扩展其它源码。

校验结果：

- reading.md：8498字符，SHA256 `4bcc6de6ab00904180efebe25533231ad4b1124791633f783908d0267ef3cca8`。
- inputs.json：SHA256 `8cc99a593cf1777ef70a6077fb00835a03d3e66c167d93dbc4fa3f6b9335682e`。
- inputs 全部9个 source_refs 均匹配。
- paper.html：539513 bytes，SHA `3ba4dd0126eca78f429d18dcb3ed29c0377d31306797352a08027445f4fe5f01`。
- paper.txt：100022字符／100691 bytes，SHA `ef2cb39de7d7c7221f8025bc035af9bc9e839666f6450c3d231cd8aa2b3a1e6c`。
- cache.json 的URL、长度和两项摘要完全一致；其自身SHA `8cd8b9e450f552b13ae270cc6dfbaeb5b56f163740fcc034094a930993570d5c`。
- prior_notes_sha256、prior-search raw SHA及3候选 record SHA均匹配。

无必要的科学返修。两处非阻断编辑建议：

1. reading.md 10、17–22行的历史“尚待／待核查”已有后半附录逐项回答，当前节标题也明确其历史性质。建议加“现已核查，见附录续读核查”，方便摘读；31、54行的“无独立角色调用／独审待调用”在发布时标明为**复核前快照**并补本次结果。
2. 第42行“k3/k10……SD重叠”宜改为“表中四舍五入后的 mean±SD 范围在边界接触；未提供显著性检验”。该处不影响目前“不宣称统计显著”的结论。

未验证：缓存的历史抓取及联网真实性、旧阅读行为、版本页提交时刻原件、作者代码／数据／完整轨迹、PDF像素、实验复现、真实宿主质量和全角色费用。HTML→TXT重新归一化尝试因缺少 bs4 在导入阶段失败，未重试，因此只确认缓存摘要和范围一致，不确认归一化过程。提交时间仅保留主控本次 web 版本页读数，不追认不存在的 local abstract cache。

本次未改文件、未测试或运行生产函数、未联网／调用实验模型／委派，未读取或删除其他作者 untracked 临时归档。全部旧耗尽／暂停门禁保持；全角色费用与实际质量仍 unknown；SYSTEM-99仍未完成，计数39不自动增加。
