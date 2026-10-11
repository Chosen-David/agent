# [MATH-81] 首次失败的条件风险预算与自适应拒用

Task-ID: MATH-81
Date: 2026-10-11

## Plan

EXECUTE持续建设要求1–10，限定1200秒、普通独立Plan/文档审核各一次；research-explore复用，单作者，无同主题活跃代理。main25e05a6已同步。缺可信ReviewSession/科学验收宿主；仅解析候选，不做科学CPU/模型/GPU/Lean、不恢复MATH65预算或改变新GPU派发入口。

主题：有限T，执行前历史F_{t-1}含策略/动作/已失败状态，E_t为该步失败，S_{t-1}为此前未失败。对S上所有正概率历史有条件失败概率≤可预测a_t。固定确定性caps推出首次失败概率≤1-Π(1-a_t)（不需独立）；自适应随机a_t、每路径Σa_t≤B推出首次失败概率≤B，以首次失败互斥分解/条件期望证明。真实逐步无条件边际风险也能union bound，但不能生成逐历史hazard或把群体平均校准直接当每步真实部署风险。禁止把随机a_t的均值代入乘积。

新增candidate.sequential-first-failure-budget@1有界文档；经典Powell2021/22条件概率/全概率/条件期望，项目自行组合证明；近期CORA arXiv2604.09155v1 2026-04-10定向读§3.4/F.2–F.5，仅把其E[ell*execute]与historyhazard区分，作者保证/proof未完整验收，正式发表未知，不复现。实际knowledge已加载prob.conformal-policy-control@1核对marginal expected风险边界；初始query漏掉该卡，人工refined结果如实保存。

历史搜索scanned131/45 errors/partial，Fano和凸投影命中与本题不同，不复用旧测量。两次独立普通文档审查，不伪装可信门禁。六个公开解析例：固定caps、稀有上下文、只给校准population、随机支出均值乘积反例、提前停止、跨域设备风险。无定理名结构题、跨域、误用反例均保存；仅结构核验，不是模型检索/未见测试。

输出advice、双navigation、来源/知识使用/复核/报告。TASK/coverage/history追加；候选不canonical，guide/Skill/runtime/旧证据/游标/MATH65/SGLang不改。给本轮以register_history索引冻结必要文档，validation unknown/contract null，不认证科学采用。最终同步再授权main并核对远端字节。真实风险证书/部署分布/干预失败/预算账本/同条件模型比较均未验证，生产defer。

## Progress

- 已同步main，治理/角色/状态/现有入口读取；历史/知识实际查询与全文保存，科学数据不复用。

- Ordinary Plan approve with full feedback retained; definitions/stopping conditions included. Six finite public analytic constructions and metadata prepared. Final ordinary document review pending; all registered refs have unknown validation.

- Final ordinary review approve (second/final call); full response preserved. No blockers; pending closeout reconciled. Frozen candidate retains nonblocking wording nits pending future version. JSON/4 ref hashes pass, 8363 old regular files preserved; metadata append-only. Scientific/production/model acceptance remains absent.
