# [MATH-75] 奇异块消元的像空间条件、能量与边界压缩

Task-ID: MATH-75
Date: 2026-10-10

## Plan

EXECUTE持续学习2/4/5/6/7/8/9/10。research-explore入口复用；主AI唯一作者；有界1200秒、两次普通独立审核session。非受管执行DAG；无可信ReviewSession/result_verifier，本轮不做实验/CPU数据/model/GPU/Lean/未见测试。不改canonical/runtime/Skill/guide/SGLang；MATH65旧预算/失败/暂停完整保留。

候选candidate.singular-boundary-condensation@1补现有math.schur-complement-block-elimination缺口，非重复常规可逆块公式：实对称PSD A、B像包含于range A才有generalized Schur能量下确界，nullspace方向导致无界的拒用；有内部线性源f时检查f−By∈range A，不能静默用伪逆。图Laplacian每个含内部节点的连通分量接触边界才使内部块SPD；无源边界映射/单位/常数gauge；star消元生成clique，变量减少不保证通信减少。多worker内部块独立时局部reduce+assemble+boundary solve+recover等价，跨worker内边破坏独立性。固定SPD谱近似的min-over-interior继承仅为精确能量夹逼，不自动给硬件性能。

先实际历史检索：scanned122且partial/errors，corpus release命中不复用科学数据；按对象实际知识查询加载两张必要卡/真实knowledge_refs。经典Higham2023-06-01 Generalized Schur Complement Theorem1，相关数学自足推导明确非新定理；近期ICML2025 Wang等Schwarz–Schur Involution官方PMLR2025正式版摘要筛选（PDF两入口分别content-type/体积错误，未读论文方法全文），不复现或移用速度数字。实际版本/日期/阅读程度单列。

普通独立Plan与不同上下文文档复核证明、源f边界、图单位、fill-in/跨块反例和来源。公开无定理名解析开发例覆盖：零曲率耦合下无界，奇异兼容多解，源不兼容，电路二串联，star填充，独立局部凝聚与跨内部边拒用，谱近似夹逼；公开材料不再当未见测试。验收仅知识/结构，不声称模型能自动检索或拒用。

写advice完整候选、results证据和候选双索引；TASK/coverage gaps/history追加，旧计数和游标不变。可靠收益未验证不接生产；后续需冻结真实矩阵/partition/通信字节/solve成本与matched A/B，托管验收条件齐备再运行。发布前重新同步、处理并发，按用户授权直接main，无PR，核对远端SHA/父/树。

## Progress

- main已同步1a7ef10，工作树原clean；AGENTS/任务/角色/知识/持续状态与协议已读。GUIDE空；未发现同主题未完成任务，保留MATH65阻塞。实际检索/知识全文保存。

- 普通独立Plan初审revise：扫描计数121误写，实际122；已纠正并记录PDF读取失败/仅摘要。一次有界返修复审approve，原反馈完整保留，非可信ReviewSession。完整候选与8公开解析例已写，待不同上下文独立文档复核。

- 不同上下文独立文档复核approve，数学/8公开手算例/单位/源项/图与分块拒用/来源已核对，非实验验收。非阻断整体向量符号建议在review记录澄清，候选原字节不变以保留已审核hash。双索引、coverage三领域缺口与history追加；旧游标/计数/MATH65不改。

- 561受保护路径与base字节一致；JSON/已审核candidate hash/历史前缀与全部非history游标、旧coverage内容、TASK仅新增本条的结构检查通过。准备同步发布；结果范围仅文档。
