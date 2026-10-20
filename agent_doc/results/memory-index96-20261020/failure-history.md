# 未接受观测、修复与环境边界

- `focused.log`：初次Windows 45项有4个cleanup错误。新测试的backup连接只用SQLite事务context未close，已改closing；旧CLI测试同类连接问题经独立远端基线复现后修复。原始日志为PowerShell捕获的UTF-16，部分系统错误已被宿主代码页替换，不能冒称无损stderr。
- `focused-wsl.log`：旧测试在Python3.14下将ResourceWarning混入JSON，独立baseline/candidate均复现。`tests/test_memory_cli_input.py`只修连接归属，不过滤warnings；新功能默认业务接口未变。
- `raw.json`/`raw-tokens.json`及对应旧manifest：v1/v2计算的是LF逻辑响应；不能支持“Windows原生binary stdout”主张。独立复核指出原index字符预算也少留一个CRLF字符；最终代码按os.linesep计预算，新测试使用真实subprocess。上述旧结果未接受，旧hash随最终代码变化失效。
- `raw-native-v3-attempt1/2.json`保留后续待验收观测。补tokenizer真实身份、规范化project_docs源码换行后重新测量并冻结当前v3。重冻结前两份v3 manifest/contract未逐份保存原字节；这一归档缺口明确保留，不能把旧raw当完整冻结证明或复用其通过标签。最终v3 manifest冻结后不再改写。
- `all-wsl.log`：首次WSL挂载盘上的修前测试运行很慢，已精确停止本会话自己的session；未完成，不能作为通过。未停止任何既有维护任务。
- `final-all-wsl.log`：隔离副本Python3.14.4运行1357项，6fail/1error/12skip。六个fail来自未改的深JSON测试；独立基线同样7项中6fail，JSON decoder在该环境可解析10000层，不再触发旧RecursionError预期。1error是缺fitz，Reader也因缺依赖未导入。该全库检查确实失败，不以本轮功能通过替代。
- `final-native-reader-core.log`：Windows默认GBK读取UTF8产物失败；启用实际UTF8模式后 `final-native-reader-core-utf8.log` 的2项通过。隔离PyMuPDF==1.26.7后 `final-native-reader.log` 的3项应用测试通过；没有改变系统Python包或生产配置。
- `environment-retry.json`：一次WSL隔离环境下载uv==0.13.3，在预设90秒超时后停止。没有取得WSL Python3.12完整全绿结果，不追加无界网络重试。最终测试的临时WSL目录随后已不可访问；保留实际执行时源码hash、命令和完整日志，不宣称该临时目录仍在。原项目未移动，scratch tar位于ignored `.agent-runs/memory-index96-final-checks/`。
- 独立检查器自身首版mutation未commit、第一次临时目录读取失败，见 `independent-harness*` / `independent-regression-attempt1.md`；是验证器修复，不伪记为实现缺陷或丢弃负记录。
- 远端并发 `dcc10b1` 已快进整合，其新增精简规则测试3项通过；上游通过数字不转抄成本轮实测。最终仅按本轮独立review给出的范围解释结果。
