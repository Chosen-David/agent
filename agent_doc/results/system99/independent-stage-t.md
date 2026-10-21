# SYSTEM-99 阶段 T 独立结果验收

结论：**blocked / revise**。默认预算与选择范围的修复本身可复现，但候选仍把文档尾部冒充时间上的
“较新进度”；仓库当前主任务采用新记录置顶，真实默认输出因此给出旧 Stage N 而非当前 Stage T。
这直接冲突于导航用于判断“当前到哪一步、下一步由谁继续”的声明，不能以 usable-with-scope 发布。

## 独立复现

冻结基线 `origin/main=1cf7258f572a9fb3ab7b6e8e967eabde93cd20eb` 由 `git archive` 解出；再以
基线模块读取候选仓库同一绝对根，避免项目根长度改变字符计数：

```text
baseline default: rc=2, DocumentError: task navigation exceeds character budget
baseline full, progress_tail_chars=1: compact JSON 80369 chars
```

候选真实入口：

```text
candidate default: rc=0, compact JSON 11792 chars
selection=unchecked total=317 selected=34 omitted_checked=283 tasks=34
checked task present=false
candidate --include-checked at default budget: rc=2
candidate --include-checked --max-chars 200000 --progress-tail-chars 1:
selection=all total=317 selected=317 omitted=0 tasks=317
```

`python -m unittest tests.test_task_navigation -v` 与 `python -O -m unittest ...` 各14项通过；
`scripts/sync_plugin_references.py --check`、runtime/插件脚本逐字节比较、
`git -c core.whitespace=cr-at-eol diff --check`通过。主控全库日志
`d48671fdb4eb9690a28e414f85993228f193403f11a7e701495cbfeafe1ea591`记录1499项、8跳过；
Reader日志`a644317e288bdfa877d208b98a0e9139f14b5d57e0b638ddfa9de52b9c771d69`记录3项通过。
本审核未独立重跑全库，只独立重跑了普通/`-O`专项与真实CLI。

测试已覆盖默认先过滤已勾选坏详情、显式全量再拒绝身份错配、60项规模、零未勾选、bool/int、
身份与预算；代码也确实在打开详情前从 canonical index 筛选。文档正确区分未勾选与受管 active，
显式披露省略、完整审计和非 token/质量范围，SYSTEM-99仍 open。

## 阻断反例

候选自身 `agent_doc/task/task_details/SYSTEM-99.md` 的 `## Progress` 当前以 Version28 Stage T 开头，
文档尾部仍是较早 Stage N。默认导航对 SYSTEM-99 实际返回：

```text
…(earlier progress omitted)…
-with-scope；独审另跑80项
定向测试。27个未登记目录、真实宿主/多轮质量、usage/费用及其它artifact快照仍open，整批
继续未完成。
```

`_progress_tail` 的标记“earlier progress omitted”在此恰好相反：被省略的是更新的 Stage T/O/...，
留下的是旧 Stage N。当前317份详情中 `### 摘要` 为0份、`Status`为0份、`Owner`仅1份；因此对主要
未决任务，旧尾部不是可由其它派生字段纠正的次要噪声，而可能成为唯一进度提示。新增测试只验证
字符截断，没有覆盖置顶/追加混用和“下一步”语义。

## 必须返修

先版本化定义可验证的进度顺序/结构，再使摘要不把文件位置推断成时间：例如统一并验证 append-only，
或在同一固定预算内显式返回无时间承诺的首/尾边界并要求调用方在顺序未知时打开详情全文。至少必须：

1. 去掉或修正 `earlier progress omitted` 的错误时间语义；
2. 文档不得再声称单一尾部可判断当前/下一步，除非格式提供并验证顺序；
3. 固定真实“新记录置顶”和“尾部追加”两种回归，确保任一模式都不把旧记录标成当前状态；
4. 返修后重跑真实317项预算、普通/`-O`专项、同步、全库/Reader，并重新独立验收。

在此之前，11792字符、34/283选择与全量开关只证明传输边界恢复，不证明导航语义可安全消费；
不得推送本候选，也不得宣称 token、任务质量或 SYSTEM-99 整轮完成。
