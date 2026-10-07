# 矩阵函数、Hermite 插值与缺陷谱

稳定 ID：math.matrix-function-jordan-calculus；语义版本1；核查日期2026-10-07。

## 对象、符号与前提
f 在谱附近解析；每个 Jordan 块 J=λI+N，N^m=0。有理函数分母在谱上非零。

## 经典结论
f(J)=Σ_{k=0}^{m−1} f^{(k)}(λ) N^k/k!。存在唯一 deg p<deg μ_A 的 Hermite 插值多项式，匹配每个λ至最大块阶−1导数，且 f(A)=p(A)。

## 证明思路与可复核推导
局部Taylor代入幂零N使级数有限。不同λ的 (t−λ)^m 互素，CRT 将 Taylor余数拼为唯一模μ的p；相似回变给f(A)。这是primary matrix function，未定义 arbitrary nonprimary square roots 的全部分支。

## 正例与边界
N=[[0,5],[0,0]]，exp(N)=I+N；只有谱0不足以用 exp0·I。λ=0 的 N²=0 块对 f(t)=t² 给 f(N)=0。

## 误用反例与拒用条件
逐元素 exp 不等于矩阵 exp；只在对角izable情况无需导数。log 在零谱或跨分支切线附近不满足本条解析前提。浮点 Jordan 分解非推荐数值算法。

## 问题结构与迁移
线性动力系统 exp(tA) 中 tA 必须无量纲；可验证低维函数作用但不保证一般神经迭代是线性。

## 前置关系与来源版本
基础前置：有限维空间、基、矩阵乘法和域算术；涉及内积的条目另需共轭转置/正定范数。本条在正文重述使用的基础结论，导航关联不要求一次加载整条课程。准确出处：[2020-06-09 Jordan definition；Hermite CRT/边界推导为本项目整理](https://nhigham.com/2020/06/09/what-is-a-matrix-function/)。Axler 使用第四版、作者2026-08-16 PDF修订；Saad 使用第二版2003；Conrad未标日期的讲义以本轮PDF哈希固定；网页按标题日期与检索日期固定。PDF哈希/近期论文筛选见本轮 sources.json/research.md。

## 验证状态与限制
已核对所列来源的相关段落，并人工检查上面的证明思路/自推公式。verify.py 对该主题给公开正例、边界或反例；Fraction精确运算与float64数值检查分别标注。数学证明核查不是 Lean 形式化证明；计算实例不证明一般结论。未做同模型Agent A/B或真实GPU系统测试；没有性能收益声明。
