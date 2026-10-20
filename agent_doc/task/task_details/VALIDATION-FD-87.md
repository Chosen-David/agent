# VALIDATION-FD-87：显示回执异常路径资源释放

Task-ID: VALIDATION-FD-87
Date: 2026-10-20

## Plan

用户授权Agent可靠性改进及验收后直推main；基线80e7bf3ba8de99e0aee55505091172c6a5816c40。[冻结方案](../../results/validation-fd87/plan.md)明确仅write_validation_context资源所有权和回归，不改变信任/预算/路径契约，不自动清理失败回执，不承诺原子性。GUIDE为空且只读；独立检出、锁及明确文件发布。主AI生产→独立验收→报告；无部署监督服务或ManagedEngine回执，独立宿主角色承担本有界验证。

## Progress

独立计划审核validation_fd87_review批准有界本地实现/测试。8个新测试修前3失败：构造OSError、构造中断和context进入失败后fd仍存活；其余控制通过。已加closefd=False借用及finally释放，待普通/-O/全库/Reader与独立结果验收。修复后不覆盖或删除失败文件；磁盘失败残留及重试冲突仍需单独恢复协议。

最终验收：普通/-O专项各32项、全库1331项（1323通过、8跳过）、Reader3通过。独立20组/臂配对中19次成功open，泄漏12→0，候选19次close；独立专项47项通过，真实fsync/异常身份/三种状态字节/不完整文件重试拒绝均核验。[独立报告](../../results/validation-fd87/review.md)结论usable-with-scope；无速度、质量或持久化成功率外推。发布前fetch仍为80e7bf3b；仅暂存本轮明确文件，采用已连接GitHub接口原子非强制更新并回读，未回读前不声称发布成功。
