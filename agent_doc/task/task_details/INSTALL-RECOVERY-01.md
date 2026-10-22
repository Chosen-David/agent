# INSTALL-RECOVERY-01：模型发现与安装恢复一致性

Task-ID: INSTALL-RECOVERY-01
Date: 2026-10-22

## Plan

Version: 2

SYSTEM-99 同一未完成批次。基线61a7ee343d36f9e211fd697282c78743a2160ab2；EXECUTE：用户授权真实入口审查、修复、必要验证后main普通发布。GUIDE.md为空，README只读，现有TASK/检查点/未提交修改及origin/main已核对。上次SETUP-DOCTOR-01只恢复导入作用域；其独审明确排除本任务问题，不能复用旧通过作验收。本次真实安装→mock发现→doctor→check→重复安装复现：生成opus字段但报告仍None、check有4错误、重复安装认为路由文件被本地修改。显式discover在mock进程成功且install预检失败时覆盖既有用户inventory，独立记录原始复现。

范围与方法：
1. 显式discover输出改为调用独占TemporaryDirectory，保留真实发现命令/目标cwd，新增与auto同为30秒的进程上限；读取/验证库存后才交install，临时结果不写项目model_inventory.json，不删除用户文件。非零退出、超时、坏JSON以ValueError报告setup blocked，不吞掉错误。
2. doctor仅对已有安装manifest更新模型相关受管文件（policy/routing和注册agents）。复用expected_files渲染及checked_target路径守卫；先校验manifest仓库/项目归属，再对所有待写模型文件进行完整fingerprint预检，本地修改/链接/外部目标/不明所有权均在任何写入前拒绝。保留其余配置、CLAUDE、skills、任务/guide与manifest未知字段；不全量重装，不强行覆盖本地非模型orchestrator。更新模型文件、manifest文件hash及model_inventory；manifest最后写。原孤立model_inventory.json不作权威/不覆盖；安装manifest一直是check与后续install的权威库存。
3. check读取manifest后先核验顶层dict；非法对象/读取失败重置为{}，既有needs_setup错误报告保留，避免后续.get在非法类型上崩溃。doctor报告在更新完成后重新check；fixes只在成功后登记。无安装manifest时保留needs_setup，不把doctor当隐式初次安装。单文件原子写已有实现保留；不承诺多文件掉电/并发事务。

验收先写回归/保留旧源码失败：首次显式发现、用户inventory在成功/安装冲突/超时/坏JSON保留与清理；真实安装→发现fixture→doctor→check→重复install→uninstall路由/清单一致、第二doctor不再发现；本地模型文件/策略/代理编辑与后段冲突都零修改；非模型orchestrator和用户正文编辑保留；外国manifest/项目/缺manifest、顶层数组/null/标量下check及无网关doctor返回needs_setup且零修改、有发现结果时在写前受控拒绝，symlink逃逸/guide别名拒绝；已有copy模式不丢清单。专项普通/-O、setup/portable/discovery/doctor/model-routing/role-process/install-profile回归；独立计划与独立结果复核后精确暂存、fetch/CAS非force发布、远端整树/关键字节核验。

本次是离线CPU正确性链路，不测网关/模型/tmux服务器/性能/质量/费用，不运行未知资源。能力名启发式、tmux错误恢复及其它SYSTEM99验证仍open。同批14篇正文阅读检查点保留，不重复计数，本检查点不计完成一轮。无架构迁移、竞争TASK或后台部署。主AI唯一写源码/测试/TASK/detail/advice；独审只写分配的.agent-runs/install-recovery-1756/审核输出；不存在可信runtime认证桥时如实只作native独立审核。

## Progress

- 原始复现见.agent-runs/install-recovery-1756/reproduction.log；上述问题已实际观察，修复与验收待完成。

- 独立计划APPROVE；显式discover、所有模型路径/manifest身份与hash预检、manifest-last及刷新check按Plan实现。14项最终专项普通/-O通过，相关57通过；原11项修前14failure/3error完整保留。
- 原集成57项1失败：旧test_setup_doctor mock全fallback但没有安装manifest。按已冻结Plan“无manifest不发现/不隐式安装”补真实empty安装前置，未放宽路由/调用断言；原integration-initial.log保留。最终57通过。新增三个边界覆盖坏fingerprint/mapping/缺所有权、缺失但有所有权文件恢复、无效发现库存零修改。
- 已核scripts/run_role.py:139–149实际消费者：先check，再读取installation.json库存，孤立model_inventory.json从非权威文件原样保留。独立结果审核补实际dry-run消费者，禁止模型调用；审核未完成前不发布。

- 独审v1额外发现check先于更新helper执行，顶层非对象manifest可触发既有AttributeError。版本2补读取端dict检查与异常后状态重置，并保留v1计划审核及专项14/57与基线18failure/3error独审记录，不把v1结果冒作v2验收；v2需重新计划审核和受影响复测。

- v2计划APPROVE后补check入口dict校验和except重置{}；2项新回归在v1代码6error，v2最终16项普通/-O与57相关通过。只读诊断的{}回退不作为写入凭据，update helper仍重读原始非法manifest并拒绝。v1专项/独审及新增失败均保留；最终独审在新hash上进行。

- 最终独审ACCEPT usable-with-scope：新hash16项普通/-O与57集成通过；最终16项对旧源码独立复现18failure/9error（包括新增非对象6error，不等于27个独立生产bug）。实际run_role无显式库存dry-run选opus，两个并发显式发现使用不同临时输出并清理，实际CLI对数组/null/数字/字符串清单返回needs_setup JSON/exit2；有发现结果时通过main受控拒绝零写。原v1审核/日志保留，公开最终hash/短日志见agent_doc/results/install-recovery-1756/manifest.json。
- 诊断回退不认证所有权；多文件I/O/掉电/并发事务、更多任意损坏字段、网关/模型/tmux实服务、性能/质量仍未验。能力名启发式和tmux异常恢复后续审查；无新增阅读数或新轮完成。发布前fetch、远端CAS及整树/关键文件回读由主控最后核对。

- 发布前证据完整性复查：生产optimized-v3.log最终读仅9行、缺summary，与先前执行stdout显示16/OK不一致；原字节保留、原因unknown，不以该部分日志单独证明计数。独立最终普通/-O完整日志各16/OK、集成57/OK已回读并另公开哈希绑定；最终接受依完整独立记录，额外限制写manifest，不把共享工作区历史异常断言为本次已知原因。
