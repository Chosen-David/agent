# SYSTEM-99 阶段N：单一顶层报告目录登记方案

基线 `4240287294ee7c90fc675902c7af5fc40a0a9cef`。这是同一 SYSTEM-99 的
可恢复阶段，不是新任务或整轮完成；只恢复一组历史材料的检索入口，不授信旧结论。

## 固定集合与边界

从阶段M剩余38个缺 `record.json` 的顶层目录中，机械选择同时满足：

1. 顶层按 `report.md`、`report_by_gpt.md`、`README.md` 优先级存在一个直接报告；
2. 子目录中没有 `report.md`、`report_by_gpt.md`、`report.json` 或 `README.md`，也没有
   `contract.json`/`manifest.json` 声明与顶层目录不同的 `run_id` 或 `result_id`，避免把
   独立子运行压进父记录；同一run的候选、复核、快照和附件仍可引用；
3. 整棵目录树有1..64个普通、非符号链接、Git已跟踪文件；
4. 报告有非空首个H1，且所有原件不超过现有 `register_history` 的256 MiB限制。

得到11目录、358文件、3349153字节；最大文件105432字节，无符号链接或未跟踪文件。
按目录名排序、换行连接并补末尾换行的SHA256为
`4b9183b865b80a59978819cb20b7abc6733de18dcb1cd4619ed8b374bbbe7c11`：

```text
concept-teaching-20261010
math-allocation-20261008
math-coupling-repair-20261010
math-geometry-20261007
math-propagation-20261008
math-rope-intertwiner-20261008
math-sequence-tv-20261008
math-softmax-kl-20261008
math-weighted-bilinear-20261007
project-doc-scope-20261008
token-001-20261009
```

358项按相对路径排序、每行写作 `path<TAB>sha256` 并补末尾换行的清单SHA256为
`cd94f4498658227686e55ce913690ea40dd8e5b6e10e3274782aa3203a2fc370`。全部原件须与
基线对应blob逐字节一致。子目录只作为同一顶层报告的候选、复核、快照或附件被引用；
本阶段不为子目录推断run身份。

不纳入仅有 `report.json` 的5个目录，因为其中4个只给 `run_id`，另一个是维护状态，
没有可作摘要的权威题名；也不纳入带嵌套报告、超过64文件或没有顶层报告的目录。
`comm20-20261009/final-integration` 明确声明已另行登记的
`comm20-20261009-final-integration`，所以父目录即使有顶层报告也排除。
活动中的 `system99` 证据目录不是一个已完成run，不能用自身阶段文档生成结果记录。

## 登记变换

每个目录只新增同目录 `record.json`，调用现有 `ResultStore.register_history`：

- `run_id` 等于顶层目录名；
- `summary` 严格为 `run_id + ": " + 顶层报告首个H1`；
- `artifacts` 为登记前整棵目录树的全部原文件，按相对路径排序并绑定SHA256；
- `context={}`、`measured_at=None`。

生成记录必须保持 `origin=historical-external-reference`、`contract=null`、validation
`unknown/proof=null`。报告内的pass、fail、性能或科学结论只是历史材料；特别是
`math-coupling-repair-20261010` 的“未通过验收”和 `token-001-20261009` 的“无效”
必须原样保留在题名中，不改写状态。不得修改358个原文件、runtime/schema、guide、旧record
或TASK索引。

## 实施与验收

1. 独立审核本方案与SYSTEM-99 Version18后才写入。写前fetch并一次性重算集合、跟踪状态、
   文件类型/大小、无嵌套报告、H1、原件hash及预期record大小；任何漂移停止整批。
   中断续接仅接受与冻结输入、summary、refs和unknown状态完全一致的已生成record；任一冲突
   停止，不覆盖。提交前必须恰有11个新record。
2. 保留写前正式查询 `historical result discovery validation unknown` 的
   `limit=20/max_scan=5000` 结果。写后同条件扫描目录数仍为252，缺record错误应由38降为27；
   `partial`、候选截断和剩余错误继续可见。
3. 逐条 `show` 核对run/summary/ref集合及当前hash；358原文件登记前后清单必须相同。
   每个run-id正式search须找到自身，并抽查失败题名、中文题名和项目文档题名可检索。
4. 全部11个 `decide_run(run_id,{})` 必须为
   `verify_delta/unknown/proof=null/automatic_skip_authorized=false`，共享verifier spy调用0。
   重复登记和坏hash在临时复制中拒绝且不覆盖。
5. 定向ResultStore、全库、Reader和同步检查通过后再独立验收。错误数下降不是模型质量、
   token、速度、费用或科学正确性收益。

本阶段仍不解决其余27目录的多运行身份、JSON-only摘要、超64文件清单分片、纯计划/失败
尝试分型，也不解决真实宿主、多轮任务质量、usage/费用或其它artifact全局快照边界。
