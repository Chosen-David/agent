# 有界密集依赖图：完整交接 API 对照通过

本次将已读2610.34763v1的完整路径资源核算、2610.21411v2的操作分工边界落实到既有机械校验：保留两轮浅图扫描和原稀疏fast-success路径，仅让最多65536依赖引用的额外密集残图复用现有线性拓扑检查。不是新论文算法、语义评分或独审替代；未知父/不支持依赖/环/特殊对象仍回退原诊断。原4N稀疏路径可能超过65536，不能称所有图都有该绝对上限。

基线固定4bbae07c；[完整输入与原件映射](evidence-index.json)保留三版方案/三份完整审核/原函数/候选/实际bench-v2/所有raw样本和日志。v2实际执行源码/test/Plan65，v3只给现有五个native job增加同41方法命令，没有重跑成功的producer。旧plan中的24-less-empty和pre-execution文字保留，当前实际31差分/已执行状态由本报告和完整结果审查明确覆盖。

计时覆盖真实Mailbox.publish→prepare_context→ack，包括artifact hash/schema、SQL、MemoryLedger、两次basis校验、payload生成与receipt落盘；夹具构造/等价断言/更正检查不在计时内。只切换冻结baseline/candidate的claim_graph函数；其他模块实际执行，非两个独立产品安装。五种**合成**输入各2warmup/variant、21对交错样本，完整[主测](producer.json)/[独立](independent.json)保留。

| 输入 | 主测耗时下降 | 独立基线→候选 ms | 独立下降 |
| --- | ---: | ---: | ---: |
| dense128 | 60.34% | 96.764 → 37.041 | 61.72% |
| dense192 | 75.70% | 275.991 → 61.921 | 77.56% |
| chain512 | 4.86% | 28.948 → 28.717 | 0.80% |
| small8 | 3.36% | 14.840 → 15.301 | -3.10% |
| empty | -8.44% | 14.231 → 14.103 | 0.90% |

固定门槛：两密集形状在两执行者均下降≥20%，三控制各退化≤15%，各形状单flow tracemalloc峰差≤2MiB，全部通过。负结果不删：主测空图慢8.44%，独立small8慢3.10%。全路径Python峰约1.06–2.16MB，最大正差主测55bytes/独立52bytes；JSON等峰可能遮盖局部邻接分配，不能说没有额外分配，也不是RSS/KV/物理内存上限。共享CPU、未绑核/锁频、每形状仅一次peak采样，21对重复不是独立真实任务群体或统计非劣。

同一夹具每次baseline/candidate完整canonical payload逐字节相同，并对照所有原claims；两独立夹具payload hash不同，MemoryLedger含生成created_at，不称跨次原件一致。仅保存hash/长度，临时DB/payload原文未全保存。五形状各48完整flow后，更正拒绝已ACK及pending投递，保持ACK存在与单条pending；不是逐字节历史receipt核对或该新夹具独立证明impact全传播。既有相关回归提供另层证据。

主控及独立均[41方法通过](regression.log)/[独立日志](independent-regression.log)，含新增六个密集late-fault子案例、既有自定义操作/多错诊断/更正/预算控制；各31差分通过，不是穷尽输入或精确65536/65537门界测试。[完整六域独审](result-review.json)usable-with-scope，无阻断项，SHA31d18550e2289c991427b91bf2e65d119c61e8ec30c423f5e5c97eab94d3f5c4。24冻结refs执行前后匹配；手工独审非trusted runtime认证。

方案审核3/3、producer1/3、independent1/3，原deadline08:01:10.510799Z不变，无隐藏重试或旧scope退款/重置。基线旧MEM-CLAIM-12只测稀疏claim_graph，本次没有复用其耗时；prior search380条/partial=true/26errors，非穷尽无旧结果。源码发布及native CI另核，新增步骤若被前序失败跳过仍是缺证据，不能算通过。

没有新读论文计数（同批67/CAVERT partial保留），没有真实宿主加载/LLM终局质量/provider输入token或全角色账单改进证据，不用局部API收益代替SYSTEM99全链验收。guide/唯一TASK索引不变；稳定Plan64→65经版本化独审后采用，普通Progress保留历史。SYSTEM99仍open，本提交不是一轮完成。
