# value运输与attention输出证书_by_gpt

Task-ID: MATH-64　Date: 2026-10-09

本轮新增按需知识 `math.transport-output-certificate@1`，复用现有Skill；加载新卡和softmax输出前置，核对归一化质量、固定value/线性输出及度量来源。学科linear-algebra/probability-and-optimization和问题结构transport-coupling/value-geometry/primal-dual-certificate/metric-mismatch同步。

## 实际增加的能力

有限非负归一化α、β，Cij=||W(vi−vj)||，可行运输π的行列边际分别α、β。边际恒等式和三角不等式给出：实际加权输出误差≤最优运输成本≤value直径×TV。任意可行π给输出上界；可行对偶势下界运输成本，原对偶相等只认证运输最优。一般结论有可复核非形式化证明，精确样例不代替证明。

同值但不同token可产生零输出误差；局部搬移运输界0.5、全局DTV界50；抵消案例运输成本1而输出误差0。因此token重合、运输成本和实际输出精度应分别报告。错误feature距离0不能认证value误差100；近似value须另加扰动项。跨域力混合示例使用同量纲N，概率无量纲；非线性执行器不适用。

固定query的真实attention α/β、V、W可用此局部证书；它不保证下游非线性、生成质量或跨频率融合。value感知离线诊断保留为候选，未改生产。

## 原始来源筛选

经典Peyré/Cuturi [Computational Optimal Transport](https://arxiv.org/abs/1803.00567v4)，2019正式出版，v4于2020-03-18修订；实际检查§2.3式2.10–2.11及§2.5命题2.4式2.20–2.21。本轮耦合输出界与拒绝条件为自己的推导。

[OTPrune](https://arxiv.org/html/2602.20205v3)，v3于2026-04-01修订，检索2026-10-09；arXiv作者标注Accepted CVPR2026，未独立定位正式proceedings。选择性检查§3/A2，视觉feature的W2与协方差/logdet替代目标不能未经映射核验就作为真实attention value证书；未复现实验。

[AttSVD](https://arxiv.org/html/2610.06927v1)，v1于2026-10-03提交，检索2026-10-09，预印本。选择性检查§3.2/附录B：若CQ=QᵀQ+λI，则||E CQ^(1/2)||F²=||QEᵀ||F²+λ||E||F²。非零ridge不能照搬无正则等价式；Q=E=1、λ=1/1000的公开反例得1与1001/1000。diag attention mass也不等于完整PᵀP。此为公式/目标范围核查，不是否定论文经验结果。

## 验收与限制

八个公开Fraction案例通过：重复value、等号、抵消、局部界、错误度量、value扰动、非法质量/边际、ridge反例。六次公开Top3查询命中；实际后端files-lexical-v1和sqlite-fts5-rrf-v1；两条目11270字符，预算16000字符。精确aliases只是词法结构测试，不是未见问题或模型推理测评。

34项知识/索引回归通过（生产者10.666秒），plugin镜像检查通过。独立审查重算与重放证据见独立receipt及review。原229个知识/候选/holdout路径保持，holdout仅哈希不读内容。CPU时间和字符是诊断，没有真实token、Lean、GPU或模型/e2e测量。浮点Sinkhorn边际残差、熵正则目标不能直接当精确运输证书。

全局项目任务元数据检查被现有COMM-CONFIRM-01身份/日期不一致阻塞；本轮知识通过不代表仓库整体通过。本轮没有可宣称为生产性能提升的改进。

## 续接与发布

冻结plan、fixtures、sources、manifest、独立原生回执、检索、回归、保留证据均在本目录。coverage/state和TASK更新，保留原GPU及其他域next_topic。下一步实测value几何、质量覆盖、输出误差与重合的关系，在同模型、工具、预算下计入solver/projection开销。直接main并核对远端，状态见publication.json；仅agent仓库，未改SGLang或human-only guide。
