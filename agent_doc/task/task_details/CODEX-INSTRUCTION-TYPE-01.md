# CODEX-INSTRUCTION-TYPE-01

Task-ID: CODEX-INSTRUCTION-TYPE-01
Date: 2026-10-24

## Plan

同未完成 SYSTEM-99。基线 `32150234` 的 Codex 安装入口会直接读取全局 AGENTS.md；目标若为命名管道，正常同步与 `--check` 均阻塞。仅在现有链接拒绝之后、读取之前拒绝既有非普通文件，保留原对象与安装状态；不改变接口、受管区块或普通文件语义。不承诺对抗并发路径替换、修复所有安装恢复问题或证明实际宿主加载。

固定验收：隔离真实 CLI 对目录/管道、同步/检查四种组合返回 exit1/blocked、无 traceback，管道不等待写端；保留原路径身份、清单与技能字节，且无 pending、备份、锁残留。Python3.9/3.12 相关回归和独立源代码/负控复核后普通发布 main、回读。不声称性能或新轮完成。

## Progress

- 先查 `codex installation instructions FIFO`，扫描200项、partial=true且存在缺登记记录。命中 codex-pull-sync 的固定版本为 `2dd302d`、环境为旧 WSL，与当前代码/环境不同且未覆盖此输入，故不复用其通过标签；其他候选是后端发现/集群规划。查询保留于私有 `codex-fifo-prior-0904.json`。
- 修前真实隔离 CLI 在3秒超时后被终止；清单未变，无 pending/锁。新增回归修前4子场景失败：两个管道超时、两个目录缺明确类型诊断。首次探针导入未设置 PYTHONPATH 的夹具错误保留说明，修正后才形成产品基线。
- 生产仅加两行预检。修后同探针返回 exit1/blocked，无 traceback；Python3.9/3.12 各36项安装/恢复/所有权回归及两版本的 -O 专项通过。源/测试 SHA256 与原始日志见私有 `codex-fifo-candidate-0904.json`、`codex-fifo-*-0904.log`；独立结果审核与发布回读另核。
- 本次未新增论文正文阅读，保留同批22篇可恢复记录；本地正确性修复不抵扣真实输入曝光、全部 actor 用量、实际任务质量和跨库存储一致性验收。

- 独立复核接受 usable-with-scope：两版本各20项 setup/ownership、-O专项及任务入口4项通过；隔离去掉两行 guard 后两版本均复现4子场景失败，源文件未改。未独立重跑主控全部36项，未做模型/宿主或性能验收。复核报告 `codex-fifo-review-0904.md/.log` 绑定同一候选源码/测试 SHA。
