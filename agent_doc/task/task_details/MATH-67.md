# [MATH-67] 结构扰动与共享子空间的重建条件

Task-ID: MATH-67
Date: 2026-10-10

## Plan

用户本次持续基础知识建设第2/6/9/10项授权有界主题、条件迁移、无收益保留候选、验证后直接main。独立主题，不恢复MATH-65或重置其预算。文档限定流程沿用MATH-58/66；预算1200秒、最多2次独立计划审核及1次不同上下文文档审核；不受管派发、不产生实验数据、不冒充ReviewSession。不修改SGLang、guide、生产入口、canonical卡或现有保留测试。只补candidate.structured-subspace-reuse@1文档及学科/结构候选导航。

检索发现 math.eigenspace-gap-perturbation@1 已覆盖普通谱隙与投影误差，故不新增同义卡；只探索结构扰动判据。有限实对称A，P为其唯一top-k正交投影，1≤k<n，Q=I−P，B=A+E实对称：QEP=0 iff [E,P]=0；由块谱排序证明P仍为唯一top-k(B) iff λmin(B|P)>λmax(B|Q)。只在不变块条件下使用限制算子。Rayleigh下界g+λmin(E|P)−λmax(E|Q)>0为充分证书（不称必要）。近似块F=PBQ+QBP，D=PBP+QBQ，h=λmin(D|P)−λmax(D|Q)>0；以现有Yu等Theorem2给sinThetaF≤2min(sqrt(k)||F||op,||F||F)/h；不把Frob界改称无维度operator界。要求证明块分解、ordering、F谱范数等于||QEP||op，明确误差上界认证与子空间残差不同。

来源：Bai作者讲义§4与Yu–Wang–Samworth1405.0680v1 Theorem2；近期Tran/Vu2510.22393v1 §2 Theorem2.1前提筛选，非全文复现、不预设它优于经典界；保留原论文常数、交互项、发表状态和日期。正例包括共同标量平移、块内重根；反例包括交换但谱排序穿越、近零间隔的小扰动、非对称矩阵/平均误差证书拒用。迁移至共享协方差投影只控制相同坐标下q^TPk，对完整注意力及RoPE跨频混合不作推论。至少3个无定理名问题和跨领域模态映射为公开解析开发材料；不是模型检索或未见验收。独立文档核对后diff检查、同步main、直接发布及远端SHA/树/父核对；保留旧游标与证据。主AI唯一写入者。

稳定Plan版本2：明确g=λk(A)−λk+1(A)>0；近似块式U为P正交基，Uhat为B降序top-k的任意选择正交特征基；若B在边界重根，该角度界不认证唯一top-k。h>2||F||op由Weyl额外保证B边界间隔正。来源采用实际可读作者2015正式版Theorem2（v1本轮访问失败，不能称重新核查v1）；2510.22393v1是2025背景扩展，不冒称30/90天新论文。2026论文发现检索命中Spectral-LSH arXiv2607.19368，但原站访问失败；只能记录未核验线索，不采纳其结论，范围停止于此。授权精确摘录和来源定位见结果目录authorization.json、sources.json。

## Progress

- main 0b0016d已同步，初始工作树clean；本地无同主题运行登记，不证明远端全无。历史检索partial=true，命中语料集成结果，仅导航不复用实验验收。现有谱隙卡已实际读取，避免重复卡片。

- 独立计划cycle1 revise、版本2cycle2 approve；实际2015作者PDFTheorem2已读，v1失败保留。进入不同上下文文档审核，无实验数据。

- 不同独立上下文文档审核 approve-with-document-scope，最终advice SHA256=2ddccc35cd19faf32430fb51e53b44d0942c38564064fdea70fac7e28c31a8a6；同次审核补齐近期定理符号定义。无CPU/模型/GPU/未见测试；完成仅文档候选。
