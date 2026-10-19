# CONTENT-COPY-60

## Plan

保持 get 输出JSON值、键序、元数据隔离、筛选和预算；复用合法不可变正文。基线4bdb071f5dc9b83c36cdc1b36df5a28a1a1f7823。固定候选计划、集成计划、历史检索与研究记录见 ../../results/content-copy60/。主控负责源码/镜像/测试/任务；独立审核者负责计划和结果审核。仅本地CPU、无付费模型/GPU；没有托管常驻宿主，未声称部署监督器。

## Progress

- 独立计划批准后单轮测量：135语义检查，16场景通过预设门槛；独立复核16输出和54边界案例，usable-with-scope。
- 主场景完整context（不含search/模型）2.46849→2.05445ms，Python追踪峰值97034→49475bytes。原始样本/input/output/source/plan hash保留在raw.json。不是RSS或推理TTFT。
- 集成计划批准；精确替换canonical与standalone镜像，保留CRLF。专项8/Reader3通过；全库和集成审核待完成。主控负责普通main发布及回读。
- 全库1301项（8跳过）/Reader3/专项8通过；测量候选与生产逐字节一致，重放脚本使用固定git基线及独立输出以保护原始结果。最终验收和发布回读继续由主控闭环。
- 独立集成验收usable-with-scope，见integration_review.md；允许发布，main远端SHA/tree回读在本次最终交付中记录。
