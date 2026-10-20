# SYSTEM-99 阶段P独立结果验收

结论：**usable-with-scope**。只接受15个历史目录的可发现登记、347个原件的完整哈希绑定，
以及这些登记继续保持不授信；不接受历史失败/通过状态复用、自动跳过验证、模型质量/性能/成本
收益或SYSTEM-99整轮完成。

在基线 `6e125d5df8a7cd48ab33a6af70830a2456c05ac7` 上独立复算得到15个record、347个
Git已跟踪普通原文件、3641161字节，最大单文件432364字节。347个工作树原件逐一与HEAD blob
相同；排序目录名和 `path<TAB>sha256` 清单SHA256分别为
`ee2c6faf0dde61b1101ebe5a5a64e5ee1aee9eb6f4ecf9b922149779c7ce56ed`、
`ea734d8c1b47b8350e86b5c07508a89087682ffe1c5a91cc7f3a9bb4397daeee`。15个record共
73400字节，排序记录清单SHA256为
`c43fb659e3c08f78ec8e9ea263ce3a05c72faf914d6e795c2b9e956fbb3a4eb0`。

逐条检查确认schema、顶层目录run_id、方案冻结summary、origin、空context、null
measured_at/contract、trust note和 `unknown/proof=null` 均精确符合方案。每个record的引用集合
恰好覆盖本目录除record外的全部原件，347个当前文件哈希全部与引用相符，没有遗漏、重复或越界
引用。原包中的blocked、registration/preflight rejected、failed、zero-success、有限scope及
publication-blocked语义仍在summary或绑定原件中：例如维护包仍有T1 unfinished，两个CPU包仍为
registration-rejected，三个token-ten尝试仍是review rejection/assertion failure/invalid
transport，R6 close仍是data-scoped accepted但publication blocked。即使旧包内部出现
usable-with-scope，当前登记仍统一unknown，未获当前信任。

## 发现性与不授信

在隔离临时根移除这15条record后独立重建正式查询，得到252目录、225个既有record、
`scanned=252, partial=true, errors=27`；15项候选全部在错误中，另外12项恰为方案排除集合。
当前真实树同一查询独立得到 `scanned=252, partial=true, errors=12`，新输出与主控保存的after
文件逐字节相同，SHA256为
`f985ec317c8facc55c1d6b53e9793f11cc1b6d996a9a17a34be8867f7894a5bf`。保存的before文件为
27项错误，SHA256
`f6121fb371052ba351758411bb75c852571553f81fc7e2dddacace95fe320f8b`；因此27→12不是用
`partial=false`或吞掉错误伪造的完整发现。

15次show合计347 refs，15次完整run-id search均找到自身。向15次
`decide_run(run_id,{})` 注入共享失败即报错的verifier，结果仍全部为
`verify_delta/unknown/proof=null/automatic_skip_authorized=false`，verifier调用数为0。

剩余12项在正式查询中逐项显式可见：5个超过64文件的目录、两个纯计划、活动目录system99、
含已登记子运行的父容器comm20、已由v2 record引用的math-linear失败包，以及两个混合身份包。
独立计数还确认5个大目录分别有118、98、78、72、113个Git已跟踪文件；两个纯计划目录各只有
两份计划/契约材料，math-linear原件确由 `math-linear-residual-20261008-v2` 引用。

## 回归与日志核验

独立实际运行：

```text
ResultStore + reuse acceptance: 46/46 passed
paper-reader: 3/3 passed
sync_plugin_references.py --check: exit 0, empty output
git diff --check: exit 0
```

主控全库日志SHA256
`1d3e1c292cf895901cb6128664e35bcb884398bbb9b8dc7ad4350dfd9782d310`，逐行核算为
1398个ok、8个skipped，尾部为 `Ran 1406 tests in 95.948s; OK (skipped=8)`；Reader与同步日志
SHA256分别为
`7cc45cb39e168c6dd7df981f26c830168f123f7345f16a7b131c90c07de49e4d`、
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。本验收没有把全库
日志核算称为第二次独立全库重跑。

阶段报告对两次主控验收脚本错误的说明准确：独立复现未设 `PYTHONPATH=tests` 时
`test_result_store` 因找不到 `test_result_validation` 而失败，补齐后46项通过；record顶层确实
不存在 `stored_validation`，直接读取会KeyError，实际字段为
`validation_at_registration.status=unknown`。这些失败已显式保留为验收工具调用/字段假设错误，
没有被改写成产品测试通过，也不改变上述有限结论。

边界仍包括真实宿主、多轮任务质量、usage/费用、其它artifact全局快照及12个未登记目录。本回执
是普通独立结果审查，不是受认证ReviewSession或可复用结果证明。
