# 旅行工作流同步：先对齐契约边界

- 状态：`aligned`（2026-10-03 用户明确同意 B；实施范围如下）
- 日期：2026-10-03 UTC
- 本仓库审查版本：`86b7c5c3d064463c0ec4c4110a5754535f9d90df`
- JourneyPilot 审查版本：`5e08d829a04048c6f6dba86b191813e22825c106`

## 已对齐决策

需要修复旅行技能入口承诺与实际加载规范的缺口，但不能把“同名合同”当作接口已兼容。已选择 B：统一可移植的行为契约，保留入口差异；JourneyPilot 继续只是可选参考，真正接入另做版本固定的适配验证。

**已对齐：采用 B，仅整理旅行规范的共享契约、入口与回归检查，暂不接入 JourneyPilot runtime。** 以下选项/证据保留为决策历史。实现入口为 [共享规划契约](../../plugins/travel-assistant/skills/travel-planner/references/planning_contract.md)。

## 目标与约束

推断本次同步意图：从仓库主调度或安装后的技能进入，都能获得完整、可执行的规划/验收指导，并避免聊天与文档不一致。这个目标合理；不是要求所有文件逐字相同，也没有授权默认部署新的旅行后台。

保留已订项目、必须活动、服务窗口、午休、逐段通勤、按人/按车的预算单位、事实时效和同版本交付。插件必须能在只分发其子目录时阅读完整规范；不得依赖安装者同时持有整个仓库。

## 可复核证据

以下本地行号对应审查基线，后续编辑可能移动。

| 观察 | 依据 | 能得出的结论 |
| --- | --- | --- |
| 仓库主调度读顶层工作流；插件 SKILL 读包内 workflow | `prompts/orchestrator.md:24`；`plugins/travel-assistant/skills/travel-planner/SKILL.md:8–11,25`；`.agents/plugins/marketplace.json` 的插件根目录 | 两种真实消费者，包内不能只链接仓库外本地路径 |
| 顶层定义流水线，实际包内参考缺定义；SKILL 仍要求该流水线 | `workflows/travel_planning_workflow.md:9–117`；`plugins/travel-assistant/skills/travel-planner/references/workflow.md` | 存在指令契约缺口；不是可执行 API 已报错的证据 |
| 另有未引用旧版、错误相对导航 | `plugins/travel-assistant/skills/travel-planner/references/travel_planning_workflow.md:3` | 第三副本会造成歧义；可考虑兼容跳转，勿再新增完整镜像 |
| 本地没有 travel runtime/schema/adapter；已有简报/事实/活动模型与新 Bundle 字段需解释关系 | 两入口工作流的记录示例；仓库源码检索 | YAML 为规范示例，不能称已编译或已接通 |
| 历史验证曾报告一致 | `docs/travel_validation.md:8,64` | 仅是过去快照，不能当本次一致性结果 |

JourneyPilot 上游代码事实（本次仅只读检查，未部署/运行）：

- [RequestContract](https://github.com/Lagom-TA/JourneyPilot/blob/5e08d829a04048c6f6dba86b191813e22825c106/src/travel_agent/entities/request_contract.py#L81) 强制 ID、generation、revision、IntentSpec、constraint_pack、clause ledger 和 hash；[StrictModel](https://github.com/Lagom-TA/JourneyPilot/blob/5e08d829a04048c6f6dba86b191813e22825c106/src/travel_agent/entities/contract_base.py#L4) 禁止额外字段。本地自然语言清单不是有效的同名 API 对象。
- [DeliveryBundle](https://github.com/Lagom-TA/JourneyPilot/blob/5e08d829a04048c6f6dba86b191813e22825c106/src/travel_agent/entities/delivery_bundle.py#L3154) 由 manifest、workspace、事实/天气快照、报告/地图/来源投影与版本血缘组成；与本地 `request_contract/facts/candidates/selection_plan/itinerary` 示例不同。
- [ChatRequest](https://github.com/Lagom-TA/JourneyPilot/blob/5e08d829a04048c6f6dba86b191813e22825c106/src/travel_agent/api/schemas.py#L57) 接收 messages 和 controlled_trip_identity 等字段，不直接接收本地 RequestContract/DeliveryBundle。[公开交付投影](https://github.com/Lagom-TA/JourneyPilot/blob/5e08d829a04048c6f6dba86b191813e22825c106/src/travel_agent/services/public_delivery.py#L1) 也不等于内部 Bundle。
- 上游 [trip input](https://github.com/Lagom-TA/JourneyPilot/blob/5e08d829a04048c6f6dba86b191813e22825c106/src/travel_agent/entities/trip_input.py#L90) 有目的地数量及天数限制。候选/停靠点的 opening_window 是可选字符串；本地 service_windows/break_windows 不能假定无损映射。需用午晚分段营业用例验证。

## 选项

| 选项 | 收益 | 成本与风险 | 判断 |
| --- | --- | --- | --- |
| A：把顶层全文直接复制到插件 | 能补齐部分缺章 | 导航不适配；继续双份漂移；放大“部署后即可映射”的未验证承诺 | 不建议盲做 |
| B：统一运行时无关的共享行为契约；分别维护入口导航 | 包内完整、职责明确，减少核心契约漂移 | 要整理共享引用与旧记录关系；静态检查仍不保证模型遵守 | 已对齐采用 |
| C：真正接入 JourneyPilot | 可评估持久状态和交付服务 | 需部署、权限、依赖、字段适配及真实端到端测试；目前收益未测 | 另行评估，不默认实施 |

## B 的最小实施范围与验收

1. 将共同核心契约放在插件内可独立分发的参考文件，两条实际入口都显式读取它；不把通用主 AI 职责塞给事实研究 Worker。导航/编排上下文可以不同。
2. 定义本地记录的字段、类型/单位、来源与未知状态；解释旧 trip_brief/facts/activities 与 RequestContract/DeliveryBundle 的关系。研究者输出候选事实，主编排负责准入/选择/组合/验收，文档交付消费同一版本。
3. 明确这些是模型执行规范，尚无程序强制 schema；JourneyPilot 需要独立适配，不保证可直接消费本地 YAML。
4. 旧未引用副本改成包内兼容入口；验证包内链接闭合、所有入口加载契约及关键规范覆盖。不要要求全部文本字节相同。
5. 用约束变更情境检查：新增 must-do、营业分段、60–90 分钟独立午休、按人数预算、交通改变和文档重排；验证旧产物失效范围与同版本交付。把静态测试、模型情境检查、实际运行结果分开记录。

无量化收益、性能或成功率主张。B 减少重复定义与遗漏的收益是结构性推断，仍需实施后验证。任何外部 runtime 接入需先确认版本、公开接口、身份/数据传输、恢复和错误语义、服务窗口信息损失及真实执行证据。
