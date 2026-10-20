# MEM-INDEX-96：记忆目录与存储观察

新增显式 `index` 分页导航：不再为浏览目录反复返回所选记忆正文，原文留在唯一私有SQLite账本。目录保留全部非content字段及内容/条目哈希；项目、过滤条件和完整所选条目绑定snapshot，更正或条目变化后拒绝旧翻页。实际使用仍经过 `check` / `basis_context` 当前依赖校验。

新增 `storage` 查看逻辑页、空闲页、状态和索引名；不执行压缩、删缓存或删记忆。它只观察SQL状态，WAL/SHM和并发文件大小限制见[独立验收](independent-review.md)。默认list/check/history行为不变。本轮没有额外持久摘要或“模型已读”缓存。

```bash
python -m agent_runtime.project_memory --root ABSOLUTE_PROJECT_ROOT index --scope TASK_ID --limit 20
python -m agent_runtime.project_memory --root ABSOLUTE_PROJECT_ROOT index --scope TASK_ID --after-id LAST_ID --snapshot EXACT_SHA256
python -m agent_runtime.project_memory --root ABSOLUTE_PROJECT_ROOT check REQUIRED_ID
python -m agent_runtime.project_memory --root ABSOLUTE_PROJECT_ROOT storage
```

后续页保持相同status/scope；`partial`/`next_after_id`表示还有页。目录不判断语义相关性，不能从来源或evidence标记直接推断正文有效。超出字符预算只返回完整条目，首项放不下则报错。索引每页仍读完整选择并重算快照，不主张数据库/CPU提速。

本轮定向精读 MemGPT、LongMemEval、KVFlow 的相关方法/实验正文，阅读范围和采用/拒绝理由见[研究记录](research.md)；未宣称通读附录或完成十篇批次。

当前两个native-v3结果经真实独立上下文完成六域验收，主宿主核对该调用及固定review哈希后显式注入，`inspect_result`返回usable-with-scope，见 `accepted-native-v3-{bytes,tokens}.json`。JSON文件自身不是身份凭据；未来消费仍重新核对来源和真实独立验证。

| 合成用例（24条，全部目录页计入） | 完整list → 目录+必要读取，UTF8字节 | 同一文本o200k_base tokens |
| --- | ---: | ---: |
| 长正文，读取1条 | 238805 → 20341 | 54147 → 6116 |
| 长正文，读取全部 | 238805 → 249411 | 54147 → 58073 |
| 短正文，读取1条 | 8659 → 10861 | 2595 → 3947 |

这是固定tiktoken==0.12.0、真实UTF8子进程stdout且保留原生CRLF的载荷计数；所有分页和声明所需正文回复均已计入。未计CLI请求/tool包装、会话历史、推理和回答，不是模型总tokens/收费或任务质量；临时路径的具体文字、长度及衍生snapshot都影响token数。短文和全量读取更贵，故只提供显式导航，success_count不增加。

验证：原生专项45项、-O新11项、独立180组合/变更失效/真实pipe预算/WAL检查通过；独立重构主测及重跑各57份返回，SHA/字节/字符/token逐项一致，独立BPE参考核对完整编码序列。Reader补验core2/app3通过，远端并发精简规则3项补验通过。

**全库未全绿**：隔离WSL Python3.14.4运行1357项，6fail/1error/12skip。六失败已独立在相同基线复现；错误为缺fitz。补依赖后只做上述Reader补验；WSL Python3.12环境下载在90秒预算内超时，未取得该版本全库通过结果。临时副本随后不可访问，保留当时源码hash和日志。详情及所有未接受数据见[失败/归档边界](failure-history.md)。仅局部功能与所列合成载荷范围可用，不保证绝对无bug。

文件与数据均归本run；原始raw保持pending标签，接受记录独立保存。`artifact-index.json`登记文件/owner/哈希，`.gitattributes`保护证据字节；依赖和tokenizer cache位于ignored `.agent-runs/`，私有记忆不进公共Git。原有json_context/progress/.gitattributes改动已保留，不纳入本轮发布。未新建监督器、定时器或模型KV服务；父任务MEM-STORAGE-01及持续优化目标保持未完成。

发布状态：独立范围验收完成，等待普通main发布及远端读回；发布后追加实际SHA和安装结果，不提前声明成功。
