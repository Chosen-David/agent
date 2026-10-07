# 每轮实验后的代码与数据独立验收

每次实验或测量产生数据，主 AI 必须在数据被汇总、画图、比较、写入结论或支持完成声明之前，安排独立代码与结果检查。测完只是取得原始观测，不代表代码正确或数据可用。有限测试只能说明在声明范围内通过，不能保证代码绝对没有 bug。

## 任务链与权限

沿用当前项目唯一 `doc/task/TASK.md` 及相关 `task_details`、人工指南和已评估建议；不创建另一份任务列表，不写 `doc/guide/`。主 AI 在实验前固定需求、允许资源、验收协议、独立验收者与消费依赖。

DAG 必须是 `producer → verify_experiment_result → consumers`。主 AI 将准确率、性能、模型、CPU/GPU、合成以及探索实验都明确分类；数据生产任务用 `task_type: experiment` 或 `produces_data: true` 并声明 `experiment_result`。不能改成 `false`、`synthetic` 或 `derived` 来绕过已声明的消费依赖。纯非实验任务和旧非测量报告保持兼容；程序无法从任意任务自然语言发现全部隐藏实验，可信主 AI/宿主负责完整分类。

生产者的 `experiment_result`、验收节点的 `result_validation`、每个消费者的 `required_result_refs[]` 使用相同合同：

```json
{
  "result_id": "unique-result-id",
  "producer_task_id": "produce",
  "producer_actor": "implementation-agent",
  "manifest_path": "results/run-001/manifest.json",
  "validation_plan": {"path": "configs/validation-plan-v1.json", "sha256": "<actual SHA-256>"},
  "scope": "exact cases, metrics, hardware and claims being accepted"
}
```

每个生产者只有一个直接依赖它的验收节点，节点 action 为 `verify_experiment_result`，owner 与生产者不同。其余全部下游节点必须包含该验收祖先及相同消费合同，包括再次加工数据的消费者。验收节点也可以消费上游已验收结果。实验前不知道结果哈希，不能编造；实验后由独立验收固定实际字节并保存到现有运行证据。

## 验收前固定协议

`validation_plan` 文件使用 `schema_version: experiment-validation-plan/v1`、与合同一致的 `scope` 及 `criteria`。以下六项各包含 `procedure`、`acceptance` 和布尔 `allow_not_applicable`：

1. `implementation`：独立阅读与执行路径核对，检查索引、形状、dtype、精度、分支、异常、状态泄漏和实际运行代码与被测代码一致性。运行单元/回归检查不替代针对性代码检查。
2. `reference_boundary`：可信参考实现、闭式解、小规模穷举或性质/变形测试；边界、退化、空输入、极端范围和错误条件。参考不能复制相同错误路径。
3. `data_integrity`：样本 ID、重复/漏项、失败样本、分母、输入/代码/配置/种子/原始日志与输出对应；断点恢复不得混入不同协议。
4. `numerical_sanity`：NaN/Inf、符号、数量级、单位、误差阈值/容差来源、统计/物理不变量、汇总与原始记录一致性；不能仅凭图形看起来合理。
5. `measurement_validity`：主张涉及性能时检查计时范围、同步、warmup、单位、分辨率、资源分配/干扰、配对和全部重复样本、离散程度与噪声。准确率检查数据划分、指标分母和协议等价。无计时主张可经预先允许并说明理由后标 N/A。
6. `reproducibility`：按冻结命令、环境、配置与种子进行独立小规模重跑/交叉检查；足够的重复性、不一致及剩余外部依赖明确记录。

阈值由科学问题和资源条件决定；没有一个通用数字能认证所有实验。需要但未能运行的检查是 `inconclusive`，不能伪装 N/A。协议/范围需要变更时版本化重排，不能看过数据后静默放松条件。合法负结果、变慢、无提升或不支持假设仍可通过数据验收；验收判断测量可信程度，不要求研究假设成功。

## 结果与独立证据

结果 manifest 使用 `schema_version: experiment-result/v1`，绑定合同的身份、范围、验收协议及 `run_id`、`code_revision`、`execution`（command 字符串数组、environment_description、seeds、repeats）。command 仅是复现信息，运行时不把 JSON 字符串作为 shell 命令、模块名或授权执行。

`artifacts` 的 `code`、`inputs`、`config`、`raw_data`、`outputs`、`environment` 均为非空 `{path, sha256}` 列表。环境记录应包含实际硬件/软件版本和相关资源条件；代码哈希覆盖真实影响路径与 dirty 内容，不能只写 Git commit；数据/配置/环境需足以复现。`metrics` 是非空 `{name, value, unit}` 列表，值必须有限，无量纲明确写 `dimensionless`。运行时核对哈希覆盖的文件，宿主独立审查是否遗漏真正依赖。

独立 verifier 是可信宿主显式注入的函数 `verifier(root, manifest, validation_plan)`，返回实际观测或受保护的独立检查记录。它不能从生产者的 pass JSON、reviewer 名称或 `independent: true` 自证身份。宿主必须认证审查者和真实开始/完成事件，确保不是生产者，实际执行或读取适用检查，并确认检查代码、环境、参考方法和证据完整。单一布尔回调或自写通过文件不构成独立验收。

返回 `experiment-validation/v1` 记录：`manifest_sha256`、完整 `artifact_hashes`（含验收协议）、`validation_plan_sha256`、`scope`；`verifier` 的 actor、independent、source、run_id、method；非空 `limitations`；六项 `checks` 各有 verdict（pass/fail/inconclusive/not_applicable）、reason 和非空文件证据绑定。宿主保存稳定的实际 review 身份和记录；重读同一验收不得每次虚构新的 reviewer run ID。实际新检查则保存新版本，原证据不覆盖。

验证前后重新核对全部绑定和独立证据，manifest、代码、数据、配置、环境、输出、协议或 review 变化会使旧完成证据失效。结果内容不是加密身份凭据，哈希不是正确性证明。

## 可执行接口

完整 checkout 提供 `agent_runtime.result_validation`，纯 Skill 只带本契约，不自动部署运行时或 verifier。

- `validate_result_plan(plan)`：在任务合同验收中检查生产者、独立验收节点和消费依赖。
- `ResultValidationHandler(root, verifier)`：可信宿主注册的 `verify_experiment_result` 处理器，不自行扩展权限。
- `check_task_results(root, task, verifier=None, report=None)`：实际 ReportingHandler 在派发/报告/复验路径调用；原始生产报告只记录 pending，消费者必须得到 scoped acceptance。
- 宿主 `build()` 返回 `result_verifier`，与 handlers/authorize 一起接入现有 supervisor；恢复、进度与完成报告重新传入同一可信 provider。不能从持久化 JSON 恢复一个“可信回调”。
- `inspect_result(root, contract, verifier=None)`：只读返回状态与原因。无 verifier 即使有通过 JSON 也停在 pending。provider 抛异常返回 retriable pending，不崩溃或当成通过。

```bash
python scripts/validate_experiment_result.py --root /absolute/project --contract controller-contract.json
python scripts/validate_experiment_result.py --root /absolute/project --contract controller-contract.json --verifier-adapter /explicit/trusted/host_adapter.py
python -m unittest tests.test_result_validation -v
```

第二条命令显式加载宿主已审查的 Python 文件，导出 `verify(root, manifest, plan)`；不能使用生产者建议的路径自动加载。第一条命令没有可信 verifier，正常输出 pending 并返回退出码 2；只有 usable-with-scope 返回 0。CLI 是本地已获授权的检查工具，不授予执行任意代码的新权限。

当前文件核验限定项目内普通无符号链接文件、每文件 16 MiB，拒绝路径逃逸/FIFO/设备；大数据需真实有界分片及完整覆盖或明确的项目适配实现，不能用几行摘要冒充全量验收。只验证被声明并独立审查完整性的依赖；不构成 OS 沙箱，不控制绕过入口的其他写入，也不安装 CI、GPU runner 或后台服务。

## 失败、修复、复测和结论

- `pending`：缺输入/独立 provider、检查尚未完成或证据不足；不得进入数据消费和结论。
- `invalid`：绑定失效、格式/域不完整、数值/边界等检查失败；不得进入数据消费和结论。
- `usable-with-scope`：全部适用检查通过，N/A 已允许并有理由，只支持 scope 内结论，limitations 随报告和交接保留。

失败或不足 → 主 AI 保留原始测量及旧失败记录 → 诊断具体代码/协议/数据问题 → 在既有权限/预算内修复 → 新 result/run ID 与版本化任务链 → 重测受影响部分 → 再独立验收。现有 supervisor 的维护/恢复路径承接此动作，不创建循环 DAG、无限自动重试或额外 GPU/付费任务。宿主没有恢复 adapter 时明确阻塞与下一 owner，不把指令文字当已执行修复。

在最终报告中分别写“测量已完成”“哪些检查已通过”“这些数据能支持的范围”“哪些仍未知”。代码、数据或实验条件更新后，旧数据仍保留为历史观测；是否可复用必须有新的明确独立验证，不得默默把旧 pass 复制到新版本。
