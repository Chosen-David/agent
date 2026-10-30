# Native uninstall-text verification — Windows incomplete

b619914cf128f156aa520613eda208abc0d25f09 / CI41053775012。
三个POSIX job成功，每组新5方法通过；两Windows job失败，各3拒绝方法通过、2编辑保留方法失败。合计新方法21pass/4fail/0skip，不是五组全绿或55/job。

完整解码日志与精确哈希见native-verification.json。日志由GitHub工具解码并经apply_patch多一个末尾LF；不是原始压缩归档字节。两失败明确为测试write_text生成CRLF与固定LF字节oracle不等；这是主控结合实际日志/测试源码的诊断，未获新的独审/重测，不称生产实现已通过Windows完整验收。后续步骤因失败未运行，也不视为通过。

unexecuted-test-candidate.txt只将两处测试夹具写入换成显式LF write_bytes，保留相同精确字节oracle；未应用、导入、执行或发布为生效源码。受管setup.py没有此候选改动。
本次源码CI提交1/1已用。遵守workflows/dual_main_workflow.md“耗尽时停止依赖分支并请求明确重编排”，不增加额度、换ID或以文档提交重跑冒充验收。需明确新的授权预算边界及有权限宿主保留旧反馈/消耗/作用后接续；原本机55/独立55只支持其限定范围。

本包为只读证据/未实施候选，非新实验或运行门禁。整卸载事务/并发/IOfailure恢复和SYSTEM99的宿主、质量、全费用仍open；不修改原报告/guide/TASK或宣称性能提升。后续文档CI可能重复已知失败，不能当作修正重试或旧失败消除。
