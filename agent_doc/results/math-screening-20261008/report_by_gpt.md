# 残差包络：让低秩候选筛选具有可核对的拒用条件

本轮新增知识 `math.residual-interval-screening@1`。不改变生产attention，也不修改SGLang。增加的是一个有条件的推导入口：将共同正交投影的逐键残差转为分数区间，再按下界阈值排除不可能进入原分数Top-k的候选。不是以条目数量宣称模型能力提升。

## 数学与实际用途

对于共同正交投影P，s_i=qᵀk_i、h_i=qᵀPk_i，误差半径e_i=||(I−P)q||₂||(I−P)k_i||₂。设L_i=h_i−e_i、U_i=h_i+e_i、tau为第k大L_i，则保留U_i≥tau并对保留项按原分数精确重排得到一个全集Top-k解。一般证明见知识正文，数值例不能替代证明。

严格映射适用于最大内积检索与同一分数目标的indexer候选选择。NoPE可对实际内容向量应用；RoPE须对实际旋转后向量核对同一P及残差；混合路径可以分别给不相交子块界后求和。near/far固定配额的区域Top-k不等于全局Top-k。单一分数保证也不等于注意力输出或e2e保证。

迁移建议保留为待测候选：在原FC选择上增加遗漏子空间的正交压缩，并缓存逐键残差半径，按不确定边界精算。必须算上投影/查询残差、候选全扫描、额外索引缓存和回退成本；最坏所有候选都需精算，尚无可靠加速证据，未接生产消费者。

## 近期研究筛选

检索日期2026-10-08。阅读 [Sample-Guided Exact Top-K Selection for Long-Context Sparse Attention](https://arxiv.org/html/2609.08450v1)，所读版本v1、2026-09-08；arXiv预印本，未核验正式发表。阅读范围§2.1及§4.1–4.4、Lemma4.1/Theorem4.2。其取样只提议候选边界，完整分数行核验和精确细化/回退承担正确性。可借鉴“提议—核验”分离，但其精确对象是已物化indexer分数，不是原模型点积，也不能据论文的算子实验宣称本项目加速。保存版本/范围在research.json。经典基础核对Wisconsin Math340 Notes3 Theorem5.3/5.10；区间筛除命题为本项目显式推导，不声称创新优先权。

## 测试与证据等级

生产者65公开开发例：45 Fraction精确二维/区间算例、20 NumPy QR浮点诊断；6拒用见证，198断言。含不点名定理的压缩检索问题、传感器内积跨域代数例、均值残差/斜投影/proxy阈值/删等号/输出不保真/浮点未外包反例。传感器例是合成算例，没有真实传感器数据。

独立不同上下文核查实际冻结代码、输入配置、raw、环境及一般证明；额外59,049精确有理投影和3,000通用区间病例通过。生产浮点数据另用逐标量参考重建，最大差3.55e-15。独立核验发现4组严格浮点包络违界，最大2.22e-15；因此浮点样例仅作容差诊断，不构成精确证书。这正是生产接入前必须证明外包舍入、正交性和量化误差的原因。完整审查/冻结哈希见independent_verification.json、manifest.json；不是Lean形式化证明或受管ReviewSession部署。

人工从3个问题提取结构，限定linear-algebra领域，文件/SQLite各检索一次，新卡六次均进入Top-3（5次Top-1），含误用问题但不等于模型自动拒用实测。六个旧代表查询Top-1仍在Top-3，范围有限而非完整语料回归。完整show含2条强依赖，序列化计数2,923 cl100k_base tokens；6次检索CLI耗时见cost.json。无API账单或省token比例主张。保留原holdout元数据和未运行协议；公开算例不再视为未见测试。

初次47项相关单测有1项因插件尚未同步而失败，原日志regression.log保留；同步后47/47通过，发布状态47项复测另见regression-published.log。并发迁移后47项知识检查仍通过，namespace首次模块调用因测试目录不在sys.path出现1项import error；以PYTHONPATH=tests正确调用后10/10通过（namespace-corrected.log），原日志保留。没有代码逻辑或新Skill修改。插件只同步知识快照，不宣称用户已有安装自动更新。

## 状态与下一步

TASK MATH-43/44维护知识、证据、限制与发布读回；保留其他学科队列。已同步main b288930，旧数学游标completed；结果库检索有缺record错误，不用旧数据替代新验证。单一作者写任务文件，独立验证者仅写自己的证据。后续优先：真实post-RoPE残差分布、外包数值实现、同索引/缓存/候选预算的GPU与e2e对照。本轮不宣称Agent整体表现更好。

提交和远端读回记录见publication.json；仅远端核对完成后才报告发布成功。

发布整合更新：远端acf85d7将工作流目录迁为agent_doc；本轮结果已迁移，冻结原manifest/raw保留，relocation.json逐项验证旧哈希。独立phase2发现检索记录缺domain参数且上游语料变动，状态pending，不冒充可重放通过。现已在新语料重新执行，knowledge-usage.json含完整argv、domain、index与snapshot；独立delta复验通过；原命令遗漏与pending记录保留。旧报告/usage/cost备份pre-relocation保留。
