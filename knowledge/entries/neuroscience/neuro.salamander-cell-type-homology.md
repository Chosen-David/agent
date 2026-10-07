# 蝾螈端脑细胞类型：同源与趋同的多证据候选

## 问题触发

两种动物的神经细胞表达相似、在整合空间共聚类，是否足以判定同源或同功能？本条为candidate，补充方法与供体层级未核完，不进入默认published检索。

## 精确结论及证据范围

Woych等2022 Science研究的PMC作者稿使用蝾螈Pleurodeles waltl成年及幼体scRNAseq、空间标记与ex-vivo示踪，比较爬行类和小鼠既有数据。Results/Fig1报告质控36116细胞、29294分化神经元，47谷氨酸能和67 GABA能分群。这些是细胞与cluster数，不能作为独立动物重复数或固定自然类别总数。

Fig2结合HCR/ISH、iDISCO及light-sheet把分子群映射到端脑区域；Fig3报告36/41/46/50幼体阶段、20261端脑细胞，以成人标签转移和Slingshot推断不同DP/VP发育轨迹。计算伪时间不等于直接谱系示踪。

Fig4三物种整合产生65群。部分蝾螈VP与爬行类centromedial-aDVR共聚类伴随转录因子表达相似；POE与rostral-aDVR的部分共聚类则可能由效应基因相似驱动。正文明确区分共享调控程序与趋同解释。Fig5的无对应群、单物种群不证明物种绝对缺失该细胞。

Fig6及Methods summary报告24–48小时ex-vivo示踪；图注VPa、MP、LPa注射n分别4、2、2。供体重合与完整补图样本表未核，不合并为独立总动物数。投射、空间表达和转录组支持待审定的演化解释，没有记录这些细胞的行为因果作用或意识。

## 前提与未完成核验

成年为变态后阶段；幼体阶段不能并作成人样本。性别、供体数、合池及抽样分布、准确数据/软件版本尚需Supplementary Methods核对。Fig2图注切片尺度200µm、局部50µm，整体成像500µm；它们是图示比例尺，不是空间分辨率或体素尺寸。

正文称Harmony、SAMap、scVI及参数变化支持主要结果；S11/S12/S17尚未读取，不能将正文的稳健性声明冒称本轮独立核验。同一数据上的不同算法不是独立生物复验。S18/S19示踪、原始图像和终版差异待读。

## 推导或证明的范围

本条没有数学定理或形式化证明。组织与分子观察、计算整合结果和演化历史解释分开记录。哺乳类同源区域、祖先保留与次生丢失等替代解释不能由一个相似度树排除。

## 算得出的例子

仅作独立算术：47+67=114个分化神经元cluster；29294/36116约81.11%是该质控集合的分化神经元比例，分母不是脑内所有细胞或动物数。不据此估计物种全脑比例、供体方差或统计显著性。

## 失败与反例

两类细胞可能因共同感受器/通道等效应基因共聚类，调控因子和发育域却不同；表达相似不能单独确定共同祖先。整合未映射可能来自采样缺失、正交基因筛选、聚类参数或真实分化。分子、解剖或同步指标不代替功能干预、行为报告或意识测量。

## 固定源码与实现边界

作者仓库ToschesMA/Salamander-telencephalon固定commit `6ffbcbe5e6071bb3d0c333d959e4b0ef8d920921`，对应Zenodo6780577的v1.0.1。README绑定2022预印本，不能假定与Science终版全部分析相同。

已读Comparative analysis中的三物种Seurat integration脚本、build_integrated_taxonomy.Rmd和Seurat_label_transfer.Rmd。前者取一对一ortholog计数、SCTransform v2、CCA anchors、IntegrateData；自定义cluster.matrix.expression.distances.S使用Spearman距离，再Ward.D2。脚本含HPC绝对路径；标签转移模板含空readRDS/未填参数。独立taxonomy笔记使用未修改的距离函数并注明函数workaround，不假定所有入口等价。

完整固定树及已读文件无明确LICENSE/COPYING授予，Zenodo只写other-open。未采用实现卡、未复制源码或运行R，local_execution=not-run；没有GPU/CPU性能结论。优先补核作者参数与成熟Seurat接口，而非从零重建。

## 任务映射与AI假设

该候选支持安排供体/整合/示踪核查、识别“共聚类即同源”的证据缺口，可减少盲目用基因相似性推出通用计算机制的重复探索。补充核验前不能作为已发布科学结论。

待验证AI假设：共享核心加可分化模块可能改善迁移。最小可证伪对照是等参数、训练数据、交互与计算预算比较完全共享、完全独立、随机分组及生物启发分组；冻结未见任务误差和旧任务遗忘指标。随机分组或完全共享相当时，拒绝特定生物分组收益解释。生物学论文未验证该AI假设；没有提升AI、测得AI意识或修改模型权重的声明。显式复现与用户必做实验仍需实际执行。

## 来源定位与尚未验证项

[Science DOI](https://doi.org/10.1126/science.abp9186)，发表2022-09-02；本轮读PMC10024926作者稿经NCBI BioC XML，非出版商PDF。Results/Figs1–6图注、Discussion、Methods summary和data availability已读，单独补充材料访问403，保留candidate。原文与固定源码的完整字节哈希及真实检查见[本轮报告](../../../docs/knowledge_learning/2026-10-07-engineering-122522/report.md)与sources.json。local_reproduction=not-run；没有动物、原数据统计重建、R执行、AI迁移或盲测。
