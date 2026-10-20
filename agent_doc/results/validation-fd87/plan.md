# VALIDATION-FD-87：显示回执写入的描述符所有权

基线 `80e7bf3ba8de99e0aee55505091172c6a5816c40`；独立干净检出 agent-audit87，持有 /tmp/agent-audit.lock。GUIDE为空且只读。仅Agent，保留其他检出/未提交工作。用户授权可靠性优化及验收后main发布。

VERIFY_OR_ASK → 低风险本地验证：`write_validation_context` 已获得真实fd后才构造文件对象，构造异常没有外层释放。先新增故障注入测试保存基线失败，再采用本库已验收的原始fd独占/closefd=False借用/finally关闭模式。仅该函数、测试、本轮证据/任务文档；不重构所有IO，不改结果验收或信任语义，不自动删除/覆盖失败文件，不承诺原子发布。

固定指标：注入构造异常后本调用所开fd仍存活数量应由1降为0；成功、write/flush/fsync失败同样关闭且异常透传。正常回执字节、幂等性、完整restore及pending/invalid不变。只用独立临时目录、标准库CPU，无模型/API/GPU/付费资源。先专项普通/-O，再全库与Reader；独立角色检查代码、故障确实触发、精确fd状态、原始日志和未覆盖边界后才发布。主AI生产→独立verify_experiment_result→报告/发布；不是ManagedEngine回执，不宣称部署监督服务（无可信宿主adapter）。

历史查询：result_store search 'memory context schema' 和 'validation context descriptor' --limit 5/3 --max-scan 200，均scanned199、partial=true及缺record错误；词法命中不支持本写入故障。直接读artifact-fd77/independent.md和ARTIFACT-FD-77详情：仅_read bytes范围，不覆盖此writer；adapt单一fd所有权，拒用旧计数作新测量。check-helper85/context-schema83已完成，不重复为新成果。

研究入口：2026-10-20检索并读 arXiv:2610.16067v1 (2026-10-12) 方法§3.2、结果§4.1、限制§6。采用异常路径状态/资源不变量及已知答案对照的工程启发，不采用其模型得分作本库收益；其跨框架迁移有条件。Python官方os.fdopen/open(closefd)契约及本库实现为直接依据。此前十篇阅读留存read-boundary56/research_a.md、research_b.md；本轮不虚称新读十篇。

独立reviewer只写本目录independent*及review.md；主AI唯一维护源码/测试/TASK。发布前fetch，显式暂存，原子非强制main更新，回读SHA/tree。
