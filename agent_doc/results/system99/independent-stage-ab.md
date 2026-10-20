# SYSTEM-99 阶段 A/B 独立结果验收（集成前）

日期：2026-10-20。Verifier：`/root/system99_plan_review`，与源/数据生产者分离，实际只读核查与本地 CPU 复验。

结论：**usable-with-scope，限当前基线上的本地 A/B 检查点**。无本范围阻断项。不是 SYSTEM-99 结案、正式运行时 provider 回执、发布许可、真实 Claude 会话/多模型后端或跨机器恢复验收。

本次对象为 `dcc10b10537a3b410a25f6ef3f2c842a3c1777b4` 加本批 A/B 未提交变化；主控随后发现远端 `8587b781`/`a48f70a1` 并发变更。该远端新增 MEM-INDEX-96、记忆实现/测试及新增任务行**不在本验收覆盖内**。后续集成、补第17处空格或任何稳定输入改变，须新快照/草稿、针对性独立复验与适用全库检查；不得把本报告重标为集成后通过。

## 采用的范围与证据

已读治理协议、v1/v2/v3 独立计划反馈、实际 `project_docs → task_manifest/prepare/validate_contract → task_context`、正式 plan_review/core 检查入口、setup 生成/安装/检查及新测试。实际检查 diff 和 Git 固定字节，不以生产者 OK 日志代替实现阅读。

| 对象 | 固定 SHA-256 |
| --- | --- |
| 当前 TASK（316项） | `31aaac8ea3e08cf3d7a9af53ead8bdbeb0cde5e2ebd84f77dfc94eea74161d7a` |
| setup.py | `6525c93b3883ea4a371226101b784c241afe27a7eb5d5148b813e5759f2dcb27` |
| tests/test_setup.py | `0b3100a38d38a775e0513ecfe58788e914238550ace681f57d123de010fe952e` |
| tests/test_repository_task_integration.py | `4e8441eaf06651e57f9233c5a4700eb7d132f0550bdbfcb6e9de5fc2c984063c` |
| stage-ab.md（本次读取版本） | `07f87ea235ce3513adcf7404ca91c48b83abafbaffae42e8c53b5c0d0ea25db4` |
| actual-cli-draft-v3.json | `fc820400e6b1c439b2029b9b9083f9475a4cb6e118e06fe3ec1278214828101b` |
| full-tests.log | `d4bc13b560d356b9e92392bf60f30346c11ffd68082c413bb3d6304746a57269` |
| focused.log | `7435ccb8d7bf73564710c61eed052436222c1f43ad40be7b0db02425cb686cc6` |
| boundary-checks.log | `dd908a411228b09a0ca6bb645c0292d56954659c82f866e313ea97bea5a55ca3` |
| before.log | `a173f23e62b9f2b2c786f9948540978f34c2afdc9d26b50064f1b7b3455bd96c` |
| install-before.log | `8c2e7caa7fbbbf923c5cbb7e695f6476883e62acf46e23d4a50c4c93e095ea3d` |

日志和大草稿均在 `.agent-runs/system99/`；这些哈希绑定所读原件，不把可写文件或本报告本身当作加密身份/宿主授权。

## 独立字节与实现核验

直接从 Git 基线读取 TASK 原始 bytes，参考变换仅为：16 个缺少前置空格的详情链接各插入一个空格，加 SYSTEM-99 登记行及其空行。实际当前字节精确等于该变换：59957→60185 bytes；原315项 ID/勾选/顺序全部不变，新增 SYSTEM-99 保持未完成；原782个 CR 全部保留，没有行尾规范化。

五份详情逐一按预定准确插入建立期望，再与当前 bytes 比较，全相等：

| ID | 当前文件 SHA-256 |
| --- | --- |
| SEARCH-DEPTH-93 | `ff8a4272946190542c989d4d1b7c4fff1bce364ce932b3e95ac8636b5e83c596` |
| READ-BOUNDARY-56 | `946efc0d320c31e5da706af49d67b6c8c449a4ec777522dcc48f0cbc8a4973e4` |
| TERMS-CLASS-27 | `d66d7857c90d477669fb8ffbfad39ae159850d8483a28ed0f5126e0d692985c8` |
| CONTENT-COPY-60 | `1612aafda3f7cc788dfddc0f081c9e2982b8acd19e75c35c11aaf257d3e86eb5` |
| CONTEXT-SCHEMA-83 | `ac781eb7209132843c9195ef5dba69abb227090e4de477749b10b5181f2b2e65` |

原正文、状态、历史证据及组织日期含义未改变。CONTEXT-SCHEMA-83 的原完成段进入 Progress，不挪动原段落；新稳定 Plan 哈希不冒充旧版。运行时 project_docs、task_manifest、task_context、core、plan_review、task_supervisor 和 result_store 均与基线逐字节相等，解析器、全局覆盖、排序/权限/终态行为未改。

setup.py 实际变换精确为批准的两行字符串：Project A 与工作流库工作流资料归属改为 agent_doc；其他字节相等。未改 install/check 算法、安装所有权、原子替换、既有用户内容、本地编辑保护、角色或 guide 防护。新测试使用普通 doc 文件的 CRLF 原始 bytes 断言保留。

对 tracked diff 核对，旧 `agent_doc/guide/`、旧 `agent_doc/results/`、旧 review/manifest/raw 无修改；本批新增文件另列。没有追溯补旧哈希或重写旧快照使其通过。此断言限当前可读仓库，不宣称不可访问外部副本受控。

## 独立实际执行

以下均为本审查真实执行，非复制生产者标签：

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_setup tests.test_repository_task_integration tests.test_project_docs_acceptance tests.test_task_context tests.test_plan_review_independent -v
Ran 85 tests in 2.805s — OK

PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.585s — OK

PYTHONDONTWRITEBYTECODE=1 python scripts/sync_plugin_references.py --check
exit 0，无输出
```

85项包含31项真正 `test_plan_review_independent`。读过并实际通过缺真实审核/verifier的派发拒绝（handler calls=0）、布尔认证拒绝、同上下文拒绝、稳定Plan/证据变化失效、Progress保留、发布范围不可派发、旧lineage不可降级、撤销后作用保留与显式reconciliation等。测试使用明确标注的 CPU fixture/模拟宿主，只验证程序门禁，不构造本项目可执行批准，也不证明真实模型独立性或后台服务已接通。

另外以 Git 固定旧 setup.py 原字节编译成独立模块，运行当前新安装回归：真实新临时项目安装后恰有1个预期 assertion failure，原因是旧输出缺 Project A/agent_doc；不是加载错误。相同回归在当前 setup 的85项中通过。原始生产者修前3 errors及安装1 fail日志已读并保留；A的修前实际snapshot失败亦在本角色早期计划调查时直接观察过。

独立首次字节诊断脚本误将已有空格链接也纳入期望插入，导致参考断言失败；随后将参考限定为“缺少前置空格”精确16处，全部验证通过。没有因此修改任何待验输入、源码或验收阈值；该失败是审查脚本错误，不计产品失败或修复收益。

## 实际完整输入与拒绝边界

当前真实 snapshot 取得316份详情、2个guide和33个advice。按固定旧真实TASK SHA及 SEARCH-DEPTH-93 旧稳定Plan SHA分别构造旧绑定，生产 `check_document_refs` 精确拒绝 task_index/task_details，要求 reconcile and version。对316份实际详情独立检查普通Progress追加前后稳定Plan及其哈希全相等；另有生产 helper/变更拒绝的fixture回归通过。此处未对活跃详情实际写入探针。

实际 task_view 选 SYSTEM-99，text2072字符、明确省略315行，并保留所有非任务文本；旧真实来源SHA、未知ID、重复ID、超预算分别拒绝。它不读取详情/指南/建议，不代表当前优先级、全局清场或完成。

已读取真实 CLI 输出和6857986-byte草稿，独立核对全部316项、当前source SHA、完整project_documents及默认main-plan-review/v1。随后本审查又直接调用**未mock的真实 prepare**：实际执行316份ResultStore查询，输出相同完整任务集合和文档快照，仍全部为configure_host_action占位，guide_reviews/advice_assessments为空；未写草稿或派发。保存草稿与本次新草稿均经正式validate_contract在 human guide review required 处拒绝，不能把这次准备成功宣称可执行。

保存草稿内316份查询按同一 `json.dumps(ensure_ascii=False)` 口径合计5111736 bytes，错误清单完全相同、每份65项；与更早有限查询64项是不同观察版本，不伪称不变。该精确序列化计数仅支持重复体积事实，不证明模型实际载入、token、耗时或任务质量收益。新查询未授信任何结果，部分/错误仍保留。

读取并逐行重数生产者全库日志：1355条实际 verdict＝1347 ok＋8 skipped，与88.590s summary一致；本审查未独立再跑全库，时间仅为生产者该次运行记录。7个skip需绘图/PDF/字体依赖，1个需opt-in真实tmux/socket，不算已验证功能。focused43与Reader3的日志相符，Reader已独立重跑。

`plan-review-gates.log` 实为 `test_task_runtime_review` 的7项文件读取/调度/授权回归，不是双主缺认证专项；不因文件名给它增加证据等级。本审查已用上述31项真正双主回归补验，未改原日志。既有较早草稿因后续稳定Plan升级而被拒是应有失效，不重写该旧草稿来恢复它。

## 六项验收

| 维度 | 判断 | 独立证据与范围 |
| --- | --- | --- |
| implementation | pass | 实际生产者/消费者、diff和旧源码字节核对；运行时门禁零修改，setup仅两行说明。 |
| reference_boundary | pass | 固定Git字节参考；真实新项目安装的旧失败/新通过；真实旧绑定、非法view及31项双主程序拒绝。 |
| data_integrity | pass | 16处/5详情精确变换、315→316稳定身份、782CR、原证据不改；当前草稿/日志哈希固定，旧失败不覆盖。 |
| numerical_sanity | pass | ID集合与数量重算；1355=1347+8，字符/bytes/任务数/时间不混用，不作token换算。 |
| measurement_validity | not_applicable（性能部分） | 冻结范围没有性能/模型收益主张，允许无计时验收；已核验确定性通过/拒绝及序列化计数。运行时间不作为收益门槛。 |
| reproducibility | pass | 独立85＋Reader3、同步检查、实际未mock prepare及字节/旧绑定/view重跑一致；全库原日志另作生产者证据，不冒充独立全量复跑。 |

## 仍未验收与恢复要求

本报告不验收十篇论文的逐篇阅读质量、不授信旧维护数据复用；研究记录及结果登记/portable终态/多生产者查询漂移另审。真实模型质量/总成本、Claude新会话入口发现、真实宿主ReviewSession、tmux断链、跨机器恢复仍受限。SYSTEM-99继续未完成，局部检查点不得计作一轮结案。

新远端/新任务或稳定Plan集成后，本报告只作为原始本地观察保留，不能修订历史哈希来充当新输入的验收。当前项目也未取得可用真实host认证器，本文件的usable-with-scope是独立本地工程判断，不是 `inspect_result` 自动可消费的可信proof；正式运行时仍应pending/blocked，直到宿主认证真实独立记录与准确合同。

只新建本文件；未修改源码、TASK、测试、guide、旧结果/审核，不启动任何项目历史任务、模型、GPU、监督器或Git发布。后续允许的是主控在现有授权内保存这个可恢复检查点并执行明确的新版本集成/验收，而不是关闭整批。

## 8587b781 集成补充验收（2026-10-20，保留上文原观察）

计划判断：**approve** canonical SYSTEM-99 `Version: 3` 的有界整合范围。结果判断：**usable-with-scope**，扩展到 HEAD `991c6594f91a16cc3352d5d9d17558f6e44d00bb` 及本次已核对的 Version3/Progress 收尾文档。仍只是本地 A/B 检查点，未给新记忆功能的模型/性能结论授信，未关闭 SYSTEM-99。

七项复核均 pass：目标/guide/资源边界未变；新假设只增加已知同类格式输入；相关证据是本次真实远端与新回归，不复用旧通过数；验收明确317项/17处、新快照与旧拒绝；风险限制为保留并发代码及历史字节、不改权限或终态。当前 Version3 将固定“316草稿”改为当前完整索引，并显式记录远端来源、任务增量和新run复验，非偷偷重标旧计划。

### 并发保全与字节参考

实际读取远端 `dcc10b10→8587b781` 的全部 changed paths；除需合并的 TASK 外，**122个路径逐一按原始bytes与8587b781 Git blob完全相等**，含113个 memory-index96结果路径、2个测试路径，以及 memory源码、MEM详情、CODEMAP和工作流/镜像。没有覆盖其负结果、报告、旧审核或独立验收原件。该122项按路径顺序及实际SHA组成的紧凑JSON清单 SHA-256 为 `082ae969cf29f6f9d884a6af6deb15aad7e07a2964c7396eb72081a1a5f558f6`；不把本核查称为重新验收那113个结果的科学适用性。

TASK 参考改用8587b781实际原字节：316个原任务→新增SYSTEM-99后317项；精确差异仍仅SYSTEM登记与17个缺空格链接各一个插入。60169→60398 bytes；782个CR全部保留，原任务ID/顺序/勾选不变。MEM-INDEX-96行独立核对，除详情链接前一个空格外与远端逐字节相同，其勾选、说明和未全绿限制不变。

| 当前输入 | SHA-256 |
| --- | --- |
| TASK.md | `58c0c234f3c7ed89bfd49d8670048c21e99193c0abc42b2365212d3e11b69bdd` |
| SYSTEM-99稳定Plan（不含Progress） | `933890e0753475ed3f9d7dc8a3be78efe34a22c942b41bd14417c64cece18419` |
| MEM-INDEX-96详情原文件 | `1302b96d35851620663993083c07824f07eb7907bfb344226220b538a0e487e4` |
| agent_runtime/project_memory.py（等于远端） | `adfb149d706965ad35220b3431b9acf1f0828238ed78cbd787f01e9ac900ea19` |

setup及两份本批测试仍为上文验收哈希，A/B的五份治理插入未增加内容改变。已读并发memory index/storage与CLI输入测试的实际diff，确认集成不是回退旧memory模块；索引分页仍是导航，内容/更正和依赖检查边界保留，不把输出缩小当内存真实性或模型收益。

### 本次独立重跑与新数据

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_memory_index tests.test_memory_cli_input tests.test_project_memory tests.test_setup tests.test_repository_task_integration tests.test_project_docs_acceptance tests.test_task_context tests.test_plan_review_independent -v
Ran 116 tests in 5.536s — OK

PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.582s — OK

PYTHONDONTWRITEBYTECODE=1 python scripts/sync_plugin_references.py --check
exit 0，无输出
```

116项包括新增memory-index的11项，以及CLI输入5项、project-memory15项和原85项；全部为本地CPU/临时fixture，不宣称真实外部模型宿主。独立重算新snapshot317份详情、2guide、33advice；317份实际详情Progress追加均不改变稳定Plan哈希。dcc基线与8587b两个真实旧索引SHA在生产文档检查均拒绝；选择MEM-INDEX-96与SYSTEM-99真实view省略315行，旧来源和unknown仍拒绝。

实际读取并完整检查新真实CLI草稿：6954245 bytes、317项、完整当前project_documents和当前source SHA、默认main-plan-review/v1/lineage SYSTEM-99、全configure_host_action占位、guide/advice评估为空。正式validate_contract拒绝当前草稿的原因仍为缺human guide审核，**不是stale错误冒充门禁证据**；旧316草稿则在TASK来源变化处明确拒绝。未执行start/派发，也未构造假的人类来源/host认证。

生产者集成后全库日志已逐条独立重数：1366＝1358 ok＋8 skipped，与102.461s summary一致；未借并发作者其他环境的旧数字替代本机结果，也未把本次日志阅读写成独立全库重跑。新增11项解释1355→1366的测试增量；8个未执行功能边界仍如上文。

| 集成后原件（`.agent-runs/system99/`） | SHA-256 |
| --- | --- |
| integrated-full-tests.log | `fb112bc0e73563aaaf27a175f1436129b2814e3073e62cad306c07173d6cb58d` |
| integrated-reader.log | `a644317e288bdfa877d208b98a0e9139f14b5d57e0b638ddfa9de52b9c771d69` |
| integrated-cli.log | `055a29c1ecf40f667a6fc61d3d14eecd745552a0695f2fb4286f4d550907c014` |
| integrated-draft.json | `d5523022cb9036af258350ebe9e363b085a739b1c5261d96f2586ab8361a9fbe` |

六项验收维持：实现/参考边界/数据完整性/数值核算/可复现均pass，性能测量仍N/A且无性能主张。原预集成回执保留为316项历史，新补充才覆盖317项当前输入；后续稳定Plan或源码再改仍需按影响复验。整批catalog/portable终态/查询漂移及真实host质量/成本/跨机缺口继续open。此次只追加本报告，未触任何源、TASK、guide或旧结果；允许主控继续已授权的文档收尾和普通发布核对，不将本报告当正式运行时批准或整批完成。

### 用户切换任务后的暂停记录

主控随后传达用户切换到 TwoLevel：Agent 本轮发布暂停。上述集成独立复核已完成并保存；没有再运行测试或修改源/TASK。当前是本地检查点，未宣称已推送、远端发布成功或整批完成。此新暂停优先于上文“继续普通发布核对”的可执行建议；本角色就此停止。恢复时仍按同一 SYSTEM-99 读取当前授权、远端/脏树与固定输入，核查已发生作用和未完成发布，再决定哪些旧证据仍适用，不自动续推。
