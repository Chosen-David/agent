# EXPL-001：独立路径误差能否保证输出不变？

**不能仅因两条路径独立评分，就保证量化后输出不变。** 给定模型先将 logits 相加，再经同一个 softmax 归一化；输出取决于两条路径误差之和、当前概率分布及固定的 $V$。

**题目例子。** 原来 $a=b=(0,0)$，所以 $p=\operatorname{softmax}(a+b)=(1/2,1/2)$，$y=5$。只把 $b$ 改为 $(0,\log 3)$，便有

\[
p'=(1/4,3/4),\qquad y'=0\times\tfrac14+10\times\tfrac34=7.5.
\]

因此另一条路径完全不变，输出仍改变了 $2.5$。这说明路径独立并不意味着输出独立；题目未定义“评分”，也未给出合格阈值，不能声称这个量化误差通过了某种实际评分标准。

**局部 Jacobian（本解释的推导）。** 令 $z=a+b\in\mathbb R^n$，$p=\operatorname{softmax}(z)$，$V\in\mathbb R^{n\times d}$，第 $i$ 行为 $v_i\in\mathbb R^d$，$y=\sum_i p_i v_i\in\mathbb R^d$。logits 无量纲，输出单位与 $V$ 一致。由

\[
\frac{\partial p_i}{\partial z_j}=p_i(\delta_{ij}-p_j)
\]

得到

\[
\frac{\partial y}{\partial a_j}
=\frac{\partial y}{\partial b_j}
=\sum_i v_i p_i(\delta_{ij}-p_j)
=p_j(v_j-y).
\]

将 $y$ 写为列向量，两个 Jacobian 均为 $d\times n$ 矩阵：

\[
J_a=J_b=V^\top[\operatorname{diag}(p)-pp^\top],
\qquad
\Delta y=J_a\Delta a+J_b\Delta b+O(\|\Delta a+\Delta b\|^2).
\]

固定 $V$，在原始点线性化，本例 $J_a=J_b=(-2.5,2.5)$，故一阶预测为 $\Delta y\approx2.5\log3\approx2.7465$。精确变化是 $2.5$：有限扰动下，一阶近似不保证精确相等。已用 Python 复算，并以中心差分核验原点的第二个偏导为约 $2.5$；数值检查不是一般证明。

**反例与边界。** 非零误差也可能完全不影响输出：若 $\Delta a+\Delta b=c\mathbf1$，softmax 的共同平移不变性保证输出不变；尤其两条误差相消时成立。反之，单独把每条路径扰动造成的有限输出变化相加，一般不能得到联合扰动的输出变化。独立误差界可以结合 Jacobian 或其他有依据的界来控制输出偏差，但“偏差有界”不等于“输出不变”。若 $V$ 的所有行相同，任何概率变化都不改变输出；一般情况下，精确条件为 $(p'-p)V=0$。

**回到材料。** 锚点为 `inputs/concept.txt` 的教学公式与给定二元素例子；没有提供论文。此例只反驳“独立评分自然保证输出不变”的无条件推论，不能证明真实模型必然显著退化、某量化算法不可靠、某路径更敏感，或预测任务精度损失大小。真实模型还需要具体评分定义、误差分布、模型结构及实测；本任务未联网、未进行模型实验。输入校验值和实际数值检查见 `verification.json`。
