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

校验器检查文件存在、SHA-256、路径边界（包括 symlink）、证据 ID 引用、任务依赖无环、done 的前置状态和完成声明一致性。未完成记录本身可以是合法记录，但 `--require-complete` 不通过。报告只说 `integrity_valid`，不说研究结论或视觉质量正确。即使完整性通过，主 AI 仍须读实际内容、日志与图像；任何模型都能写一个声明，声明本身不是执行证据。

本地记录不自动调用 backend、不读取凭据、不上传资料。新输入版本需要重新判断受影响范围；不能仅改 input_version 字段就复用旧验收。
