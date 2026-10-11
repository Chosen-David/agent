# MATH-80：已有数学知识的发现链核验与补登记

本轮没有增加新定理或Skill。实际发现MATH-78/79材料虽然已写入advice/coverage/navigation，结果检索器却要求每轮record.json：缺记录使它们不被该入口发现。沿用现有register_history为两轮补登记，并给本轮登记；未知验证状态保持unknown，contract为null，measured_at为空。原始文档、反馈、失败记录和科学证据未修改。

## 实际入口与检查

入口：scripts/result_store.py search → ResultStore.search只检索summary/run_id/result_id/producer_task_id/context → show返回历史引用 → 调用方核对并读取实际advice。search不全文检索advice，也不自动检查历史引用最新字节；本轮显式检查所有引用哈希。这是资料发现链修复，不是知识自动应用或科学验收。

固定limit=3、max-scan=200，三条公开英文结构查询保持相同。登记前后扫描127目录，缺记录错误45→42（45含新建本轮未登记目录）。partial始终true；此标志也由截断到limit导致，不能解释成穷尽文献或目录扫描一定达限。未处理其他42个错误，不能声称结果库整体修复。

| 无定理名查询 | 登记前前三项包含目标 | 登记后第一项 |
|---|---|---|
| compressed state transition history | 否 | math-state-aggregation-20261010 |
| whole task probability any failure | 否 | math-marginal-contraction-20261010 |
| device alarm sequence distribution | 否 | math-marginal-contraction-20261010 |

精确命令、完整输出、计时见search_commands.json、before_*/after_*；搜索0.15–0.42秒/次为本机元数据运行时间，不是LLM/token收益。登记结果与show/引用核对见registration.json、reference_checks.json、load_trace.json。MATH78仅有历史JSON复核记录，不补造其缺失的完整原反馈；MATH79完整Markdown反馈保持原字节并绑定。

## 数学对象、应用与拒用

使用既有math.sequence-tv-coupling@1，实际knowledge search/show和semantic hash见knowledge_use.json。初始自然结构查询未命中该卡；加入sequence/total variation/coupling的人工修订才找到，保留两次输出。不把人工知道目标后的检索当未见模型成功，也不把新历史记录当canonical卡。

1. 状态压缩：对象为有限微状态P、分区g及宏状态Q。目标是对任何初始律预测下一宏状态；应加载MATH78，逐个检查同块所有微状态到每个目标块的转移质量相同。只看稳态平均或某固定动作不能满足该条件；授权、版本、撤销等非预测需求仍分别保留。
2. 全程失败：对象是长度T的完整历史条件核P_t/Q_t，目标为路径事件A=“至少一次失败”。若每个相关共享前缀的核TV≤epsilon_t，既有卡给|P(A)-Q(A)|≤TV(pathP,pathQ)≤1-Π(1-epsilon_t)。这是条件论证，真实任务核/误差包络仍未知；没有预测真实成功率。
3. 跨领域设备告警：有限同一告警字母表、固定时间步/长度、相同停止规则，目标是整段告警概率差。满足完整共享前缀条件时可沿用上一式。数学关系为条件概率链，不是物理因果模型；真实设备采样和故障机制未验证。
4. 表面相似反例：只给单时刻TV≤.01、Q收缩rho=0就要求全程失败差≤.01，拒用。MATH79已给P各行(.99,.01)、Q各行(1,0)，同初始0。每时刻TV=.01，而T步“曾失败”差=1-.99^T。T=2已是.0199>.01；该确切手算复核并非新科学数值实验。不能把边际的epsilon/(1-rho)替换路径界。

经典依据重新核查Powell 2021/22讲义§3.2有限TV/最大耦合。近期筛选仅确认Michel/Siegle arXiv2403.07618当前页面仍为v3（2024-08-06，related DOI可见），本轮HTML失败，未重新审核全文或期刊版。2607.19510页面亦失败，不新增其版本/发表结论。来源和访问限制见sources.json；沿用既有理论，不制造“最新进展”。

## 验收与续接

这是公开结构/元数据检查：三个预先固定查询返回准确目标，三个新记录所有历史引用哈希一致，全部保持unknown验证；未做真实模型检索/拒用、GPU、Lean、科学CPU数值实验或未用holdout。普通独立Plan/文档复核不等于可信ReviewSession或verify_experiment_result。没有部署或性能收益；不修改SGLang。

下一主AI：通过existing result_store按任务对象查少量资料，show后核对必要引用，读取前提及拒用，再决定应用。其他42个无record目录逐一按实际证据决定是否历史登记，不批量制造pass。canonical提升、同模型同权限同预算检索/拒用测试、真实轨迹核认证和生产策略仍需既有可信宿主与预算；MATH65耗尽预算/失败/blocked保留，不能改ID绕过。本轮仅采用历史发现桥，所有数学/生产候选仍defer。
