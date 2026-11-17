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
