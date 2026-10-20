# SYSTEM-99 阶段O方案：TASK单次快照绑定

基线 `5379fb9e8541df478ccbdb3c682ed6eff4c6e486`。本方案只处理任务索引在一次契约校验内的
双读竞态，不迁移agent_doc、不改schema、任务语义或历史结果。

## 修前证据

`validate_contract` 先以 `digest(path)` 读取TASK.md并比对计划SHA，随后
`requirements(path)` 再次打开同一路径解析任务。临时真实文件夹具在第二次读取前把
`[OLD]` 替换为 `[NEW]`，读取后恢复 `[OLD]`；绑定OLD摘要、但任务只覆盖NEW的计划被接受：

```text
{'accepted_ids': ['NEW'], 'bound_sha_is_original':
'aabce6bf85cf17ef46901259006c130ed98382e856fbe438b3810f2a1fb51193',
'disk_after': '- [ ] [OLD] original requirement', 'swapped': True}
```

这不是外部攻击认证，而是可重复的同进程文件版本不一致：契约声称校验的摘要与实际用于覆盖
判定的任务列表不是同一快照。

## 有界修复

1. 在task_manifest内部增加一次读取的任务快照辅助函数：用现有project-doc普通文件读取边界
   获取最多1 MiB原字节，严格UTF-8解码，以现有canonical判定调用 `parse_requirements`，并由
   同一字节计算SHA256。
2. `validate_contract` 只使用这一份快照完成摘要比对和任务覆盖判断；不得先哈希后按路径重读。
3. `prepare` 从一次任务快照生成任务项和task_source，并确认随后取得的project-documents中的
   task_index身份与该快照完全相同；中间变化必须拒绝生成混合草稿。公开 `requirements(path)`
   保持返回类型与解析行为，只改为复用同一普通文件读取边界。
4. publication freeze用一次任务原字节同时解析所有权ID、计算摘要，并要求该摘要等于已冻结候选
   树中的TASK文件摘要；不得把另一版本的任务ID写入发布状态。
5. 不把该修复外推为TASK、详情、guide和advice多文件原子事务；现有后续重验仍保留。

## 验收

- 修前真实替换并恢复的反例必须从“接受NEW”变为拒绝；另测ABA、读取后替换不污染已绑定快照。
- prepare在任务读取与文档快照之间变化时拒绝混合草稿；publication在候选冻结与所有权解析间
  变化时拒绝；普通canonical和legacy路径保持成功。
- 无效UTF-8、FIFO/目录/符号链接等非普通或重定向输入失败闭合，不放宽现有错误。
- 定向task-manifest/project-doc/supervisor/publication回归、全库、Reader和同步通过；独立审阅代码、
  反例与边界。无真实模型、token、速度、费用或跨文件事务主张。

SYSTEM-99继续open：剩余27个历史结果目录、真实宿主/多轮质量、usage/费用与其它artifact读取
边界均不在本阶段完成范围。
