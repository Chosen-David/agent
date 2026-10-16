# MEM-REVISION-11 独立计划审查

Verdict: ACCEPT（仅有界手工审查，不代表受管 ReviewSession 或部署监督器）。

源码确认 `_revise` 在 `_insert` 调用共享 `_ids` 之前先执行 `set(deps)`；None、整数、含 list/dict 的引用在这里泄漏 TypeError。使用既有 `_ids(deps, 'deps')` 紧邻集合检查之前规范化，保留 reason/source、旧状态和后代读取的现有优先级，是符合当前 Agent 可靠性目标的最小修复。

验收约束：对每个非法输入核验 MemoryError 及 entries/dependencies/events/document_dependencies 的完整事务前后相等；覆盖有效 tuple/list、重复 ID、缺失 ID、禁止旧节点/后代 lineage、新版本证据和原后代 stale 传播、candidate accept。不要广泛捕获 TypeError 或掩盖内部账本损坏。CLI 本身对部分引用做预处理，不把 CLI 路径替代公共 Python API 复现。保持源冻结，独立复核最终代码和数据后才可发布。

已有检索结果为 partial 且若干缺失记录；这些候选不构成当前缺陷的证明或可直接复用的验收。没有模型/GPU/KV 性能主张。人类 guide 不可编辑；生产与文档由主 AI 单一作者维护，审查仅写本私有文件。

Plan SHA256: 147321c92954a49069ade72a0bee699cfdf5cc885d5676405b46be8ea5880714
