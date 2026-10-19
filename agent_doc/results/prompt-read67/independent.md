# PROMPT-READ-67 独立复核

独立检查者：`/root/prompt_read67_verify`。范围：`agent_runtime/prompt_context.py` 的 prompt 文件读取边界；不修改生产代码，不执行发布。

已独立阅读 AGENTS、decision_review、result_validation、实际 `_read` / `compose_entries`、CLI 调用入口及既有/新增测试。定向历史检索 `prompt.*read|prompt.*limit|prompt-context` 未得到可替代本次复现的同路径结果；非穷尽检索。主测报告未作为独立通过依据。

## 缺陷与路径

旧 `_read` 使用 `Path.read_bytes()`，在 `len(raw)>1000000` 拒绝之前无大小限制地读完文件。独立包装真实文件句柄记录 `read()` 参数，1,000,001、4,194,304、16,777,216 字节输入均得到无参数 read，返回完整输入。`compose_entries(root,['general'])` 也先读取 canonical decision，独立复现同样先读入16MiB再拒绝；`scripts/prompt_context.py` 调用该接口。内容最终拒绝正确，缺陷是拒绝前的读取/分配预算失效。

候选仅改为二进制 `read(1000001)`，随后保留原长度判断、UTF-8解码及原始字节SHA256。接受阈值没有放宽。检查时生产文件SHA256：`303c762d2345e12e0f6d955b15288e3400d8a7c2b6c19f8ab23282c9bd73d92b`。

## 实际验证

在同一Python进程加载 audit64 基线与 audit67 候选，临时普通文件生成在 tracemalloc 启动之前。独立脚本比较完整返回值或异常类型/文本，12项一致：空、CRLF/CR混合换行、中文/emoji、BOM、非法UTF8、999999/1000000/1000001/16777216字节、缺失文件、目录、符号链接。另在相同三入口夹具上比较3种选择×2种去重开关，6项完整 compose 字典一致。

原始短输出：

```text
read_compatibility_cases 12
compose_compatibility_cases 6
baseline ('ValueError', 'prompt source exceeds byte limit') peak_python_bytes 16782174
candidate ('ValueError', 'prompt source exceeds byte limit') peak_python_bytes 1005226
candidate_reads [[[1000001], 1000001]]
python -m unittest tests.test_prompt_read_bound -v
Ran 3 tests in 0.007s
OK
```

结论：usable-with-scope。16MiB拒绝输入的Python追踪峰值由16,782,174降至1,005,226字节，且实际read只请求/返回1,000,001字节；支持拒绝路径的有界分配改进。两者仍返回相同拒绝异常。该测量包含 `_read` 校验/异常包装，不包括输入生成，单次诊断不证明延迟、RSS、模型token成本或完整任务性能。未复现并发文件替换/恶意TOCTOU，不声称此补丁提供OS沙箱；未独立运行全库回归或真实LLM任务。生产者全库日志需由主控另行核对，不能由这3项测试推断全库通过。
