# SYSTEM-99 阶段M：历史结果登记第二批方案

基线 `49bd76036097966a30014898576598c99a5e946a`。这是同一 SYSTEM-99 的
可恢复阶段，不是新任务或完成一轮；只恢复历史材料的有界发现入口，不授信旧结论。

## 选择规则与固定集合

从 `agent_doc/results/` 当前81个缺 `record.json` 的顶层目录中，机械选择同时满足：

1. 顶层叶目录，没有非缓存子目录；
2. 本层按 `report.md`、`report_by_gpt.md`、`report.json`、`README.md` 优先级存在
   至少一个直接报告；
3. 本层有1..64个普通、非符号链接、Git已跟踪文件；
4. 所有原件单文件不超过现有 `register_history` 的256 MiB限制。

得到43目录、618文件、6108516字节；最大文件207364字节，无符号链接或未跟踪
文件。按目录名排序、换行连接并补末尾换行的SHA256为
`d81fad885eadd022fa3e7243db383eaab98f0af4f91e56cf86273b28f8b3dbc5`：

```text
artifact-bound-20261012-2221
artifact-equality-20261012
artifact-fd77
artifact-localized-20261012
artifact-read76
artifact-unique-splice-20261012
causal-orchestration-20261008
check-helper85
communication-ledger-20261009
concise98
contamination-20261011
contamination-integrated-20261011
contamination-release-20261011
content-copy60
context-metadata35
context-schema83
dag-cycle-20261013-1601
dag-membership-20261013-0659
ingest-scope58
knowledge-fence-20261014-0705
knowledge-mirror-repair-20261012-1856
mailbox-pagination-20261011
math-burst-service-20261009
math-completion-packet-20261009
math-condensation-residual-20261010
math-conditioning-20261008
math-coupling-repair-20261010-v2
math-factor-certificate-20261010
math-gibbs-menu-20261010
math-input-policy-20261010
math-mass-box-20261009
math-singular-condensation-20261010
math-softmax-merge-20261010
math-structured-subspace-20261010
math-support-feasibility-20261010
paper-skill-links-20261009
prompt-read67
prompt-scan69
read-boundary56
readme-20261008
result-search-invariant-20261014-0304
search93
validation-fd87
```

其余38目录明确不在本阶段：18个含嵌套报告、15个无上述直接报告、5个超过
64文件。它们继续显示为检索错误并待逐类处理；不能自动选择部分文件或写空壳记录。

618项按相对路径排序、每行写作 `path<TAB>sha256` 并补末尾换行的清单SHA256为
`a11c31a0d039645ff711e13b61a75576693b85285a2f2ab2ae9db4a9c6b9c3d4`；全部原件须与
基线 `49bd76036097966a30014898576598c99a5e946a` 的对应blob逐字节一致。该清单哈希与
目录名哈希共同冻结输入，不能只凭文件数或当前工作树重算结果接受漂移。

## 登记变换

每个选中目录只新增同目录 `record.json`，调用现有
`ResultStore.register_history`。参数固定为：

- `run_id` 等于目录名；
- `summary` 仅为 `run_id + 报告首个H1`；
  若首选为JSON或没有非空H1，本阶段停止该目录，不从正文猜摘要；
- `artifacts` 为登记前该目录全部原文件，按相对路径排序的精确path/SHA256；
- `context={}`、`measured_at=None`。

程序生成的record必须保持 `origin=historical-external-reference`、`contract=null`、
`validation_at_registration.status=unknown`、`proof=null`。报告中可能出现pass、fail、
blocked或性能数据，全部只是被引用的历史内容；摘要和record不得把它升级成当前验收。
不把 `historical/result/discovery/validation/unknown` 等公共治理词批量写进可检索summary；
信任限制由上述结构字段、`applicability=unchecked`及程序固定 `trust_note` 表达。
不改618个原文件、源码、schema、guide、TASK索引或旧record。

## 实施与验收

1. 独立审核本方案及Version16后才写入。写前fetch并一次性重算选择集合、跟踪状态、
   文件类型/大小、目录无record、全部原件hash、H1 summary和预期record大小；任何并发
   变化停止整批并重新审查，不覆盖现有record。`register_history`逐record原子但43条不是
   批量原子；中断续接仅接受字段、summary、refs、空context/measured_at、unknown状态及
   冻结输入完全一致的已生成record，再继续剩余目录。任一既有record不同即停止整批；
   Git提交前必须恰有43个新record，不能发布部分集。
2. 保存写前正式查询：`historical result discovery validation unknown`，
   `limit=20/max_scan=5000`。写后同条件重跑；扫描目录数不变，缺record错误应由81降为38，
   但partial、剩余错误和候选截断继续如实返回。
3. 对43个record逐一 `show`，核对run/summary/ref集合及每个原件当前hash；登记前后618
   原文件总哈希清单逐字节相同。对每个run_id执行正式search并确认自身可发现；另以若干
   H1特征词查询，确认题名可检索且没有公共治理词制造的43条同分污染。重复登记在临时复制
   或单个受控调用中拒绝，不能覆盖。
4. 全部43个执行 `decide_run(run_id,{})`；均须为 `verify_delta/unknown/proof=null`、
   `automatic_skip_authorized=false`，传入同一verifier spy的总调用次数必须为0。另人工抽取
   一个旧通过报告、一个旧失败/blocked报告和一个数学候选，核对summary没有改写原状态。
5. 定向ResultStore测试、全库、Reader和同步检查通过后再独立验收。测试数量、错误数下降
   或旧报告指标都不是模型质量、token、任务总时延或当前科学正确性收益。

本阶段只消除结构清晰的一批检索盲点。它不解决嵌套run身份、超64文件的清单分片、
无报告目录的语义分型、真实宿主/多轮质量、模型usage/费用或其它artifact快照边界。
