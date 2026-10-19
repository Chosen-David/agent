# INGEST-SCOPE-58: 知识导入隔离校验的复制范围

Task-ID: INGEST-SCOPE-58
Date: 2026-10-19

## Plan

目标：保持知识条目、依赖检查、候选状态、provenance 与原子发布接口，避免导入时复制不被 KnowledgeStore 消费的根目录缓存/索引/附件。基线 cacbee7663282bcd17b8e08de6b4a00945a0a9fb。本任务只授权 Chosen-David/agent；不涉及 TwoLevel/SGLang、付费模型或部署。

只读检查发现 knowledge_ingest.ingest 当前 shutil.copytree(store.root, stage)，而 KnowledgeStore 仅递归读取 entries。候选方案将复制源和目标限定为 entries 子树；不删除、改写或过滤 entries 内文件，不放松 symlink/孤立 Markdown/依赖验证。继续保留提交前全语料 snapshot 比对及目标文件系统暂存/rename。比较方案：保持全根复制为固定旧基线；只复制 entries 为候选；从内存重建语料会改变路径/格式语义，本轮拒用。

历史实际检索见 ../../results/ingest-scope58/prior-search.json：237 目录，partial=true、68错误，五候选都是语料检索或通信改动，不覆盖导入复制；四项 pending、一项历史 usable-with-scope，均不复用作当前验收。定向 rg 命中旧完整源码快照及 read-boundary56 报告；后者字节读取修复保留，但不证明复制范围正确。数学知识不需要；工程依据是本地入口/消费者和 Python 3.12 shutil 官方文档。已完成的十篇正文阅读记录位于 read-boundary56/research_a.md、research_b.md，本轮沿用为方法背景，不计新阅读或把论文数字当本机收益。

执行链：真实独立 plan review → root 保存修前失败/实现/测试测量 → 独立 verify_experiment_result → root 汇总和发布。完整范围由本文件固定；主控唯一写 TASK、源码、测试、测量和报告，审核者只写分配的 review 文件。max_inflight=2，测量阶段单进程，无并发测试计时；本机标准库，临时合成附件上限 16 MiB，7次交错配对、1次预热；每次对照输入hash相同。tmux 不可用，没有可信常驻 adapter，不声称部署 managed Engine/ReviewSession；独立上下文审核通过宿主真实 agent 调用。

验收：
1. 先构造有效语料旁的 dangling symlink/FIFO 与普通附件；旧实现失败或复制无关字节，候选不访问非 entries 内容且导入成功。entries 内相同非法对象仍拒绝。
2. 正常无附件、根部大附件和真实 SQLite 索引三组 old/new 最终记录/snapshot/引用相同，provenance 除时间外一致；非法依赖不修改语料，重复 ID仍拒绝，条目子树附件保留。
3. 复制字节量以实际 copyfile 调用及源大小计数，为逻辑复制负载，不能称磁盘物理 IO；计时单独无 instrumentation，涵盖完整 ingest 含三次语料验证、两次复制、rename和清理，初始化/生成输入不计入。记录所有样本和中位数，不以合成缓存样本外推生产或模型延迟。0附件允许噪声，无可靠速度收益则只报告去除无关复制/恢复可用性。
4. 针对性、全部 tests、Reader tests 和独立插件镜像/隔离入口检查；保留失败和短日志，更新 CODEMAP。独立审核六项：实现、参考边界、数据完整、数值、测量有效、复现。无GPU或模型质量主张。
5. 发布前 fetch，若并发修改受影响文件则重审/复测；仅本次文件原子普通更新 main，回读 SHA/树。未验收不推送。

## Progress

- 计划待独立审核；尚未实施。
