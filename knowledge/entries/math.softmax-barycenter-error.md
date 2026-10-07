# 有限 softmax 与归一化加权输出误差

ID: `math.softmax-barycenter-error`；版本 1。问题触发：分数误差已知，如何控制加权输出？选出的集合重合度能否替代输出质量？先抽取支持集、归一化方式、value、输出度量；只需本卡，整体二范数误差转排序时另读 `math.score-difference-bound`。

## 对象、前提和结论

固定非空有限集合 J，同一支持集上的有限实数 logits s,t；α=softmax(s)，β=softmax(t)。温度和 1/√d 已计入 logits。固定 value v_j∈R^p，固定线性映射 W:R^p→R^h，输出用任意范数。设 y=Σα_jv_j，ŷ=Σβ_jv_j，D=max_ij‖W(v_i−v_j)‖，e=t−s，w=max e−min e。

经典 TV 恒等式（来源1，§4.1 Proposition 4.2，印刷页48）是 TV(α,β)=½Σ|α_j−β_j|。本卡以下是独立给出的有限推导，不声称研究新颖性，不是形式化证明：

\[
\|W(y-\hat y)\|\le D\,\mathrm{TV}(\alpha,\beta)
\le D\tanh\!\left(\frac{\operatorname{osc}(t-s)}4\right).
\]

此界对两个 token 可以取等号。误差的共同平移不起作用；若 ‖e‖∞≤ε，则输出≤D tanh(ε/2)。若已知整体 ‖e‖₂≤η，则 w≤√2η（最大最小坐标差与柯西不等式），得到 D tanh(η/(2√2))。不能把逐坐标 ε 当整体 η。D=0 时，无论排序/概率如何变，输出都相同。

## 可复核证明

令 δ=α−β，其正、负部分总质量均为 T=TV。T=0 时结论显然；否则 WΣδv=T(a−b)，a,b 分别是正、负部分归一化后的 Wv 的凸组合。展开这两个组合的乘积权重，以三角不等式得到 ‖a−b‖≤D。

令 X_j=exp(e_j)，m=min X>0，M=max X，μ=Σα_jX_j。β_j=α_jX_j/μ，所以 TV=E_α|X−μ|/(2μ)。m=M 时 TV=0。否则凸函数 |x−μ| 不超过区间端点的弦，取期望后

\[
\mathrm{TV}\le\frac{(M-\mu)(\mu-m)}{(M-m)\mu}
=\frac{M+m-\mu-mM/\mu}{M-m}
\le\frac{\sqrt M-\sqrt m}{\sqrt M+\sqrt m}
=\tanh(w/4).
\]

最后一步用 μ+mM/μ≥2√(mM)。这是实数数学证明；计算时不应直接 exp 大误差，使用稳定 softmax 和 osc/tanh，避免溢出。尖锐例：w≥0，α=(1/(1+exp(w/2)),exp(w/2)/(1+exp(w/2)))，e=(w,0)，β 恰交换概率。v=(0,D)、W=I 时两界同时取等号。

## 改变支持集：必须单独处理剪枝

非空 S⊆J，p_S=Σ_{j∈S}α_j>0，y_S=Σ_{j∈S}α_jv_j/p_S。若 p_S<1，令 y_barS 为补集的同样归一化输出，则

\[
y-y_S=(1-p_S)(y_{\bar S}-y_S),\quad
\mathrm{TV}(\alpha,\alpha^S)=1-p_S,\quad
\|W(y-y_S)\|\le D(1-p_S).
\]

p_S=1 时误差0，不定义补集均值。硬 mask 的 −∞ 不满足有限 logits 前提，不能直接塞入有限 w 的公式。

若在 S 上使用代理 logits t、近似 values vhat，β^S=softmax(t|S)，ŷ_S=Σβ^S_j vhat_j，以三角不等式分三段：

\[
\|W(y-\hat y_S)\|\le
D(1-p_S)+D_S\tanh(\operatorname{osc}_S(t-s)/4)
+\sum_{j\in S}\beta^S_j\|W(v_j-\hat v_j)\|.
\]

D_S 是原始 values 在 S 上的直径。S 可由代理自适应选择；上述界对每个实际 S 逐点成立，无独立性要求。但 p_S 必须来自完整 α，不能用代理概率冒充。若粗筛只决定 S，最终计算用原 logits 和原 values，后二项为0；代理误差影响选集，不能重复计为最终归一化误差。

## 正例、边界和误用反例

- 两 token 尖锐例 w=2、D=3：输出差=3 tanh(½)≈1.38635。共同 logits 平移或共同 value 平移均不改变界。
- α=(.45,.30,.20,.05)，v=(0,1,0,−6)，完整 y=0。质量最大的两项 S={0,1}，p=.75，y_S=.4；S'={0,2}，p=.65，y_S'=0。S' 对 full top‑2 的重合率只有½，输出反而精确。这不是端到端模型实验。
- 保留 .999 质量仍不保证小绝对误差：α=(.999,.001)，v=(0,10000)，只留第一项误差10。需要 D 或实际几何，不能只报质量。
- 同一排序/选集也不能保证相同输出：s=(0,1)、t=(0,2)、v=(0,1)，全支持集重合100%，概率和输出不同。
- 空 S、负权重、不同温度却未缩放、变化的 value/支持集、非线性聚合均不符合对应前提。高 value 均值本身不重要，直径才平移不变；相对误差在 y≈0 时不可靠。

## 迁移及不适用范围

Attention/indexer：qᵀk/√d 对应 s，FC/低秩预测决定 S，V 对应 v，输出投影块对应 W。NoPE/RoPE/混合均可在位置变换已完成后使用本界；本界不授权跨频率无损融合。应同时测 p_S、重合度、输出绝对误差和实际任务精度；最大质量降低最坏情况界，但不最小化具体 values 的实际误差。多头可逐头用 W_h 后把界相加，不能拿单头误差充当整个模型证书。

物理线性混合：v 是同量纲 actuator force，权重是非负归一化混合，W 是固定坐标/测量映射；D 和误差单位均为 N，logits/TV 无量纲。真实非线性执行器不适用。Agent 文本通信的“消息重要性”不是此线性平均；没有实际对应对象只能保留类比，不据此删消息或修改生产路由。

端到端：后续残差、非线性、多层及自回归状态未纳入。只有另行证明相应 Lipschitz 界/决策间隔和传播预算，才可能形成局部决策证书。不能由本卡或较小输出误差直接宣称 FASA 精度/省 token/速度改善。

## 来源与验证等级

1. Levin–Peres（Wilmer contributions），*Markov Chains and Mixing Times*, second edition，作者 PDF https://darkwing.uoregon.edu/~dlevin/MARKOV/mcmt2e.pdf ，§4.1 Proposition 4.2/Remark 4.3，pp.48–49；检索2026-10-07。引用的是 TV 事实；attention 及 tanh 推导由本卡独立展示。
2. OVAL arXiv:2610.06686v1，2026-10-05提交，https://arxiv.org/html/2610.06686v1 ，A.2 Lemma A.2/Propositions A.3–A.5；其 A.4 是直径乘∞范数路径界，不把本卡 tanh 界归因于作者。局部谱目标的均匀参考/isotropic query 条件另见 A.3/A.5。本轮只筛选，不复现模型。
3. MC‑Sparse arXiv:2610.06801v1，2026-10-05提交，https://arxiv.org/html/2610.06801v1 ，§4.2式(1)、§4.3、Algorithm 1、§5：oracle 最大保留质量仍可能遗漏尾部贡献，扩散步间 residual 复用依赖其场景，不直接迁移到自回归 KV。

来源2/3截至检索2026-10-07只有v1，arXiv预印本，所见记录未提供正式接收信息。数值/结构开发验收及独立审查见 `doc/results/math-softmax-20261007-v2/`。无 Lean、无模型同预算 A/B、无真实 GPU/indexer 运行；数值例不替代上述证明。公开验收题均为开发题，不再作为未见测试；原有未见题保持未使用。
