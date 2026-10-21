# SYSTEM-99 阶段R独立验收

结论：`APPROVE (zero blocker)`，限定为基线
`069a988dcfa3fb7bdb8d6dee226adef5a596d7e3` 上当前冻结候选的外部 JSON／控制文件边界。
候选可作为 `usable-with-scope` 正确性检查点；这不是 SYSTEM-99 结案，也不证明全库无缺陷。

## 独立复核

我只读检查了候选的67个已跟踪修改文件及4个既有未跟踪候选文件，沿真实入口核对共享读取器、
consumer 校验、错误映射和副作用顺序。重点结论如下：

- `agent_runtime/external_json.py` 在同一 FD 上使用 `O_NONBLOCK`、`O_NOFOLLOW`、`fstat` 和大小上限，
  拒绝非普通文件并在全部路径关闭 FD；小文件按实际大小读取，增长才回退到上限加一字节。
  SHA 校验和 JSON 解析绑定同一份原始字节。
- 严格解析拒绝非法 UTF-8、重复键、NaN/Infinity、`1e400`、畸形/超大整数及超过256层的容器；
  `JSONDecodeError`、递归和读取异常统一进入结构化边界错误，而不泄漏 traceback。
- supervisor/core 的 TASK、计划、配置和 crash-state 在建库、写状态、启动 adapter/tmux 前完成读取与
  消费结构校验；TASK 或 crash-state 失败时启动锁可释放。communication、memory、result、publication、
  knowledge/context、setup/backend、eval/benchmark 等显式文件入口采用同类先验证后副作用顺序。
- publication 的 candidate、文件 mode/OID/SHA、任务/文档绑定及 lifecycle 深层字段在 callback 前校验；
  token probe 在创建输出前冻结 TOML/JSON 配置；token optimizer 在推进 cadence、建 tick 目录、同步或
  启动 backend 前冻结 exact-v1 role registry。合法 plan 大小、legacy/review 分支和原字节哈希契约由原有
  回归与全库回归共同覆盖，未见候选引入的兼容性阻断。

复核过程中曾以 `REVISE` 退回 token optimizer：旧候选虽安全读取 role registry，却在状态推进和目录/
backend 副作用后才验证其嵌套结构。当前候选已前置 exact schema、非空安全唯一 ID 校验，并让 tick、probe
和 direct worker 复用同一冻结配置；`[]`、`null`、坏 role、FIFO、目录、末端符号链接、重复键、非有限数
和257层输入均在副作用前失败。返修后未再发现本阶段范围内 blocker。

## 独立执行的验证

环境：Linux 6.18.55 x86_64，AMD EPYC 9V74，CPython 3.12.14；未调用 GPU、模型或网络后端。
固定测试输入 SHA256：

- `tests/test_external_json_boundaries.py`：
  `17b2e1e1a0c676264b96d7dd856d936bb68104e02057762425b3c842ffe1ab17`
- `tests/test_token_optimizer.py`：
  `93811040c65c2be545778d4185e6d399f97ebe94d925afaf961563b8926a0ae0`

```text
python -m unittest -q tests.test_external_json_boundaries tests.test_benchmark_json_inputs tests.test_token_optimizer
Ran 55 tests in 10.722s — OK

python -O -m unittest -q tests.test_external_json_boundaries tests.test_benchmark_json_inputs tests.test_token_optimizer
Ran 55 tests in 10.598s — OK

python -m unittest discover -s tests -q
Ran 1479 tests in 110.485s — OK (skipped=8)

python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.583s — OK

python scripts/sync_plugin_references.py --check
python -m compileall -q agent_runtime scripts plugins/research-assistant/skills/model-with-knowledge/scripts
git diff --check
三项均退出0、无输出。
```

定向测试真实使用子进程和 POSIX 特殊文件，覆盖 FIFO 不阻塞、目录/末端符号链接拒绝、精确大小和深度
边界、非法编码、重复/非有限数字、错形嵌套、锁后恢复及失败前无 DB/state/output/backend 副作用；普通
和 `-O` 均通过，避免依赖可被优化删除的 `assert`。全库与 Reader 结果是我在该冻结工作树上的实际重跑，
不是复用主执行者的退出码。

## 范围与未验证边界

- 未在 Windows 真机验证特殊文件语义，也未验证恶意同权限写者并发替换父目录组件；当前保证只覆盖最终
  组件不跟随、同一 FD 快照和已固定的普通文件竞态。
- 未执行真实 tmux、SSH、模型、网络、费用或跨主机/NFS 场景；CPU 回归不证明生产宿主部署、任务质量、
  token 成本、吞吐或峰值内存改善。
- `scripts/sync_plugin_references.py` 对仓库内固定受控 registry 的生成期读取不属于本阶段声明的外部控制
  文件边界；若未来允许外部替换该输入，应单独接入同类有界读取与消费校验。
- 全库1479项和本次静态检查只支持当前候选及所列入口；不能外推为所有未来消费者、所有文件系统或绝对
  无 bug。SYSTEM-99 的真实宿主、多轮质量、总成本和其余任务仍保持 open。
