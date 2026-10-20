# MEM-INDEX-96

Task-ID: MEM-INDEX-96
Date: 2026-10-20

## Plan

v1 / EXECUTE: 用户要求持续优化 agent 库，对齐远端，精读 agent infra，重点 cache 存储、文件管理、memory 与 token。PROJECT_ROOT=WORKFLOW_ROOT=C:/Users/WI/Desktop/home_work/AI_LLM/agent。只改本库；保留原有 dirty 文件与 stash，不改人类 guide、SGLang、既有服务/定时器。guide 文件存在且为空，无额外目标；不代写人类指南。

本轮有界工作：给 MemoryLedger 增加显式 index 导航，分页目录省去 content 正文，保留来源、依赖、状态、scope、内容哈希和条目哈希；完整账本仍为唯一存储，不新增持久摘要/模型已读缓存。目录仅导航，实际使用走 check/上下文依赖门禁。每页绑定项目、过滤条件及完整所选条目快照；后续页必须提供该 snapshot，修正/接受/新增/移除/正文或元数据变化拒绝旧 cursor。默认 list/check/history 不变。硬字符上限内只返回完整条目；不能容纳首项则失败，不能静默截字段。增加只读 storage 统计用于定位账本空闲页/索引占用，不自动 VACUUM 或删除证据。

依赖：实际历史查询/相关源码与原始文献 → 独立计划复核 → 实现/针对性回归与输出字节测量(producer=root) → verify_experiment_result(owner=独立原生 agent) → 必要最终回归 → 普通发布/远端SHA读回/安装同步。原生工具提供独立上下文；不声称部署 ReviewSession、受管后台 DAG 或新监控。唯一任务索引作者 root；reviewer 只写本轮 independent* 产物。最多两轮有界修复，无付费推理/GPU实验。

预定验收：目录翻页无漏/重/重排；空库/Unicode/同时间戳/候选/更正后 stale/superseded/精确scope/legacy schema/错误预算和旧snapshot拒绝；来源/依赖原样保留，目录绝不授信；storage 全程只读。固定合成长正文库比较 full list 与完整目录+一条必要正文读取的 UTF-8 字节；必须减少且原文精确恢复。不是总tokens/现金/QA/TTFT验收，不增加 token 成功计数。真实 token 与模型质量保持 unknown。

历史结果：ResultStore.search('cache memory token', limit=5,max_scan=500) 实际扫描249目录，partial=true，多处旧目录无record.json；词法候选主要为通信，条件不同不复用性能结论。另定向读取 memory-storage-20261015/research.md/report/task MEM-STORAGE-01，以及现有 memory-* 回归。已有分层访问/纠错方法可复用；本轮新目录/存储统计主张必须重新验证。建议 ADVICE-20261007-result-storage=adapt（沿用新 agent_doc/results 路径而非旧 doc/results 文字，避免重复复制）；DUAL-20261007-v1=adapt（真实独立上下文，明确手动宿主与运行时认证区别）。

产物：agent_doc/results/memory-index96-20261020/（本轮测试、测量、源码/环境绑定、研究与独立验收），tests/test_memory_index.py，agent_runtime/project_memory.py，workflows/project_memory_workflow.md 及生成镜像，CODEMAP。生产者 root；消费者独立验证者和未来 CLI 用户。保留历史失败/未完成父任务；不冒称整库优化完毕。

### v3 当前稳定验收（保留以上v1方法历史）

采用已独立复核的 validation_plan-native-v3.json / validation-dag-native-v3.json 与 contract-native-v3-bytes/tokens.json；方法改为真实UTF-8二进制子进程stdout，完整保留本机CRLF/LF，固定tiktoken==0.12.0/o200k_base并绑定rank/pattern/special/package/cache身份。全页+必要读取输出均计入；CLI请求/tool/history/推理答案不在本轮测量中，总model tokens/现金/QA/KV仍unknown。硬预算含os.linesep真实长度；字节/局部payload-token结论须经独立六领域验收，v1/v2测量口径被拒并保留。计划审核见本轮 independent-plan.md / independent-v3-plan.md。最终回归在WSL本地文件系统隔离副本执行，逐文件哈希核对真实candidate源；不冒称该临时git提交为远端版本。两轮有界修复限额保持，原文/旧失败不删除。

## Progress

- 已 fetch/ff 到 50c1ca1e74df1026ba05b4cfd53903605315b234，核对 HEAD=origin/main；setup_codex 和 --check 成功，16 skills/522 files。preexisting stash `codex-preserve-preexisting-20261020` 已 apply 并保留备份；.gitattributes、progress.json、三个 json_context 文件不纳入本轮提交。
- 知识工具：实际读取安装 model-with-knowledge 并执行其检索，命中 infra.pagedattention-kv / flashattention 等GPU卡；其GPU/负载前提与SQLite目录不同，拒用数值和算法保证，仅保留分层存储的研究线索。精读范围另记 research.md；不把摘要当全论文通读。

- v2补充验收（不改实现/原字节协议）：按相同六场景新增固定tiktoken==0.12.0/o200k_base的实际CLI载荷计数，隔离依赖/cache在ignored .agent-runs内；完整页/必要read/换行计入，工具调用/服务端/推理输出及本会话成本未知，非总token成功验收。原raw.json保留；新协议validation_plan-tokens-v2.json、新raw-tokens.json另存。首次历史查询249后本轮目录创建再查询250，差异来自新增本轮目录，非覆盖原观测。

- v3有界修复：独立验证指出v1/v2 StringIO与合成换行只计LF逻辑载荷，原生Windows stdout实际CRLF，原硬预算少预留1字符。保留旧数据/manifest为superseded不接受actual-wire主张；预算改按os.linesep，新增真实binary subprocess预算测试；measure_native.py/PYTHONIOENCODING=utf-8保留原生换行，新的validation_plan-native-v3.json、结果身份及数据另存。固定本轮源码为LF以匹配Git提交，重新冻结完整依赖，不沿用旧hash。

- 最终独立上下文/root/memory_index_verifier完成verify_experiment_result，两个native-v3合同通过六域usable-with-scope；宿主按实际调用身份与固定review SHA核验并显式注入inspect_result，accepted-native-v3-bytes/tokens.json记录结果。长正文24条目录+1正文载荷54147→6116 o200k tokens，非总model token；短文/全读反增保留。全库1357项6fail/1error/12skip，已独立确认基线同6fail，Reader原生UTF8 core2/app3及新远端精简规则3项通过；不声称全库通过。详细report/failure-history列原始证据与归档限制。
- 已整合并核对origin/main=dcc10b1；安装同步因本轮Skill引用未提交而按保护规则blocked，原安装保留，待发布后同步。原始三个json_context文件逐字节与stash一致；progress JSON值/.gitattributes内容仅正规换行差异，原改动保留不提交。等待普通发布与独立远端回读，父任务持续保持未完成。

- 发布闭环：feature main a48f70a156c94b155e760dbf27be21b02182db6b，tree319eb6e77b32e9f1d17eaa73837178fc0c33a6b5与完整暂存候选相同；GitHub普通带expected-parent更新、native fetch/HEAD及独立连接器读回确认。post-publication两个_snapshot绑定有效。setup_codex及--check均configured，16技能/525文件、9更新；不宣称运行中的模型已热加载。publication.json记录局部完成与全库/持续任务未完成边界。
