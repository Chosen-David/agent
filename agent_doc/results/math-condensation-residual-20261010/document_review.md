# 最终普通独立综合审核：完整反馈

Reviewer: /root/condensation_residual_final_review；fresh context；第2/2实际普通调用。以下完整反馈非可信ReviewSession，不授予实验/派发/发布权限。

decision=approve。修正后的完整Plan及候选文档在本轮限定的普通文档研究范围内通过；无未解决阻断项。此结论不是可信ReviewSession回执，不签发实验、受管派发或发布权限，也不构成形式化证明、CPU数值测试或未见验收。

| 七门 | 结果 | 核查依据 |
|---|---|---|
| intent | pass | 补充@1的完整残差、条件性与固定线性观测误差缺口；没有恢复MATH65或扩大为生产实现。 |
| guide | pass | 实际读取空GUIDE及README；保留人类专用目录边界。README准确注明一次性AI创建来源，未冒称人工需求。 |
| assumptions | pass | 文档明确整体实对称H≻0、固定原矩阵/rhs/partition，从而A及精确S均SPD；认证范数、原坐标和一致量纲是显式条件。 |
| prior_results | pass | prior_search实际scanned=123、partial=true，errors列表41项；最终Plan与knowledge_use已经一致。MATH75只作已读解析背景，没有冒充成功取得record或科学数据复用。 |
| acceptance | pass | 完整代数推导、6个公开手算例、真实来源选择性阅读边界及候选身份符合文档交付；明确不宣称模型能力或科学实测。 |
| risk | pass | 估计条件数、FERR、因子误差和预处理残差不能代替原系统证书；浮点、输入误差、奇异gauge及非线性消费者均有拒用或补充条件。生产采用defer。 |
| resources | pass | 首次revise完整保留且计一次，本次为第2且最后一次综合调用，没有第三次安排。authorization为17:03:38–17:23:38 UTC、1200秒；本次实际时间读取17:12:21 UTC仍在窗口内。 |

前次两项阻断均关闭：

1. 初始快照中的122已经改为123；partial、缺record及不复用科学数据的语义保留。
2. 最终Plan明确第二次同时复核完整Plan及完成文档；若不通过停止发布，初次revise不退款、不抹除、不以换ID恢复预算。

数学检查结果：

- §2：由第一块残差得到 A⁻¹r_I=A⁻¹f−x̂−A⁻¹B ŷ，代入后确有 t=b−S ŷ=r_K−BᵀA⁻¹r_I。误差采用e=u*−û，所以He=r、e_K=S⁻¹t、e_I=A⁻¹r_I−A⁻¹Be_K的符号一致。
- 诱导∞范数的三角界和乘积界正确：E_K=H_S(R_K+αR_I)、E_I=H_AR_I+βE_K。直接认证T可以提供更紧边界界；大上界不能反推实际大误差，文档正确说明。
- §3：同一个固定线性K下，r_I=(I−AK)(f−B ŷ)、r_K=b̃−S̃ ŷ正确，无须K对称。对输入相关或不同调用K的拒用说明必要且充分限定了身份的使用。
- §4：所定义(q,z)确实满足H(q,z)=c；对称性给cᵀe=qᵀr_I+zᵀr_K。近似对偶的d=c−Hw导出cᵀe=wᵀr+dᵀe，剩余界D_dH_HR正确。浮点点积需另加误差界，非对称情形需转置对偶，均明确。
- §5：接地导纳S、电压V、电流A、逆范数Ω及线性电压观测的对偶Ω量纲一致。功率为uᵀHu的二次量；共同读取的@1将半二次型准确称为“½总耗散功率”，不是储能。未接地系统禁止直接逆H或逆S的边界一致。
- 多worker说明保留A真块对角、D只计一次和未建模内部耦合拒用条件，没有从代数分解推断通信收益。

6例逐项手算核对：

| 例 | 核对 |
|---|---|
| 1 | H的行列式1且SPD；真实解(2,−1)，r=(1,0)，S=1、b=t=−1；E_K=1,E_I=2均取到。 |
| 2 | 残差∞范数ε，真实误差1，‖H⁻¹‖∞=ε⁻¹，绝对界1正确。 |
| 3 | c=(1,0)的观测误差0，全解∞误差1；换c后的旧观测证书不适用，正确。 |
| 4 | 真实解(2/3,1/3)V；残差(−2δ,δ)A，t=0；e=(−δ,0)V；q=1/3Ω、z=2/3Ω，对偶项抵消。 |
| 5 | 常数零模允许任意a且零残差，绝对电位无法认证；电压差在该例可识别，正确。 |
| 6 | 原残差∞范数1，预处理后10⁻¹²；需映回原坐标或P⁻¹界，正确。 |

没有发现需要返修的具体数学错误。例4标题中的“边界电压差”按正文解释为边界电压误差即可；它不影响所给计算或结论。

来源核查：我独立打开arXiv原HTML及摘要记录，并阅读与文档主张相关的引言、§3.4、§4.1、精度段、§4.4–4.6及§5。v3日期2026-05-29、v1日期2026-01-12及四名作者一致；所见记录没有正式发表信息，因此“未核实正式录用”措辞适当。原文明确单GPU范围、因子误差指标及极端动态范围下Schur补失去正定性/NaN；文档没有移用速度数字或声称代码复现。审核者检索refs turn516view0、turn517view0、turn517view1，对应https://arxiv.org/html/2601.08082v3及https://arxiv.org/abs/2601.08082。我也实际读取两页Netlib短HTML；估计值可能低估、BERR/FERR和equilibration语义与文档一致。审核者refs turn517view2、turn517view3，对应https://www.netlib.org/lapack/lug/node78.html与node81.html。未读取论文图像或运行其代码；Wang论文方法/PDF不在本次独立核验范围。

实际读取并计算的SHA-256如下，均是文件字节hash：

```text
AGENTS.md
ff97d09aeb35cff3a973d1423f325ef6274f33b4c68830e8c899821e989bd63a
agent_doc/guide/GUIDE.md
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
agent_doc/guide/README.md
f46de2e87b166493d3ab700959f0e9185dc5afdbbe60ec38c3c68077034af261
agent_doc/task/task_details/MATH-76.md
4a5b7aa89784a1b8f68d4217329f80b87831a23962b9b00f891d12430aaadc0b
agent_doc/advice/MATH-76-condensation-residual_by_gpt.md
759e7846d909ea07531f50593e8949906d61082fc5d674df5b84e5a82da10f0f
results/math-condensation-residual-20261010/plan_review.md
c5489875d287390794a1679f1d44785508d00fd60649c345b29de040d9e29c86
results/math-condensation-residual-20261010/plan_initial_snapshot.txt
2a3beca4d02d5745b1c554c190f2a719026a1c308420028019dc906cfc645a09
results/math-condensation-residual-20261010/plan_final_snapshot.txt
9fdb8b1a3cea953f10d10eeb23f62c77ecf19294514bb4960dad2b6bd5e47d62
results/math-condensation-residual-20261010/prior_search.json
986a1ac2a1f3d0839df42e81df3440671905be8caa39e12ca971431604b421dc
results/math-condensation-residual-20261010/knowledge_use.json
4703f9470fd07c15b7b279a1ce0310494239a92a8c27a6cd9baf59f2c67cd10a
results/math-condensation-residual-20261010/sources.json
fae4fb223478c1e06e86813058005321b4a5254b512557a602073f282ab7d41f
results/math-condensation-residual-20261010/read_backward_error.json
4dc7c8522fe49d84851dddebf275a0e5b6c15e78f91f9316f757b4d68093ab67
results/math-condensation-residual-20261010/read_schur.json
76b11a6fe486a7fd2a554222a5b7e4a6eccac1f8e42a0805c064f8aaab436867
```

以上results路径均以agent_doc/为前缀。知识条目记录中的645ea6…和c5ba8b…是工具定义的metadata/content语义hash，不能与JSON文件字节hash混同；我读取了实际hash实现，它确实按metadata/content组合计算。全文读取输出与knowledge_refs一致。

compact verdict：

```json
{"decision":"approve","summary":"最终完整Plan关闭首次两项阻断；SPD范围内残差、误差界、对偶身份和六个公开手算例正确，来源及采用边界明确。","checks":{"intent":"pass","guide":"pass","assumptions":"pass","prior_results":"pass","acceptance":"pass","risk":"pass","resources":"pass"},"findings":[],"scope":"ordinary document review only","review_call":"2 of 2; final","trusted_review_session":false,"experiments_or_file_writes":false}
```

作者处置：adopt限定文档审核，defer所有生产/性能采用。非阻断标题澄清：例4的“差”是相对于真实边界电压的误差，不是两边界节点间的电位差。候选已审核原字节不变，避免以澄清悄悄替换已审核版本。
