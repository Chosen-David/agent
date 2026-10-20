# SYSTEM-99 阶段P独立方案复审

结论：**approve**。Version21已消除前次两项阻塞：15条summary成为逐目录确定输入，正式
查询与逐run查询参数也已冻结。本结论只批准按该版本实施和验收，不批准旧结果复用、自动
跳过验证、扩大集合或把阶段P算作SYSTEM-99整轮完成。

审核基线为 `6e125d5df8a7cd48ab33a6af70830a2456c05ac7`；复审时fresh fetch后本地HEAD与
`origin/main`一致。已重读项目规则、决策门禁、项目文档/结果复用与结果验收契约、SYSTEM-99
Version21及 `catalog-wave4-plan.md`。本文件是独立普通审核记录，不是受认证ReviewSession
回执。

## 独立复算与实跑

- 冻结15目录均存在且无 `record.json`；共347个Git已跟踪普通文件、3641161字节，最大文件
  432364字节，无符号链接、特殊文件或未跟踪文件。每目录3..44个文件，满足现有
  `register_history` 的1..64引用及单文件256 MiB限制。
- 排序目录名清单SHA256为
  `ee2c6faf0dde61b1101ebe5a5a64e5ee1aee9eb6f4ecf9b922149779c7ce56ed`；排序
  `path<TAB>sha256` 清单SHA256为
  `ea734d8c1b47b8350e86b5c07508a89087682ffe1c5a91cc7f3a9bb4397daeee`，均与方案一致。
- 当前252个结果目录中恰有27个缺record目录。225个既有record含1813条历史引用，未引用
  这347个候选文件；顶层目录名无大小写冲突，15项也没有既有record。
- 15条冻结summary逐项与包内状态/范围记录相符：incomplete、blocked、registration/preflight
  rejected、失败尝试、有限scope验收与publication blocked均未被改写成当前通过。所有新记录
  仍固定为 `historical-external-reference`、空context、null measured_at/contract及
  `unknown/proof=null`。
- 在隔离临时结果根按这15条精确summary实际调用当前 `ResultStore.register_history`。正式查询
  `historical result discovery validation unknown`、limit20/max_scan5000由
  `scanned=252, partial=true, errors=27` 变为 `scanned=252, partial=true, errors=12`；剩余
  error ID精确等于方案的12项排除集合。
- 临时根中15项完整run_id查询均找到自身，15项show合计精确347条引用；15项
  `decide_run(run_id,{})` 均为 `verify_delta/unknown/proof=null` 且
  `automatic_skip_authorized=false`。登记前后347个原件hash一致。重复登记被不可变ID门禁拒绝；
  坏hash被stale-artifact门禁拒绝且未生成目标record。

## 排除与恢复边界

排除12项可复现：3个knowledge目录、`math-singular-bilinear-20261008`和
`memory-index96-20261020`超过64文件；`comm-route-bind-integration-20261009`与
`result-time97`仅计划；`system99`仍活动；`comm20-20261009`含已登记子运行；
`math-linear-residual-20261008`三项失败原件已被v2 record引用；另两项为混合身份。
这避免用空壳record消除错误或重复包装。

现接口先校验全部引用，再以临时文件、fsync和硬链接作单record原子不可覆盖发布。方案又规定
中断续接只接受冻结summary/refs/unknown状态完全一致的记录，并在发布前fetch；若远端main偏离
基线则停止、重算并升级版本。因此局部写入不会被误当整批成功，并发漂移不能沿用旧清单。

## 七域结论

| 域 | 结论 |
|---|---|
| intent | pass：只补历史发现索引，不重新授信或宣称整轮完成。 |
| guide | pass：不写人类guide，不改runtime/schema/旧原件。 |
| assumptions | pass：集合、hash、summary、身份与接口边界均已确定并复算。 |
| prior results | pass：既有引用无冲突，排除已包装、活动、计划、父容器与混合目录。 |
| acceptance | pass：固定查询及隔离实跑复现27→12，逐run不授信与失败原子性可检。 |
| risk | pass：unknown/null字段、不可覆盖写入、漂移停写和中断续接约束成立。 |
| resources | pass：仅本地文件哈希、CPU登记副本与回归，不需模型/GPU/付费资源。 |

实施仍须按方案执行写前fresh fetch与全部重算、只新增15个record、完成定向/全库/Reader/同步
检查，并另做独立结果验收。任何集合、summary、查询响应、原件hash或远端基线漂移都使本批准
失效，须版本化返修后重新审核。
