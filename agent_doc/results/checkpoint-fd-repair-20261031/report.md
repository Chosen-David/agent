# Checkpoint FD ownership repair

`task_manifest.atomic_json` 在 fdopen 构造入口抛错时未关闭 mkstemp 返回的原FD。修复让流以 closefd=False 借用，由创建者 inner finally 在第二次guard/replace前关闭；JSON/UTF8/默认平台换行/flush/fsync/原子替换/临时清理及人类guide守卫保留。未引入第二实现或新依赖。接口语义参考[Python open文档](https://docs.python.org/3.12/library/functions.html#open)。

复用旧v2测试方案（平台物理换行oracle），保留所有旧失败和完整revise。当前源码hash与旧诊断相同；本次3方法baseline是当前集成确认，不是新缺陷：一个构造故障方法下，既存/不存在目标两FD断言失败，正常Unicode与NaN控制通过。修后与独立各48方法exit0，0error/failure/skip；真实fstat在测试自身清理/重试前确认FD已关闭，旧字节/临时名/异常身份/撤销故障后完整重试仍验。完整[输入映射、方案/六域原反馈与三组原始流](evidence-index.json)可回读。

本次是既有用户授权可靠性修复的明确有界补充：plan1/baseline1/fixed1/independent-review1/independent48-run1/sourceCI1，自动retry0，10:35Z截止；旧manual1of1/revise/原deadline不改写或退款。Plan65→66仅新增此范围，唯一TASK/guide不变。手工独立host审核usable-with-scope，不冒称受认证ReviewSession迁移；历史登记unknown。

原生五job新增3方法的实际结果在本冻结报告时待新提交验证；本机48不替代Windows/macOS验收。计时只是测试元数据，无速度/自然FD故障发生率/实际耗尽/模型质量或全角色费用结论。close/unlink失败、恶意FD复用/父路径竞态、断电/全事务/真实tmux或SSH未验；同一SYSTEM-99继续open。
