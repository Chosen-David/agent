# Codex全局指令读取修复：本机边界通过，原生平台另核

scripts/setup_codex.py原来在初读、锁下重查和写后验证直接read_bytes。已有静态非普通文件守卫不覆盖检查后替换，也没有大小上限。现三处复用未改动的regular_bytes，保留缺文件、raw bytes、受管区块/偏好/所有权/人类guide守卫；新增16MiB读取及合并输出上限，超限拒绝而非截断。合并输出预检先于state/锁/备份/技能写入。此前任意大文件现在会被拒绝，这是明确新增兼容边界；恰16MiB的已配置完整文件可同步/检查。不是总内存上限、全部安装文件边界、任意竞争或整个同步事务保证。

独立方案[原完整approve](frozen/08-plan-review-v1.json.txt)后按冻结源码/七方法执行。修前七方法有五个判别方法触发六个失败断言：超限CLI同步/检查两子断言、合并超限、is_file后FIFO、锁前FIFO、is_file后链接；两兼容控制通过。两FIFO各在3秒join后由测试终止并join其自有子进程，不留此类挂起进程。修后同新方法加三个相邻模块 **47/47通过**；一次独立同命令执行 **47/47通过、0fail/error/skip**。完整原日志、环境、源码/测试/方案和原版本字节通过[evidence-index.json](evidence-index.json)映射，24原引用21份去重公共快照，不将dedup当token收益。

[原六域独审](independent-review.json)实际结论 **revise**：代码和本机回归usable-with-scope，但主控最初将macOS新run插到旧legacy步骤与env之间，造成旧TMPDIR归属改变。原无效YAML/反馈不改写。原审明确许可精确hash绑定的机械纠正；现恢复旧env，给新步骤独立同TMPDIR，完整更正SHA dea2558d39851ff69f83cd9615b327b960e032277d1ad7f42a2030fd6d68e2e7。[reconciliation.json](reconciliation.json)保留原revise，按原审条件验证：去掉恰两个新步骤后完整YAML解析对象与base相同，全部旧steps/env/顺序不变，其余23原引用及生产源码/测试不变。仅关闭R1，不补造第二独审或重跑47；[原workflow](baseline-workflow.yml.txt)与[纠正版](corrected-workflow.yml.txt)均保留，真实五job新步骤尚需原生日志。

边界：七方法只注入两个POSIX FIFO阶段和一个POSIX链接阶段；写后读取仅正常路径覆盖，不称任意Windows最终链接竞争/敌对父路径或后续I/O回滚。空state目录可能由锁前重查失败留下，测试不声称整个文件系统零创建。普通raw二进制/CRLF偏好原字节保留，不加UTF8规范化。旧helper FD行为、installed_files无界读取、setup.py整体事务与原Windows卸载失败均不在本修复内，未改/未重跑旧冻结范围。

方案1/max2已用，无需第二审；baseline/fixed/independent各1/max1已用；原deadline2026-10-31T04:56:16.419636Z内，原生源码CI最多2提交仅本scope真实失败才考虑第二次。Plan63→64仅新增本scope；唯一TASK和整个人类guide不变。本机Linux3.12，原生CI结果另记，原始elapsed只是调试元数据：baseline7与fixed47不同，不能比较为加速。没有模型/后端/服务、真实会话加载/任务质量/token或全角色费用测量，手工独立角色非受信runtime认证。

CASE2610.38800v1另完成正文及独审，与本修复无算法因果关系，不能称论文性能应用。同批历史63→64只新增一篇；旧三包六私有原件缺失、2610.39790v1过期缺独审0credit及全部旧scope失败/耗尽边界保持。SYSTEM99真实宿主/全输入/终局质量/全费用/并发恢复/整体卸载仍open；本次是实际可靠性修复检查点，不算整轮完成。
