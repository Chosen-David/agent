# 近期筛选（检索2026-10-07）

Ye等，Fix the Structural Bottleneck: Context Compression via Explicit Information Transmission，arXiv:2602.03784v4，2026-06-18修订（首次2026-02-03）。abs列v1–v4；未核实正式刊会发表。https://arxiv.org/abs/2602.03784 ，固定原文 https://arxiv.org/html/2602.03784v4 。

读取§1、3–5、6.1–6.2、A.1.1–A.1.2。ComprExIT用冻结层特征、跨层门控与带边际约束的运输计划形成压缩槽；作者报告QA优势。未独立复现实验、未审核全部附录。A.1.1的重建NLL使用固定decoder和teacher forcing，是作者明确采用的proxy，不能写成已测互信息或任务充分证明。abs称接收后放代码，v4 HTML已给代码链接；记录两处不一致，不据此断言当前代码可运行或论文已接收。

自己的筛选结论：soft-token方案需要模型内部特征、训练与decoder适配；仓库当前是文本知识检索/版本账本，不满足直接接入条件。最小迁移实验应冻结同模型、数据/工具/预算，对遗漏版本与撤销状态的反事实任务检查，而非只比较摘要长度或重建NLL。本轮只保留候选，不承诺性能或普遍充分性。

2026-09检索另发现StateComp arXiv:2609.27298；abs请求DisabledError，未核对版本、正式状态、正文，不算已阅读进展。
