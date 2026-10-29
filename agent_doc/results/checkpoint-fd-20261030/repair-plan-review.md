# CHECKPOINT-FD-FIX-01 Version57 独立方案审核

Decision: **revise**。存在1项阻断性方案发现：新增持久测试的完整字节oracle固定LF，不能正确验收保留原生产newline语义的Windows运行。当前冻结方案不能执行；先版本化修正测试/冻结输入，并按已耗尽1/1方案额度处理后续授权。不是修复结果通过、原生平台通过或SYSTEM-99整轮完成。此次只做静态审查，没有运行任何测试、旧诊断、旧门禁或 MemDerive。

审核根：`/workspace/scratch/95d615402a52/agent-run-1202`。对象：`.agent-runs/checkpoint-fd-fix-0200/plan-v1.json`，SHA256 `567baf00a6660f1bae6114361582d266c959e6933db2536bb10829077af31dbb`，base HEAD `d243266e9b9707ea6aac666e21a3ba8edb8e3a34`。15个 source_refs 全部独立实读且匹配；Plan56稳定前缀实读SHA `0a4da103f6621dc34a2b094177b60b3838318711e654a21410e4a4063fe33ba7` 亦匹配。逐项核验及相邻测试/原始日志补充哈希见本目录 `plan-verification.json`。

## 完整七域

| 域 | verdict | 审核理由 |
| --- | --- | --- |
| intent | pass | 原地修复当前 generic task_manifest.atomic_json 在构造流之前抛错留下 mkstemp 原FD的明确缺陷；不把小修复或提交当整轮。Version57除版本号只新增阶段AL，完整保留Version56旧目标/暂停项/未决。 |
| guide | pass | 实读 AGENTS、文档治理、双主、结果复用/独立验收规则与唯一索引；GUIDE.md为空，README只说明人类专用边界，未虚构具有人类目标内容。候选写入不含guide；本角色仅写本review目录，不抢唯一TASK或producer路径。 |
| assumptions | pass | fdopen(closefd=False)让创建者继续拥有raw FD，内层finally覆盖构造、进入及dump/write/flush/fsync/退出异常；正常流退出仍在显式os.close之前。只在关闭成功后重新guard及replace，外层临时名清理不变。close/unlink自身失败、恶意FD复用/父路径等明确排除，未被用作批准所需前提。 |
| prior_results | pass | 复用刚独审的当前源码诊断：源码hash、VALUE、故障、Linux/CPython环境均有确切绑定，producer/independent原始日志各3方法、同一个构造方法2失败子场景。此前fd95仅为所有权模式背景，不转用旧数字。原结果搜索含25 errors及知识空结果不能作全覆盖，继续保留该限制。baseline重执行max0恰当。 |
| acceptance | fail | 新持久测试相对原runner仅删除私有sys.path/ROOT/main启动、导入正规化和正常读取显式UTF8；原系统调用oracle、异常身份、两目标存在状态、旧字节、临时名、故障撤销后完整成功控制均保留。固定三模块静态计数3+42+3=48；完整代码及原始数据须后续独立验收，新3方法不应skip。但EXPECTED固定LF与Windows保留的CRLF文本输出冲突，见B1；不能把确定的oracle不一致留作CI发现。 |
| risk | pass | 生产diff只改这一个函数FD所有权，未加框架/schema/迁移或放宽guard、JSON或覆盖式更新协议；合成文件都在自有TemporaryDirectory内。相邻模块的guide/迁移测试只写自建项目，tmux调用为mock，无真实安装、服务或付费模型。风险及外推边界与Plan一致。 |
| resources | pass | 方案额度1/1本次已占；baseline0，fixed最多1，independent最多1，每命令120秒，共享截至2026-10-29T18:23:42.472068Z，无重试。时钟实读18:09:45Z，审查发生在截止前。仅CPU、已有环境、可回收临时数据；tokens/费用unknown如实保留，不假称满足未提供的付费预算或受信runtime认证。 |

## 生产及测试审查

完整source-before/source-after diff只在atomic_json增加借用式fdopen及inner finally的显式os.close，其他源码字节相同。成功路径仍先dump（ensure_ascii=False、indent=2、allow_nan=False）→换行→flush→fsync→流退出→raw FD关闭→guard_write_path→os.replace。对象构造失败时，finally不依赖不存在的stream，直接关闭mkstemp已返回的FD。NaN失败和其它序列化失败均先关闭流及FD，再由外层删本方临时名，不触碰原目标。没有早于fsync的关闭、成功后重复拥有关闭权或默认closefd=True与显式close的双关闭。closefd=False与fdopen整数FD接口适配；是否在目标原生平台通过仍由新CI决定。

测试以真实mkstemp返回值跟踪FD，os.fstat只把EBADF判为关闭，其余错误传播。构造失败注入在fdopen调用入口抛同一OSError，既不替换mkstemp也不伪造FD。is_closed在测试自身清理及撤销故障后retry之前取值，避免靠测试清理制造通过。目标既存与不存在分别核对原状态；旧字节、临时路径消失、retry完整字节及目录唯一成员均验。正常Unicode路径核完整序列化UTF8字节、内容、FD和temp；NaN路径核ValueError、旧字节、FD和目录。嵌套subTest保留失败后retry的可观察性，finally只清理仍打开的本方FD；不把两个子断言数当两个根因。该注入证明确定性缺陷与修复路径，不证明标准库自然失败频率或真实资源耗尽。

## B1 阻断：Windows完整字节oracle错误

位置：`.agent-runs/checkpoint-fd-fix-0200/new-tests.txt` 的全局EXPECTED及`test_normal_unicode_checkpoint`、`test_stream_construction_failure_preserves_state_and_releases_fd`中的path.read_bytes断言；并关联workflow-after四矩阵新增步骤。

EXPECTED由`(json.dumps(VALUE, ensure_ascii=False, indent=2) + '\n').encode()`生成固定LF。生产fdopen指定encoding但不指定newline，方案明确保留既有文本模式换行行为；Windows写入时会把indent生成的行分隔与末尾LF转为CRLF。因此正常写入及撤销构造故障后retry的完整字节断言在Windows比较LF预期与CRLF实际，必然错误。此前Linux诊断正常对照不能覆盖这个平台差异。这是静态标准文本IO控制流判断，本次未运行Windows或任何测试。

具体修改建议：保持生产换行协议不变，只让持久测试EXPECTED按平台文本输出换行构造完整UTF8预期，例如先在json.dumps文本加末尾LF，再把这些LF替换为os.linesep后encode('utf-8')。继续核完整read_bytes及JSON内容、FD关闭、temp清理、旧目标和retry，不能删除字节断言或加Windows skip。原私有诊断/原始失败保持不变，持久测试相对原runner的这项平台oracle差异必须显式说明。

复验：新冻结方案静态确认LF/CRLF预期都符合目标文本模式，之后在获得有效后续方案审核/预算边界下执行约定一次本机fixed/independent及新四矩阵/macOS原生日志核对。不得在旧冻结plan-v1或当前1/1额度下偷偷换testhash、再调用review或直接执行。需要新的预算决定时由主控按原授权与可信宿主恢复规则处理，审查者无权自动重置。

持久测试相对原runner的其余精确diff均已核对，无删oracle/skip/动态代码装载。生产所有权修复本身未发现阻断；B1修正前不批准整份候选。

CI完整diff仅在既有Ubuntu/Windows × Python3.10/3.12四矩阵，以及macOS3.12作业增加新测试module各一行；没有在Windows加入test_task_manifest或fcntl导入链。原pin、权限、timeout和既有测试不变。只允许新源码提交触发的新观测，不重跑旧失败job；四矩阵和macOS须分别读取新日志、执行数、skip/error/failure，不能拿本机48方法替代。

## 返修后的执行、验收及停止边界

以下是返修并获得有效新版审核后的执行要求，不是对当前候选的执行许可。主控应用与冻结候选同字节的source/test/workflow/Plan57后，只执行一次 `python -B -m unittest tests.test_checkpoint_json_fd tests.test_task_manifest tests.test_crash_restart -v`，保留真实argv/cwd/解释器/环境、起止UTC、stdout/stderr、退出码、timeout与执行前后源码/测试hash。预期48方法不是已测结果；任何失败/超时/超deadline应保留并暂停该分支，不自动重试或扩展测试。

随后本角色可在同一冻结范围、同一deadline内独立执行同一三模块一次，并复核实际代码/inputs/完整原始日志及限定结论。相邻测试及crash_restart实现补充hash已固定在核验元数据，后续执行应核对这些字节；候选或相关输入漂移不得拿本回执覆盖。只有适用检查通过才能接受usable-with-scope。不能以exit0或主控JSON代替独立代码与数据验收。

本revise是独立AI手工方案审查，不是ReviewSession认证、受保护DAG派发、真实宿主部署或用户发布许可。可信宿主认证接口缺口仍保留，不用本文件替代。全角色tokens/费用unknown。SYSTEM-99的真实宿主、完整输入/用量/最终质量、并发恢复、原有耗尽/受阻门禁与论文计数42保持原义；未测close/unlink失败、敌意FD/父路径、断电/全事务、线上发生率/耗尽、性能或模型质量，不保证整轮完成。
