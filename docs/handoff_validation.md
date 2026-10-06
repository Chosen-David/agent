# 可检查的本地产物交接

适用于复杂任务、评测或跨角色交付；简单回答不强制生成记录。不替代现有 research/travel 领域对象，也不是 JourneyPilot API schema。

`python scripts/validate_handoff.py handoff.json --root outputs --require-complete --request consumer-request.json`

```json
{
  "schema_version": 1,
  "run_id": "unique-run-id",
  "role": "research-explore",
  "input_version": "actual-input-hash-or-version",
  "status": "partial",
  "limitations": ["实验尚未运行；获得对应硬件后继续"],
  "artifacts": [{"id":"A1", "path":"answer.md", "sha256":"actual-sha256"}],
  "checks": [{"criterion":"来源核验", "status":"not_run", "artifact_ids":[]}],
  "tasks": [{"task_id":"RES-T001", "depends_on":[], "status":"blocked", "reason":"缺硬件；取得后运行", "evidence":[]}]
}
```

`status`: completed / partial / blocked / failed / not_run。`checks.status`: pass / fail / not_run。任务继续沿用 todo / doing / done / blocked / skipped，不混为运行状态。

`tasks` 是此交接范围内的任务，不是整个项目的未来 backlog。仅完整性检查时可省略；完成验收须与消费者请求中的任务集合完全一致。单次回答可以用显式空任务清单。
`completed` 时，列出的任务只能是 `done` 或由消费者明确允许且有非空文字理由的 `skipped`；仍有 todo / doing / blocked 时应报 `partial` 并写恢复条件。
skipped 仅用于允许跳过的范围，不能用来隐藏未完成要求，也不满足 done 任务的前置依赖。
主 AI 从根 TASK.md 和本次授权范围建立独立请求；程序据此检测漏项和未授权跳过。不能从生产者记录反向生成消费者请求，否则无法检测遗漏。

此本地 schema 中的 `tasks[].evidence` 必须是 `artifacts[].id` 的字符串列表，done 时不可为空。
外部 URL、自由文本或领域 evidence 对象须先保存为本地产物，再引用其 ID；这只是归一化交接，不改变
`backend_handoff.md` 或科研/旅行领域对象的 evidence 含义。非 done 任务可省略 evidence；若提供，仍校验引用。
例如 `{"task_id":"RES-T002","status":"done","depends_on":[],"evidence":["A1"]}`。
旧校验器曾误放行非空对象/悬空引用；旧记录应补登记真实产物。若工作确实未完成，则改为 partial，
把相应任务改为非 done，并删除或纠正非法 evidence；仅改 partial 不能修复非法引用。不能添加占位证据来凑通过。

校验器检查文件存在、SHA-256、路径边界（包括 symlink）、证据 ID 引用、任务依赖无环、done 的前置状态和完成声明一致性。未完成记录本身可以是合法记录，但 `--require-complete` 不通过。报告只说 `integrity_valid`，不说研究结论或视觉质量正确。即使完整性通过，主 AI 仍须读实际内容、日志与图像；任何模型都能写一个声明，声明本身不是执行证据。

本地记录不自动调用 backend、不读取凭据、不上传资料。新输入版本需要重新判断受影响范围；不能仅改 input_version 字段就复用旧验收。

这是显式调用的 CLI/API，不是自动挂接全部角色的执行引擎；当前入口是上面的命令。
损坏路径、符号链接循环和文件读取失败返回完整性错误。校验时应使用稳定的本地输出目录；
不把此工具当对恶意并发文件替换的安全沙箱，也不把文件哈希相符当作主张正确或权限充分。

## 消费者拥有验收范围

在派发任务前，由主 AI/接收方从可信任务状态建立 `consumer-request.json`，保存在消费者控制的位置；不要由产出报告的 Agent 修改，也不要从返回的 tasks 自动推导。模板见 [handoff_request.json](../templates/handoff_request.json)。

```json
{
  "schema_version": 1,
  "input_version": "actual-input-hash-or-version",
  "tasks": [
    {"task_id": "RES-T001"},
    {"task_id": "RES-T002", "allow_skip": true}
  ]
}
```

`tasks` 必须显式提供，ID 唯一并按原字符串精确比较；不修剪空格或自动合并别名。默认 `allow_skip=false`，只有消费者可设为布尔 `true`；生产者的同名字段、理由或内嵌 request 都不能授权跳过。消费者允许跳过仍必须在交接中列出任务与真实理由，且 skipped 不能满足后续 done 节点的依赖。集合相符不证明任务语义已经完成，独立验收仍须读产物。

程序拒绝缺失任务、范围外任务、未授权跳过、请求版本与交接版本不一致、重复 ID 和畸形契约。CLI 同时拒绝重复 JSON 键，避免同一请求有歧义。部分交接带 request 时也必须列出整个派发范围，未完成条目用 todo/doing/blocked，不能直接删除。

简单的一次回答使用 `"tasks": []`；交接也不能额外列任务。复杂工作不能通过人为清空请求来逃避验收。校验器不能证明请求文件来自可信消费者，宿主负责保管与传入；不提供签名认证或恶意并发写入隔离。此契约只绑定版本、任务成员及跳过权限，未绑定每条依赖边或语义评分标准。

### 迁移已有调用

- `--require-complete` 现在必须提供 `--request`。只传旧 `--expected-input-version` 会返回 unverified 和非零退出码，避免在未知范围上宣告完成。
- API：`validate(record, root, True, consumer_request=trusted_request)`。request 提供输入版本；如另传 `expected_input_version=`，两者必须一致。
- 不需要完成验收时，原 `validate(record, root)` / 不带 `--require-complete` 的 CLI 继续用于完整性检查；可以另传 `--expected-input-version` 检查版本。
- CLI 的 `completion_verified` 仅在请求范围、文件完整性与完成条件均通过时为 true。`consumer_scope_verified` 只表示提供的范围一致，可在合法 partial 记录上为 true，不能代替 completion_verified。任一校验失败时验证字段均为 false。
- 历史记录保留原始字节；先从可信任务记录重建请求再重新验收，不将历史测试日志改写为新版本已通过。

输入版本字符串一致也不能阻止生产者伪造结论；需要真实执行日志、数值/视觉检查与独立审查。此 CLI 是显式工具入口，不会自动替所有宿主、角色生成请求或接管任务调度。
