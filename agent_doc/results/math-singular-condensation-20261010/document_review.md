# Ordinary independent document review

Reviewer: /root/singular_condensation_document_review, fresh context; one turn. Not trusted ReviewSession/result_verifier. No experiment or unused test access. Source citations below normalized to durable URLs; review text otherwise retained.

**approve（仅研究文档）**。没有发现需要阻断发布的数学或来源问题。

候选文件实际SHA256：
`490a4b4e9dd35c274d081ac6198ae4466180d9abdba8e8b095062f5111a3154b`

实际阅读范围：候选全文§1–9；`agent_doc/task/task_details/MATH-75.md`全文；本轮` sources.json`、`knowledge_use.json`、`schur_entry.json`和`pseudoinverse_entry.json`全文；直接打开Higham作者网页及PMLR正式记录。没有修改文件，没有运行实验，没有读取unused或未见测试。

逐项核查：

| 项目 | 证据与判断 |
|---|---|
| 广义Schur必要充分条件 | §2的零空间方向论证给出必要像包含条件；配方恒等式和取`x=−A⁺By`完成充分性及S必要性。正确。Higham原网页Theorem1确实列出这三个条件，实对称版本是其Hermitian定理的特例。[原网页](https://nhigham.com/2023/06/01/what-is-the-schur-complement-of-a-matrix/) |
| 固定y与所有y源项 | §3固定y只需`f−By∈range(A)`；所有y时取y=0得f条件，再作差得B条件，反向显然。最小值、全部极小点、b及常数项的符号均正确。 |
| 零空间无界 | 不相容h在`ker(A)`上有非零投影，沿该方向线性项可趋于负无穷。例1、例3准确，伪逆没有掩盖不相容性。 |
| 图条件 | §4以内部向量延拓边界0证明`L_II≻0`的连通分量条件。正确，包括全图奇异而内部主块可逆的区别。 |
| gauge与注入 | `S1=0`推导正确；边界源方程、内部源的仿射偏置符号正确。无源独立内部连通分量的常数自由度与不平衡注入无解判断正确。 |
| 物理单位 | 西门子×伏特=安培，电导二次型为瓦特；½二次型是半耗散功率而非静电储能。例4的功率½瓦及½二次型¼瓦一致。 |
| 8公开解析例 | 逐例人工代数检查均成立。例2得S=½、φ=y²/4；例5电流(0,−1)；例6对指定边界电压功率¾；例8缩放确实取到夹逼上界。没有把这些例子当实验。 |
| fill-in | 星图凝聚产生`I−11ᵀ/d`及叶间电导1/d，边数`d(d−1)/2`正确；d=4例得到6条边。低秩表示限定也合理。 |
| 局部分块、D一次 | §5在A块对角且局部SPD时各项相加、边界求解及恢复公式正确。例7独立接地分支得S=1，重复完整D错误得S=3。 |
| 跨内部边反例 | 路径内部A含−1非对角，真实凝聚是`⅓[[1,−1],[−1,1]]`；丢耦合仍用对角2得½I，破坏常数gauge。正确。 |
| 谱夹逼继承 | §6固定y取内部能量最小值，逐点下界直接取inf，上界在H的极小点取值。SPD及δ<1保证所需极小点存在；无源、固定划分及精确消元限制充分。 |
| 来源与知识边界 | 两张entry的ID/version/记录哈希与knowledge_use一致，候选哈希吻合。PMLR记录确认作者、题名、卷267、页62172–62221及13–19 July 2025，并支持摘要层面的边界矩阵凝聚与GPU小稠密运算描述。[正式记录](https://proceedings.mlr.press/v267/wang25a.html) |

非阻断编辑建议：§3写“线性系统`Hx=(f,g)`”与前面内部变量x的定义有维度上的符号重用，可改为`H(x,y)ᵀ=(f,g)ᵀ`或使用独立整体变量u。

重大限制：这是普通独立数学/来源文档复核，不是可信ReviewSession或独立结果验收。没有Lean、CPU数值稳定性、模型检索、GPU、通信或真实应用证据。近期论文仅阅读正式摘要和书目信息；记录中的两个PDF获取失败原因未独立重演，论文方法、实验及速度主张没有全文验证。结论不授权算法或性能生产采用。

## Author disposition

Mathematics/source review adopted for documentation scope only. Minor nonblocking whole-vector notation is recorded here: the system in §3 is H u=(f,g), where u stacks the internal x and boundary y; no claim that the m-dimensional internal x alone is the whole vector. Reviewed candidate bytes kept unchanged to preserve exact review hash. Performance/production acceptance remains deferred.
