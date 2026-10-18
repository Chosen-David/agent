# CONTEXT-BUDGET-28: 完整依赖包的预算前置判断

Task-ID: CONTEXT-BUDGET-28
Date: 2026-10-19

## Plan

授权：用户持续优化 Chosen-David/agent、验证后直推 main；EXECUTE。基线 5b1765cb1e228dff27794ca067171fd2f31c0d3a。干净独立 clone；主控为源码、测试、任务及报告唯一写者，独立审查只读。空 GUIDE 与整个人类 guide 目录不修改；其他仓库不在范围。

既有结果：result_store 查询 `knowledge cold load tokenization`，limit5/max-scan500，扫描233目录，缺登记导致partial；命中无关通信/导航历史。直接检索现有报告及 TERMS-CLASS-27，仅作背景，不复用旧速度数字；未找到对应预算拒绝实测，不证明历史绝无。既有12篇论文方法/实验矩阵为历史阅读；新增 AgentIR v1 §3–5.1、§6 筛选条件化省工，拒绝其近似时间裁剪/检索路由直接迁移，保持现有检索语义。来源 https://arxiv.org/html/2605.25092v1 。本候选是精确可行性剪枝，不声称复刻论文算法。

方法：保留 context 的输入校验、导航和 get(seed) 完整依赖解析；得到未选依赖 keys 后，若 len(selected)+len(keys)>max_entries，直接追加相同 skipped 记录并继续下一seed。不再装配必定拒绝的包。其他路径保持原样，镜像同步。适用构造器验证后的未被外部修改的快照；不保证 records 直接篡改、猴子补丁或并发外部写入等价。

DAG：独立计划复核 → 实现/差分/配对测量 → 独立代码数据复核 → 必要全库及Reader回归 → fetch并普通main发布/回读。实际 native ReviewSession/tmux adapter 不可用，受管派发和受管发布保持blocked，不伪造回执。本轮仅在用户直接授权下人工有界维护，独立上下文审查不冒充native门禁。

验收先冻结：scripts/benchmark_context_budget.py 使用git固定baseline，隔离globals。synthetic chain20/21/100/300，各测完整context与load-search-context；真实语料 matrix/量纲/attention量纲/zzqxnonexistent，各测完整context与load-search-context，共16例。每例2预热+11AB/BA对；比值为候选11次中位数/基线11次中位数，不是配对比中位数。目标chain100/300的context比值≤0.80；其余14control各候选≤max(基线×1.10,基线+0.2ms)。生产者与独立复测均须达标。加载为新Python store，OS页缓存不清空，不称磁盘冷启动；imports不计入。tracemalloc单独报告，不混入测速。

正确性：完整JSON差分，真实全部published单seed × max_entries1/8/20 × max_chars1/20000；合成chain/fanout、共享已选依赖、重复skipped seed、后续能装下seed、导航开关、恰好条目边界、恰好字符边界及少1字符。非法/过期输入比较异常类名和消息，保留验证顺序与get(seed)。输入和代码前后hash核对；不改变质量/预算/排序。基线无益操作调用数作为结构回归，不当成真实任务速度。

资源：本地CPU串行，无GPU/付费/模型实验；最多2候选、实验及针对性回归合计15分钟墙钟上限（全库测试另限10分钟）。保存失败和原始样本；未达标不发布生产改动。最终只报告对应CPU范围，真实Agent任务成功率/LLM质量未验证。

## Progress

- 完成独立检出、锁及历史检索。只读profile显示该混合查询中加载和词法处理占主要成本，profile不作为benchmark。
- 首轮独立计划复核要求canonical登记、明确统计/控制/时间界与错误比较；已在本Plan落实。native门禁缺口保留。
- 新专项测试修前运行3项，其中chain/fanout两子例暴露24次get而预期优化后3次；before.log保留。这是性能结构回归，非原功能输出错误。
- 生产者与独立复测均通过16项预定性能门槛；每轮750项完整JSON差分及11项异常一致。独立另验27项边界，判定usable-with-scope，原始数据与审查见`agent_doc/results/context-budget28/independent/review.md`。两个超预算合成目标context耗时下降97.23%/98.56%；真实控制存在最高5.45%小幅变慢，不能概括为普遍提速。
- 必要回归实际执行：`python -m unittest discover -s tests -v`，1281项/107.737s，OK（8 skipped）；`python -m unittest discover -s apps/paper-reader/tests -v`，3项/1.626s，OK。专项4项通过；插件镜像字节一致，`sync_plugin_references.py --check`通过。
- 发布前fetch仍为基线5b1765cb1e228dff27794ca067171fd2f31c0d3a。实现与有界验收完成，待main原子发布及远端SHA/关键内容回读；主控负责收尾。native受管路径与真实LLM端到端效果仍未验证，不作为本轮验收。
- 初次发布因大批原始日志被安全检查拒绝；不重试原payload。改为仅公开实现、测试/复现脚本、简报与短日志；大批样本/逐项日志留本地，报告明确第三方无法仅凭公开简报复算统计。结果索引仅登记实际公开文件，不授予自动复用。源码与测量数据不改动。
- 发布闭环：缩减为18文件/576行；含raw的未发布旧commit不在新增历史中。CLI普通push因缺Username失败，已连接GitHub接口以expected_sha=5b1765cb、force=false原子更新main至[766e56e79da9828cfafecea678ebd1ef4585c0b3](https://github.com/Chosen-David/agent/commit/766e56e79da9828cfafecea678ebd1ef4585c0b3)。再次fetch及API回读一致，远端tree=5e573ad7a96afcecccd4edc28ac65f86fc2ee857与本地已验证内容一致，完整diff为零；关键预算分支与公开文件清单已读回。此有界任务完成，后续真实任务/模型指标仍须独立验证；持续优化任务不停止。
