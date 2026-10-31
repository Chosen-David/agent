# 修复 Windows CI 字节夹具错误

用户本次明确要求处理持续CI失败、将调研落实为改进。最新基线28d5d308/CI41175540017，Windows3.12 job124462205129的完整原日志私有保留：SHA256 eeb9329b692ec04baa0ee8a919018382bbe872dcf168bec3b6a62ba74e8d830a，45527bytes，BOM/453CRLF未转换；GitHub原日志可从该job读取。两失败分别actual `new concurrent edit\r\n`/`locally edited agent\r\n`，expected固定LF。Windows3.10亦失败于相同步骤，不以相同step替代其逐行日志核查。

只将tests/test_uninstall_text.py两处write_text改为显式write_bytes，同内容/同LF期望；全部断言和生产/工作流不变，不skip或放宽比较。本机与[独立复跑](review.json)各11方法通过，完整[本机](local-tests.log)/[独立](independent-tests.log)日志保留，各一次无重试。Linux结果不能当Windows验收；新源码原生CI另核。不是性能提升或论文算法应用，本次先修验收基础设施。

旧一次CI/审核预算原历史保持，不覆写或退款；此为用户当前明确CI修复要求下的窄范围执行。SYSTEM99继续同批，论文精读仍67，CAVERT仍partial。后续优先把既有文献形成可证伪实现候选与同条件任务质量/实际上下文/全角色成本对照；仅新增读记不算优化成果。必需独审/guide/唯一TASK和未测门禁不因此放宽。
