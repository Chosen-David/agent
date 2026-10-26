# CONTEXT-WIRE-01：五个CLI的实际输出边界

SYSTEM-99同批；基线80c4a368。原地修复source/advice/grid/artifact/dispatch_context，复用context_serialization；没有并存旧/快版生产实现。
成功输出固定UTF-8；最终JSON格式、派发父配置/内层转义和原生终止换行均计入显示字符预算。
超预算exit2、stderr JSON、空stdout，不截断成功包；source/artifact/dispatch原输入数据错误仍exit1/stdout。
原文、取消/异议、完整声明依赖、父config/reasoning/approval/sandbox与readonly派发范围不改变；派发入口仍只生成计划。
artifact先为原生换行预留字符再选择codec，避免错误拒绝原本可容纳的完整表示；可选token counter API仍计其原JSON包，不改成真实provider usage。
共享helper默认1M显示字符上限不变，artifact显式保留原16MiB预算数值范围；字节/字符/token与读取/分配上限不是同一单位。
artifact两处预算异常改成ContextBudgetError(ValueError子类)，其余API选择/字段、错误文案及数据失败协议保留。

## 固定回归与失败保留

- 原生产源码、新fixture v2：baseline.log/json，7方法，21失败/14错误；其中包括新helper参数缺失和fixture问题，不能全部称生产缺陷。
- 首轮修后：result-v1.log/json，119方法1失败/2错误；两错误为fixture误读dispatch顶层root，旧预算测试与新协议冲突导致另1失败。原件未改。
- 独立静态复核plan-review-v3接受精确oracle修正：dispatch完整params/内层project_root仍严格核对；旧预算断言改为exit2/空stdout/stderr JSON并补只读。
- 最终主控固定suite：result.log/json，119方法通过、无skip、未超120秒。主控3/3调用已用完，不追加重跑。
- 可复现入口：`python -B agent_doc/results/context-wire-20261026/run_checks.py`。实际命令/解释器/平台/源码hash见各JSON，已冻结fixture-v2.py用于原失败重放。

真实子进程核对cp936终端下UTF-8、原生换行、实际stdout恰好预算成功/少1字符拒绝；成功与拒绝均验证输入字节不变。
还核对五类完整内容/恢复、受控counter、默认/显式helper硬界、artifact超过1M合法包、原数据错误协议和direct-main Popen拒绝调用。
有限mock及静态无RPC路径不证明未知宿主所有API零调用。独立代码/原始输出复核与唯一一次同suite见result-review.md和independent.log/json，不用本报告自评代替。

## 发布与范围

plan-v1/v2/v3/v4及所有审核意见保留。v4只在现有portable-install四组矩阵增加新wire测试步骤；固定actions/read权限/10分钟job上限不变。
发布后CI状态另行读取，本文不预先声称原生Windows通过；已有安装范围也不覆盖完整库或实际模型任务链。
本次未运行旧全库/PID/ALIAS/role/Codex受阻分支，旧预算和失败不重置；原生PID身份前提、遗失候选、真实加载/所有actor usage/任务质量继续open。
本地日志耗时只用于超时审计；基线7方法与修后119方法不可作速度对照，无性能/任务质量普遍收益主张。
同批十篇新正文记录见coordination-code-reading-20261026/inputs.json；本次补读SWE-agent v3 A.2不再计新篇。
