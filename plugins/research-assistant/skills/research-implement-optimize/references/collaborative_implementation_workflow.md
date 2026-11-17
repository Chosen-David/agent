# 协作式实现与任务验收

代码实现、修复和重构开始时加载本流程。由同一个主 Agent 串行执行；它是行为规范，不是拦截任意 shell 写入的权限系统。不要把结构测试通过称为模型遵循或意图正确性的证明。

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

## 每一小步

1. **说明本小步**：改哪个行为、为什么、采用哪个验收；有关键歧义先讨论。
2. **按讨论采取行动**：先准备上述测试/约束和变异，再实现最小变更；不同时推进下一功能。
3. **共同看代码与结果**：展示关键 diff、实际命令、退出码、断言结果和副作用。记录规格、代码、测试版本及原始输出位置；文件存在和哈希只标识内容，不证明执行或人类批准。
4. **暴露新发现**：报告失败、变异存活、未覆盖输入、工具缺失和模型假设；不能悄悄降低阈值或改期望来变绿。
5. **共同确定下一步**：按用户已约定的协作粒度继续；需要新语义决定时停在具体问题上。已有明确授权无需机械重复审批。完成需要真实任务验收，不能用报告里的 PASS 字段代替。

验收脚本更新后重跑受影响检查。记录命令未执行、失败、跳过和未覆盖范围；不宣称本流程保证零缺陷、不理解偏差或未实测的性能提升。已有独立验收合同继续保留，作者自检不替代独立证据。

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
