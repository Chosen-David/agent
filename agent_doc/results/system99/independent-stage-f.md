# SYSTEM-99 阶段F独立结果验收

状态：**按用户切换TwoLevel请求，阶段F已暂停，本文仅为未发布检查点。最新v5最终全库v3未读、pending，未作最终结果接受。** 下述首个候选在实际本地CPU范围内曾获得 `usable-with-scope`；主控随后补充v5白名单对称负控与query空白校验，不将首候选结论静默移植到新字节。双生产者中央登记/独立算术gate/原输入冻结/重启/拒绝变化及日志失败围栏已完成的独立检查保留。该记录不是实际多模型宿主认证、部署、性能或SYSTEM-99整批完成证明。

## 版本、写入归属与先查

基线HEAD：`789697f2b3e2e190a6954248d4b18cbbe0b44a4d`。Plan6审核已由本角色在 `search-review.md` 记录；本次是独立结果验收，不重新批准目标。主控持有锁及源码/TASK单写权；本角色只新增本文，未改源码、测试、TASK、guide、search-review或旧证据。所有测试输出只在其自有临时fixture内，未启动模型、GPU、收费、未知作业或生产监督服务。

最终逐字节核对：

| 对象 | SHA-256 |
| --- | --- |
| `agent_runtime/task_manifest.py` | `17e78440043377628be54e371070e603e0ae4b4c2206aff97ca30acc318ecbe8` |
| `tests/test_prior_search_drift.py` | `b1280526c9ae8ab7581ce0fe231d87881ecbd8e3fca750cc463830ffe980d8cb` |
| `agent_doc/task/task_details/SYSTEM-99.md` Version6 | `b639ade3b4135ef68c4b5c6a33e68f03c7c20b578b869aa3ea74d1a2b4e457af` |
| `agent_doc/results/system99/research-d.md` | `0edbe5df53a958cdd3c019fe0c935d0d526f89ad240bf9621558f8dd11547f29` |

先查实际调用 `ResultStore('.').search('prior_result_search scanned drift', limit=5, max_scan=5000)`：scanned252、errors81、partial=false、status=incomplete、无候选；这不证明没有旧文本或可复用数据。本角色已经独立见证before-v3的8方法2fail/6pass/0error；旧分析与CPU红证可支持问题定位，不能替代新代码验收。

## 全文代码/测试审查与实际行为

完整阅读生产diff及最终13个测试方法。生产改动仅增加私有比较器、替换保护producer/reuse的全响应比较，并在纯扫描差异时写分类journal；没有修改prepare、ResultStore返回、缓存、plan SHA规则、派发task、reviewer调用、授权、独立结果验收或注册逻辑。

比较器先保留原结构相等且标准JSON相同的same路径；新增例外只对两端完整9键v1/lexical、无errors/partial、默认扫描范围、合法顶层与hit类型进行分类。除scanned外的标准JSON必须完全相等，hit记录哈希/分数/列表顺序不会被归一化。same路径也用JSON拒绝bool/int/float宽相等，并保留原结构比较拒绝tuple/list和数字/字符串键的编码碰撞。相同旧格式仍走原same兼容，不因此获得新的scan-only许可。helper是派发比较器，不是取代ResultStore的所有语义/内容验收。

| 验收点 | 本轮直接证据 | 结果 |
| --- | --- | --- |
| alpha→独立gate→beta→独立gate | 真执行两份冻结CPU代码，分别中央manifest/raw/output/record；producer调用顺序恰为alpha/beta且各一次；两个gate done并有独立算术/代码/数据检查。 | 通过；不是仅根据producer自报pass。 |
| 完整输入冻结 | 正向断言两次handler收到的整个task等于Store内原冻结任务；persisted plan全对象、plan_sha256和receipt均未变化。 | 通过；未静默刷新搜索输入。 |
| 观察与审查分离 | beta活搜索scanned1，原任务仍scanned0；原完整prior_result_search journal保留，另分类journal准确记0→1。 | 通过。 |
| 重启与审查次数 | 重开Engine后beta正常执行，收到旧搜索；活查询重新journal，host.requests仍为1。 | 通过；不自动重审核，不冒充真实宿主模型调用。 |
| 候选/缺口/未知/类型变化 | 新相关登记、新无record目录、partial、unknown、bool/负计数均独立fixture实际查询并阻塞beta；边界表覆盖hash/score/order、候选增删、missing/extra字段、schema/query/strategy/authority/status、计数范围、非有限值等。 | 通过；未为了流水线忽略新信息。 |
| 显式复现/新主张 | 两个真实producer任务均有explicit_reproduction/new_claim，仍分别执行与验收，没有转入复用。 | 通过于本有限合成范围。 |
| 分类日志失败 | 强制Store.log在分类事件抛OSError，beta在底层handler前blocked；恢复日志并重开Engine后仍blocked，只有alpha调用。 | 通过；不自动重放、不吞异常放行。 |

测试中独立算术控制器与生产者不同owner，实际重新检查执行代码、边界及数据；这属于可信CPU测试宿主程序契约，不是与生产模型实际隔离的调用认证证据。应用声明依赖、最终检查与外部动作非原子等既有限制没有被此修复消除。

## 实际独立命令与计数

最终候选实际执行：

```bash
PYTHONPATH=tests PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_prior_search_drift tests.test_plan_review tests.test_plan_review_independent tests.test_result_store tests.test_result_validation tests.test_task_manifest -q
PYTHONDONTWRITEBYTECODE=1 python -O -m unittest tests.test_prior_search_drift -q
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s apps/paper-reader/tests -v
PYTHONDONTWRITEBYTECODE=1 python scripts/sync_plugin_references.py --check
git diff --check
```

依次138/138通过（11.234s）、优化模式13/13通过（4.627s）、Reader app3/3通过（1.620s）、同步exit0且无输出、diff检查通过。138包括新增13与相关计划审核/结果/项目文档链，非全库。首次组合命令未设PYTHONPATH，`tests.test_result_store`中旧式`from test_result_validation`产生1个加载error，其余117项通过；修正调用路径后全138通过。该加载错误不归为生产回归，也未隐去。初始生产候选的138及-O13也曾通过，但最终结论只绑定上表最终哈希。

额外独立same快路探针（非测试表自报）：调用比较器核对`{'v':[]}`/`{'v':()}`、`{'v':{'1':'a'}}`/`{'v':{1:'a'}}`、`{'v':True}`/`{'v':1}`、`{'v':1}`/`{'v':1.0}`，四组均None；完全相同future格式仍same。实际断言通过。

独立红对照没有改工作树文件：`subprocess.check_output(['git','show','789697f2b3e2e190a6954248d4b18cbbe0b44a4d:agent_runtime/task_manifest.py'])`读取原模块，SHA `b9ec8f8881e26265fec368570bfb2b9fde2aed01ae6643ee0dab7f4543cd0e41`，在私有临时内存module编译，仅将当前进程的`ReportingHandler.run`替换为原函数。现有helper保留用于新版test import，但原run不调用helper；其余测试条件没有改。仅跑新版两个正向/重启方法，2fail/0error，均`'blocked' != 'done'`。这是精确旧wrapper函数的差异判别，不是声称全仓切回旧版本；进程退出后补丁消失。此前冻结8方法before-v3才是完整旧生产源码的原始红证。

## 失败记录与候选版本不可混同

- `drift-before-v3.log` SHA `f0654e4be7dad59c387cea9a5aeb0b0a343eda24dbb9b69cf35b00eb6e6c1d4d`：旧源8方法，2业务断言失败、6通过。原更早canonical布局错误仍保留，不作此红证。
- `drift-after-v2.log` SHA `1effbbd1e940b56ed0ce50d6d5d5b207ddc7cf495d259fe848823f36fcd6660d`：13方法中测试误从Engine.tick的state取plan而KeyError；已核对日志。修正为Store.snapshot是fixture取数修正，不是生产wrapper变更或把错误当作成功。
- `drift-after-v3.log` SHA `a7206fa408238be35efded335098504f556ac3e9e988d56aab38e1a05bd235fd`：13通过，属于同计划前一生产候选；其JSON-only same快路还未补结构比较。
- 最终`drift-after-v4.log` SHA `98906060a49189b91cc1ddd7236a15f953da86ffd7ebe932775b5a01feb4a7c2`：13通过，绑定最终结构比较修正。
- `full-f.log`的1390/8skip属于前一生产候选，不能拿来声称最终源全库通过。最终`full-f-v2.log`须独立核算终结状态。主控根Reader/Memory4方法与Reader app3方法也分别标识，不能互称全套。

## research-d核对与范围限制

已完整读research-d笔记，实际核对原PDF SHA `71c547d4aa0d49b82d0669abeffd718ed451f40e743ff990257325373cbb6e3e`、本地表1原页PNG，以及正文表1上下文、E范围/假设与F持续更新对应原文。0/30→30/30是**固定S-Bus验证器、补继承版本**的消融；PlanFence自身该表是29/30且初始化失败保留分母，笔记没有混为30/30。30例live和F的持续相关/无关更改结论有对应原文，语义正确/授权/动作原子性限制明确。计时研究排除generation，不是完整请求提速。

笔记明确只报告§1–7及E/F、表1原页核对，不宣称其它附录/图完整审读或代码复现；本验收也仅上述原文点核对，不把我核对部分原文写成全篇重读或证明所有阅读事件。作者的30例成绩和论文阅读计数不充当本库模型收益、可部署性或整批完成证据。阶段F仅adapt“冻结输入与活观察分离”，未引入论文服务/默认自动重规划。

## 验收意见与未完成范围

`blocking_findings=[]`。在冻结最终版本、本地CPU和声明输入的范围内接受本修复；计划回执、授权和独立数据gate仍独立生效。未知/错误/截断引发的阻塞是保留设计，不是本次承诺解决的并发问题。无真实多模型宿主/生产安装/任务质量/费用或速度结论，SYSTEM-99仍有其它未完成分支；阶段性验收或发布不能算整轮完成。

## 最终全库/主控报告核算（同一最终哈希）

最终 `full-f-v2.log` 已终结。独立读取全部日志并按每条test outcome行核算：1390条=1382个ok+8个skipped，0 FAIL/ERROR；末尾`Ran 1390 tests in 108.201s; OK (skipped=8)`一致。7项图形依赖/字体跳过和1项真实tmux opt-in跳过均保留，不算通过。没有独立重跑全库，以下是主控实际日志的独立核算，不能与本角色直接执行138项混称。

| 主控最终日志 | 核对结果 | SHA-256 |
| --- | --- | --- |
| `full-f-v2.log` | 1390总数、1382通过、8跳过 | `31f344b298dd4504a2cbfc5640fec214f4a145b7776f029f3e7060576c36d25b` |
| `focused-f-v2.log` | 105项通过，12.454s | `7f889ef636e6c2205445d4f6bc07a7c86bd800c29e41a3aa4913042eb2417fe5` |
| `optimized-f-v2.log` | -O13项通过，4.758s | `b4ccf51bb2d27835f5da76eab2beb312311920b096de904208c29889eacbef72` |
| `reader-f-v2.log` | 根Reader/Memory4项，0.491s | `0fc6db23b9be6bf447461673a6d145d2cf557384a89a08e3d555790b3364b588` |
| `reader-app-f.log` | Reader app3项，1.607s | `174210d8a3affaa600575ec8ba360d8bf90a4029c34af0b9efb3ba65b2b0391d` |

同步silent日志 `sync-f.log` 为标准空文件哈希 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`；空日志本身不证明exit0，但本角色已独立执行同命令并读回exit0。

完整阅读主控 `stage-f.md`（核对时SHA `3326ab858ed7207b9e2577b055cda98edd14a572a4f4f0837273acb60e7e5359`），其红绿版本区分、最终哈希、边界和未完成项与本轮证据一致。另核对既有算术fixture SHA `79e3840fe6b39432526e4c75fcf98f9c6bf2a3aa410e58d2d281550902482377`，样本`n=[0,1,2,7,19]`、repeats3、seed0、dimensionless及闭式验证描述准确。“两个producer各一次”指受管producer handler派发次数；setUp的`make_fixture`也会运行准备用CPU代码，不能将handler计数解释为整个测试进程只执行过两次code.py。

上述v4/full-v2核对时源码/test/Plan SHA与当时表一致，`git diff --check`通过。本段描述该候选，不代表之后新字节。其CPU范围结论为 `usable-with-scope; blocking_findings=[]`，不能关闭SYSTEM-99未完成的真实宿主/任务质量等验收。

## v5候选增量复核：对称畸形元数据/空白query

主控在前候选核算期间继续修正：源码仅将query合法性补为非空白（`not search['query'].strip()`），并保留原长度限制；测试增加第14方法，令两端partial/error/unknown/schema/strategy/query/authority、畸形hits及无效计数相同、只scanned不同，直接证明白名单在门禁路径生效，而不是仅凭其它字段不等阻塞。已完整读取新增方法及源码差异；此修改在Plan6范围内，无新权限/语义放宽。前述全库v2不能自动覆盖新版本。

当前核对源码SHA `b9bef1029d9aa1b5b0d83c793c0f676b05ccdacc20a21be948f1cccaefcf1729`，test SHA `4778fc87b0c0e279f729b866ef2c34a33befc8de39c207089da0b906d69bed7b`，Plan6不变。相同组合命令独立实际运行139/139通过（12.711s）；优化模式14/14通过（8.403s）。尚未将旧全库1390项的通过声明成v5验收；主控最终全库v3终结核算待追加。

### 暂停交接

收到主控传达的最新用户切换请求后立即停止阶段F实质工作，不发布，不再运行检查或读取未见的最终日志。`full-f-v3`的进度、终态与内容本角色均未核对，明确pending。恢复时须重新核对当前授权、源码/test/Plan哈希、实际运行/副作用及主控保存的resume检查点，再核算最终候选全库日志、补验最终Reader/同步（按新候选绑定）与主控stage-f事实版本；不得仅用本文旧候选通过数标最终完成。已完成的139项及-O14项仅绑定上述v5已读字节，不覆盖后续变更。没有删除或覆盖历史证据。
