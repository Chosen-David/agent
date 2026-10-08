# MATH-39/40：概率KL的中心化分数几何

2026-10-08；基线main b327113958124f2025a35f8cf15965cdc898c01c。先pull，读AGENTS、空只读GUIDE、唯一TASK、15角色、学科索引及持续状态。既有数学运行completed；本轮有界直接宿主，不宣称tmux/ManagedEngine/保护ReviewSession已部署。

## 真正增加的推导入口

已有math.softmax-barycenter-error已经包含TV尖锐tanh界，因此不重复造卡。新增math.softmax-kl-fisher@1补齐有限指数族的KL积分、中心化误差、Fisher曲率及概率下限。共同logit平移对概率无影响；有界路径方差控制KL，单点曲率只在有跨度控制时才可作代理；饱和反例拒绝全局正二次下界。一般推导自足、非形式化，公开数值例不替代证明。

迁移到indexer：同query/历史/有效支持上的代理分数可测中心化MSE、参考Fisher、精确KL和跨度。仅用于选集合的代理KL不是最终输出KL；attention token轴与生成词表轴不同。尚未证明代理→value输出→后续层→词表概率的完整链，不修改生产行为或SGLang。跨域有限Boltzmann权重严格共享指数族结构；真实平衡机制未验证。

实际旧结果查询在prior-results.json。有限扫描发生7条旧记录缺失错误，检索不完整，不声称全库不存在同结果。已直接阅读现有TV正文，确定不重复；旧传播/序列数据不替代新KL开发案例，不复用旧数字支持新主张。

## 原始文献筛选及限制

经典依据：[Blanchard/Higham/Higham作者稿](https://www.pure.ed.ac.uk/ws/portalfiles/portal/150063512/paper.pdf)，May15,2020认可版，正式IMA JNA41(4)2311–2330，DOI10.1093/imanum/draa038。核查LSE梯度、Hessian/Jacobian和shift算法。KL有限推导由项目自足展开，不把此稿说成证明全部界。

近期：[How Much Rank Does LoRA Need?](https://arxiv.org/abs/2608.26052)，当前abs记录仅v1，2026-08-26 17:25:03UTC。网页工具arxiv访问失败后通过requests取得原始HTML和abs；定向读§3 Theorem3.1、§5.1、AppendixE。作者的跨度约束下Fisher界比卡内简化包络紧；LoRA受限类的下界不能直接扩展为FC/indexer候选类。这里只采用可自足核对的有限KL结构；谱rank与饱和构造完整证明未采纳，无模型复现，正式接收未核实。

[Softmax as Linear Attention in the Large-Prompt Regime](https://proceedings.mlr.press/v306/boursier26a.html)，ICML2026 PMLR306:9392–9429正式出版，已取finalPDF；定向读§2 Gaussian全测度和§3 iid/subGaussian浓度。该模型忽略位置/mask，不作为真实长文本RoPE自动线性化的证书。未读完整训练证明，不复用论文成绩。原始访问版本、私有取回文件hash及失败入口见research.json；不宣称穷尽截至今日所有最新研究。

## 验收与成本

Producer64组、905断言，另10组边界与4个饱和配置；实际支持范围待独立六项代码/输入/数据验收。真实host接收独立协作后才消费数据；manifest/validation绑定记录随后追加。无Lean、真实模型/GPU/物理实验。

三个公开自然问题先人工抽取结构，再用files/sqlite各查三条；6次目标均第一，完整单条show包3625 cl100k_base tokens。8次CLI调用只计index+search+show，不含网页、宿主总token与回归；不是账单、token节省或模型自主提取/拒用成绩。所有公开题用于开发，holdout-protocol只保留未来新文档/轨迹协议，未运行未见测试。

下一步：用真实生成路径一致的概率trace比较精确KL、Fisher代理与e2e；层/位置/温度和硬mask分开检查，冻结方法与预算后再独立校准和留出。缺这些数据时不部署候选、不声明性能提升。

同步插件后74项知识回归通过（12.846s）；同步前仅exactmirror缺新卡而失败，原日志保留regression-before-sync.log。两语料格式/引用与项目TASK结构检查通过；这些不是模型质量验证。

并发同步：origin/main新增0e26c87/0347d0e两RL卡；普通merge保留其TASK/工程rotation/state/证据。旧184语料manifest与检索文件保存pre-sync/，旧独立记录只适用旧快照，不能认证当前文件；当前188语料重做检索/绑定，数学原始代码/config/raw不变。从origin/main比较自身增量，不改其他轮次冻结CRLF字节。

最终独立validation-v2六项及实际host inspect_result均usable-with-scope。64组+10边界+4饱和高精度参考通过，最大直接KL误差2.88e−16；raw/summary重跑一致，188文件全部核对。当前manifest6c74f665f6c480648a6ba96bbaa020344ff73436013f694512de09adc127b019，validation-v2 SHA c6ef5da41f29effe12d32c1e2f24930cae9439e6ef107e01e3457db963537694。合并后74回归通过（12.398s）；上述支持范围仍无真实模型/GPU、形式化或节省主张。

普通main实现提交`730bfb344c1636285e9cea87c0f51dda31fa149e`已fetch读回，树7104c1b28c6cd29ed49196436c37aa06cf1b34b5与本地一致；未force，并发修改保留。后续模型/真实trace留出仍未完成。
