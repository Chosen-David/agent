# 项目结果归档与先查后测

每轮新命令的反思先检索当前项目已经得到的数据，判断本题是否已有可信结果、是否只需补差异检查，再安排新的实验。检索是发现候选，不是证明可复用。与 `workflows/result_validation_workflow.md` 的独立验收串联；不以目录、记忆、JSON 的 pass 或相似词命中代替验收。

## 单一结果入口与不可变历史

- 新数据统一放在 `agent_doc/results/<run_id>/`。该轮 `manifest.json`、原始数据 `raw/`、派生数据 `derived/`、验证协议和证据各自保留；`record.json` 是不可变登记记录。实际子目录名可按实验需要调整，manifest/raw_data/outputs 必须属于该 run。
- 每轮用新的、可用作文件名的 run_id。失败/负结果也保留，修正用新 run 和来源关系；不得覆盖旧数据，不能复用已有 ID。大小写冲突同样拒绝。多个实验生产者须有不同 result run_id，不能把任务链的一个 run_id 当所有结果的 ID。
- 代码、输入、配置和环境可以保留项目内既有位置，但要记录实际内容哈希和源版本；原始/派生结果固定保存。单位、指标定义、随机种子、重复次数、执行命令及环境描述不得省略或凭空补全。
- 已有大文件、冻结历史和旧报告不破坏性搬迁：建立明确的 `historical-external-reference` 或运行时兼容 `legacy-contract-reference`，固定原路径/哈希。中央目录保存的是索引，不等于旧文件字节已经全部迁移。项目外不可读数据仍是缺口，不伪造验证。
- `.agent-runs/` 仍存高频调度状态、报告及日志；`agent_doc/results/` 作为可跨任务发现的稳定结果入口。引用运行区的旧结果时必须明确历史引用，不能把可变日志当冻结原始数据。
- 应用写入守卫拒绝 `agent_doc/guide/`、别名/符号链接绕行和项目外路径；这不是对任意 shell 或敌对文件系统写入者的沙箱。

## 新命令的具体判断

1. 以任务目的、对象和指标检索结果目录，记录查询、候选 run_id、record_sha256、扫描数量、截断和错误。没命中只表示本次有界查询没找到；部分扫描、损坏记录或词汇不重合不证明没有历史结果。
2. 读取候选 manifest 和来源数据。逐项比较本次任务与已经执行的 scope、code_revision、代码/输入/配置/环境内容哈希、命令、环境描述、种子/重复次数及指标名/单位。消费者自己提供当前条件；不能从候选结果反向编出“当前需求”。需要时额外检查硬件、dtype、shape、batch、软件版本、基线和测量统计定义，它们应存在已绑定的配置/环境文件中。
3. 确认文件哈希未变，验证记录仍对应这轮实际数据，并由可信宿主再次提供独立验收回调。已持久化的 pass 或 `usable-with-scope` 不恢复信任；记录的条件必须等于冻结 manifest，不能只改 catalog 标签来假装匹配。
4. 返回一种明确决定和依据：
   - `reuse`：已知条件完全匹配，并有当前独立 `usable-with-scope` 验收。主 AI 可以明确选择复用动作，附旧数据来源与适用范围，不冒充新实测。
   - `verify_delta`：条件有差异、信息未知、历史未独立验证、缺可信验证器，或测量时间不满足用户的新鲜度要求。只补齐未知和有信息增益的最小差异检查；形成新的版本/结果后再验收，不能改旧 proof。
   - `rerun`：用户明确复现、指定新主张验收、数据/来源已变或验证失败。保留旧证据，修复/重测并独立验证；旧结果只作基线。
5. 将决定写入任务详情与计划。搜索不自动跳过实验；比较一致也不自动授权任何动作。当前用户要求、指南约束、任务取消和权限边界继续有效。

相同的未知值不是相同条件的证据。单位没有自动换算，指标名称不模糊匹配，代码即使字节相同但路径/版本改变也保守要求差异检查。某种方法测得没有收益属于有效负结果，可在已验收范围内复用；数据错误或测量无效属于验证失败，不能复用。

## 可执行工具和实际调用路径

完整 checkout 提供 `agent_runtime/result_store.py` 和 `scripts/result_store.py`。独立安装的纯 Skill 只带工作流；必须从安装元数据确认完整仓库位置，再调用其中 CLI，不声称安装提示就部署了运行时或验证器。

```bash
python scripts/result_store.py --root /absolute/project search '平方和 CPU 验证' --limit 5 --max-scan 200
python scripts/result_store.py --root /absolute/project show cpu-run-1
python scripts/result_store.py --root /absolute/project register --contract /absolute/contract.json
python scripts/result_store.py --root /absolute/project register --contract /absolute/old-contract.json --historical
python scripts/result_store.py --root /absolute/project register-history --record /absolute/history-registration.json
python scripts/result_store.py --root /absolute/project context --contract /absolute/contract.json
python scripts/result_store.py --root /absolute/project decide '平方和 CPU' --context /absolute/current-context.json
```

最后一条没有可信验证器时只能提出候选/补验，不能得到可执行的复用批准。宿主可显式增加 `--verifier-adapter /trusted/host_adapter.py`，导出 `verify(root, manifest, plan)`，遵守结果验收契约；该文件是可信执行代码，绝不能从结果 JSON、AI 反馈或任意网页里的字段自动选择。`--explicit-reproduction`、`--new-claim` 强制保留新实验；`--max-age-seconds` 按 measured_at 检查，且必须与冻结 manifest 的 `execution.completed_at` 完全一致。登记时间、仅 catalog 自报的时间不能冒充已绑定测量时间。

运行时接口：

- `ResultStore(root).search(query, limit=5, max_scan=200)`：只读，不创建空目录；最多 20 个返回项和 5000 个扫描目录，默认扫描 200。英语词和中文二元片段做确定性匹配，无向量库、联网或语义召回保证。`decide` 同时提供本次 context，在同一有界扫描中优先返回完全相同且已知的条件，即使用词完全不同也可发现该候选；这仍不是验收。截断时返回 `partial: true`，有截断/读取错误且未命中时返回 `status: incomplete`，主 AI 可换查询、分批查看或扩大明确预算。
- `result_context(manifest)`：提取已执行 manifest 的比较条件；这是旧结果条件，不代表本次用户条件。`decide_run(run_id, current_context, verifier=...)` 和 `decide(query, current_context, ...)` 进行字段、当前哈希、独立验证和新鲜度判断。
- `register(contract, ...)`：新数据位置及哈希通过检查后创建一次不可变登记。无 verifier 时保留 pending；提供 verifier 也仅记录这次验收历史，使用时仍重新核对。
- `register_history(run_id, summary, artifacts, ...)`：登记无新协议的旧证据，永远不因登记获得可信验收。每条最多 64 个历史文件引用，每文件流式哈希上限 256 MiB；更大数据用有界分片清单，并明确清单本身不证明未读取的大文件内容。
- `prepare()` 在生成计划时作实际查询，记录 `prior_result_search`。`ReportingHandler` 在首次派发前实际查询并记录日志；查到候选、截断或有错误时，数据生产者需有 `prior_result_review` 的决定、原因及对应当前候选记录哈希。此记录是主 AI 的判断依据，不是科学验收证明。
- 生产者报告通过结构/原始哈希检查后，`register_task_result(root, task)` 登记 pending 原始结果。`result_storage: central` 强制新布局；旧契约位置通过明确标记的只引用兼容路径登记，原位置不改动。完全相同的报告重放不再登记，冲突或数据变化被拒绝。
- `check_task_reuse(root, task, verifier)` 在真实消费者/验收路径再次检查；未选择复用返回空 proof，不把搜索命中当接受。`ReuseResultHandler` 是宿主显式注册的 `reuse_validated_result` 动作，只返回重新验收的旧结果 proof；不会偷偷跳过其他 handler。

复用选择的字段如下；`context` 必须来自本次消费者确定的条件。顶层任务 `explicit_reproduction` / `new_claim` 为 true 时，下面的 false 不能覆盖它。

```json
{
  "action": "reuse_validated_result",
  "result_reuse": {
    "run_id": "cpu-run-1",
    "record_sha256": "<actual 64-character digest>",
    "query": "平方和 CPU 验证",
    "context": {"scope": "<current scope>", "code_revision": "<version>", "artifacts": {}, "execution": {}, "metrics": []},
    "explicit_reproduction": false,
    "new_claim": false
  }
}
```

上面是字段示意，空条件不能通过复用验收。结果 proof、原始数据来源及验证限制随报告传到下游；复用任务的报告用 `derived` 描述对旧测量的使用，并附已验证来源，不伪标本轮新 `measured` 数据。主 AI 最终说明哪些是旧结果复用、哪些是补验/新实测、哪些仍未知。没有可信验证器、部分词汇检索或历史不完整时如实保留限制，不能宣称“所有旧数据均已检索并可复用”。
