# SYSTEM-99 阶段 A 独立计划审查

日期：2026-10-20。审查角色：`/root/system99_plan_review`，不负责源代码、TASK 或测试写入。

技术决定：**revise**。16 处索引格式修复与 5 份详情补齐的方向成立；先关闭下列三个阻断项再冻结执行版本。阶段 A 只能是 SYSTEM-99 检查点，小时唤醒、小 bug、单次提交均不计作一个完成批次。

本文是独立技术反馈，不是 ReviewSession 认证回执、工具授权、结果验收或发布许可。没有真实宿主接口不得人工补造通过；缺少的模型 A/B、跨机器、监督/恢复后端等继续使相应分支及整批验收未完成。

## 审查对象与实际读取

项目根：`/workspace/scratch/6416f20dc59b/agent-audit97`。读取时 HEAD 为 `dcc10b10537a3b410a25f6ef3f2c842a3c1777b4`。

已读 AGENTS、decision_review、project_document、dual_main、result_reuse、result_validation、concise_engineering、review_main，当前索引、五份问题详情、两份 guide，以及实际 project_docs/task_manifest/task_context/core/plan_review 的相关生产者、消费者和恢复门禁。GUIDE.md 为 0 字节；README 说明其为用户一次性要求 AI 创建的目录说明，不据此推定新的人工业务授权。

| 对象 | SHA-256 |
| --- | --- |
| `.agent-runs/system99/plan.md` v1 | `60cedd47b9e6f7d37c6de2a0219cdf74523c938b3b6229ce4ba20a70332ba592` |
| `agent_doc/task/TASK.md` | `8d323ae1e121affb304279dedcc2f06dbfbff6bfb3247ed436bad8f642c545bf` |
| `agent_runtime/project_docs.py` | `a2712d093f4012350f6654401a15aa1d22e442d6993482025996b63183477a57` |
| `agent_runtime/task_manifest.py` | `b9ec8f8881e26265fec368570bfb2b9fde2aed01ae6643ee0dab7f4543cd0e41` |
| `agent_runtime/task_context.py` | `d03ac5314bac5df15e0892d2fa9fa9854a138ef6dcdcc75d621766c9d8b34870` |

只读诊断调用了真实 `snapshot_project_docs(root)`，它在 canonical 链接格式处抛出 DocumentError。随后仅在内存修正 16 处链接前空格，用原解析器重读；未修改任何输入、源码、旧快照或旧结果。该诊断用于计划核查，不是修复后数据验收。

## 七项判断

| 项目 | 判定 | 依据 |
| --- | --- | --- |
| intent | pass | 保留系统级批次目标、十篇本批正文阅读和跨入口/恢复/真实任务质量要求；阶段 A 不冒领整批完成。 |
| guide | pass | 不改 guide，任务索引仍由主控串行维护；未发现与当前可读指南内容冲突。真实来源证明仍由宿主负责。 |
| assumptions | pass | 原解析器明确要求详情链接前空格；内存修复后得到原 315 个 ID，顺序与勾选完全一致，并恰好暴露所述 5 份详情问题。无需放宽解析器。 |
| prior_results | fail | v1 只有 UTC timestamp overflow 查询，不对应本阶段。实际相关查询命中既有 metadata-only 修复和全局门禁先例，须记录采用/拒绝理由；旧 pass 不可充当新 checkout 验收。 |
| acceptance | fail | SYSTEM-99 尚未登记唯一 TASK；v1 尚缺冻结的字节保留、完整文档集合、正式门禁失败路径与稳定段/Progress 恢复判据，准备草稿与可执行计划的边界也须明确。 |
| risk | pass | 窄修复、不改 parse/排序/全局门禁、不改历史证据是合适边界。实际混合行尾及历史哈希失效风险须落实为下述硬验收，不能仅靠文字承诺。 |
| resources | pass | 本地只读检查及 CPU 回归可在现授权内进行；不调用外部模型/GPU/付费、不启动缺失适配器、不接管未知作业。真实托管能力缺失如实 blocked，不妨碍独立已授权本地检查。 |

## 已独立核实的缺陷范围

16 个格式不合规 ID 为：CONCISE-98、RESULT-TIME-97、RESULT-FD-95、SEARCH-DEPTH-93、VALIDATION-FD-87、CHECK-HELPER-85、CONTEXT-SCHEMA-83、ARTIFACT-FD-77、ARTIFACT-READ-76、PROMPT-SCAN-69、PROMPT-READ-67、INGEST-SCOPE-58、READ-BOUNDARY-56、CONTEXT-METADATA-35、CONTENT-COPY-60、ATX-BOUNDARY-62。

| 详情 | 必要修复 |
| --- | --- |
| SEARCH-DEPTH-93 | 补准确 Task-ID；原 Date 2026-10-20 保留。 |
| READ-BOUNDARY-56 | 补准确 Task-ID；原 Date 2026-10-19 保留。 |
| TERMS-CLASS-27 | 补 Task-ID 与所属索引组织日期 2026-10-19。 |
| CONTENT-COPY-60 | 补 Task-ID 与所属索引组织日期 2026-10-19。 |
| CONTEXT-SCHEMA-83 | 补 Task-ID/Date 2026-10-20；在原稳定文字前加 Plan，在原“完成：”段前加唯一 Progress；不改原段落。 |

基线 TASK 有混合行尾：572 个 LF，其中 412 个 CRLF，后者含 370 个 CRCRLF；共 782 个 CR。不能用通用文本重写或行尾规范化把“一处空格修复”扩大成全文件字节改写。上述计数不是互斥类别。

## Blocking findings 与最小返修

### F1：唯一 TASK 中缺少本批稳定身份

- target：v1 计划、`agent_doc/task/TASK.md`、待新增 `task_details/SYSTEM-99.md`。
- feedback：当前 315 项中没有 SYSTEM-99；运行区 plan.md 不是第二份活跃 TASK，也不能替代正式登记。只修老任务不足以让新工作经真实 TASK→snapshot→prepare 绑定。
- requested_change：主控登记未完成的 SYSTEM-99，详情稳定 Plan 保留整批验收矩阵、阶段 A 检查点、允许动作、阻塞项和下一负责人；旧任务原 ID/顺序/勾选/要求/证据不变。不为阶段 A 新造“已完成一轮”。
- acceptance_check：原 315 项投影逐项一致，新增 SYSTEM-99 独立可追踪。若只新增这一项，修后 snapshot/prepare 应覆盖 316 项；禁止把 315 写成修后永久常数，也不能为避免历史任务而放松全局 coverage。

### F2：当前阶段缺少相关历史取舍

- target：v1 末段的 prior_results 及 SYSTEM-99 详情。
- feedback：UTC 查询不支持文档恢复阶段的复用决策。审查实际执行 `ResultStore(root).search('TASK snapshot prepare document', limit=5, max_scan=200)`：scanned=199、partial=true、64 errors，返回 5 个候选；不是完整历史枚举。
- requested_change：记录相关查询、候选版本和取舍。最相关 `advice-context-20261009` record SHA `52ac654513a845b8d39e08be1271fe6f89aa0dcd93225b984ea9638a4d3fae93` 已读 record/manifest、validation_plan 和独立审查原文：可参考 metadata-only 字节核验、保留全局 guide/advice 门禁和显式 reconciliation 方法；其旧 194 任务、旧代码和旧通过数据不能验收当前 315/316 任务。其余四项为 corpus-v4、条件信息文档、advice-link、corpus-delta-v2，词法相关但不覆盖本次实际 TASK 恢复缺陷，不复用为新结果。
- acceptance_check：当前计划明确选择 verify_delta/新回归，保留扫描缺口；不宣称旧登记或旧 pass 已提供当前独立认证，不改任何旧 record/manifest/报告。

### F3：冻结可操作验收及宿主/历史边界

- target：v1 “新回归”段与待冻结 validation_plan。
- feedback：当前方向正确，但应把具体接受/拒绝条件写定，防止“prepare 返回 JSON”被误报为恢复成功或正式审核通过。
- requested_change：实现前冻结本地阶段 A 验收协议，至少覆盖以下条件：

  1. 固定实际 Git 基线字节重放修前 snapshot/prepare/task_view 的失败；保留失败，不使用重新拼写的伪基线。
  2. 16 处空格和五份详情插入有精确 byte transform/逆投影核对；除允许插入及明确的本批登记外，原字节、ID/勾选/顺序/证据不变。治理说明追加到 Progress，不把新约束藏入 Progress 绕过稳定哈希。
  3. 直接对实际 checkout 调用 snapshot，严格详情集合无缺失/孤儿，ID/Date/唯一 Plan/Progress 全部通过。prepare 返回完整真实任务集合、正确 task_source 新 SHA 和默认 main-plan-review/v1；不选 review_required=False，不走 legacy-unprotected，不使用发布 scope 来缩小默认执行覆盖。
  4. 明确 prepare 只是 `configure_host_action`/`configure_acceptance` 占位草稿，既不执行 315 个历史任务，也不宣布它们完成。guide_reviews/advice 尚未具备已核实来源和完整取舍就保留未就绪，不伪造 owner_authored/owner_approved 或空通过。
  5. 用实际正式检查路径确认缺可信注册/回执/verifier 时 fail closed；结果只报告实际触发的拒绝原因。单纯在草稿中检查 plan_review 字段不等于已验双主门禁；不得为了得到成功路径写一个“总是 True”的宿主。
  6. task_view 用新来源 SHA 读取实际指定任务并保留所有非任务文本；unknown、重复 ID、stale SHA 和预算不足拒绝。它只做导航，不读取详情、不验证指南/建议、不签发全局完成证明。
  7. 稳定任务输入/索引改变使旧 document_refs、旧派发和旧 task_view SHA 失效；只有普通 Progress 追加保持稳定详情哈希。恢复必须核对授权/取消、旧作业/已发生作用与 evidence，再以新 run/版本重规划；有 requires_reconciliation 的作用不能因为唤醒而自动重做。
  8. 原旧快照、历史报告、raw/record/manifest 哈希保持；当前稳定详情增加元数据必然形成新哈希。旧结果中指向旧活跃详情的哈希允许失效并被当前消费者拒绝，不追溯修改旧清单、哈希或旧“通过”来冒充新字节。确需再次消费必须显式新验证。
  9. 独立核查实际修复 diff/原始结果，保留全库、Reader、生成同步检查范围及 skip；数据产生后按 producer→verify_experiment_result→consumer，缺正式 verifier 时说明其受限状态。独立技术审查可以支撑本地工程判断，但不能冒充运行时可信 provider。

- acceptance_check：新版固定上述协议和证据依赖，独立验收根据实际 diff/log 逐项裁定；没有宿主能力的部分明确 blocked。阶段 A 的有限通过只允许报告文档准备链路检查点，不得报告完整恢复部署、模型收益、绝对无 bug 或 SYSTEM-99 批次完成。

## 结论与交接

不要求修改解析器、另造活跃视图或重写历史。请 planner 在唯一 TASK 中完成 F1、把本审查 F2 记录为有界历史调查并说明取舍，再冻结 F3 的新版协议。稳定输入改变需给新版本并重新审查；旧 v1 哈希和本反馈原文保留。

本审查未执行修后测试、外部模型、受管派发、监督器、Git 发布或历史结果重验；不新增正文阅读计数。仅新建本文件。审查末尾观察到主控新增的未跟踪测试 `tests/test_repository_task_integration.py`，未读取、修改或归属其内容；它不在本次 v1 审查对象内。

## v2 复核（2026-10-20，追加保留 v1）

技术决定：**approve，仅限阶段 A 的有界本地修复与验收方案**。F1/F2/F3 的规划阻断已关闭；修复、结果通过、正式宿主认证与发布均尚未发生，不能由本决定替代。

复核固定对象：

| 对象 | SHA-256 |
| --- | --- |
| `.agent-runs/system99/plan.md`（原 v1 全文加 v2 修订） | `9148947643a6eb200b450e324715ed66169ac917fb1ca606e06f56792f994ffb` |
| `agent_doc/task/TASK.md`（仅新增登记，旧缺陷未修） | `9d1da04be429446cd29a59bb575d544e969fd35972b81c02f3e52e93ea877e72` |
| `task_details/SYSTEM-99.md` | `97d166620639acc84e9cae2035828fce8b09e6ba6bb2f1c1f6f9bbe82b6a77c4` |
| `tests/test_repository_task_integration.py`（当前初始三项测试） | `56af072fe1e2f73f5f5b5c2e18b365f5fc3fc85e2f0beb0f52fae8db90eb6b63` |

已独立按字节从当前索引移除准确的 SYSTEM-99 登记行和所附空行，结果与 Git 基线 `dcc10b10537a3b410a25f6ef3f2c842a3c1777b4:agent_doc/task/TASK.md` 完全相同。原 315 项未改，新增未完成 SYSTEM-99 后为 316 项；新增详情严格具有 Task-ID、所属日期和唯一 Plan/Progress。16 个缺空格行及五份详情仍待修，不把登记误作修复结果。

读取实际 `.agent-runs/system99/prior-search.json`，查询/199扫描/partial/64错误/三个候选与 v2 陈述一致。它们的已返回 scope 是旧语料/旧文档集成，不覆盖当前字节或入口；不复用为当前验收合理。v2 也接纳独立查询发现的 advice-context 元数据修复先例，不复用其测量或旧 pass。无需为了此次窄修复重跑旧 corpus 测量。

| 七项 | v2 判定 | 关闭依据 |
| --- | --- | --- |
| intent | pass | 系统级总目标、阶段检查点及未完成后端/质量条件保留，不把小时或小修计一轮。 |
| guide | pass | 原目录只读；未添加或伪造来源评估，空指南不充当新授权。 |
| assumptions | pass | 缺陷仍限定为原 16 行与五份详情；原解析器和全局 coverage 不变。 |
| prior_results | pass | 相关查询与不复用决定已有实际记录，当前有界新回归仍必要。 |
| acceptance | pass | 本批正式入 TASK；新字节/完整316草稿、旧哈希失效、Progress不失效、独立验收与检查点范围已明确。原 F3 的精确拒绝/恢复判据继续作为后续结果审查标准，不被当前三项测试代替。 |
| risk | pass | 计划明确固定旧字节、仅插入与逐字节差异核查，历史快照/哈希不改，不从旧 run 恢复派发。实际字节是否满足仍由独立结果验收裁定。 |
| resources | pass | 仅本地CPU/可逆临时输入；无付费模型、GPU、未知作业或虚构常驻/托管宿主。 |

当前三项回归的范围已读：prepare 测试替换了 `_prior_result_search`，所以它只验证真实 checkout 文档装配，不是实际结果查询、真实 CLI prepare 或正式审核门禁的端到端证据。后续必须按已承诺的真实 CLI 与生产检查路径补证；保护字段存在、空 guide/advice 列表以及 `configure_host_action` 占位不构成派发批准。没有可信宿主时只接受 fail-closed 事实与精确 blocker，不要求伪造成功回执。

主控报告的 `/tmp` apply_patch 探测未由本审查重放，不作为修后字节证明；独立结果审查仍直接对固定 Git 原字节和实际修后文件做精确变换核对。正式验收前保留原 F3 全部历史/恢复门禁，稳定方案发生实质变化需新版本重审。此次仅追加本文，未运行修后测试、修改输入或签发任何运行时回执。

## v3 阶段 B 计划复核（2026-10-20，追加）

技术决定：**approve，仅增加 CHAIN-ENTRY 两行生成说明修复及其回归**。阶段 A 的实际数据验收仍交独立结果角色；本次没有复核其全部原始字节或宣告通过。CHAIN-RESULT-CATALOG、CHAIN-TERMINAL 及其他核心行为不在本次批准范围。

| 固定对象 | SHA-256 |
| --- | --- |
| `.agent-runs/system99/plan.md`（含 v3） | `ff1008585fbf5539be0f53a263d58eec5689e6df2995466496150f26fcc1ac3a` |
| `task_details/SYSTEM-99.md`（稳定 Version 2） | `3b0e6948e7317b67151c9997c31affefc56cca7bbb4a6a3a03d4285327caaf4f` |
| `setup.py`（尚未修复） | `7eb07273bccf7213ac8d9c0418f71e30dd87a87837575a71c9c183066ff121df` |
| `tests/test_setup.py`（含新回归） | `e6c42ff6ac1e2a7ab8a56da9ea5bd4d168bd9cc9b8479c86e23870b5df4cef48` |
| `independent-chain-audit.md` | `3022bbd8658dcbeedf95f37c1799901ab90b1b385f5f426c79eab89c8ceedaf2` |
| `.agent-runs/system99/install-before.log` | `8c2e7caa7fbbbf923c5cbb7e695f6476883e62acf46e23d4a50c4c93e095ea3d` |

已读真实 `setup.block → merge_block → install → check`、项目文档初始化/归属与只读边界、新测试及修前 log；确认当前 setup.py 仍逐字节等于固定基线。block 的相邻两行把 Project A 和工作流库指向 doc，后续同块和真实初始化却明确 agent_doc，属于具体说明冲突。改这两个字符串足够，不需改变安装算法或扩大写入范围。check 将模板等于自身检查为 configured 不能证明路径说明语义正确，新增测试直接检查真实新项目输出，适合补此缺口。

| 七项 | 判定 | 依据与接受边界 |
| --- | --- | --- |
| intent | pass | 同批入口/项目归属目标，局部检查点，不重新计轮。 |
| guide | pass | 统一 canonical 路径符合现文档契约；guide 全目录仍只读，普通 doc 不迁移。 |
| assumptions | pass | 实际 block 两行和初始化生产者不一致；新测试失败 log 指向 Project A/agent_doc 缺失，不推测模型必然写错。 |
| prior_results | pass | 本批独立 CHAIN 审查提供实际新项目复现，当前修前回归记录可追溯；不借旧 configured/生命周期绿灯冒充该语义已验。 |
| acceptance | pass | 冻结范围为两行字符串；真实 install/check、canonical入口断言、普通doc内容保留，加现有生命周期/全库及独立diff结果复查。修前失败保留。 |
| risk | pass | 不改安装所有权、原子替换、本地编辑/用户文本保护、角色或权限。修后须核对 diff 仅两处 block 文案，不改其他 doc（尤其遗留 guide 防护和兼容路径）。 |
| resources | pass | 临时新项目、本地CPU足够；不要求安装/调用Claude、模型或监督宿主，不把 configured 当实际会话加载成功。 |

非阻断补强：新测试可直接断言普通 `doc/notes.md` 的原始 bytes，避免以后文本比较掩盖行尾改写；当前两行文案修复本身不应进入该文件的任何写入路径。现有 repeat install、用户文本、本地修改保留、冲突预检与卸载归属测试继续执行，不因“只是文案”免除实际生成产物回归。

修后可声明生成入口说明已统一且本地安装契约通过；真实 Claude 新会话是否发现/加载入口仍未验证。阶段 B 没有改变阶段 A 的正式宿主阻塞、历史哈希处理和系统级整批未完成状态。此次仅阅读与追加审查，未运行安装测试、修改 setup/TASK、执行终态核心变更或签发正式回执。

## CHAIN-TERMINAL 下一阶段方案评审（2026-10-20，恢复同一 SYSTEM-99）

最新授权已明确恢复 Agent，而非继续 TwoLevel；上轮暂停不再是本阶段阻塞。技术决定：**revise，保留修复方向，补齐终态专用转换和事件/恢复边界后冻结实施**。本意见不影响已经验收的 A/B 检查点，也不授权改写活跃链、取消、调度或正式审核权限。

固定读取 HEAD `ec5edaa2dbd6f997ef060681dad61c25d2bcd7ec`；core.py SHA `ebb82f1b5f2529f7ebf89ba64a2e61dc3938ef437b9ce9d20c7cb49dc677b158`，task_supervisor.py SHA `dfba7e71bad618ecc3f08a41214dbc840a5ab5f124449f533d2b9f43a5652660`，test_task_runtime.py SHA `4819c53745f2f1299f5829bd9ac5e5543c41f842ce7bd6a140b98d3b5b367589`。实际阅读 tick/_check_done/_summary/reconcile、Store持久化/取消、portable CLI、LocalScheduler、ManagedEngine及worker完成分支、ReportingHandler.verify和现有runtime/managed/plan-review相关测试。

本次新只读结果查询 `portable terminal evidence tick`：199扫描、partial=true、66错误；三个词法候选为advice-context、ATX边界、旧corpus-delta，不覆盖该完全终态路径，不复用为本阶段正确性证据。当前有直接源码及本批独立CHAIN探针，既有局部完成依赖失效测试可作兼容对照；没有当前修复后的数据。本次未运行测试、服务或实验，仅核对接口与追加本文。

### 七项

| 项目 | 判定 | 依据 |
| --- | --- | --- |
| intent | pass | 可信新tick后不把历史done当当前有效，并保留已发生作用/不自动重放，符合声明用途。 |
| guide | pass | 同SYSTEM-99有界可靠性修复，guide只读、不扩大宿主授权。 |
| assumptions | pass | done快返确在证据复核之前；managed worker另有_check_done，不能把portable缺口外推为managed一定误发最终报告。 |
| prior_results | pass | 已有具体探针与实际源码，旧局部链/审核撤销测试只提供兼容边界，不冒充完全终态修后结果。 |
| acceptance | fail | 仅“调用_check_done并_summary”不能达到要求的blocked/reconciliation；需固定下述持久化、闭包、重复事件与恢复负控。 |
| risk | fail | 若直接改通用_check_done为blocked，会改变活跃链既有failed语义；若只移快返，可能误进入后续claim或无可用reconcile路径。 |
| resources | pass | 本地CPU/临时SQLite与文件足够；无需外部模型、服务或付费，实际host门禁继续独立有效。 |

### Blocking F-T1：不能把通用证据失效语义一并改掉

`_check_done` 当前遇到handler缺失、verify=False或异常时，将原done节点标failed；其依赖闭包也标failed。`_summary`不会凭此生成requires_reconciliation；`reconcile`又只接受blocked节点。因此，只移动done快返会得到failed而不是目标状态。直接改变通用_check_done则影响现有 `test_changed_upstream_proof_prevents_downstream_dispatch` 和 `test_invalid_proof_propagates_through_completed_dependency_closure`，这些active链仍须保持原failed/后继blocked语义。

最小兼容办法是把新行为限在**进入本次事务时整体status为done**的分支：沿用原_check_done完成实际verify及非拓扑依赖闭包；仅将本次终态复核中由done失效的节点转为blocked并设置requires_reconciliation。保持已有evidence、attempts、dispatches、next_at、claim_cursor及作用信息；保留具体失效原因，不能清空原证据或伪造新proof。已有plan_review_after_effect原因/标志不应被普通证据原因覆盖。

无需必须新增公共参数；可以在terminal分支记录原done ID并对本次失效节点做局部转换，或给私有_check_done增加默认保持原行为的显式终态模式。二者选一即可，不重复实现verify/闭包，不全局改变active/failed/cancelled策略。随后_summary、save、审计记录并立即return，**不进入claim/retry处理**。

验收：根证明失效与其已经完成的传递消费者均blocked/requires_reconciliation，非拓扑排序也一致；独立无关done节点保持done。反复新tick、重启Store/Engine或proof恢复本身均不自动清标志、不run。显式reconcile仍要求当前审核、权限、非取消、已done依赖和新证据；需要按依赖顺序恢复，各节点不重放旧副作用。

### Blocking F-T2：固定事件顺序和观测范围

在保留当前顶层 `_review_plan` 的前提下：cancelled仍原样快返；已登记event仍快返，不因该修复重跑证据检查、递增attempts或增加同event审计；只有新事件进入终态复核。新终态事件应与其复核后的state在同一SQLite事务中登记/保存，以便重复event和崩溃后重放可判定。全done且证据仍有效时仍done，副作用次数不变。

本阶段不是让Store.snapshot/CLI status自行认证，也不使停止的monitor自动继续poll。LocalScheduler当前遇到done会停止且不调用tick；本方案只保证**实际收到可信新tick**后的当前状态。不要声称所有终态读取、所有后台唤醒都新增了验证能力；不为覆盖这个缺口自动重新arm已停止monitor。

顶层审核撤销原本就会在终态快返之前blocked。它的恢复/撤销策略不得因本补丁被关闭或伪造批准；继续现有独立审核回归。managed worker使用通用_check_done并另行publish/final-report：若本阶段采用terminal局部转换，它原有failed结果语义保持，不必顺带改worker。若决定统一managed状态语义，则应另外明确范围和测试，不藏进本portable补丁。

### 实施前冻结的必需负控

1. **真正完全完成**：单节点、链/菱形依赖全部done（含逆拓扑列表）后verify变False；新tick返回且SQLite重开仍为blocked/requires_reconciliation。不能只复用尚有todo后继的旧测试。
2. **真实产物与错误**：固定ArtifactHandler原哈希文件完成后改字节；另测handler缺失、verify抛异常。均保留原evidence，不崩溃、不运行actor。至少一例使用非幂等计数器证明不同事件/重启不重放。
3. **正控与去重**：有效done收到新event继续done；已处理的原完成event和新终态event重复均不新增claims/attempts、事件行或重复观测。handler.verify计数需区分原完成阶段本来就有的调用；顶层review调用仍遵循既有门禁，不用“verify未调用”误断言所有检查都没调用。
4. **取消优先**：先cancelled再使proof坏/verify会抛错，新event保持cancelled且不调用handler.verify/run；不恢复取消、不重新arm、不清除取消原因。
5. **闭包与隔离**：失效根的所有已完成后继被围栏，无关完成支线不改；多个同时失效、非拓扑输入不漏节点。原active局部完成的failed/后继blocked两项回归原断言保持。
6. **不可自行痊愈**：proof恢复有效后多个新event仍blocked；Store/Engine重建也不解除requires_reconciliation。未授权/空证据/取消下reconcile拒绝，合法显式reconcile成功但actor次数仍不增加。
7. **生产入口与门禁**：portable CLI真实init/tick在临时项目文件上证明新状态被持久化，status仅回读该状态；测试可显式legacy fixture但不能把生产计划降级。独立双主缺认证/撤销/作用fencing回归及managed worker完成/失败/取消现有回归保留，不启动真实服务。
8. **保存修前失败与新合同**：冻结原core字节/测试输入/预期、保留失败输出；将所选终态专用方法和验收写入同一SYSTEM-99稳定详情及版本/run（主控维护），实现后再做独立代码/数据复验、全库/Reader。无性能主张，测试通过数不充当模型质量或整批完成。

返修最小接受条件：明确采用F-T1的terminal-only处理和F-T2的事件/观测边界，并固定上述负控；不需要设计新调度器、改存储schema或安装真实host。待核对新版后再给技术approve；本次revise不是授权先实现未冻结的替代。只追加本文件，未触源码、TASK、测试或旧证据。

### CHAIN-TERMINAL Version4 返修复核（2026-10-20）

技术决定：**approve，限当前整体done、顶层审核仍有效、收到可信新event的portable终态复核路径**。F-T1/F-T2规划阻断已关闭。实现/测试结果尚未验收，不是正式host认证或整批完成；保护计划先被撤销、随后恢复审核时的旧终态恢复策略仍单列open，不把本补丁宣称为其修复。

固定读取HEAD `68e883e986c97ffbfc96602e96baafef46880e4d`：canonical SYSTEM-99 Version4文件 SHA `1bee647bec0bbacb4fa78b1f5efb0cce5a0ed2cb17305f3185da039cc27d2048`；新tests/test_terminal_revalidation.py SHA `8a9712b5574a96ce3ea1d61e7581158f9b169c32a1913e3461203c6ab00463cb`；terminal-before-v2.log SHA `e9dac9abac08d584dbb4aee35d683d0fd030bca0d80ca67afc456ad6b7189f1a`。core仍为上述未改SHA，尚无生产修复。

已读完整六项新测试与修前日志：6个test methods、8个失败（False/missing/exception为三个子例），失效观察均是旧done/未新增verify，而非加载或fixture错误。当前测试包含真实ArtifactHandler/SQLite、文件恢复仍需显式reconcile、非幂等逆序菱形及多节点失效、无关支线、有效新事件/SQL事件数、重复/取消verify计数和真实portable CLI。CLI的显式legacy只限定合成fixture，未将本项目生产计划降级。未在本次复核重新执行这些测试。

采纳的方法为terminal分支记录原done ID，沿用_check_done；仅该次变failed的完成节点转blocked并持久requires_reconciliation，随后_summary/save/log并return。顶层review照旧；cancelled早返、已处理event早返，新event先原子登记；active/managed通用_check_done的failed语义保持。该方法恰好关闭“只移快返仍failed”与“通用语义扩大”两项问题，也保留原plan_review_after_effect标志，不需改schema或权限。

| 七项 | v4判定 | 关闭依据 |
| --- | --- | --- |
| intent / guide | pass / pass | 同一SYSTEM-99窄可靠性目标，人类guide和当前授权边界不变。 |
| assumptions | pass | 明确原done/新event/当前审核有效三个条件；撤销后恢复和自动monitor观察未冒领。 |
| prior_results | pass | 使用具体修前失败和已读源码，旧非本范围数据仍不复用。 |
| acceptance | pass | 六项可执行回归连到真实输出、闭包、持久化、去重与取消；原active/managed/双主回归继续是硬门槛。 |
| risk | pass | terminal-only转换、无claim、无证据清空、不自行解除reconciliation；旧通用语义保持。 |
| resources | pass | 本地CPU/临时文件及SQLite，无外部服务、付费或模型后端扩展。 |

后续独立结果验收的非阻断补强：首个restart helper目前重建Engine而复用无连接状态的Store包装器，SQLite连接本身每个事务都重开；可显式重建Store以把“完整Store重建”也直接写进测试。对具备当前有效review的保护fixture，可再验证一次完成后handler证据失效进入同一新分支，避免把legacy CLI负控当成所有受保护入口实测；该CPU fixture不等于真实host批准。非法reconcile/active失效/managed final-report的既有测试须继续原断言，不为本补丁修改预期。

本批准允许主控按Version4已授权窄方案实施并产出待验数据；任何改成通用_check_done语义、恢复审核策略、scheduler自动重arm或其他副作用恢复的新取舍须另审。只追加本文，未写源/TASK/测试、未执行外部服务或发布。

Version4同范围补强回读：restart现已显式`Store(self.db_path)`后重建Engine，源码只增加Store导入和该重建；新测试SHA `0e5a62242ef9600db8ee64bb5b35381d3a19062af199a524a684e7518cf55c21`、新增保留red日志terminal-before-v3.log SHA `2d7a4f29c651264b8ad1cbddf3aa2be598b18cda290eb873a3deaf3b095e6222`，尾部仍6项/8失败（0.385s），core仍未改。此修改不变更方法/阈值，本阶段技术approve继续适用，以此测试版本进入后续独立结果验收，旧v2日志不覆盖。
