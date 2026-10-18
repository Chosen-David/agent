# FTS-BATCH-21：知识索引增量删除合批

Task-ID: FTS-BATCH-21
Date: 2026-10-18

## Plan

同接口精确优化 build_index 中按 UNINDEXED id 逐条删除 FTS 文档/片段的扫描。
基线8cf78b709f49e4ecaa3030b57a341940c3f780a1；候选最多128个id一次IN绑定，
保留同一事务、相同changed插入顺序、元数据与返回值。不得变更schema/engine版本、
检索排序或知识正文。主AI唯一实现和TASK作者；独立新上下文审核计划及结果。

实际DAG：research+prior-review → independent-plan-review → implement+measure
→ verify_experiment_result（独立上下文）→ report+regression → publish+readback。
全部为本地有界人工执行；未绑定原生ReviewSession/tmux宿主，不宣称自动部署。
仅用现有CPU，无付费模型/远端资源。研究复用既有去重精读矩阵并核查当前来源，
不把旧阅读或摘要筛查说成本轮新精读。

先独立计划审核；总预算45分钟、最多2候选、7对交错wall计时/场景。
计时完整build_index（含连接、事务、分词、插入、commit），数据库复制/语料准备
在双方同等计时区外。真实当前knowledge语料及400/1600文档确定性多节合成语料；
no-op、单条、64条、全量更新、全量删除、rebuild，另测127/128/129批边界。
正确性要求返回字典、entries/meta、docs/chunks含rowid内容、5个固定查询完整输出一致；
失败事务回滚、engine迁移、混合新增/删除/更新均不得退化。
保留阈值：合成400/1600全量更新和删除各至少15%中位数wall下降；其余各场景
中位数不得慢于max(基线×1.15,基线+0.5ms)。不达标保留负结果，不发布优化代码。
固定PYTHONHASHSEED=0、SQLite/Python/设备版本及输入hash；每轮用相同seed数据库。
独立复测至少一组bulk及小输入，检查全量原始样本/统计/语义与实际源码。
源码及插件镜像同改；知识专项、完整tests与Reader回归通过后普通推main并回读。
硬约束：guide只读、保留历史与他人工作，不触碰TwoLevel/SGLang。

### Plan v2：测量前冻结细节

知识阅读复用 `agent_doc/results/memory-storage-20261015/research.md` 的12篇方法矩阵；
本轮核查 SQLite FTS5 官方 UNINDEXED 文档及 MemScope 2610.21170v1 §3.3–4，
采用局部修补/同初始状态对照原则，不声称完整复现其算法或任务准确率。
既有搜索扫描229目录，partial=true且含缺失record错误；仅证明所检范围未找到
可复用性能证据，不声称穷尽全部历史。
五个固定查询：`memory retrieval`、`low rank`、`量纲`、`batch update`、`zzqxnonexistent`。
每场景先一对不计时warmup，随后7对交替AB/BA；收益为两组中位数之比，
不是挑最佳单次。输入和源码hash在计时前生成，单独报告每个场景，不加权混合。
真实语料为本基线knowledge；合成语料每条含四节（memory/retrieval/batch/update），
id按数字顺序，内容含i%17类别以形成重复分数；SHA由实际记录内容计算。
全量更新只追加一行文本并更新hash；删除移除记录；混合案例更新前64条、删除
接下来64条、末尾新增64条。未发布记录不参与索引。所有数据库种子均由基线构建。
六项验收：implementation核对两份源码与真实CLI路由；reference_boundary对照
固定git基线完整逻辑表（rowid含在内）及五查询/返回值，批边界/rollback/迁移；
data_integrity保留输入hash、全部7对样本、源码hash及条件；numerical_sanity检查
有限正wall秒并重算中位数/阈值；measurement_validity核对完整build调用和交错顺序；
reproducibility独立执行小规模与bulk对照。六项均必需，不标N/A。
本次数据身份fts-batch21-20261018，生产者root，独立验收另一个真实fresh context；
测量后冻结原始JSON和代码hash后才交给消费者。验证记录是人工宿主独立审查证据，
不是自称原生experiment-validation/ReviewSession认证。

## Progress

已fetch；main无新提交。已有结果查询见私有prior-current.json，命中旧语料检索
验证但没有本次build_index性能证据，不能复用为新性能结论。知识查询命中GPU/
推测解码卡，与SQLite更新条件不匹配，拒作本次实现依据。

2026-10-18：fresh-context fts21_plan_current批准本地有界计划；无原生ReviewSession
认证宣称。实现候选128-ID IN删除，镜像同步；源码hash5266ec9a…a9e7e。
33场景7对完整build_index计时及逐对完整逻辑/检索比较完成，独立fts21_result_verify
复算462个时间样本、全部输入和DB种子hash，重跑400条bulk及小输入，六项验收通过。
真实语料全量更新/删除中位耗时降低29.68%/48.18%；单条/no-op慢8.40%/10.77%，
均在预定容忍范围内。synthetic400/1600的全量更新和删除均超过15%门槛。
新增单元测试最初依赖历史Git对象，按独立意见解除该依赖；冻结基线对照仍由专用
benchmark提供。证据在agent_doc/results/fts-batch21-20261018/；全库回归及发布待完成。

最终集成：1271项全库回归通过（8跳过），Reader3项通过；源码和benchmark冻结
hash未变。TASK勾选只指本次有界优化，不表示持续优化的所有任务已完成。
发布前fresh fetch仍为8cf78b7；普通非强制main更新和远端回读由主控执行。
