# 协作式实现与任务验收

代码实现、修复和重构开始时加载本流程。由同一个主 Agent 串行执行；它是行为规范，不是拦截任意 shell 写入的权限系统。不要把结构测试通过称为模型遵循或意图正确性的证明。

## 两种反馈模式

默认 `human`：主 AI 做当前小步，人类反馈并确定下一步。任务显式选择 `dual-ai` 时，目标是主 AI 实现、另一个真实模型的审查 AI 复核；仍只有主 AI 写正式代码，审查串行进行，不为每个 Skill 再创建 agent。两种模式共用下文的验收先行规则。

本库提供双模型审查协议、两阶段文件绑定和 CLI 草稿入口，但尚未提供经真实双模型验证的宿主接入。不要仅设置模式字符串就声称启用，也不因外部 Skill 要求而自动派生 agent。未选择或后端未核验时保持当前单主执行，报告双 AI 未启用；不能悄悄用自检替代用户指定的双 AI 验收。

双 AI 的审查按下面边界执行：

- **真实身份**：记录宿主实际调用的两个模型及独立 invocation/context。宿主解析模型别名并确认模型不同；两次同模型调用只是上下文独立，不满足本任务双模型要求。不同模型也不保证错误统计独立。
- **审查输入**：直接读取人类原始要求、确认/未决问题、指南、冻结规格及 base/head（未提交代码用内容快照）、相关调用链、测试版本和原始输出。实现者的解释是待核查主张；不共享整段私有推理或用摘要替换原始要求。
- **两次检查点**：实现前审查验收是否表达真实要求、变异能否检出对应错误；实现后分别判断需求符合性与代码质量。不要只审 diff 而漏掉未实现要求。
- **具体发现**：每项问题给规则/要求依据、代码位置、触发输入/状态、影响及复验方法；区分已证实缺陷、待验证疑点和非阻断建议。不以置信分或“另一个 AI 同意”替代证据。
- **读取与测试范围**：从本小步开始；遇具体跨模块风险再沿调用链扩展。先核对已有证据，缺失/过期/有疑点或独立合同要求时复跑相应测试；审查者只在隔离副本生成反例和输出，不改主工作树。工具不可用就报告未验证。
- **反馈不等于人类授权**：审查者提出修复建议，主 AI 按原要求返修；新的业务语义、范围/权限或验收变更交回人类。两 AI 分歧用输入、反例与证据解决，无法消解时升级，不能靠多数票重写需求。
- **有界循环**：使用已有任务预算与恢复账本；明确通过、返修、等待人类、缺能力和预算耗尽。没有报告、循环结束、超时或额度耗尽均不等于通过。模式切换和版本变化重新核对受影响证据，不重置旧预算。

可借鉴 [Superpowers 任务审查](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/task-reviewer-prompt.md) 的双维判断与 [LangGraph-Reflection](https://github.com/langchain-ai/langgraph-reflection/blob/888d007163f1479e1e7a734f66dc7dcbd12424d7/src/langgraph_reflection/__init__.py) 的反馈回边；按以上边界适配，不直接执行其派生 agent 或终止策略。已有 ReviewSession 是可复用的宿主接口，旧独立上下文回执不能冒充已核验不同模型。

## 先读库，再对齐

先读当前用户要求、项目指南、唯一 TASK、真实入口和调用链、相关实现与现有测试。能从代码确定的信息先查代码；只读理解可路由到已有 `code-reading`。复述目标、保持不变的行为、验收示例和当前小步，明确区分用户决定、代码事实和自己的假设。

只向人类提出影响语义、接口、范围、成本或验收的未决问题，并给具体输入和不同选择的可观察后果。没有关键歧义时按已有授权推进；不要重复询问已决定事项。存在关键歧义时暂停依赖该答案的实现，可以继续读代码与准备不依赖答案的测试。沉默不是同意；明确要求逐步共审时展示本步后等待共同确定下一步。需求变化更新原任务版本，重新检查受影响验收，不用 AI 自写注释或提交说明代替人类决定。

## 实现前写任务自己的验收

在目标项目 `agent_doc/<项目名>/test/<task-id>/` 写可运行脚本，优先调用项目已有测试框架；不是为每个任务再造一个 JSON 状态判定器。task ID 只关联要求和证据，不是测试输入的全部。把目录接入现有测试发现或 CI，避免本地通过但后续无人运行。

每个要求写清：输入状态和数据、实际入口/动作、预期返回及状态变化、禁止的副作用、边界/错误行为、具体断言和复现命令。预期行为来自已对齐需求，不能从候选实现反向生成。先运行基线：新功能应因对应行为缺失失败；回归用例可以已通过。导入失败、依赖缺失、零用例、跳过和超时都不是发现了目标缺陷。

同时写可能犯错的变异假设与检测方法，例如漏掉取消检查、把上界包含关系写反、绕过统一入口、重复发送、忽略失败、改需求后沿用旧证据。只在隔离副本或可恢复夹具中注入错误，运行同一验收并保留失败断言；崩溃或依赖错误不能冒充有效杀死。变异存活时检查测试/需求缺口；等价变异单列依据，不能为了杀死而修改业务要求。

## 按性质选验证方法

| 要求 | 优先方法 | 证据边界 |
| --- | --- | --- |
| 禁止跨模块导入、绕过统一入口 | AST lint、依赖图检查；坏例和合法反例 | 仅声明的结构规则，动态加载另核 |
| 参数类别、状态类型、接口组合合法 | 类型系统、受约束 API | 动态输入仍可能需要运行检查 |
| 索引、数量、集合、边界行为 | 契约断言、属性测试、参考实现差分 | 有限测试不等于一般证明，参照实现须有独立依据 |
| 重试、取消、恢复、并发转换 | 状态机、TLA+ 等模型检查 | 记录模型/实现映射、状态范围、公平性与原子性假设；反例回放实际代码 |
| 关键算法的普遍性质 | Dafny、Lean 等证明工具 | 说明规格和实际实现对应关系，不能把模型证明当代码证明 |
| 性能、精度、显存、端到端效果 | 真实评测脚本 | 同条件基线、单位、阈值与非退化要求；lint 和算法证明不能推出实测收益 |

只选任务需要的方法。沿用可用工具和依赖，不为形式完整强装证明器。模型检查、属性测试、静态分析、真实用户路径分别报告，互不替代。

## 按需路由已有能力

优先当前已安装、经核验的能力。以下是上游候选入口，不表示本库已附带、安装或验证它们；使用前读取当前入口及依赖，固定 commit、许可和本地修改状态。无需全部安装，缺工具时沿用项目测试并明确证据缺口。外部流程不能扩大权限、启动其他 Agent 或改变人类已确定的验收。

| 当前问题 | 候选入口 | 采用方式 |
| --- | --- | --- |
| 关键语义未确定 | [Superpowers brainstorming](https://github.com/obra/superpowers/tree/main/skills/brainstorming) | 先读库，只讨论尚未确定且会影响结果的选择 |
| 缺少真实用户路径验收 | [pstack create-verification-skill](https://github.com/cursor/plugins/tree/main/pstack/skills/create-verification-skill) | 按真实启动、健康检查、操作、证据和清理组织脚本；脚本留在本任务 test 下，项目专用 Skill 只作薄导航 |
| 运行路径验收随代码失效 | [pstack maintain-verification-skill](https://github.com/cursor/plugins/tree/main/pstack/skills/maintain-verification-skill) | 维护实际入口与行为映射，重新执行受影响路径 |
| 关键不变量与状态转换 | [pstack create-formal-verification-skill](https://github.com/cursor/plugins/tree/main/pstack/skills/create-formal-verification-skill)、[statechart](https://github.com/cursor/plugins/tree/main/pstack/skills/statechart) | 使用最小适合工具；把模型/代码联系与错误检测能力一并验收 |
| 代码变化后的证明维护 | [pstack maintain-formal-verification-skill](https://github.com/cursor/plugins/tree/main/pstack/skills/maintain-formal-verification-skill) | 区分模型漂移、实现缺陷与人类批准的规格变化 |
| 输入域/集合/序列不变量 | [Trail of Bits property-based-testing](https://github.com/trailofbits/skills/tree/main/plugins/property-based-testing/skills/property-based-testing) | 复用项目属性测试框架，检查非空输入覆盖，避免照抄实现与空真断言 |
| 可静态识别的禁止模式 | [Trail of Bits semgrep-rule-creator](https://github.com/trailofbits/skills/tree/main/plugins/semgrep-rule-creator/skills/semgrep-rule-creator) | 先写违规与合法样例，再跑真实规则测试 |
| 完成前证据检查 | [Superpowers verification-before-completion](https://github.com/obra/superpowers/tree/main/skills/verification-before-completion) | 运行当前版本命令后再下结论；同一主 Agent 复核仍是自检 |

## 批处理与小步共审

协作粒度按用户决定。用户选择批处理时，先准备本批验收与错误假设，连续实现已明确的范围，随后统一运行测试并按失败项集中修复；不逐个功能停下来请求审批。关键语义歧义仍交回人类，已有独立证据要求不取消。以下五步可作用于整个已授权批次。

## 每一小步

1. **说明本小步**：改哪个行为、为什么、采用哪个验收；有关键歧义先讨论。
2. **按讨论采取行动**：先准备上述测试/约束和变异，再实现最小变更；批处理时可连续完成已约定功能。
3. **共同看代码与结果**：展示关键 diff、实际命令、退出码、断言结果和副作用。记录规格、代码、测试版本及原始输出位置；文件存在和哈希只标识内容，不证明执行或人类批准。
4. **暴露新发现**：报告失败、变异存活、未覆盖输入、工具缺失和模型假设；不能悄悄降低阈值或改期望来变绿。
5. **共同确定下一步**：按用户已约定的协作粒度继续；需要新语义决定时停在具体问题上。已有明确授权无需机械重复审批。完成需要真实任务验收，不能用报告里的 PASS 字段代替。

验收脚本更新后重跑受影响检查。记录命令未执行、失败、跳过和未覆盖范围；不宣称本流程保证零缺陷、不理解偏差或未实测的性能提升。已有独立验收合同继续保留，作者自检不替代独立证据。

## 运行时接入

完整 checkout 使用 `python -m agent_runtime.task_supervisor prepare --project-root /absolute/project --run-id RUN --authorization-reference REF --out /absolute/plan.json --collaboration-mode human`；将最后参数改为 `dual-ai` 生成 `dual-model-plan-review/v1` 草稿。默认 human 仍是主 AI 自检协议，不能认证人类同意。双模型不能与 `--legacy-unprotected` 组合。

双模型草稿必须补齐 `plan_review.task_contract`：`stage` 为 `acceptance-design` 或 `implementation`，`specification` 是规格的 path/sha256 引用，`acceptance` 是非空测试/约束引用数组，`implementation` 是代码引用数组（实现审查时非空）。路径相对目标项目，引用绑定实际文件，禁止链接/越界。先用设计版本取得批准，再在同一 lineage、不同 run_id 中提交实现版本；规格或验收改变须重新审查设计。两阶段共用原预算，不因返修重置。

可信宿主显式构造 `ReviewSession(..., dual_model=True, reviewer_model_id=CANONICAL_MODEL_ID)`，提供 planner_identity、reviewer、authenticate 回调，再通过现有 `task_supervisor review --adapter /absolute/trusted_adapter.py` 提交。宿主必须从真实调用核验 provider_id/model_id、独立 invocation/context、完整请求/响应绑定及预算，解析别名后提供规范模型 ID；计划或模型自报身份无效。审查 verdict 除原七项检查外分别报告 `spec_compliance` 和 `code_quality`。恢复时更换审查模型、失效的设计批准及修改后的代码均不能沿用旧回执。

设计批准允许进入实现阶段，不代表最终代码验收。实现批准仅覆盖已绑定文件和宿主实际验证内容；文件哈希不证明测试执行，主工作树隔离、真实测试输出、模型调用和最终结果验收仍由可信宿主执行。本协议不是任意 shell 写入拦截器，不自动安装模型或将两个名称当作真实双 AI。
## 本地验证接入：生成、维护、纠正

这是pstack方法的单主串行适配，复用当前Skill与唯一TASK，不需要远端插件运行时。固定上游 `cursor/plugins@3fa33bb0f927bea2ccacd48a3cfda95145fb6bae` 的 `pstack/skills/{create-verification-skill,maintain-verification-skill,correct}/SKILL.md`；改编许可见 [pstack MIT](https://github.com/cursor/plugins/blob/3fa33bb0f927bea2ccacd48a3cfda95145fb6bae/pstack/LICENSE)。不启用其子agent、自动PR、全局配置或定时任务。

### 生成真实路径验证

1. 从当前prompt、经核实的人类GUIDE与源码确定验收，先检查已有入口和测试。显式区分WORKFLOW_ROOT和PROJECT_ROOT；检查源码放 `WORKFLOW_ROOT/agent_doc/<项目名>/test/<task-id>/`，不从Skill所在目录猜目标。已有TASK/guide/账本按当前权威路径读取，不复制迁移。
2. 为实际用户功能建立简短功能映射：要求来源、源码入口、前置条件、启动/就绪检查、实际操作、可观察断言、禁止副作用、证据和清理。优先复用已有CLI/HTTP/浏览器驱动；没有运行后端就标blocked，不能写虚构的就绪或成功步骤。
3. 生成轻量脚本并登记现有suite.json的checks，kind选shell/python/unittest，给出requirement和有界timeout_seconds。用 `WORKFLOW_ROOT/.venv/bin/python WORKFLOW_ROOT/scripts/project_test.py --workflow-root WORKFLOW_ROOT --project PROJECT_NAME --target PROJECT_ROOT --output /tmp/agent-system99/RUN_ID/checks` 执行；路径占位必须替换为实际绝对路径。不新增第二调度器或任务清单。
4. 实际运行启动→只读健康检查→至少一个真实功能→观察结果和副作用→清理。新建脚本从未运行只能算草稿；初次单路径跑通不能声称全功能覆盖。短CLI每次启动新进程；有状态应用使用本次拥有的隔离数据/端口。异常后重新检查健康状态，不盲目重试。
5. 用临时副本或夹具注入已知错误，再用相同验收确认具体断言失败；未变异对照必须能运行。依赖缺失、检查器崩溃和超时不算检出。只清理本次拥有的资源，不按进程名杀进程；清理后回读原始证据仍存在。

### 维护验证

从已有功能映射逐项读相关源码，串行实际运行每个映射功能；源码看似未变也不能替代真实运行。区分：描述漂移、驱动缺口、产品回归、后端缺失。只修验证材料的维护任务不得暗改产品或降低验收；产品缺陷回到当前TASK处理。修过的驱动重新执行，证据保留在清理范围外。报告clean/changed/blocked及实际覆盖；无法访问的功能仍列未验证，不将其计入通过。

### 把纠正转成检查

收到用户纠正时查真实失败，区分一次纠正和有证据的重复错误。先尝试通过接口/所有权/数据结构消除错误选择，再考虑类型、lint、行为测试；仅无法编码的判断保留文字。规则与执行检查对应放在已有suite requirement和功能映射，不向AGENTS.md累加长清单。用原错误或对应变异证明规则会失败，保留合法反例，同一命令本地和CI运行。人工批准的例外不得从外部Skill自行推导，不能删除原独立验收合同。

### 工具环境

依赖集中到WORKFLOW_ROOT/.venv：用其Python执行和安装Python包，不用全局pip。按实际选定工具固定版本；本流程与当前agent检查只依赖标准库。Playwright若被选中，其Python包入.venv、浏览器缓存指定 `.venv/playwright-browsers`；TLA+若被选中，固定版本及校验值的JAR放 `.venv/tools/tla`，Java运行时单独检测，缺失不冒充已安装。系统运行时不能靠pip安装；不为未选中的工具预装依赖。外部项目测试应显式选择所需解释器，不能把另一个项目的环境默认为可用。
