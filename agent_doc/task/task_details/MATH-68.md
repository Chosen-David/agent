# [MATH-68] 子模覆盖保证与知识前提互补的边界

Task-ID: MATH-68
Date: 2026-10-10

## Plan

用户持续建设要求第2/4/6/8/9/10项授权有界数学主题、条件迁移、未验证方案保留候选和验证后直接main。EXECUTE独立文档工作，沿用MATH-66/67文档范围，不恢复MATH-65、不重置保护审核预算、不派发受管实验。预算1200秒，最多2次普通独立计划审阅及1次不同上下文文档审阅；这些审阅不冒充可信宿主ReviewSession。主AI唯一写入者；不修改guide、SGLang、生产代码、canonical知识卡或保留测试。

candidate.submodular-context-guard@1：有限集合、归一化单调子模函数、统一单位成本与精确最大边际贪心，证明有限k保证1−(1−1/k)^k及近似边际加性误差递推；明确这不是e2e质量保证。加权覆盖证明及反例：互补前提、异质成本的简单密度贪心、非单调目标。固定mandatory集合P后的残余覆盖g(S)=f(P∪S)−f(P)保留子模性；不能由此声称前提依赖或实际任务成功也是子模。传感器覆盖为精确跨域映射，Agent上下文为带限制的候选。3个无定理名公开解析问题，不称模型实测/未见验收；不运行新实验、不产生实测数据。

来源实际读取NWF1978原文摘要、§2 Proposition2.1与§4 Theorem4.2（printed280）；短递推为本轮自行推导而非逐字原证明。近期筛选PACMS2606.20047官方摘要页面检索明确v1 2026-06-18/v2 2026-09-03，原网页直接读取失败、全文未核验，仅保留候选，不接受其算法/收益。PC-SubMax2609.32474发现检索命中但直接正文失败，不作为已核验来源。检索日期2026-10-10。

先前实际结果检索scanned112、partial=true（缺record）；命中3个语料集成结果与不相关知识卡，仅导航，不复用其验收。记录检索缺口，不能宣称无重复或新方法。新增advice与元数据、coverage候选导航、learning_state.history，保留next_topic/last_completed_round/旧证据。冻结guide/canonical卡/旧MATH65文件哈希（不读取保留测试内容）。完成需独立文档审阅、diff检查、同步远端main、直接非强制发布和远端树/父/SHA读回。

稳定Plan版本2：有限V，f:2^V→R≥0，f(∅)=0，单调和边际递减，整数1≤k≤|V|；OPT=max_|S|≤k f(S)，S0=∅，执行k次添加。k=0仅空集。近似选择要求真实Δchosen≥max真实Δ−εt，εt≥0，最终减去Σt=0..k−1(1−1/k)^(k−1−t)εt；每项估计绝对误差ηt时εt=2ηt。固定mandatory P，g定义于V\P，总基数预算K的剩余r=K−|P|，仅与包含P的可行最优集比较；|P|>K不可行，r=0不运行贪心。来源与授权绑定sources.json/authorization.json；计划审阅意见不作为宿主回执。

## Progress

- main 8d73326已同步；初始clean。本地无.agent-runs目录，不能据此断言远端无作业。同主题TASK无登记。

- Ordinary independent plan cycle1 revise; version2 cycle2 approve. New document written within remaining one document review, no experiments. Concurrent main dc0244a integrated; old evidence unchanged.

- Different independent context document review approve-with-document-scope, advice SHA256=9e68901729b9998ac481c501d4bda35fecb8cade18fcacabc7449dd00f4ee426; all206 preservation hashes match. Completed document scope only. No model/GPU/formal/holdout checks. Candidate navigation and history updated without advancing canonical cursors or MATH65.
