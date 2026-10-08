# 保留坐标的线性预测与Schur残差

稳定ID：math.linear-prediction-residual；版本1；核查2026-10-08。背景为经典Schur补；下面统计预测和索引分数公式为本项目自足推导，不标为新论文定理。

## 问题触发与数学对象

保留向量的一部分a，能否用它预测被遗漏的b，并将可预测信息折入查询？令x=(a,b)，a∈R^s、b∈R^h，s,h≥1，E||x||²有限。使用非中心矩Caa=E[aaᵀ]、Cba=E[baᵀ]、Cbb=E[bbᵀ]，Cab=Cbaᵀ；要求Caa正定。固定预测T∈R^(h×s)，目标min_T E||b−Ta||²，是**无截距的线性重建**，不等于所有函数的最优预测，也不默认均值零。固定坐标分割/分布/矩；拟合与留出工况不同须重新检查。

## 准确结论和证明

B=Cba Caa^(-1)，e=b−Ba，S=E[eeᵀ]=Cbb−Cba Caa^(-1)Cab。

E[eaᵀ]=Cba−B Caa=0。展开残差二阶矩，利用B Caa=Cba，得到S。对任意T，b−Ta=e+(B−T)a，交叉期望为零，故

E[(b−Ta)(b−Ta)ᵀ]=S+(T−B)Caa(T−B)ᵀ。

后项为PSD，因为对任意w，其二次型为E[(wᵀ(T−B)a)²]≥0。取迹得损失差tr((T−B)Caa(T−B)ᵀ)≥0；Caa SPD使其仅在T=B时为零，因此B为唯一线性重建最优。S≥0直接由残差外积得到，与整体非中心块矩的Schur补一致；整体块矩可奇异，不要求S SPD。

S=0当且仅当b=Ba几乎处处：E||e||²=trS=0，非负变量期望零给e=0 a.s.。低误差不是零误差；a.s.只限当前支持，不保证任意输入。数值实现解B Caa=Cba，不显式形成逆。奇异Caa、病态误差/regularization或support伪逆不由本SPD接口自动解决；加ridge改变拟合目标，不能称同一最优。

## 非中心、条件期望及score区别

均值非零仍用上述非中心矩。若要仿射预测，先中心化并加回Eb：Eb+Cov(b,a)Cov(a,a)^(-1)(a−Ea)，需另核对该协方差可逆。或者把常数1加入a，用非中心正规方程；此时增广矩仍需可逆。不能只换中心协方差又漏掉截距。

E[eaᵀ]=0是线性正交，**不推出e与a独立、E[e|a]=0或S为条件协方差**。只有另加适用模型（如非退化联合高斯、正确仿射形式）才能作相应条件分布解释；本条未使用该模型。

设实际query q=(u,v)，分数s=uᵀa+vᵀb。恒等式

s=(u+Bᵀv)ᵀa+vᵀe。

因此只缓存a时，可使用折入查询u+Bᵀv；这是在所拟合分布下补入可预测遗漏内容，不要求把不同FC直接相加。误差为vᵀe。若q独立于x且E||q||²有限，则E(vᵀe)²=tr(E[vvᵀ]S)，B亦使任意固定PSD查询权重下的线性重建风险最小；不保证唯一score最优（query可能有零方向）。证明：独立将E[vvᵀeeᵀ]分离，前述PSD差取查询加权迹非负。真实paired q/x通常不独立，需另核对联合混合四阶矩可积并直接计算E[vᵀ(b−Ta)]²；重建最优可能不是score最优。未给一般paired最优求解器。

## 正例、边界与误用反例

独立a,ε均匀±1，b=2a+ε：B=2，S=1；直接删除b重建MSE=5，线性预测MSE=1。若ε=0则S=0、预测精确，但只在b=2a支持上。改变工况为b=−2a则原B预测MSE=16。

非零均值a≡1,b≡3：非中心B=3,S=0；中心协方差Caa=0不可逆，省略截距更不能得到此结论。

非线性a均匀取−2,−1,1,2，b=a²：Caa=5/2,Cba=0，B=0,S=17/2；b完全由a决定，真实条件协方差为零。E[b|a]=a²不是Ba，最优无截距线性MSE=17/2而非线性MSE=0。这也反驳把S称一般条件方差。

paired score反例：a≡1,b均匀±1，u=0，v=1_{b=1}。B=0为重建最优，MSE=1；T=1重建MSE=2。但真实scoreMSE分别1/2与0；折入查询可改变最优目标，不能由重建改善推出排序/softmax/output/e2e改善。普通E[ea]=0并未消除查询选择偏差。

Caa奇异例a=(z,z)，z均匀±1：不能直接求逆；本接口拒绝，而不是证明没有任何预测器。预测/重建的不同目标和拒用须一并记录。

## NoPE、RoPE与混合模型的迁移

NoPE：固定坐标/学习基分割后，可缓存a并折入Bᵀv；可选额外残差码z=Uᵀe，再增加(Uᵀv)ᵀz。此时误差vᵀ(I−UUᵀ)e，U列正交；未给残差维数/学习方法的最佳选择保证。新增残差码占额外缓存，不自动降低总KV。

仅RoPE：若a,b已经在各自真实位置旋转，可对post-RoPE分布拟合B，折入实际旋转后的query，潜变量不再叫某个固定频率FC。若想在旋转前拟合并沿原频率使用，必须检查Rh(n)B=B Rs(n)对所需位置n成立，才能把Rh(n)Ba替换为B Rs(n)a；同频复线性块允许，异频一般不允许。强前提math.rotation-intertwiner给准确整数位置/反频/退化分类。内容可预测不代表整个旋转轨道可预测。

NoPE+RoPE：NoPE为平凡旋转，pre-RoPE非零跨块B一般不满足交织；可保留结构分块预测或学习post-RoPE联合分布。两者都仅为明确条件的索引候选，需固定位置范围、长度、头、层、prefill/decode与合法query/key配对；不修改模型原RoPE或生产注意力。

最小可证伪实验：固定保留坐标数s、总索引字节和候选token预算，对比直接删除遗漏块、折入预测、折入预测加残差码、同预算直接更多FC；记录留出真实paired score、排序margin/候选、V/W输出与e2e，校准/solve/query变换/写缓存/读取开销都计入。方法选择与最终验证文档分开。若仅重建下降而score/output不改善，则不采用；未经实测不声称优于FASA或节省token。

跨域：a为保留电压传感器V，b为另一电压V，B无量纲，q的u/v为电导S，分数为电流A。b=2a+ε模型中v=3S时遗漏误差45A²，折入后9A²；这里只保留线性响应、同工况分布和单位，未测硬件；换工况反例仍有效。

## 来源、近期筛选与关系

强前提math.schur-complement-block-elimination@1（块矩基础）、math.rotation-intertwiner@1（pre-RoPE交织分类）。math.paired-bilinear-risk、math.attention-output-geometry、math.weighted-bilinear-low-rank是目标差异与后续导航，不能将其独立/固定score前提静默忽略。

[Higham作者文](https://nhigham.com/2023/06/01/what-is-the-schur-complement-of-a-matrix/)，2023-06-01（页面显示更新2023-06-06），块定义/因子化及PSD段落；检索2026-10-08。它支撑Schur基础，统计预测/score式为上述项目推导。

[AttSVD](https://arxiv.org/html/2610.06927v1)，arXiv2610.06927v1，2026-10-03预印本，2026-10-08核查相关方法/App B：post-RoPE查询度量的SVD是固定完整分数矩阵目标；加入ridge改变度量。仅作目标/前提筛选，不把作者方案或实验当本条预测公式的证明，不宣称已发表/复现或最新研究穷尽。读取范围/原始HTML哈希在本轮sources.json。

## 实际验证状态

本轮agent_doc/results/math-linear-residual-20261008-v2保存Fraction有限矩分布、SPD正规方程、残差外积、PSD差、分数恒等式、paired/非线性/非中心/旋转及单位反例，独立六域回执限定范围。公开三类无定理名查询的文件/SQLite检索和完整强前提闭包，是结构验证；人工判断拒用不等于模型拒用实测。未使用旧封存题内容。无Lean、真实模型/GPU、token计量或e2e收益；一般证明依赖上述推导而非有限数值样例。
