# Advice会议的变更导航与SGLang提交复盘

Task-ID: ADV-POLL-01
Date: 2026-10-10

## Plan

针对用户要求阅读SGLang以前advice提交，核对高频会议路径后改善agent库。PROJECT_ROOT和WORKFLOW_ROOT均为本库；SGLang仅公开Git只读案例，不修改/回复/催办它，不执行其代码。先fetch/fast-forward并安装同步。保留原意见、当前约束、未决反例、独立验收及全局覆盖规则；人工guide禁止写入。

按当前结果检索 `advice lifecycle incremental`，113个候选目录、partial=false、32个历史路径错误，发现advice-context-20261009。只复用已读实现及设计线索，旧CPU/体积/验收数据不当本轮模型效果。安装知识搜索 `agent memory communication context` 返回QLoRA/HNSW/FlashAttention，训练/ANN/attention成本假设不能证明会议协议效果，拒绝迁移；不挂不存在的knowledge_refs。

冻结SGLang two-level-indexer为e771d2d，查看advice路径77个提交标题、8个详细diff、6份文件；只核对报告/回应内容，不重验其科研数字或执行成绩。增加有界、项目/SHA绑定的advice库存比较及显式CLI；首次枚举、修改/新增/删除全报，唯一同字节路径迁移只做导航，多义匹配不归并。CLI不输出正文/全量库存、不自动ACK/关闭/调度、不覆盖原文。无变化不能消除未决任务或其他依赖变化。

验收包括真实CLI、目录读取错误、坏/跨项目基线、路径/链接、预算、并发变化、归档后编辑、多义迁移与原全局advice门禁回归。先冻结来源/输入/代码/六域计划，由不同owner的verify_experiment_result复核CPU及静态来源后才使用结果。没有付费模型对照，不计第10次；若后续测模型，须新冻结小任务并计全部成本。最后普通发布main/远端读回/本机同步，保留并发改动。

## Plan v2 - 用户追加监督器审查

在原Plan不变的范围内，用户追加核查监督器运行原理与Claude新推意见。只读现有task_supervisor/scheduler/core/task_manifest及计划/结果verifier接口，保留Claude原报告，另写来源建议的adopt/adapt/reject/defer与真实调用边界。没有部署ETA计时器、修改其他会话定时任务或增加模型测量；CPU正式结果范围仍为原冻结八份代码。

## Progress

### v1 - 提交阅读与实现

完成上述只读来源获取及两条连续往返链复盘，定位archive仍被递归库存覆盖。已实现agent_runtime/advice_poll.py及scripts/advice_poll.py，并给出8项导航边界测试、7项旧全局范围测试。开发检查Windows14通过、1项符号链接检查因权限SKIP。独立静态审核发现并已修复：os.walk目录错误静默遗漏、JSON null基线冒充首次观察、Windows反斜杠snapshot-out越界。正式冻结/不同owner复核待完成；开发输出尚不作为验收数据。

### v2 - 固定宿主独立CPU与来源门禁

静态复核明确两次扫描非原子事务、资源数量并非实时延迟上限；随后换成逐项scandir并增加目录数预算及负例，原不可读目录回归保留。冻结8份当前源码/测试/直接治理依赖及六域计划后，正式Windows生产15项：14通过、1项符号链接权限SKIP。固定独立宿主在既有WSL tmux agent-token-optimizer实际执行15/15，含符号链接；LinuxPython3.14与WindowsPython3.12各自范围保留，不合成性能数据。不同owner verify_experiment_result复算原始Git元数据、8个diff统计/6个文件SHA/54文件体积，检查真实本项目CLI空变更及八份源码exact，ResultStore登记usable-with-scope。结果agent_doc/results/advice-link-20261010；来源/CPU范围限定，不执行SGLang、不增加付费模型A/B或第10次计数。

补充会议文档和角色文档入口，生成15份文档引用；同步时发现既有两份知识快照落后于已合并的数学提交，按当前knowledge源码刷新，不计新研究或token成功。普通发布/远端验证及最终安装同步待完成。

### v3 - 监督器调用链与并发提交

合并最新main 4b31485，保留MATH-68任务/数据与Claude更新的session_supervision_burn；TASK日期区冲突保留双方条目。已移除本轮误纳入索引的Python缓存，物理文件保留。监督器readback确认：每秒心跳为本地状态检查，scheduler已有变更合并及core空闲退避；worker到期maintain没有语义变更判断，publish复核可进入宿主verifier。回调是否推理、实际用量都取决于显式adapter，不把心跳频率当模型调用频率。

完成docs/token_optimization/supervision_cost.md，记录Claude数字仅为来源自报，适配事件/ETA/临时列表清理/职责去重的边界；不采纳跨宿主dangling依赖无害假设或删除canonical任务/独立验收。已读Anthropic Managed Agents官方全文和AgentDropout摘要，仅作设计线索不迁移实验收益。本轮没有新模型对照、部署或成功计数。

发布前再次fetch并保留75dc4ba的新GPU监督意见；补充“GPU空闲只是候选事件，不能证明作业完成/成功”的adapt/reject边界，要求owned job、退出状态、产物和独立验收。未执行或改变SGLang/GPU任务。

### v4 - 普通main发布与接入同步

已普通非force发布b41d1313b64103f686b0690d466f61f8aa7bcd18，GitHub独立读回ref与tree f385787b9a7148f80eb72f198f01f9216caedb2f一致；原生fetch后核对完整树、保留工作文件并同步到该HEAD。setup_codex更新17份受管文件（15份角色文档引用与2份知识快照），随后--check通过。合并并发数学/Claude提交；冻结8份生产源码与16项验收artifact绑定在发布后仍一致。

本任务的来源/CPU/文档及工具发布完成，publication.json记录其范围；尚未部署宿主模型唤醒门禁或验证真实token节省。100次连续优化仍9/100，本轮不增加计数，没有新增模型A/B或hourly优化器。后续独立任务需针对可信adapter的无变化maintain/重复verifier请求，先冻结短对照和质量失效oracle。
