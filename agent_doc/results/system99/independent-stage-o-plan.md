# SYSTEM-99 阶段O独立方案审阅

结论：`approve-with-scope`，但实现前须吸收以下边界。

独立复现确认 `validate_contract` 可让绑定静态 `[A]` 摘要与project-documents的计划接受瞬时
`[B]` 任务ID，磁盘读后恢复为A。该校验位于主计划审阅、提交审阅、start、每次tick和进度派生
链；不是纯显示错误。`prepare` 也可在多次读取间生成旧标题/goal与新摘要混合的草稿。

修复应一次打开普通文件、禁符号链接、限定大小、从同一原字节完成摘要、严格UTF-8解码和需求
解析。prepare须将该身份与project-documents的task_index路径/摘要交叉核对；validate还须拒绝
task_source与project-documents身份不一致。枚举所有 `requirements` 调用后，publication freeze
也应纳入：其所有权ID解析必须与已冻结候选树中的TASK摘要一致。

必须覆盖真实替换/恢复、prepare与publication中间变化、source/doc摘要冲突、中文CRLF、非法
UTF-8、超1 MiB、目录/FIFO/文件及父目录符号链接、canonical/legacy、required_task_refs，以及
plan review/start/tick/review/publication调用链。正常静态UTF-8输入不得改变语义。

接受范围仅是单次TASK读取内部一致性和各现有快照之间的显式一致性；不证明跨TASK详情、guide、
advice的事务快照，不抵御有写权限的恶意OS对手，也不关闭SYSTEM-99其它缺口。
