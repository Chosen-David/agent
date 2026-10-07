# [INDEX-04] 按用户FC融合新想法完善既有独立设计文档，区分post-RoPE残差压缩/有限距离频率分组，核验来源与数学反例并交付；不镜像私有论文材料或修改SGLang。

Task-ID: INDEX-04
Date: 2026-10-07

## Plan

按用户FC融合新想法完善既有独立设计文档，区分post-RoPE残差压缩/有限距离频率分组，核验来源与数学反例并交付；不镜像私有论文材料或修改SGLang。

## Progress

### Preserved implementation and evidence

- [x] [INDEX-04] 按用户FC融合新想法完善既有独立设计文档，区分post-RoPE残差压缩/有限距离频率分组，核验来源与数学反例并交付；不镜像私有论文材料或修改SGLang。

证据：docs/knowledge_learning/2026-10-07-quadratic/report.md。固定联合高斯/真实可分离协方差仅限受控模型；未测Agent模型质量/拒用、GPU或真实传感器。50有限检查通过，非形式化证明；监督适配器/tmux不可用，独立授权工作继续。既有优先游标保留。

INDEX-04交付：既有子空间设计文档v1.1已更新，增加不重叠FC补空间低秩、位置锚点/有限距离相位误差，以及CA与输出/e2e质量的区别；SAS v1（2026-09-11）与OVAL v1（2026-10-05）原文近邻筛选。81新增有限开发检查及原57检查通过，真实模型/GPU/生成token收益未测。外部文档SHA256 c52b1dff152b7491277c4e91cf0a18784b5ee4b99035e6b0463cdf901a138b8c；公开仓库仅保存交付状态，不保存私有材料。

MATH-24发布闭环：实现commit c787730ddb6fd6bbcd7d564f288e1c8d9062631b、tree 798d83ad4de5c78b7c62c779a5bf1d7b808dca58，与验收树一致，以新鲜expected_sha/force=false直接更新main。API/独立ls-remote/Git完整tree核对通过；84条=81published+3candidate，50有限检查，4新/8旧查询双后端无新增退化，548程序540通过/8跳过及Reader3/3。5,043 tokens仅是按需完整上下文编码计数，未测模型性能或账单节省。INDEX-04独立文档v1.1交付，81新/57原有限检查；实际indexer/e2e/GPU待验。回执见publication.json；保留既有优先游标，不改SGLang。

### Historical context

Original task: [line 479](../legacy/TASK.bcc6c7ef7b73c77ee01aaccb5ac2c470ebef4d66e46c1c6ebda447613c2112ab.md#L479).
Shared methods, results and evidence: [source section, lines 455–485](../legacy/TASK.bcc6c7ef7b73c77ee01aaccb5ac2c470ebef4d66e46c1c6ebda447613c2112ab.md#L455-L485).
Source SHA256: bcc6c7ef7b73c77ee01aaccb5ac2c470ebef4d66e46c1c6ebda447613c2112ab
Bare code paths and archive-relative links retain the original project-root base.
Migration preserves the original checkbox as history, not independent acceptance.
Dates use the nearest dated heading, or the explicitly supplied migration date.
