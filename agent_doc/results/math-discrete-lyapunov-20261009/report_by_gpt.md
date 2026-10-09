# 离散二次稳定性证书与非正规瞬态_by_gpt

本轮新增math.discrete-lyapunov@1，已有Skill检索→完整强依赖→前提核对→条件式推导。经典来源Boyd EE363 Lecture13 slides21–25；从旧动量特例扩展为固定A的一般等价/唯一级数/P范数收缩，保留欧氏条件数代价。不改变生产行为。

8个公开精确Fraction检查通过（计算约0.004850秒）；6个file/SQLite Top3查询命中；完整目标+Jordan/Hermitian上下文9991字符/12000预算。53相关回归通过；5candidate未变，knowledge镜像字节相同。全局快照检查仍有既有无关code-reading_execution.md stale，未扩大修复。检索与哈希不是适用性/语义认证。

固定线性求解器e_next=Ae+w可认证扰动误差管；逐层谱半径小、独立每层P、LLM自评均不能认证全系统。交替使用两个谱半径1/2矩阵的精确反例可发散。仅数值P_hat小残差还需严格正定/残差误差余量。

近期原文筛选：Wei/Zhao/Liu arXiv2508.01410v2(2026-03-13)，读§III–IV和§V相关离散/成本段落。连续可微P(t)与网格求解分开；未复现流体数值，无GPU/模型性能收益。2603.08191v2仅元数据/摘要，混沌主张defer。检索日期2026-10-09；arXiv无journal字段不证明尚未发表。

本文件冻结为producer报告，原始数据尚须独立审核；最终acceptance.json/independent_review_by_gpt.md/receipt记录独立判定，publication.json记录实际发布。8个算例与3个公开检索问题是开发结构检查，未充当未见模型测试。无Lean、GPU、模型A/B、token成本/节省或e2e验收，未加载holdout内容。下一步需新未用测试和真实轨迹，不能通过本轮推出生产收益。

实际执行：verify.py；retrieve.py；python -m unittest tests.test_knowledge tests.test_knowledge_handoff tests.test_knowledge_index tests.test_knowledge_math tests.test_knowledge_reuse -v。原始结果见raw.json、retrieval.json、regression.log；来源定位见sources.json；完整合同见plan/manifest/validation_plan。
