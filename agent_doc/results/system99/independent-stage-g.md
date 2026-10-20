# SYSTEM-99 阶段G独立审核

## Plan

结论：Plan Version7 阶段G **approve**。只新增CPU跨模块回归与必要记录，不改runtime/schema/guide，不发布；此意见不是运行时认证回执或真实模型能力证明。审核基线main `d033c9f045b0211441abca2eb63b9c6b4e61cd4f`，主控锁99917，唯一任务仍SYSTEM-99。

已读AGENTS、决策协议、项目文档治理、结果复用/验收、双主、通信及记忆契约，实际Plan7与TASK；当前GUIDE为空且只读。先检索后执行：ResultStore查询`correction memory communication recovery`，limit6/max_scan200，scanned199、partial=true、65读取错误；候选combined-corpus-delta-v2/v4、comm-ack-confirm、comm-batch-integration、comm-confirm-integration、comm-route-bind均为旧语料或局部通信证据，不能复用为本次跨模块更正链验收。另读真实`independent-chain-audit.md` H2及memory-context10的更正测试记录，采用现有边界和fixture，不把旧pass当当前验收，也不声称穷尽历史。

| 七域 | 判断与依据 |
| --- | --- |
| intent | pass：补齐已声明更正依赖到实际消费者和终态恢复的有限CPU证据，不制造生产bug。 |
| guide | pass：现有人类guide空文件；保持全目录只读、唯一TASK及原证据。 |
| assumptions | pass：保护计划/SQLite/显式memory_refs可实际运行；CPUHost是测试认证桩，隐藏依赖不自动发现。 |
| prior_results | pass：真实查询及原报告只支持局部复用；本次针对跨模块缺口补验。 |
| acceptance | pass：真实上下文/ACK、旧done围栏、重启/reconcile拒绝、无关分支、取消、新身份及新审核、true→false决策与原字节保留均需代码和执行检查。 |
| risk | pass：临时项目、有限CPU、已有接口、无runtime/schema/guide改动；ACK不升级为结果验收。 |
| resources | pass：仅当前CPU与本地SQLite，不运行模型/未知服务；真实宿主、SSH/tmux和成本质量仍open。 |

私有探针SHA256 `adf9cc10de4d3ff78717fbd1fa665a1a9739b72fd91896e377e35e0f02f20848`已核对，独立实际运行通过：initial=done、after_correction=blocked、unrelated=done；取消旧run后新run=done，旧决策true、新决策false，审核次数2、消息E2，原raw/报告/ACK保留。原错误kind=intent是fixture输入错误，不能记为生产修前红证。

代码审查特别限制：消费者通过prepare_context检查完整声明依赖，随后从真实账本/原始JSON复算阈值；reviewer任务另读writer报告比对。Handler.verify只验报告身份/evidence，语义检查位于run；这不是独立科学结果gate或LLM质量试验。unrelated报告哈希来自固定原字节，实际文件未改由后续直接字节比较另证。计划中的合成标记仅描述本控制流fixture，不用于绕过声明的数据消费合同。

## Final

公共测试SHA256 `70e2f4aac8bf28a9c0a3f422ae344a8ee406a132364b82dc7752588f62431ae6`。逐行diff确认主体逻辑与冻结探针相同，仅ROOT、fixture模块引入、说明和unittest/静默包装改变；模块引用避免重复发现BasisTests。独立执行普通及`-O`各1项通过（1.960s、1.938s），只发现新增测试。

额外独立检查不修改磁盘源码：内存插桩确认两轮计划SHA/request_id及回执不同，新旧各2条ACK均consumed、新run每节点attempts=1、writer/reviewer均由true变false、旧run实际snapshot=cancelled。分别临时替换`Engine._check_done`为空操作、`Mailbox.impact`为空列表，两次均触发新测试AssertionError，证明主要围栏/影响范围断言实际执行。

最终结论：**usable-with-scope**，接受阶段G的有限CPU控制流/声明依赖跨模块验收。无阻断发现；不据此关闭SYSTEM-99整批或H2的真实模型宿主部分。公共测试SHA未变，Plan7详情当时完整SHA为`83b3d9fcadab702b86efa122a384a33dd7fe77c878a01ce22e4a6d4a934b03e8`；后续Progress追加不改变本次稳定Plan含义。

独立读取并核算主控完整日志：full-g共1392条测试行、8条skip、1384执行通过，103.161s，末尾OK；新增测试只有一条实际测试行。full-g SHA256 `bb38da10e10196872ae510670c0396417c6fed78d9c5f037816251b3dcb509ad`。Reader应用3项通过，1.599s，日志SHA `38d007fc4c104ee0611809ae53b79d3cdd7b5285837b379a82af473c0b04799c`。没有独立重跑全库/Reader；同步检查另独立执行`python scripts/sync_plugin_references.py --check`退出0。普通/-O主控日志SHA与阶段报告逐项一致。

已读stage-g事实与scope，符合实际代码和上述执行。research-e只核对取舍及原PDF SHA256 `9360ef8010a9013817a28cbf929ecfa1868be1e349f422059dfcad61bb92b1c8`，不冒称本审核者全文重读或复现论文。接受其“保留观测/旧回执、分开更正与恢复”的有限启发，不将词序/时间/整库回滚或论文成绩迁入本库能力声明。
