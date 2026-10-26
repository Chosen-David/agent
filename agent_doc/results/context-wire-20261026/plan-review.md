# CONTEXT-WIRE-01 v1 独立方案审核

Verdict: **revise**。共享终端边界修复方向合理，但当前冻结 fixture 尚不足以验收方案承诺；补强下列判据并冻结新版本后再执行。此结论不是测试结果或实施批准。

审核对象：PROJECT_ROOT = WORKFLOW_ROOT = `/workspace/scratch/6416f20dc59b/agent-run-1303`；HEAD `80c4a368dc3453304f9c5398cafec2cfc9a3b5ed`。本审核仅静态读取，未运行测试、论文示例或模型调用，未派发任务。唯一写入本文件；不触碰外来 zip、guide、旧证据、TASK/Plan 或预算账本。GUIDE.md 当前为空；README 是目录职责，不能补造成新授权。

## Blocking findings 与返修要求

1. **artifact token_counter 的 CLI 换行筛选未固定反例。** plan.md 明确要求按终端预算选择 codec，新增 fixture 却未触及 `--encoding`，现有 test_artifact_token_selection 只测 API 的无终端换行预算。增加可控 counter 的 CLI 回归：counter 偏好的长候选恰占用户 cap、加原生换行即超限，而另一完整候选加换行后可容纳；CLI 必须返回后者，不能先选择长候选再拒绝。同时固定“所有候选均不容纳”时 exit2/stderr JSON、空 stdout；API 的原 max_chars/counter 无换行语义须继续通过原测试。无需真实 tokenizer/模型，也无需 Windows。可在既有新 fixture 内调用 CLI main 并 patch 工厂，仍保留子进程实际 wire 测试。

2. **内容 oracle 只验证可解码和出现一个 Unicode 字符，未固定实际来源完整性。** `test_all_success_packets...` 对 source/artifact/advice/grid 没有验证源字节、引用、坐标、行号/选段或取消/异议内容；dispatch 仅检查 model/write_scope/一段文档，遗漏父 config、reasoning、approval、sandbox、thread IDs 和完整 source_dependencies。请用 fixtures 中独立保存的原文/引用作 oracle：source 核对 chunks/行位与所需原文；artifact 恢复两版并与原文逐字相等；advice 核对 leading_text/选段及 headings 模式的有意省略；grid 恢复完整有序坐标与 metadata；dispatch 核对完整 params/input_text/dependencies 与取消/异议。断言不能通过同一 serializer 长度公式重写；现有实际 stdout 精确边界 oracle 保留。只读检查应覆盖成功及拒绝路径前后（当前仅 UTF8 成功测试作文件快照）。

3. **共享 helper 新上限参数缺少验证。** >1M 的 artifact 成功样例有效，但不能单独证明新 `max_chars_limit` 受 16MiB 硬上限保护、默认仍为1M、其他消费者不被放宽。为显式参数固定 bool/非法数值/超过16MiB拒绝与默认1M拒绝；artifact 保留原合法范围（最终包与换行总量仍受上限），避免通过复制 serializer 或把共享默认改为16MiB实现。新预算拒绝须与 source/artifact/dispatch 既有数据错误 exit1/stdout 分开；尤其所有 artifact token 候选不满足显示预算时不能落进旧 ValueError→exit1 分支。原 API 仍按原输入/解析上限构建并保留选择语义。

## 七域检查

| 域 | 结论 | 理由 |
| --- | --- | --- |
| intent | pass | 真实 CLI UTF8 与完整终端输出预算是有界缺陷假设；不把本地回归升级为模型/性能收益实验。 |
| guide | pass | 已读 AGENTS、三工作流和空 GUIDE/README；只读人类目录，SYSTEM-99 保持 open，无新权限。 |
| assumptions | pass | 五 CLI 尚未使用统一终端渲染；source/dispatch API 上限100000、advice/grid 1M、artifact LIMIT=16MiB；输出格式/父 config 可超内部预算。换行是运行平台实际 os.linesep，不宣称原生 Windows。 |
| prior_results | pass | 对照现有 context CLI、serialization、artifact token/API 回归；这些不能替代新的实际五 CLI wire 判据。旧 PID/ALIAS/role/Codex 受阻/耗尽预算、旧 fullsuite/真实宿主门禁继续保留；无旧收益复用。 |
| acceptance | fail | 上述三项 fixture 缺口须补齐；当前 complete JSON/UTF8/cap=实测长度与cap-1空stdout判据方向正确。 |
| risk | pass | 共享 render_cli_context optional max_chars_limit 优于复制新 serializer；需先构建再一次 print、统一 UTF8 stdout/stderr。静态五脚本及 API 无 backend 调用路径；结果复核必须重查最终 diff，不能把输出“data”文案视为不派发证明。 |
| resources | pass | 主控最多3次 targeted，每次<=120s（newtest1、fixedsuite1、必要修复余1）；独审后续最多1次同一冻结 fixedsuite<=120s，当前使用0次。不得 fullsuite、Windows、模型实验或旧候选重试。单个 subprocess timeout 15s 不等于 suite 总时限，宿主执行需外层120s硬界并保留超时/原始日志。 |

## 认可的实现边界与后续门禁

保持 `render_context` 和 API 选择/调用语义；在共享 `render_cli_context` 增可选、有16MiB总上限的 max_chars_limit，默认1M。CLI source/dispatch/advice/grid 按各自 API 原硬上限构建后，以用户 max_chars 检查实际最终格式和原生终止换行，防止 API 内预算先以旧错误协议拒绝新的显示预算。artifact token_counter 的候选筛选须预留终止换行；不因修复改动任意 token-counter 的 API 调用行为。成功一次完整 UTF8 JSON 输出；新显示预算错误 exit2/stderr JSON，空 stdout；source/artifact/dispatch 既有输入/数据错误 exit1/stdout JSON，advice/grid 错误 exit2/stderr，无 traceback。无截断、无额外 backend/写入。

runner 的15模块列表为有界相关 suite；基线只运行新 fixture，修后由主控冻结补强后的 plan/fixture/runner 及生产源码 hashes，再请求独立结果复核。保留基线失败与修后原始日志、实际命令/解释器/平台/超时状态。本文不消耗任何运行额度，不替代明确要求的独立结果验收；未读新原始结果前不能发布“通过”。如果返修超出上述实现边界，应先再对齐方案，而不是借剩余调用扩展任务。

## 冻结输入 SHA-256

| 路径 | SHA-256 |
| --- | --- |
| `AGENTS.md` | `97f35fc8fb91097a34380c12a9581936f8a78c6f9c10a05183c84511645738ed` |
| `workflows/project_document_workflow.md` | `6ee07eca5091187b27e02056c3ae83f66183cfc07dc4c7af5c80742ffacdaaf4` |
| `workflows/result_validation_workflow.md` | `349cebab1a78baa63b5c7d422f239c2d802f9f77a1ad180ceb4871ebea372888` |
| `workflows/dual_main_workflow.md` | `639f19cf9de42d65935b3a42b8e9f6e8aa6e4a2145254ad59202642974eb9644` |
| `agent_doc/guide/GUIDE.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `agent_doc/task/TASK.md` | `cac11b59a920f4dc1dd398568ba6b2d0d0593ae5ac25d59858c53a2b739c706f` |
| `agent_doc/task/task_details/SYSTEM-99.md` | `f289e37a4d6a2148204fbc357b43f73ca75cba7b97f5f612767d548ded567fbf` |
| `agent_doc/results/context-wire-20261026/plan.md` | `048a6b1794e0dd0f07cc0359bc232bb2eafe72be19d03336c1161f04d50db3fe` |
| `agent_doc/results/context-wire-20261026/run_checks.py` | `80565f43d01e48cd6304ec5eb11323243fe06dc9dd421aaca5f0ba57f80d9c53` |
| `tests/test_context_cli_wire.py` | `6ff0cb65b98a081cdc8b3c820e5651d2d78829fa7f919f3f99608daa1b77205b` |

生产范围读取绑定：

| 路径 | SHA-256 |
| --- | --- |
| `scripts/source_context.py` | `64412a2a675f9cded5c0a541ac35e7bf1ce45cc45f1205dd03b07849360544ac` |
| `scripts/artifact_context.py` | `b1f434ff9f1c18ad815962f5fee098429d1315c3d70b3814693cf80e729a4213` |
| `scripts/dispatch_context.py` | `758e9585fe40c94aa88a69709befce0d5c3fb61890f2abb7c5d9e96adbbb9209` |
| `scripts/advice_context.py` | `0591fb46e219243136bd6e3f42bc545b3270979f0ff9c9a63e45947fb9640c67` |
| `scripts/grid_context.py` | `4bb0b4741c400beca94427d69e976a4e6e34a5dc6df2db6dc623077b857738bd` |
| `agent_runtime/context_serialization.py` | `4dedbf2e11ba7d41ea91107fa6f9c21fc68c9e78dd1ab9a3920d0bb412775e9d` |
| `agent_runtime/source_context.py` | `bf6e13a0be7832032a88cbdf8c1f6f3c1e6c7c827d00a6be95a6bd8af26a8ab6` |
| `agent_runtime/artifact_context.py` | `6bacce144f71a9c162681a4bd7929f0614119009ac96a52e0a38bb9da2616168` |
| `agent_runtime/dispatch_context.py` | `5f07b28b44ec623191c331274a63e6c5599c6036086665ad774e9e8c2b734e5a` |
| `agent_runtime/advice_context.py` | `1cdbf1eede0b18cc483ab38e9b4888b15dc20dad393012ccd416fa73d2d9c6b0` |
| `agent_runtime/grid_context.py` | `0b93d48eaa9acfc1aa09f7053b22b59010f033c5dbb5b5e5580c0c3f49cb7862` |
