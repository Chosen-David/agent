# SYSTEM-99 阶段P：JSON/状态型历史包登记方案

基线 `6e125d5df8a7cd48ab33a6af70830a2456c05ac7`。本阶段继续修复历史结果可发现性，
不修改 runtime/schema，不把旧结论重新授信，也不算 SYSTEM-99 整轮完成。

## 冻结集合

从阶段N剩余27个缺 `record.json` 的顶层目录中，只选择同时满足以下条件的历史包：

1. 整棵目录树含1..64个 Git 已跟踪普通文件，无符号链接、特殊文件或未跟踪文件；
2. 顶层存在可定位该包结果状态/范围的 JSON 或失败记录；
3. 不是活动目录、纯计划、已登记子运行的父容器、混合运行身份或已被后继记录包装的旧包；
4. 现有 `register_history` 足以冻结全部原件，不扩展引用上限或另造聚合格式。

得到15目录、347文件、3641161字节，最大单文件432364字节。排序目录名清单
SHA256为 `ee2c6faf0dde61b1101ebe5a5a64e5ee1aee9eb6f4ecf9b922149779c7ce56ed`；
排序 `path<TAB>sha256` 清单SHA256为
`ea734d8c1b47b8350e86b5c07508a89087682ffe1c5a91cc7f3a9bb4397daeee`：

```text
comm20-20261009-r01-attempt1
figure-review-binding-20261008
opt-inplace-20261012
token-010-maintenance-20261011
token-010-maintenance-cpu-20261011
token-010-maintenance-cpu-r2-20261011
token-fifty-01-20261012
token-hourly-repair-20261011
token-hourly-repair-r2-20261011
token-hourly-repair-r4-20261011
token-r6-close-20261014
token-r6-resume-20261014-1800
token-ten-1-20261011
token-ten-1-r2-20261011
token-ten-1-r3-20261011
```

两次独立只读分类均认可这15项。另一审阅者还建议纳入
`math-linear-residual-20261008`，但其失败尝试已被已登记的后继 `v2` record引用；本方案
保守排除，避免重复包装。另排除纯计划 `comm-route-bind-integration-20261009`、
`result-time97`，活动目录 `system99`，已登记子运行父容器 `comm20-20261009`，混合身份
`token-fifty-03-20261012`、`token-usage-unknown-20261011`，以及超过64文件的5个目录。

## 登记与摘要

每目录只调用现有 `ResultStore.register_history` 新增本目录 `record.json`：`run_id` 使用顶层
目录名，artifacts按路径排序绑定全部原文件；`context={}`、`measured_at=null`。summary冻结为：

```text
comm20-20261009-r01-attempt1: incomplete harness migration root mismatch; metrics not accepted
figure-review-binding-20261008: workflow/static contract verification only; no visual quality or runtime deployment
opt-inplace-20261012: OPT-INPLACE scoped workflow validation; historical review only
token-010-maintenance-20261011: blocked maintenance trace; T1 unfinished
token-010-maintenance-cpu-20261011: registration-rejected CPU maintenance attempt
token-010-maintenance-cpu-r2-20261011: registration-rejected CPU maintenance attempt
token-fifty-01-20261012: preflight-rejected advice discovery attempt; no paid call
token-hourly-repair-20261011: pending-failed-preflight hourly repair attempt
token-hourly-repair-r2-20261011: scoped hourly repair historical bundle
token-hourly-repair-r4-20261011: scoped hourly repair bundle reusing r2 native observations
token-r6-close-20261014: data-scoped-accepted-publication-blocked R6 evidence bundle
token-r6-resume-20261014-1800: usable-with-scope R6 metadata/publication follow-up
token-ten-1-20261011: preflight-review-rejected artifact-identity attempt
token-ten-1-r2-20261011: failed artifact-identity attempt; zero accepted successes
token-ten-1-r3-20261011: invalid-transport artifact-identity attempt; zero accepted successes
```

这些字符串只转述各包状态/范围，不构成当前验收。`token-010-maintenance-cpu*` 和
`token-ten-1*` 内部重复producer ID仅是原始历史，不能替代顶层目录身份。

所有record必须保持 `historical-external-reference`、`contract=null`、validation
`unknown/proof=null` 和既有 trust note。347个原文件、旧record、guide、runtime/schema均不改。

## 实施与验收

写入前再次fetch并重算集合、身份冲突、跟踪/文件类型、数量、两项清单hash和原文件blob；
任一漂移停止。中断续接只接受与冻结summary/refs/unknown状态完全相同的既有record，绝不覆盖。

登记前后的统一正式查询固定为：

```text
python scripts/result_store.py --root "$PWD" search \
  'historical result discovery validation unknown' --limit 20 --max-scan 5000
```

逐run查询固定为同一CLI，以完整顶层目录名为query，`--limit 20 --max-scan 5000`；逐run
`show`/`decide_run` 使用完整顶层目录名和空context。登记后要求：

- 缺record错误由27降为12，`partial=true` 和剩余错误继续可见；
- 15个 `show` 覆盖精确347个引用，run-id查询均可发现自身；
- 15个 `decide_run(run_id,{})` 均为 `verify_delta/unknown/proof=null`，共享verifier调用0；
- 重复登记与坏hash在临时副本拒绝且不产生部分record；
- 原件清单登记前后相同，定向ResultStore、全库、Reader与同步检查通过，再做独立结果验收。

剩余12目录仍显式open：5个超过64文件的包需分片/身份设计，2个纯计划、1个活动目录、
1个父容器、1个后继已包装失败包和2个混合身份包。真实宿主、多轮任务质量、usage/费用及
其它artifact快照边界也不在本阶段；不声称模型质量、token、性能或成本收益。

发布前再次fetch；若 `origin/main` 不再等于基线，停止写入/发布，基于新main重算集合、清单和
查询基线并升级SYSTEM-99与本方案版本，不能把旧冻结结果重放到新树。
