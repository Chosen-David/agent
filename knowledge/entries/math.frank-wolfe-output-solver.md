# 固定凸输出的逐步重赋权与停止证书

稳定ID `math.frank-wolfe-output-solver`，版本1。经典方法来自Jaggi2013§2–3 Algorithm1/3、Theorem1。以下平方目标递推是项目独立特化推导，非新定理。不是生产求解器、attention机制等价或模型收益证据。

## 对象与准确条件

非空有限原点v_i∈R^p，固定已知z；C=conv{v_i}，f(y)=1/2||y−z||²，f*=min_C f，h_t=f(y_t)−f*。所有权重β_i≥0、Σβ=1，y_t=Σβ_i v_i。D=diam(C)=max_{i,j}||v_i−v_j||。量纲：f,h,g,D²均为输出单位平方，不能当token overlap或attention mass。

精确oracle选j_t∈argmax_i (z−y_t)ᵀv_i，d_t=v_j−y_t，g_t=(z−y_t)ᵀd_t。完整max给g_t≥h_t≥0；g_t≤ε认证f(y_t)−f*≤ε，即平方误差距最优≤2ε，不表示绝对误差≤2ε（f*可能正）。

更新y_{t+1}=y_t+γ_t d_t、β_{t+1}=(1−γ_t)β_t+γ_t e_j，0≤γ≤1保证可行。两种policy：固定schedule γ_t=2/(t+2)，t=0开始；精确线搜索 γ=clip(g_t/||d_t||²,0,1)，d=0时γ=0。

对schedule和精确线搜索都有

$$h_{t+1}\le(1-\bar\gamma_t)h_t+\tfrac12\bar\gamma_t^2D^2,\quad\bar\gamma_t=\frac2{t+2},\qquad h_t\le\frac{2D^2}{t+2}\ (t\ge1).$$

只有线搜索保证f每步不增，固定schedule可能上升。h_t的O(1/t)不等于最后一步g_t同样O(1/t)；必须实际计算gap，不能按次数误报停止。D=0时所有点相同、h=0，但绝对f可为正。从一个顶点初始化，t步最多t+1个正权点；一般m_0点初始化最多m_0+t，不保证最小支持。

## 可复核证明

由前置投影卡，完整残差gap给h≤g。精确平方展开任意γ：

$$f(y+\gamma d)=f(y)-\gamma g+\tfrac12\gamma^2\|d\|^2.$$

可行y、v_j∈C，||d||≤D。取schedule并用g≥h得到递推。t=0时γ=1，因此h_1≤D²/2≤2D²/3，不依赖任意大h_0。若h_t≤2D²/(t+2)，递推得h_{t+1}≤2D²(t+1)/(t+2)²≤2D²/(t+3)，最后一步由(t+1)(t+3)≤(t+2)²。线搜索最小化同一线段的精确凸二次函数，目标≤schedule候选，故同样递推且可取γ=0证明不增。归纳β更新保持simplex；每步最多添一个点。

## 近似oracle的方向与局限

若只找到可行v_hat，令g_hat=(z−y)ᵀ(v_hat−y)，要有**认证上界**η≥max_i(z−y)ᵀv_i−(z−y)ᵀv_hat≥0，才可保证h≤g_hat+η，递推多出γ η。未规定η随时间的准确控制，不沿用上述无误差rate。采样max是full max下界，不能自给η；一次线搜索仍可不增，但不保证朝全域最优或能合法停止。近似梯度还需额外oracle/gradient误差，不强行套用。

## 正例、边界与误用

- 配方v=(0,3),z=5/6，y0=0：完整oracle=3。线搜索γ=5/18，一步到目标；schedule γ0=1跳到3，f由25/72上升至169/72，随后满足一般界。这个上升不是实现bug。
- v=(0,1),z=2：最优y=1，f*=1/2；gap0认证最优而非零输出误差。负权(−1,2)不得作为可行输出。
- C三角形(0,0),(1,0),(0,1)，z=(1,1)：最优y=(1/2,1/2),f*=1/4，有限迭代不需精确达到才能界误差。
- C=conv{0,2,4},z=4,y=2：只查0,2得g_hat=0却h=2，full gap=4。合法η=4恢复上界，禁止假收敛。
- 重复点/单点允许，不要求独立坐标或可逆Gram；空C、负权、变动z/改变可行点都需拒用或重建问题。固定policy没有统一线性收敛保证。

## 检索、迁移与成本

结构触发：非负权重迭代拟合固定输出、混合配方逐步添加成分、候选部分最大残差假收敛。先核对固定对象/目标/单位、simplex可行性及全oracle，再使用ID和强前置`math.convex-projection-certificate@1`（包含`math.dual-certificates@1`）。

Indexer严格映射：对固定query，z是dense teacher输出，v_i为固定选中原values，β是允许新权重。可离线比较初始softmax子集重归一化与迭代结果；达到gap≤ε才认证与此子集的最优误差相差≤2ε。保持value和非负归一结构，丢失跨query共享、softmax参数化、跨层非线性与运行开销；不是线上选择速度或e2e改善。若原权重不可改变，本求解器只给诊断基准。

每步穷举oracle约O(np)点积，加O(p)输出更新；若显式更新全部权重需O(n)，稀疏支持可按其大小处理。取得z与n个value已经有成本；投影-free不等于读数据-free、token-free或GPU更快。完整支持太大时只能研究可认证近似oracle，不能靠漏点省成本并称gap已认证。配方/传感器平均是同一数学问题；协方差、负权回归等不是。

最小可证伪检查：固定C/z下每步β合法；展开等式成立；全gap上界误差；与独立解析最优比较。实际模型实验需要同模型权限/预算、matched index维度和完整e2e输出对照，未测不接生产。

## 近期研究边界及验证等级

Alcalde等《Attention’s forward pass and Frank-Wolfe》，ICML2026 PMLR306:1767–1800终版，检索2026-10-09。读取§1–3定义/假设与§4定理前提：研究hardmax token动力学，限制value矩阵与key-query符号，token凸包可随步数改变。与本卡固定已知z、固定C的误差优化不同；不因同名迭代把动力学定理搬给真实attention/indexer。未核验全部附录或复现实验。

验证：公开10例/两policy12步的Fraction检查、无定理名三结构查询×两后端及知识回归，经过实际独立验收；不是Lean、浮点外包、模型检索拒用或未见测试。留出题内容未读。实际token、GPU、model A/B/e2e未知，不宣称收益。来源版本/hash/read extent见`agent_doc/results/math-frank-wolfe-20261009/sources.json`。
