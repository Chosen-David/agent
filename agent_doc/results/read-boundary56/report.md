# READ-BOUNDARY-56：知识文件实际读取字节上限

日期：2026-10-19。基线 `ffd9abfeb2264a21e46322e4bedf310947229b2b`；只涉及 Chosen-David/agent。代码、测试及测量脚本哈希见 [environment.json](environment.json)。

## 问题与修复

`agent_runtime/knowledge.py` 基线 115–120 行及 `agent_runtime/knowledge_ingest.py` 22–26 行在检查 stat 大小后直接 `read_text`。普通文件在检查后增长，实际读取无界；文本换行归一化还会缩短导入正文，使后续 staging 的大小检查无法发现原始输入超限。不是假设的漏洞：四入口（语料元数据、语料正文、导入元数据、导入正文）各 +1/+4096 的八个确定性场景均在基线接受。

修复在 `knowledge.py:40–49` 增加 `_read_utf8_bounded`，调用者保留原有路径/stat 预检，在真正读取时最多请求 `MAX_BYTES+1` 字节，按实际返回长度先拒绝超限，再严格 UTF-8 解码并保留 CRLF/CR→LF 行为。`knowledge.py:127–132` 与导入入口共享实现，独立插件镜像逐字节同步。原诊断 `entry/import exceeds byte budget` 保持。非法超限编码优先报告预算错误，边界内非法编码仍为 UnicodeDecodeError。

这限制的是 Python 返回的原始字节缓冲；默认 BufferedReader 可能物理 read-ahead，不能称内核 I/O 精确上限。未解决恶意路径替换、原子文件快照、无限增长语料总大小或全应用内存上限。

## 修前修后证据

冻结 [plan_v1.md](plan_v1.md) 经 [独立计划审核](plan_review.md) 后执行，结果与摘要可复查：

| 检查 | 修前 | 修后 |
| --- | --- | --- |
| 四入口×两增长量，输入先恰好 1,048,576 字节 | 超限接受 8/8 | 超限接受 0/8，拒绝 8/8 |
| 上述目标 Python read 请求 | `read(-1)` | `read(1048577)`，返回 1048577 字节 |
| 针对性测试 | 5 tests，8 failures + 1 error | 5 tests，OK |
| 合法文本/正常导入 | 对照路径 | 空/短/精确上限、ASCII/UTF-8、CRLF/CR、Unicode分隔符、hash/snapshot兼容 |
| 插件 | 原有路径 | 复制后 `python -I` 实际 ingest 通过，两个镜像字节一致 |
| 总回归 | 未重复宣称旧结果 | 1290 tests，OK，8 skipped；Reader 3 tests，OK |

[before.log](before.log) 保留原失败；[after.log](after.log)、[full-tests.log](full-tests.log)、[reader-tests.log](reader-tests.log) 保存本轮结果。每个增长 hook 仅在预检后的实际 open 时注入；修后还断言读取请求/返回长度。导入拒绝前后语料字节与目录不变。正常导入以原 `read_text` 行为对照 metadata/body provenance hash、全部记录及 snapshot。

[measure.py](measure.py) 从固定 git SHA 加载原函数，再与当前函数运行相同 fixture；[measurements.json](measurements.json) 保存每个原始/增长后输入 SHA-256、实际文件大小、接受状态、异常及 read 记录。旧版返回长度是**已归一化文本字符数**，新版是字节，不能将两列相减作 I/O 或内存收益。这里没有壁钟、LLM token、质量评分或端到端速度改善结论；全量测试耗时仅为执行记录。

复现（仓库根目录）：

```sh
python -m unittest discover -s tests -p test_knowledge_read_boundary.py -v
python agent_doc/results/read-boundary56/measure.py
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
python scripts/sync_plugin_references.py --check
git -c core.whitespace=cr-at-eol diff --check HEAD^ HEAD -- . ':(exclude)*.log'
```

环境：Linux x86_64，AMD EPYC 9V74，Python 3.12.14/Clang 22.1.3；本修复仅标准库文件读取，不涉及 GPU/kernel、第三方框架或模型调用。原 CRLF 文件保持，默认 git 空白检查将 CR 报为行末空白，因此使用 cr-at-eol 检查。原始 before.log 第4行含 unittest 产生的行末空格，暂存后全范围 diff 检查会报告它；原始日志及哈希保持不改，源码/文档检查显式排除 *.log。

## 文献与采用边界

[研究 A](research_a.md) 与 [研究 B](research_b.md) 合计十篇原始正文方法、实验、消融或缺失消融及限制定向精读：AgentChaos、ACON、AgentFold、AgentFly、Reflexion、MemGPT、Mem0、MemoryBank、A-Mem、MEM1。不是十项模型复现，也不是完整 PDF 视觉审读。2608.14680 原文不可访问，明确未计数。

本轮适配 AgentChaos 的真实故障触发核验与 Reflexion 中可信失败证据的评估原则；具体字节读取修复为本库工程实现，不伪称论文算法创新。其他语义记忆/压缩/训练算法暂缓，原因是它们不能替代应用层字节契约，且缺同模型任务质量验证。原论文速度、token和质量数字均未转记为本库收益。

## 历史与未完成边界

实际 prior-search 扫描 236，partial=true 且有缺失记录。四个候选 stored pending，一个历史 usable-with-scope，均与本次读取窗口不适用；不宣称全历史无结果。旧 scratch 原始证据不可用，因此重新保存修前失败，未覆盖历史报告。以前接受的超限输入可能影响旧导入有效性判断；现有内容语义未改变，不重写知识数据或历史实验，只修复之后的读取拒绝行为。

本地 flock 用于互斥，tmux 不可用；没有伪造常驻监督器、ReviewSession 认证或托管执行回调。完整计划仍由真实独立上下文复核。执行中 Reader 短测与全量测试尾段重叠，已在任务进展记录；没有以该并发时段计时作优化依据。

[独立结果审核](result_review.md) 六项均 pass：独立旧新对照、六项导入编码边界、343种换行组合及115条语料完全一致。验证者独立重跑针对性测试，读取并核对主控全量日志，不冒称自己重跑全部1290项。main 发布与远端回读在此提交形成后执行，最终回执另报；没有验证的模型能力不计完成。
