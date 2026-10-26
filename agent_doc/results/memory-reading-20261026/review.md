# 独立阅读检查点审查

2026-10-26；结论：**approve，仅限文献阅读与源码映射**。无本检查点阻塞；不是实证结果验收、生产修复验收或 SYSTEM-99 完成证明。

## 实际阅读与版本

独立读取 AGENTS.md 的文档权威、独审与结果验收边界、project_document_workflow.md、result_validation_workflow.md；完整阅读所供 `2610.07707v1.txt` 的正文 §§1–7、Algorithm 1、Tables 1–8、Figures 1–4 文本/说明及附录 A.1–A.7，并核对 HTML 版本/章节与 SHA256。未做 PDF 逐页视觉审查，未检查作者原始实验代码/数据。

核对 reading.md、inputs.json、私有 input-refs.json；基线七个仓库文件均与 `git show 2bf58e97:<path>` 字节哈希匹配，HTML 哈希与记录一致。SYSTEM-99 当前变化仅在 Progress，稳定 Plan 与基线相同；旧 refs 是明确的 baseline_refs，不冒充当前文件版本。

审查固定字节：
- reading.md：`6898e3d2d37723f837e2ea845998b29abfcaccef8349a0c8e6bbae3f2cdf54fa`
- inputs.json：`f4d4dbb3cae147c067e7db83891b6bad7771ea91633cf077f0a57d0965eab6d2`
- 当前 SYSTEM-99.md：`ed434ab3ab00efcccd580cf27ac9dc13944e0066b3728c10afa75b65053b42ac`

## 核查结果

论文数字归属正确：60/147/179 为三组会话规模；87.5%→0% 是核心 literal 的 pending 污染，65%→95% 为同组终态任务准确率。组件 held-out 仅测终态污染，没有 pending window；没有借产品的会话级暴露测量替代该指标。合成数据、小样本、单字段、未测计划问答/保留策略与五例纠错标签争议均有原文依据；模型调用开销没有被解释成免费或本库性能收益。

仅定向读取 project_memory.py 的 `_read_entry/_walk/_insert/_revise/accept/correct`、project_memory_workflow.md、test_project_memory.py 的候选接受与纠错相关源码、handoff_basis.py 的 `basis_context` JSON 路径。候选门禁、新 revision、后代 stale 及 JSON 保留完整未省略 memory entry 元数据的映射成立。active 是账本有效状态，不是外部事件发生证明；已确认 intention 可 active。表格编码、cache 省略后的当前上下文与自然语言消费仍未核验，记录没有把它们宣称为已知缺陷。

暂缓新分类器/暂存表/竞争层、先核查消费者的决定与证据相称，无重复记忆层或大迁移主张。新增可恢复正文记录只计一篇，没有重认十篇门槛或恢复旧55篇；既有 PID 身份视图、遗失候选、真实后端及端到端质量等阻塞继续保留。

本审查未运行测试、模型、后端、PID/ALIAS/role capture 或 Codex 重试；未改生产、TASK、指南或 reading.md，未触碰外来 zip。未来语义实验与任何修复仍需单独固定合同和独立验收。
