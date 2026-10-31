# Codex全局指令修复的原生CI：新增步骤通过，旧Windows仍失败

源提交0ab7226fb9fccc5c3a9c2a1339bb969618caa16c，GitHub Actions run41167563794。五job的实际checkout SHA和完整解码日志已核对，新增test_codex_instruction_read步骤全部success；35方法执行中 **29通过、6跳过、0失败**。macOS/Ubuntu3.10/Ubuntu3.12各7通过，Windows3.10/3.12各4通过+3个明确POSIX场景跳过，不能把跳过当Windows链接/FIFO验收。

三个POSIX完整job成功，两Windows完整job失败。两个旧test_uninstall_text断言仍为写入CRLF却比较LF：new concurrent edit、locally edited agent；完整原失败日志保留。新步骤在旧失败之前确实运行，后续被跳过的其它步骤不算通过。新Codex读取范围没有原生失败，不使用第二源码候选额度，不改旧Windows测试或重置旧scope。

[jobs.json](jobs.json)/[summary.json](summary.json)保留真实job/step/计数与每份完整日志SHA。日志是GitHub工具解码文本的精确UTF8副本，BOM与Windows451/507个CRLF保留，没有压缩ZIP字节/截图审计或人为添加LF。此CI只认证声明的新七方法平台夹具，不验证实际宿主技能发现、模型遵从、任意并发/全事务、完整token/费用或最终任务质量。

原方案/代码与本机47+独立47、原revise和精确YAML机械闭环见[源修复报告](../codex-instruction-20261031/report.md)。没有额外实验/复审/服务/探针。CASE本次完整阅读新增1篇已经单独登记，同批历史64不再增加。后续新论文2610.34763v1仅实际读取15000/61061字符，Eq5后/实验结果/附录/独审未完，[准确续读检查点](next-reading-checkpoint.json)0credit，不能用摘要结论充抵全文。

下一步应从真实完整checkout的全角色安装/受管check与安装后工具实际导入链补足离线验收，再区分真实宿主/会话加载；先固定新范围与独立验收，不能用现有两Skill夹具或文件存在当全链成功，不重开旧model/backend预算。整个人类guide和唯一TASK不变，Plan64保持；SYSTEM99实际加载/全输入/终局质量/全费用/并发恢复/整体卸载继续open，本次不是整轮完成，没有性能提升主张。
