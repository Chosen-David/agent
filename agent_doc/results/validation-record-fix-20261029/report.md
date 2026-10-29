# 验收显示记录：暂存完成后不覆盖发布，失败后同请求可恢复

SYSTEM-99 / Version55，修复已独审诊断d023cfef的显示记录恢复缺口。只原地改write_validation_context及四个必要新测试；无schema、默认输出/存储字节、来源SHA或结果授信协议变化。整个系统批次尚未完成。

## 变化与同条件证据

旧实现先创建最终validation-<SHA>.json再写入，构造/部分write失败会留下坏文件并阻断恢复。现在先同目录私有mkstemp，write/flush/fsync并关闭本方FD后重新guard，以link不覆盖发布。任何EIO/ENOTSUP均闭合报错，不使用覆盖fallback；仅相同完整字节的已有或竞争记录幂等接受，异字节拒绝且不修改。已存在记录不为幂等重新fsync/link；本方temp在finally清理。没有自动删除/修复用户已有坏记录。

一轮独立方案审核批准后固定测试，保留修前完整日志：baseline精确旧9方法+A共10，exit1，7失败断言均来自A、0error/skip，旧9方法通过。7项是四个阶段最终残留、construct/partial-write两项无人工删除恢复拒绝、fsync前最终可见一项，不是7个独立根因；flush/fsync撤销故障后的retry本来能通过。B/C/D是新发布机制专项，只fixed/independent执行，不以旧实现没有link回调当缺陷，也不比较两套总方法数为收益。

修后及独立唯一一次复跑均执行tests.test_validation_context、tests.test_result_validation、tests.test_local_path_guards：39方法，37通过、2明确native Windows junction skip；四新方法全执行通过无skip。共同A的上述恢复性质修后通过。固定原始stdout/stderr、源码/测试快照、实际argv/环境/起止/所有SHA及独立逐项验收保留；未运行旧2059脚本、旧全库/PID/alias/role/model额度或额外变体。

| 新方法范围 | 实际检查 |
| --- | --- |
| A staging failures | construct、部分write、flush、fsync注入；FD为EBADF，fsync前无final，本方temp/final无失败残留，故障撤销后完整恢复。 |
| B publication errors | EIO/ENOTSUP保留errno、只调用一次link、无覆盖fallback、无final/temp，撤销后可恢复。 |
| C deterministic publish-point races | 同/异字节竞争目标原字节与inode保持，只有同字节接受，私有暂存权限和清理；不是压力并发或所有竞态覆盖。 |
| D existing idempotency | 已有同字节记录不需要新的fsync/link；既有修改记录保护另由旧回归保持。 |

既有真实CLI pending退出2、完整Unicode观察值/错误协议/恢复显示、独立result gate和path负控均通过。这里是临时本地回归，不是实际可信后端或模型任务。

## 冻结协议、发布与范围

plan-v1是事前冻结版本；其中“macOS job只测ingest”措辞经独审指出不精确：它还测usage/setup等，但不运行validation_context，本修复macOS原生覆盖未取得。实际portable-install四个Ubuntu/Windows×Py3.10/3.12 job会运行完整validation_context模块，新增4方法随其进入；新提交CI与普通main回读另核，当前证据仅本机Linux/Py3.12。

源码逐字匹配批准替换块和tempfile import，测试匹配冻结fragment，序列化/哈希/错误/显示和live验收边界未变。采用既有ResultStore._save的标准库暂存/link模式，不调用其不同schema接口或建立平行writer。fixed-source.txt/baseline-source.txt/tests-source.txt为不可执行证据快照，不是运行时旧实现副本；实际命令与源码路径见inputs/independent-execution。

独立报告usable-with-scope接受限定代码/数据，五项检查pass、无性能measure N/A；手工意见非可信runtime回执。历史登记仍unknown/null/context{}，不因本回归产生用户更正确认或结果授信。正式prior查询336目录partial=true/25errors，旧诊断只复用来源机制、两个corpus候选拒绝适用，不把部分查询当全历史闭包。

只承诺被注入的四种暂存失败及两种link失败边界。FD-close/unlink失败未注入；link已发布成功后cleanup失败可以报错而完整记录保留，之后仍严格幂等。父目录/暂存inode敌意替换、目录fsync/断电持久性、全事务、真实并发压力/宿主、任务质量/token/费用均未验证。原生平台尚待CI，不把“37通过”说成39无skip或整个项目无bug。

方案实际1次（上限2），baseline/fixed/independent各1已用完，单命令120秒/分支300秒/共享1200秒，未重试。唯一TASK的55/AK更新及Progress串行维护，guide只读；40篇同批正文不增计，全部旧耗尽/暂停门禁保持。此局部可靠性修复和发布检查点不计新一轮完成，SYSTEM99其余系统级未决继续open。
