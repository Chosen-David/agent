# 可检查的本地产物交接

适用于复杂任务、评测或跨角色交付；简单回答不强制生成记录。不替代现有 research/travel 领域对象，也不是 JourneyPilot API schema。

`python scripts/validate_handoff.py handoff.json --root outputs --require-complete`

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

`tasks` 是此交接范围内的任务，可省略或为空；不是整个项目的未来 backlog。
`completed` 时，列出的任务只能是 `done` 或有非空文字理由的 `skipped`；仍有 todo / doing / blocked 时应报 `partial` 并写恢复条件。
skipped 仅用于允许跳过的范围，不能用来隐藏未完成要求，也不满足 done 任务的前置依赖。
主 AI 仍需核对任务清单是否覆盖原请求、跳过是否合理；程序不能发现被故意省略的任务。

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
