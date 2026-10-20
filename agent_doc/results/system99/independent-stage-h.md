# SYSTEM-99 阶段H独立审核

## Plan

结论：Version8 阶段H **approve**，仅限现有接口的离线编码计数、冻结输入及结果独立复核；不是模型质量/性能验收，也不是repository runtime认证回执。基线main `874452cfba65b638bf95fbe314e7c4b391b027d2`。已读AGENTS、决策/文档治理、双主、结果验收、精简工作流及实际Plan8；唯一TASK中SYSTEM-99仍未完成，GUIDE为空且只读。

| 七域 | 判断与依据 |
| --- | --- |
| intent | pass：用实际tokenizer而非文件大小观察上下文，服务已声明加载成本缺口，不改用户目标。 |
| guide | pass：不写人类目录，不另造任务清单，不以advice授权迁移。 |
| assumptions | pass：当前三入口、显式SYSTEM-99导航及顶层33份advice可读；编码是离线代理，不假定真实宿主加载这些文本。 |
| prior_results | pass：实际查询下述旧记录只支持其它语料/原生短调用；不能复用为当前源码/语料计数或质量证据。 |
| acceptance | pass：固定tiktoken0.12.0、两种编码、输入/源码hash，展开协议后精确相等，分开JSON与文本；正式数据须再跑并独立复核。 |
| risk | pass：只读源码和CPU编码，输出在现有运行记录，不改runtime/指令/schema；导航删掉其它任务不当等价知识。 |
| resources | pass：仅已安装私有依赖及缓存、本地CPU，无模型/GPU/付费任务；真实宿主/质量/总成本继续open。 |

先查：`advice context token prompt deduplicate task scope`，limit6/max_scan5000，scanned252、partial=true、81读取错误。候选token-fifty-01-r2、02、03-r2、04、06及token-five-1；另实际show 02、03-r2和five-1的summary/冻结条件。它们是合成NDJSON、其它显示合同及旧原生短调用，不是当前三入口/TASK/advice语料。未授信或宣称历史检索完整。

最终审查脚本`context_token_probe.py` SHA256 `7b1134a3b9a286c66ef4611cd5b02bca175ac58f334fb494e9d7e19baa38f7cb`；先前fba2版本仅加元数据前审查，正式未跑。新增probe自身SHA、Python/平台和编码缓存hash属于同一观察范围。展开检查只证当前文本可恢复，不能证明LLM同等遵循；`encode_ordinary`排除chat framing、cache及输出。任务视图不含所选详情和依赖闭包，顶层advice全读不是当前生产加载链；不得从计数相减宣称等价质量或总费用降低。实际JSON的绝对project_root亦进入计数，复跑须同根或注明差异。

执行前保留初探JSON/日志，不把正式结果覆盖为唯一历史。正式记录应补脚本与真实依赖源码、tokenizer版本/编码资产和输出hash；所有正式结果仍待下节独立验收。没有生产变更，不需把已验全库重跑作为本观察的收益证据。

## Final

结论：**usable-with-scope**，接受阶段H的当前源字节、两种离线编码计数及可恢复性观察；未发现本范围发布阻塞，不接受模型质量、性能、费用或整批完成主张。

正式脚本SHA仍为`7b1134a3b9a286c66ef4611cd5b02bca175ac58f334fb494e9d7e19baa38f7cb`；实际运行同一脚本，未改算法或公共输出。私有重跑JSON与公共冻结`context-tokens.json`逐字节相同，SHA256
`5046cab11f2be03a8efc3eb20ad52c2201c795979c3ea0d642fd6e5f87016a4b`。
独立stdout与主控普通/-O日志同为
`2b15febfd225c69700c8143fc3896de88282363aafb7f0cc5f32307adf2a7e24`。
重跑只写原脚本的私有输出，并另存`independent-context-tokens.json`，未覆盖公共冻结结果。

实际命令（项目根）：

```text
PYTHONPATH=.:.agent-runs/system99/tokenizer-lib TIKTOKEN_CACHE_DIR=.agent-runs/system99/tokenizer-cache python agent_doc/results/system99/context_token_probe.py
python -m unittest tests.test_prompt_context tests.test_task_context tests.test_advice_context tests.test_advice_context_scope -v
```

| 检查 | 实际结果与边界 |
| --- | --- |
| implementation | 逐行审查脚本及真实compose_entries/task_view；生产两模块未改。两模块SHA分别为a897b5ac60584f07be47de7f163c7993a7b93654a9a0737e34923a1f3584b618、d03ac5314bac5df15e0892d2fa9fa9854a138ef6dcdcc75d621766c9d8b34870。 |
| reference_boundary | 另按原始三文件直接拼接，与关闭去重的实际prompt逐字相等；用encode(disallowed_special=())另核两编码计数。临时修改research协议时完整保留、TASK修改拒旧SHA；内存删compact首字符使实际probe展开断言失败。未改磁盘生产源码。 |
| data_integrity | 3个prompt、33份顶层advice、TASK各SHA与当前读取原字节相同；8行计数、316省略任务行及展开相等均复现。文本/JSON分母分开，没有把全索引与局部视图当同内容。 |
| numerical_sanity | 所有token计数为有限非负整数；每个编码decode回原文本。表中各行两列与原始JSON逐项一致，JSON字段开销未省略。 |
| measurement_validity | 仅固定编码器的确定性离线计数；计时、模型成功率、cache、usage/费用不适用且未声称测得。当前JSON绝对路径与序列化方式进入实际计数，不推广其它宿主。 |
| reproducibility | Python3.12.14、tiktoken0.12.0实际重跑完全一致；另独立34项相关回归通过、0.170s。没有独立重跑全库，无新增生产实现。 |

编码缓存SHA223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7、446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d与安装包openai_public.py内置expected_hash相同；该文件SHA为`954392738e60d0fb6dca1dad80872efc47c8e2733babecbbf0a23970ed66c2cb`。
独立边界探针日志SHA`78aaa8c020ab98ccf77051887b4b8c4d566715faa655607f703b22af7b68b305`；34项日志SHA`775862832721ca4dcc1b5a0a6ea70cb89c48da21696c6197487b82b5b3fc518e`，保留在私有运行目录，不冒充原生模型调用。

已核对stage-h表格与限制，建议的“首次”改为“本次”已由主控采纳；partial查询不能证明首次。research-f只核记录的适用边界及论文PDF SHA，不宣称本审核者重新全文精读或复现作者实验。任务视图不是完整任务包，advice全拼接不是默认加载事实；文本可恢复也不证明LLM同等遵循。真实宿主、任务质量、跨会话总成本及更正/异议/依赖召回仍待验，SYSTEM-99继续未完成。
