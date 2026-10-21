# SYSTEM-99 阶段R：外部 JSON 的读取与消费事务边界

问题ID：`SYSTEM99-R-EXTJSON-001`（安全读取）、`SYSTEM99-R-EXTJSON-002`
（先验证后副作用）、`SYSTEM99-R-EXTJSON-003`（消费结构）。基线
`069a988dcfa3fb7bdb8d6dee226adef5a596d7e3`。这是同一系统级批次的正确性检查点，
不是一次完整优化轮或 SYSTEM-99 结案。

## 缺陷与修前证据

基线中的启动、交接、记忆、发布、探针和维护入口混用 `Path.read_*`、`json.load(s)` 与
局部校验。固定反例证明：FIFO 会永久阻塞并占住启动锁；末端符号链接、重复键、`1e400`、
非法 UTF-8、超限或深层 JSON 可被接受或以 traceback/`TypeError` 结束；若顶层类型正确而叶字段
错形，部分入口会先建 SQLite/输出目录、推进 cadence、启动 verifier/backend，再失败。

最初最小回归在基线上得到：

```text
python -m unittest tests.test_external_json_boundaries -v
Ran 4 tests in 6.034s
FAILED (failures=5, errors=1)
FIFO: handoff、memory、TASK/start 三处超时；symlink与1e400被接受；max_bytes参数不存在。
```

扩展审查又固定了 publication candidate/lifecycle 深层错形、首次 memory add 的 document refs、
communication envelope/receipt/context、token probe TOML/JSON 和 token optimizer role registry 的
“副作用后失败”。这些回归先在基线或候选旧实现上失败，修复后才保留为测试；不把测试挂钩错误
或候选实现回归冒充基线缺陷。

## 修复

- `agent_runtime/external_json.py` 统一以 `O_NONBLOCK|O_NOFOLLOW` 打开最终组件，在同一 FD 上
  `fstat` 普通文件、读取 `max_bytes+1`、严格 UTF-8/JSON，并拒绝重复键、NaN/Infinity、非有限
  指数及超过256层的容器。小文件只按实际大小分配，不按16 MiB上限预分配。
- supervisor/core/crash、manifest/result/publication、communication/memory、handoff、backend/setup、
  eval/benchmark/knowledge/context 等真实消费者改为有界单快照；原始字节 SHA、TASK/plan 身份、
  既有业务语义和错误分类保持不变。knowledge 的插件镜像逐字节同步，CRLF 属性只为保持原文件
  行尾，不扩成格式化改写。
- 每个入口在首次持久化、建库、启动 verifier/backend 或写输出前，纯校验实际消费到的嵌套
  字段。publication 还校验 candidate 聚合哈希、文件 mode/OID/SHA、任务/文档绑定及 lifecycle
  一致性；错形列表/字典不再触发未捕获的可哈希性异常。
- token probe 先冻结并验证 TOML model/effort，再创建输出；token optimizer 在 due cadence 写入、
  tick 目录、同步和 app-server 前冻结 exact v1 role registry，并把同一配置传给 worker。
  `[]`、`null`、缺字段、重复/越界 ID、FIFO/目录/symlink、重复键、非有限数和257层输入均保持
  state 原字节、零 backend 调用和结构化 CLI 失败。

主要实现按候选树分组位于 `agent_runtime/external_json.py`、`task_supervisor.py`、
`task_manifest.py`、`publication.py`、`communication.py`、`project_memory.py`，以及
`scripts/token_probe.py`、`token_optimizer.py`、`knowledge_maintenance.py`。回归集中在
`tests/test_external_json_boundaries.py`、`test_publication.py`、`test_token_optimizer.py` 及各消费端
原测试文件。路径定位以本阶段候选树为准；根因基线为上述 `069a988d`，不写尚不存在的自引用提交 SHA。

## 验证与结论

环境：Linux 6.18.55 x86_64，AMD EPYC 9V74，CPython 3.12.14；无 GPU、模型或网络调用。
最终固定输入 SHA256：`tests/test_external_json_boundaries.py` 为
`17b2e1e1a0c676264b96d7dd856d936bb68104e02057762425b3c842ffe1ab17`，
`tests/test_benchmark_json_inputs.py` 为
`e5f8b56530a967f5d693683fd9a4f5a7641ee93c285a98b978e18542b9ba5070`，
`tests/test_token_optimizer.py` 为
`93811040c65c2be545778d4185e6d399f97ebe94d925afaf961563b8926a0ae0`。

```text
python -m unittest -v tests.test_external_json_boundaries \
  tests.test_benchmark_json_inputs tests.test_token_optimizer
Ran 55 tests in 10.682s -- OK

python -O -m unittest -v tests.test_external_json_boundaries \
  tests.test_benchmark_json_inputs tests.test_token_optimizer
Ran 55 tests in 10.602s -- OK

python -m unittest discover -s tests -v
Ran 1479 tests in 109.380s -- OK (skipped=8)

python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.589s -- OK

python scripts/sync_plugin_references.py --check
exit 0

python -m compileall -q agent_runtime scripts tests \
  plugins/research-assistant/skills/model-with-knowledge/scripts
git diff --check
exit 0 / exit 0
```

独立复核先退回 token optimizer 的 role registry：旧候选虽安全读取，却在 cadence/目录/backend
副作用后才校验结构。返修和 normal/`-O` 各55项复验后结论为 `APPROVE (zero blocker)`；冻结树报告见
[独立验收](independent-stage-r.md)。

本项恢复的是 fail-closed 正确性和可恢复性，没有性能、token、模型质量、吞吐或峰值内存收益主张；
修前永久阻塞不能换算成加速比。未验证 Windows 特殊文件、父目录被同权限攻击者并发替换、真实
tmux/SSH/模型/网络/费用和跨主机文件系统。内部生成器 `sync_plugin_references.py` 的受控仓库输入
不在外部控制文件边界内。真实宿主、多轮质量/总成本、历史登记覆盖等 SYSTEM-99 缺口继续 open。
