# 最终 v6 合并候选

当前依据：`release-summary.json`、`independent/upstream-v6-review.json`、`doc/results/final-delta-v6-20261007/`。基线为 main `a52e95e`；历史验收只引用原tree/回执，不再递归复制库存或旧JSON。

本次28路径增量中26项逐字节保留，TASK/CODEMAP合并。新增INDEX-04、MATH-23、MATH-24都是上游已完成记录，不启动新设计或研究。唯一任务索引130项，127份既有稳定Plan不变；人类专用doc/guide无文件。

语料/镜像176文件与上游完全一致，81published、3candidate、4个reserved holdout。运行时、测试、脚本、Reader、工作流与此前验收一致。10项索引测试通过，最终任务文档及插件同步通过；独立检查验证81个published ID、3个候选排除和与实际a52e95e基线的6组完整查询输出一致。

旧全仓730项（729通过、1跳过）和Reader3仅限定未变范围复用，不冒称本树重跑全量。没有当前全目录或AIK满分主张；既有失败、raw/叙述范围差异和手工补读限制保留于原记录。新增科学卡仅保持上游状态，不扩大科学有效性验收。

AIK既有发布回执与五个二进制工件不变；所有二进制对象及此前v4完整tree已可复用。最终v6 tree/commit/ref和独立远端读回仍待发布方完成。DOC-04/VEX-03未提前勾选，独立SEM本地修改明确不在本批。
