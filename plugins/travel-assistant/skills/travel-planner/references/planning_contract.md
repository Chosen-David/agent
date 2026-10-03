# 旅行共享规划契约

[技能入口](../SKILL.md) · [详细工作流](workflow.md) · [输入模板](travel_brief.md)

本文件是仓库入口与插件入口共同读取的唯一核心契约，版本 `local-travel/v1`。它是供模型执行的规范与记录格式，不是可执行 schema、调度引擎或 JourneyPilot API；本仓库没有生产级旅行校验器、持久化后台或外部 runtime adapter。只问单点事实时直接查询，不强制创建完整记录。

## 1. 先确认目的和边界

先识别用户真正目标、硬约束、指定方法与可调整偏好，检查实际输入输出和可用能力。合理方案在授权范围直接执行；重大更优路线、接口/权限/预算变化先写提案并等用户对齐；未知先查证。不得用文件名、阶段名相同证明接口兼容。对话只报告结论、证据和待决策点，不输出私密思维链。

复杂旅行遵循以下流程。阶段可以由同一个模型顺序承担，不能据此声称已启动独立 Agent：

```text
RequestContract → ResearchQueryPlan → typed candidates/facts
→ Admission → Intent Evaluation → Ranking → CandidateSelectionPlan
→ Itinerary Composer → Intent Fidelity Gate → DeliveryBundle
```

### 职责与输入输出

| 角色/阶段 | 读取 | 交付与限制 |
| --- | --- | --- |
| 主编排 | 最新用户要求、旧版本与能力清单 | RequestContract、研究任务、版本/依赖；负责取舍及一致性，不凭空补事实 |
| 研究 Worker | 合同的必要投影、query_id、required_fields、权限 | typed candidates/facts、来源、unknown/conflict；不自由生成最终行程，不扩大权限 |
| Admission | 候选实体/来源、硬约束 | admitted/rejected/needs_repair 与理由；未知不当通过，硬约束不靠软分补偿 |
| Intent Evaluation / Ranking | admitted 候选及意图 | 匹配依据与相对优先级；无数据不造分数/胜率 |
| Selection | 可用候选、风险与替代 | CandidateSelectionPlan：Primary / Alternative / Fallback；拒绝/待修复候选不直接成为已确认安排 |
| Composer | 当前选择计划、通勤/天气/营业事实 | itinerary；只使用获准选择的 candidate_id，明确草案与条件分支 |
| Intent Fidelity Gate | 当前合同与完整日程 | intent_coverage、pass/needs_repair/blocked；失败回研究或组合，不靠解释抹掉硬冲突 |
| 交付角色 | 通过相应验收的同一 DeliveryBundle revision | 聊天/Word/PDF/地图投影与 QA 记录；不自行改时间、事实或承诺 |

## 2. 本地记录：唯一字段与旧状态映射

字段以下表和示例为准；`null` 表示未知，不是已确认、0 或空字符串。ID 为非空字符串，在同一 trip 内稳定且唯一；引用必须存在。`revision` 为正整数，每次 amendment 递增；`schema_version` 与内容 revision 不同。排程与查询时点用包含偏移量的 ISO 8601 字符串，另存目的地 IANA timezone；跨午夜写完整次日日期。来源只提供发布日期而无时刻时保留原日期精度并标记 date_only，不虚构发布时间/时区；未知为 null。

### RequestContract

`request_contract` 是用户意图的唯一可写入口：

- `trip_brief`：destination（字符串或城市列表）、timezone、dates（start/end 当地日期）、people（正整数或 null）、anchor（kind/entity_id）、arrival/departure、budget（金额区间/币种/口径）、rest_preferences（default_enabled、midday_minutes、needs_room、walking_tolerance）、assumptions。
- `hard_constraints`：约束 ID、内容、来源及是否用户确认；已订预约/返程/禁止项不可自动改变。
- `desired_intents`：intent_id、目标、must_do 布尔值、验收条件；must-do 不能因不好排程无声删除。
- `soft_preferences`：偏好及来源；默认值标 default，不伪称用户确认。
- `unknowns`：必要输入缺口和修复负责人；`acceptance_criteria`：可核对的验收条目。

### ResearchQueryPlan 与候选

`research_queries` 是数组，每项含 `query_id / owner / intent_id / entity_scope / required_fields / preferred_sources / fallback_sources / done_when / status`。owner 为 places/transport/context 等当前实际角色，不代表已创建服务。记录输入合同 revision。

`candidates` 每项含 `candidate_id / entity_id / kind / name / navigable_address / intent_ids / fact_ids / price / duration_minutes / admission / unknowns`。admission 为 admitted/rejected/needs_repair；价格状态与实体准入不同。餐厅/写真馆默认比较 2–4 家具体候选（不足说明，不凑数），含完整分店/地址/楼层、目标匹配、服务窗口、套餐时长、价格及电话/预约入口（可得时）、锚点通勤与推荐理由。无法取得价格或档期就标 unknown；不能退化成“附近吃饭”“找一家写真馆”。

`selection_plan` 每项含 intent_id、primary/alternatives/fallbacks（candidate_id 引用）、选择依据和 conditions。具体名称/地址缺失的条目只能作为研究缺口或区域草案，不进入可执行最终 itinerary。必需预约、适用营业等关键条件未知时不得通过相关验收；可以交清晰标注的受限草案。

### DeliveryBundle

一个 trip 的当前 Bundle 使用以下本地结构。数组元素以稳定 ID 相互引用，不复制可独立修改的第二份同义状态：

```yaml
schema_version: local-travel/v1
trip_id: example-trip  # 示例，实际运行用唯一 ID
revision: 1
as_of: null
request_contract:
  trip_brief: {}  # 使用上文完整字段；示例空字典不代表满足验收
  hard_constraints: []
  desired_intents: []
  soft_preferences: []
  unknowns: []
  acceptance_criteria: []
research_queries: []
capabilities: []  # 实际工具、权限、版本、验证及限制
facts: []
experiences: []
weather: []
candidates: []
selection_plan: []
itinerary: []
commutes: []
budget: {}  # 聚合区间、币种、机动金与未计入项
intent_coverage: []
sources: []
open_questions: []
change_log: []
deliverables: []
run_state: {stages: []}
```

- `facts`：fact_id、entity_id、claim、value、applies_on、timezone、source_ids、checked_at、status。status 为 verified/user_confirmed/reference/historical_reference/estimate/unknown/conflict；其中 historical_reference 不参与当前排程。网页可读不自动等于 verified。
- `sources`：source_id、url（用户提供的事实可为 null）、source_type、published_at、checked_at、access_scope（full/snippet_only/login_required/blocked）、适用范围。保留冲突双方来源；不编访问记录。
- `itinerary`：slot_id、kind（activity/rest/transfer/buffer）、candidate_id（非实体时间块可 null）、intent_ids、start/end、条件与事实依赖。引用选择计划中的具体实体；休息不假造商户。
- `commutes`：commute_id、准确起终点/入口、mode、路线/方向/站点/换乘、duration_minutes 区间（含步行候车）、price、人数、来源/状态、理由及备选。
- `price`：amount 或 min/max 区间、currency、unit（per_person/per_room/per_car/per_package/total）、quantity、includes/excludes、source_status（verified/reference/estimate/unknown）、checked_at。quantity 必须对应单位；per_person 乘实际人数，per_car 按车数，不能再乘乘客数。budget 汇总同币种/同计费范围；未知项目单列不按0计，已支付与新增预算分开；机动金通常10%–20%，注明假设。
- `intent_coverage`：intent_id、slot_ids、outcome（satisfied/conditional/unmet）、证据及原因。must-do 未覆盖或关键约束冲突不得记 pass。
- `open_questions`：引用 unknown/修复 ID，不另建一份可冲突的事实；交付路径和核验范围归入 deliverables。

### 旧记录迁移（仅在实际读取旧行程时）

| 旧字段 | 新权威位置/处理 |
| --- | --- |
| trip_id/revision/as_of | 保留值；升级记录格式也记 change_log，不伪造完成历史 |
| trip_brief 的日期/人数/锚点/预算/休息/假设 | request_contract.trip_brief；其内 budget 是用户预算约束，顶层 budget 是计算结果 |
| trip_brief.hard_constraints | request_contract.hard_constraints；移出旧位置，避免双写 |
| trip_brief.desired_activities / optional_activities | request_contract.desired_intents；保留原优先级/来源；可选项 must_do=false；不把“想去”偷偷降级为可选 |
| activities | 转入 candidates，原活动 id 可保留为 candidate_id；补实体/证据/准入。不能因旧日程用过就默认 admitted |
| itinerary.activity_id | 显式映射到 candidate_id；纯休息/通勤改 kind；未找到 ID 标修复，不能丢弃 |
| facts 的 source_url/source_published_at 等 | 提取 sources 并用 source_ids 引用；保留时间、事实状态与来源精度 |
| capabilities/experiences/weather/commutes/itinerary/change_log/open_questions/deliverables | 保留原信息，补 ID、revision/dependencies 和下述状态；不把未知值改 verified |
| 已存在的 run_state 或 run_state.json（run_id/tasks） | 保留 run_id 与来源 revision；tasks 的键映射 stage_id，status 保留为历史执行状态，artifact 映射 outputs。未知 input_revision/depends_on/validity 标未知并重审，不丢历史，也不凭 COMPLETED 直接复用 |
| 实际缺失的 research_queries/selection_plan/intent_coverage/run_state 等 | 明确待建立，不补造已完成状态；先重新检查可复用结果 |

迁移后旧版本作为只读历史保留；新版本删除旧别名或只作明确只读投影。若旧值与新字段冲突，保留冲突证据并查证，不用方便排程的一方覆盖。不得自动将私人行程提交本仓库。

## 3. 可行性与验收不变量

- 营业 `service_windows` 为同日期/时区窗口数组；`break_windows` 单列，另有 last_order/last_admission/holiday_override 与来源。活动连同退出余量须完整处于**同一个**适用窗口。`10:30–14:30 / 16:00–21:00` 不得合并；闭店日、节假日覆盖及跨午夜按实际日期处理。
- last_order 是最后下单时间，不等于最后离店：order_at <= last_order，同时 end+exit_buffer <= close；last_admission 单独检查。没有下单时点只能明确假设/待核，不把 close 替代它。
- 覆盖午间的旅行日默认60–90分钟独立午休，起草可取75分钟。用户可明确调整/取消；固定票面冲突须记录原因及取舍，不算自动满足硬性午休。吃饭、乘车、排队不能冒充休息；回酒店交通、用房资格及费用另算。
- `arrival = previous_end + transfer + traffic_buffer`，活动再加候位/入场。通勤方式或时长改变必须重排下游时段和预算，返程余量/已订时窗不被挤掉。
- Intent Fidelity Gate 逐条检查 must-do、具体实体、营业天气、所有地点转换、休息、返程、预算与未知信息标记。缺候选回研究，组合冲突回 Composer；无法满足的硬约束提交最小取舍等待用户，不自动改变预订。
- 文档由同一 Bundle revision 投影；Word/PDF 要实际生成、渲染逐页检查及验证访问。只生成未 QA 的文件不能称最终验收通过；无能力则如实交受限产物。

## 4. Amendment、失效与恢复

每次新增要求先写 change_log：amendment_id、from_revision/to_revision、changed_fields、来源/用户决定、受影响 IDs、原因及后续任务。增加 revision，然后沿真实依赖传播失效，不以全量重跑代替依赖检查。

每个派生产物记录 `built_from_revision / validated_for_revision / depends_on / validity`，validity 为 current/stale；仅已复核且依赖未变才能把 validated_for_revision 更新到当前 revision。built_from_revision 保留原值。事实 status 与 validity 不同：过期 verified 来源仍保留历史 status，但不能当 current 使用。

| 变更 | 至少重审/重算 |
| --- | --- |
| 新 must-do、酒店/锚点、日期、服务窗口/关闭 | 相关 queries/facts/candidates → selection_plan → commutes/itinerary/budget → intent_coverage → deliverables |
| 通勤方式/时长/车费、人数 | commutes/价格数量 → itinerary、budget → intent_coverage → deliverables；人数也重查套餐/房型/容量 |
| 午休、返程、已订时窗 | 相关选择与通勤/itinerary → budget、intent_coverage、deliverables |
| 天气转差 | 受影响户外候选/选择/路线/日程/预算及后续验收交付；同区可行备选需重新验收 |
| 只改文档排版 | 该文件的渲染/视觉 QA，不擅改规划数据 |

上表是最小传播范围，实际依赖可能更广；无关、有效的历史研究可复用，已发生的行程只保留历史，重排仅改未来。stale 产物不能作为当前最终链接。

`run_state.stages[]` 含 stage_id、status（PENDING/RUNNING/COMPLETED/FAILED/INTERRUPTED）、input_revision、depends_on、outputs、error/blocked_reason。COMPLETED 只表示那次阶段执行完成，不保证产物在新 revision 仍有效。恢复先核对合同/依赖/来源有效期；当前且未过期的完成结果可复用，stale 或版本无法验证的结果重审，受影响阶段回 PENDING。失败/中断记录原因和待修复项，不从进程结束推断交付成功。

`deliverables` 含格式、实际路径、bundle_revision、validity、QA状态（not_run/passed/failed/limited）、checked_pages/total_pages、限制与访问检查。只有本次 revision、current 且相关 QA 已通过的产物才能称最终通过；limited 可交付，但必须说明范围。

## 5. JourneyPilot 是可选参考，不是已接通后端

本地 RequestContract、ResearchQueryPlan、DeliveryBundle 是便于人和模型协作的记录名，**不兼容**同名 JourneyPilot Python schema。即使环境已部署 JourneyPilot，也不直接把上述 YAML 当 API 入参，不声称已有 adapter。

核查的 [JourneyPilot 版本](https://github.com/Lagom-TA/JourneyPilot/tree/5e08d829a04048c6f6dba86b191813e22825c106) 在 [ChatRequest](https://github.com/Lagom-TA/JourneyPilot/blob/5e08d829a04048c6f6dba86b191813e22825c106/src/travel_agent/api/schemas.py#L57) 接收 messages/controlled_trip_identity 等公开字段；内部合同含严格 ID/revision/hash，公开交付是另一个投影。部署成功不证明这些契约兼容。

真正接入须另有用户授权及版本固定的适配设计，验证公开输入/输出、目的地/天数限制、认证与传输权限、多营业窗口、价格单位、未知/冲突、恢复与交付版本。保留无法无损映射的字段，失败时停止相关集成并回退已授权的本地工具流程，不静默丢失约束。不自动安装 runtime、创建持续访问、上传私人资料或启用后台监控。
