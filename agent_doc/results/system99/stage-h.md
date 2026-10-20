# SYSTEM-99 阶段H：现有上下文接口的离线token计数

Version8独立方案审核后测量；基线`874452cfba65b638bf95fbe314e7c4b391b027d2`。
本次固定当前三入口/TASK/顶层advice的编码计数，不是新增压缩算法或提速。
生产runtime、指令、目录、人类guide未改；SYSTEM-99仍未完成。

先查`advice task context correction dependency token quality`，limit6/max_scan5000：
scanned252、partial=true、81缺record等错误；候选advice-link、advice-context、
comm-pending-index及comm20旧批次不含当前源字节和编码条件，不复用其pass。
另由独审核对旧原生token候选亦不适用；不声称穷尽历史结果。

## 固定输入与结果

[测量脚本](context_token_probe.py)SHA256
`7b1134a3b9a286c66ef4611cd5b02bca175ac58f334fb494e9d7e19baa38f7cb`；
[原始计数/各源SHA](context-tokens.json)SHA256
`5046cab11f2be03a8efc3eb20ad52c2201c795979c3ea0d642fd6e5f87016a4b`。
tiktoken0.12.0、encode_ordinary、两种固定编码；每条编码后decode与原文相同。

| 输入边界 | cl100k_base tokens | o200k_base tokens |
| --- | ---: | ---: |
| 三入口全文，compose_entries关闭去重 | 26927 | 19749 |
| 同三入口，现有精确共享协议去重 | 19753 | 14591 |
| 全文返回对象，Python默认JSON序列化 | 27845 | 20708 |
| 去重返回对象，同JSON口径 | 20503 | 15376 |
| 完整TASK索引文本 | 22111 | 18533 |
| 显式SYSTEM-99 task_view文本 | 984 | 890 |
| 同task_view返回对象，含行号等的JSON | 3759 | 3666 |
| 顶层33份advice按路径加Document标题拼接 | 104966 | 83045 |

三入口按现有API选decision/general/research，去重只在本次组合中生效。
把共享指针展开后与完整prompt逐字节相等；只证明文本可恢复，不证明LLM
同等遵循。TASK视图省略316条任务行，且不含选中详情与依赖闭包；不能把
984或3759作为完整任务上下文成本，不能将不同scope相减称等价质量提升。
33份advice全读是明确的对照拼接，不代表生产宿主确实默认加载这些文件。
JSON数含当前绝对project_root及默认空格，不是工具传输流的实际计费token。

## 复现与验证边界

私有独立依赖目录安装`tiktoken==0.12.0`，不改项目依赖。在项目根执行：
`PYTHONPATH=.:.agent-runs/system99/tokenizer-lib TIKTOKEN_CACHE_DIR=.agent-runs/system99/tokenizer-cache python [-O] agent_doc/results/system99/context_token_probe.py`。
普通/-O结果JSON逐字节相同，stdout SHA256
`2b15febfd225c69700c8143fc3896de88282363aafb7f0cc5f32307adf2a7e24`。
初探JSON/日志另保留，正式结果未覆盖为唯一历史；27项prompt/task/advice原回归通过。
Python3.12.14、Linux6.18.55 x86_64/glibc2.39；编码资产SHA在原始JSON，
openai_public.py SHA256 `954392738e60d0fb6dca1dad80872efc47c8e2733babecbbf0a23970ed66c2cb`。
独立验收为[independent-stage-h.md](independent-stage-h.md)的usable-with-scope：
实际独立重跑JSON/stdout一致、所有源/编码资产SHA及直接参考核对通过；修改
协议/过期TASK/破坏展开三类负控通过，另34项相关回归通过。没有独立重跑全库。

没有chat framing、cache-read/write、输出、多轮重载或真实模型usage；编码名字
不表示当前Claude/Codex使用该编码。没有模型质量、延迟、总费用或真实宿主收益
主张，不依据静态计数删指令、缩掉异议/更正/依赖或迁移agent_doc。
[新正文阅读](research-f.md)支持等内容对照、分开过程与结果及检验力约束；
下一步仍需固定真实任务、实际加载链和可调用可信宿主，测遗漏及质量非退化。
