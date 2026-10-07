# 工程知识库升级与核验

来源核查始于 2026-10-06，WSL 重启恢复与部署验收在 2026-10-07。用户授权扩展已有知识库及本机 WSL/tmux 定时维护，沿用 main 发布授权，不改 SGLang。原库为 10 条数学/物理知识，整合并发新增的 7 条数学知识后现为 39 条。保留 Git JSON/Markdown 事实源、SQLite FTS5/BM25 派生索引、章节导航、上下文与版本引用，未重建独立知识平台。

新增 22 张卡，阅读 13 篇原论文实验/消融与 6 个成熟仓库的固定源码/许可证。原始文件 SHA256 和完整 commit 见 [sources.json](sources.json)，正文定位见每卡 sources.locator。原文未随库镜像，代码实现未复制或本机执行。选材包括历年顶会与 2026 年资料；FlashAttention-4 明确是预印本。不是完整文献普查，也不能声称 Agent 总体性能或 GPU 性能提升。

主 AI 先查原实验条件、负结果与最小迁移检查；代码 Agent 获取固定源码/API、许可证和正确性/目标性能检查入口。结构化 `decision` 精确比较已提供条件，未知/不匹配可见，始终不授权自动跳过；字符串相同不证明实验等价，显式复现保持原要求。实现指针不等同安装或 benchmark。

## 验证与部署

检索评估是作者编写的合成回归，不能替代独立任务评估。详见 [retrieval.json](retrieval.json) 与 [validation.json](validation.json)。新的 15 个检索案例包含 14 个正例和 1 个无命中；最终 39 条知识的两后端 Recall@3/MRR/context recall 均为 1。决策测试覆盖条件缺失/硬件不符、显式复现、实现类型过滤、拒绝非固定代码版本、原 schema 与独立 Skill 相同输出。

本机 WSL 3.0.1、Ubuntu-26.04 (WSL2)、tmux 3.6 已实际安装。旧原生 CLI 0.114.0 对配置模型返回 unsupported；升级为桌面应用自带 CLI 0.160.1 后，WSL tmux → Windows Python → Codex 的真实登录探测返回 READY，未复制登录凭据进 Linux。最终调度/回归读回见 validation.json 与 [维护说明](../../knowledge_maintenance.md)。定时器只保证本机运行时调度；停机/睡眠期间不执行，恢复沿用持久状态。不把模型退出 0 当作独立科研验收。

最终全仓 494 项：483 通过、11 项因可选依赖跳过；真实 tmux 测试通过，Reader 3/3。完整日志随本报告保存。原检索集 raw Recall@3 为 20/21；词形 SQLite 集 raw Recall@3 为 3/4，依赖上下文召回为 1；文件后端不支持这些词形变化。扩库后的 residuals 排名拥挤仍需改进，不将上下文命中混称为原始排名命中，也不把合成查询当成盲测。

原生 Windows Git 宿主 4/4 隔离 fixture 通过。模型 Git 写入仍由 sandbox 拒绝；宿主仅在完整工作文件树与远端一致时对齐元数据。旧 never 审批策略拒绝 GitHub 写工具；改为本进程 granular MCP 审批并接入官方 auto_review 后，实际创建无分支引用的无害 blob `80a6f5fd7f9b40163d956f72c87d0775e12cc391`，主 AI 独立读回完全一致。该探测证明实际写能力，不保证未来论文质量或每轮发布成功。

整合并发的知识交接升级后，首次 Linux 检查发现 Windows 路径分隔符导致两份插件链接未同步；494 项中该项失败，失败与修复见 [integration-failure.json](integration-failure.json)。改用跨平台路径并重新生成，最终状态以 validation.json 的最新冻结回归为准。

## 采用与边界

复用 ACL/FAISS/HNSWlib/FlashAttention/FlashInfer/PEFT 的固定实现指针，避免重新写成熟内核；原论文不外推为本机高性能。暂不引入向量模型、GPU 服务、全量论文抓取或复制实现。NSA 的负结果、CAR-LoRA 训练预算差异与 FA4 比较基线变化均保留。新环境仍需小规模迁移验证，用户明确要求的实验不能用论文替代。

下轮优先分布式通信/训练与内存吞吐权衡，再轮转后训练算法和缓存/并发数据结构。见 coverage.json 缺口与 learning_state.json 独立 engineering 游标。

## 逐卡来源阅读与决策边界

<a id="impl.flashattention-library"></a>

### impl.flashattention-library

复用 FlashAttention 公共接口（v1）。

- [原始来源](https://github.com/Dao-AILab/flash-attention/blob/47e91f1f7dd8a22649cee0dd9a182b69ffe782ef/LICENSE)：LICENSE。
- [原始来源](https://github.com/Dao-AILab/flash-attention/blob/47e91f1f7dd8a22649cee0dd9a182b69ffe782ef/flash_attn/flash_attn_interface.py)：flash_attn/flash_attn_interface.py。
- [原始来源](https://github.com/Dao-AILab/flash-attention/blob/47e91f1f7dd8a22649cee0dd9a182b69ffe782ef/README.md)：README.md。

条件：operation=supported dense attention variant；device=supported NVIDIA GPU；semantic=exact attention within floating-point tolerance。

- flash_attn_interface.py 提供普通与 varlen 入口；README 列设备/构建和版本能力。

限制：FA2 入口与 FA4/cuTe 路径不自动同 API；不要依据论文名称猜兼容性。；没有本机 GPU 编译/benchmark，不声称已安装或更快。

最小检查：核对输入布局和 causal 对齐，独立 dense reference 对照。；目标设备编译和一组代表性形状延迟，保留 fallback。

<a id="impl.flashinfer-plan-run"></a>

### impl.flashinfer-plan-run

复用 FlashInfer plan/run 接口（v1）。

- [原始来源](https://github.com/flashinfer-ai/flashinfer/blob/ea8135c0bdf641f54214e9ae777d5b75b5133079/LICENSE)：LICENSE。
- [原始来源](https://github.com/flashinfer-ai/flashinfer/blob/ea8135c0bdf641f54214e9ae777d5b75b5133079/flashinfer/decode.py)：flashinfer/decode.py。
- [原始来源](https://github.com/flashinfer-ai/flashinfer/blob/ea8135c0bdf641f54214e9ae777d5b75b5133079/flashinfer/prefill.py)：flashinfer/prefill.py。

条件：operation=paged or ragged attention inference；device=supported NVIDIA GPU；lifecycle=explicit plan then run。

- decode.py / prefill.py 包含不同场景 wrappers，plan 准备元数据后 run 执行。

限制：不自动安装依赖，不修改 SGLang。；plan 元数据过期、workspace 复用和 stream 错误会破坏结果。

最小检查：核对 indptr/indices/last_page_len、heads、workspace 大小。；先 correctness reference，再独立计入 plan/run 延迟。

<a id="infra.flashattention-io"></a>

### infra.flashattention-io

FlashAttention：用 IO 分析选择精确注意力实现（v1）。

- [原始来源](https://papers.nips.cc/paper_files/paper/2022/file/67d57c32e20fd0a7a302cb81d36e40d5-Paper-Conference.pdf)：§3; §4.1–4.3; Figures 3–4。

条件：operator=dense exact attention；hardware=NVIDIA GPU；metric=attention IO and end-to-end training。

- §3 的分块算法不在 HBM 保存完整 N×N 分数矩阵；§4 分别比较运行时间、内存和训练。
- §4.1 的端到端 GPT-2 训练与核算子加速分开报告，不能混用。

限制：算术仍为 O(N²d)；线性的是额外中间存储。；短序列、mask、dtype 或实现版本变化后，旧收益不保证成立。

最小检查：核对 mask/dropout/梯度语义及浮点容忍度。；先测代表性一个形状的算子和端到端占比，再决定是否扩展。

<a id="infra.flashattention2-occupancy"></a>

### infra.flashattention2-occupancy

FlashAttention-2：小 batch 下的并行划分（v1）。

- [原始来源](https://proceedings.iclr.cc/paper_files/paper/2024/file/98ed250b203d1ac6b24bbcf263e3d4a7-Paper-Conference.pdf)：§3.2–3.3; §4; Figures 3–5。

条件：hardware=A100；operator=dense exact attention；metric=kernel forward/backward throughput。

- §3.2 将序列维度也并行；§3.3 减少 warp 间 shared-memory 通信。
- §4 报告 A100 的 50–73% 峰值 FLOPs 利用率；GPT 训练的最高 225 TFLOPs/s 是另一指标。

限制：不能把 kernel 利用率当端到端模型加速。；不承诺 A100 结果适用于 Hopper/Blackwell；原子累加与确定性要求要单独核查。

最小检查：核查 batch×heads 是否足够填满目标 GPU。；比较现有库和新实现的数值、确定性及目标形状延迟。

<a id="infra.flashattention4-blackwell"></a>

### infra.flashattention4-blackwell

FlashAttention-4：Blackwell 非矩阵瓶颈与过时基线（v1）。

- [原始来源](https://arxiv.org/pdf/2603.05451)：§2.2–3; §5.1; Figure 4 caption。

条件：hardware=B200；dtype=BF16；operator=attention forward；baseline=cuDNN 9.13 and Triton in paper。

- §5 设置总 token=32k，序列 1k–32k，hidden=2048；head dims 64、128 和 (192,128)。
- §5.1 Figure 4：相对 cuDNN 9.13 为 1.1–1.3×，相对 Triton 为 2.1–2.7×；图注说更新 cuDNN 性能可相近。

限制：预印本身份，未标为顶会已接受；不把峰值 1613 TFLOPs/s 当整模型速度。；B200 条件不能直接迁移到 A100/H100；新 cuDNN 基线会改变收益。

最小检查：读取目标硬件和当前 cuDNN/库版本。；先做数值/梯度和一个目标形状的库比较；单独检查确定性反向。

<a id="infra.flashinfer-scheduling"></a>

### infra.flashinfer-scheduling

FlashInfer：不规则 KV 与负载平衡（v1）。

- [原始来源](https://proceedings.mlsys.org/paper_files/paper/2025/file/dbf02b21d77409a2db30e56866a8ab3a-Paper-Conference.pdf)：§3.2–3.4; §4; Figures 7–11。

条件：hardware=A100 40GB SXM or H100 80GB SXM；workload=ragged/batched LLM inference；metric=attention latency and end-to-end serving。

- §3 描述动态调度、plan/run 分离与 CUDA Graph 兼容；§4 分别测 kernel 和端到端。
- 论文摘要的 ITL 降低 29–69% 属于所测服务栈；长上下文与并行生成是另外实验。

限制：计划、JIT、graph 建立成本不应被遗漏；冷启动不等于稳态。；论文服务实验含 SGLang，但本仓库明确不修改 SGLang；仅复用独立算子知识。

最小检查：核对 paged/ragged 格式、heads/dtype、stream 与 plan 生命周期。；在目标 workload 单独记录 plan、run、冷启动和稳态。

<a id="infra.pagedattention-kv"></a>

### infra.pagedattention-kv

PagedAttention：KV 分页与服务吞吐（v1）。

- [原始来源](https://arxiv.org/pdf/2309.06180)：§6.1–6.6; Figures 12–18。

条件：hardware=A100；models=OPT and LLaMA-13B；workload=ShareGPT/Alpaca length traces with Poisson arrivals；metric=normalized end-to-end latency versus request rate。

- §6.1 用长度合成请求和 Poisson 到达；Orca 是作者重实现，Oracle 预知输出长度，是不可部署上界。
- §6.2 ShareGPT 中相近延迟下可承受请求率相对 Orca Oracle 提高 1.7–2.7×；Alpaca 的 OPT-175B 余量更大时差距缩小。

限制：不是单个 attention kernel 加速，不能替代 TTFT/ITL/SLO 的本机验证。；2023 系统基线不是 2026 最新服务栈；跨工作负载倍数不可直接迁移。

最小检查：核对长度分布、到达率、KV 占用和延迟 SLO。；先在一个负载点检查分配浪费/队列/吞吐，保留现有强库基线。

<a id="infra.speculative-acceptance"></a>

### infra.speculative-acceptance

投机解码：接受率不能单独决定速度（v1）。

- [原始来源](https://proceedings.mlr.press/v202/leviathan23a/leviathan23a.pdf)：§3.3–3.4; §4.1 Table 2; Appendix A.3。

条件：hardware=single TPU-v4；target=T5-XXL 11B；batch=1；tasks=WMT EnDe and CNN/DailyMail。

- §4.1 Table 2：EnDe temp=0、γ=7，T5-small α=0.75、3.4×；T5-large α=0.82、1.7×。
- 相同 small draft 在 EnDe temp=1 报告 2.6×，CNN/DM temp=1、γ=5 报告 2.3×。

限制：精确采样算法保留目标分布，不保证不同实现相同随机种子的逐 token 一致。；不能由 batch=1 推断高并发吞吐；拒绝修正、tokenizer 和 sampling 处理必须正确。

最小检查：先验证拒绝采样/目标分布，核对 tokenizer 和解码参数。；只用少量目标输入测 α、draft 时间、验证时间，避免盲扫 draft 大小。

<a id="algo.car-lora-transfer"></a>

### algo.car-lora-transfer

CAR-LoRA：量化迁移结果与训练预算混杂（v1）。

- [原始来源](https://proceedings.iclr.cc/paper_files/paper/2026/file/72491c8fd75d85b4b5adf561a15bcd2c-Paper-Conference.pdf)：§4.1; §4.2 Table 1; §4.3 Table 2; temporal evolution experiments。

条件：models=Llama-3.1-8B Mistral-7B Gemma-2-9B；compression=INT8 FP4 NF4 structured pruning layer skipping；metric=reasoning benchmark accuracy。

- §4.1 基线训练 5 epochs、CAR-LoRA 20 epochs，不是等训练预算比较。
- §4.2 Table 1：Llama-3.1 GSM8K 的 BF16 LoRA 38.9%，CAR-LoRA NF4 38.1%、layer skipping 31.1%。

限制：模拟 continued pretraining 不等于任意厂商未来版本；需结构兼容与迁移质量验收。；存在训练预算混杂，不能把全部收益归因于压缩感知机制。

最小检查：对目标基座/量化做小 held-out 测试。；若声称方法优越，补等训练预算对照；只做迁移决策时先不重做全论文。

<a id="algo.dora-magnitude-direction"></a>

### algo.dora-magnitude-direction

DoRA：幅值/方向观察与额外训练成本（v1）。

- [原始来源](https://raw.githubusercontent.com/mlresearch/v235/main/assets/liu24bn/liu24bn.pdf)：§3 Figure 2; §4; §5 task tables。

条件：method=magnitude plus low-rank directional updates；models=LLaMA LLaVA VL-BART in paper；metric=downstream task quality。

- §3 Figure 2 比较 FT/LoRA 的幅值与方向变化；§5 表格比较下游结果。
- §4 的归一化方向和可学习幅值能够合并推理权重，但训练计算/内存须单独考量。

限制：不能由几层权重趋势推出所有模型 LoRA 失败机制。；同 rank 不一定同训练成本；应同时比较参数/显存/耗时和质量。

最小检查：核对列/行方向、范数梯度与 merge 结果。；做一个固定预算 LoRA/DoRA 对照；不重复论文全部权重趋势实验。

<a id="algo.dpo-offline-preferences"></a>

### algo.dpo-offline-preferences

DPO：离线偏好优化的适用前提（v1）。

- [原始来源](https://proceedings.neurips.cc/paper_files/paper/2023/file/a85b405ed65c6477a4fe8302b5e06ce7-Paper-Conference.pdf)：§4; §6.1–6.3; Figures 2–4; Tables 1–2。

条件：data=paired chosen/rejected offline preferences；objective=KL-regularized preference learning；metric=preference quality versus KL。

- §4 从 Bradley–Terry 偏好模型推导目标；§6 在 sentiment、TL;DR 和 HH 比较。
- §6 包含 GPT-4 评测与人工比较；评测器和生成温度会影响 win rate。

限制：离线数据分布、偏好噪声与 reference policy 必须核查。；论文不能替代新领域安全/质量验收；不能宣称离线方法永远胜在线 RL。

最小检查：验证 chosen/rejected 标注、token log-prob 掩码和 reference 冻结。；用少量 held-out 对照、KL 与质量联合看，避免仅训练 loss 决策。

<a id="algo.gqa-uptraining"></a>

### algo.gqa-uptraining

GQA：额外训练与质量/速度折中（v1）。

- [原始来源](https://aclanthology.org/2023.emnlp-main.298.pdf)：§3.1; Table 1; §3.3 Figures 4–5。

条件：model=T5.1.1 XXL；uptraining=5% original pretraining steps；timing=8 TPUv4 chips greedy decoding。

- §3 Table 1：MHA-XXL 平均 47.2、GQA-8 47.1；时间为 1.51 s 与 0.28 s，每 sample 每 TPUv4 chip。
- §3.3 Figures 4–5：mean pooling 优于 first/random；5% uptraining 有收益，10% 增量变小。

限制：不能把不同任务指标的平均值看成一个标准精度；图/表时间标注须以方法与表为准。；5% 对应约 600 TPUv3 chip-days，不是无成本；直接替换 decoder-only 新模型需质量验证。

最小检查：核对 Q heads/KV heads 分组与转换权重。；少量代表输入检查质量，再决定是否值得 uptraining；不盲重做已报道 pooling 全网格。

<a id="algo.lora-intrinsic-rank"></a>

### algo.lora-intrinsic-rank

LoRA：低秩更新与合并边界（v1）。

- [原始来源](https://arxiv.org/pdf/2106.09685)：§5 Tables 2–4; §7 rank ablations; Appendix。

条件：method=frozen backbone plus low-rank weight update；models=RoBERTa DeBERTa GPT-2 GPT-3 in paper；metric=task quality and trainable parameters。

- §5 Tables 2–4 比较多任务适配；§7 分析 rank 与更新子空间。
- 可合并 W+BA 后不加推理分支；未合并、多 adapter 切换时不是零开销。

限制：冻结权重仍有存储与激活成本；rank 增大不保证单调改善。；原论文含引用的他人基线和不同设置，不能当严格同条件本机 A/B。

最小检查：核对 target modules、rank/alpha、初始化与 merge 语义。；先选小规模 rank 对照与 held-out 质量，不重复全量秩扫描来证明普遍低秩。

<a id="algo.nsa-native-training"></a>

### algo.nsa-native-training

NSA：原生稀疏训练不等于无损替换（v1）。

- [原始来源](https://aclanthology.org/2025.acl-long.1126.pdf)：§3.1 Tables 1–2; §4 efficiency; Appendix C–D。

条件：model=27B total / 3B active MoE with GQA；training=270B tokens at 8k then 32k continuation；method=compression selection sliding-window branches。

- §3.1 指定压缩块 32、步长 16、选择块 64、16 块、窗口 512。
- Table 1：MBPP 从 full 0.482 到 NSA 0.466，MMLU 0.567 到 0.565；平均收益不掩盖退化。

限制：稀疏 FLOPs 减少不必然转为硬件速度；必须计入选择和布局开销。；原生训练结果不证明替换任意 checkpoint 无损，64k kernel 图不是全模型吞吐。

最小检查：核对训练架构授权和质量约束；若仅要求等价 kernel 则不采用。；只做目标块布局/选择开销的最小 profile，再决定研究规模。

<a id="algo.qlora-memory"></a>

### algo.qlora-memory

QLoRA：存储 dtype 与计算 dtype 分离（v1）。

- [原始来源](https://papers.neurips.cc/paper_files/paper/2023/file/1feb87871436031bdc0f2beaa62a049b-Paper-Conference.pdf)：§3–4; quantization and adapter ablations; Appendix。

条件：method=NF4 frozen backbone plus LoRA；model=65B model in paper；metric=finetuning memory and task quality。

- §3 区分 4-bit 存储和 BF16 计算，double quantization 减少量化常数，paged optimizer 应对峰值。
- §4 的消融考察 NF4、double quantization 和 LoRA 配置；对 chatbot 的评级存在评测器局限。

限制：不代表全参优化；activation、optimizer、KV/序列长度仍可 OOM。；不把 Vicuna 自动评分比例当通用 ChatGPT 能力等价。

最小检查：核对量化格式、计算 dtype、target modules、梯度检查点与序列长度。；测一小批显存峰值和 held-out 质量即可先评估可行性。

<a id="impl.peft-lora-dora"></a>

### impl.peft-lora-dora

复用 PEFT 的 LoRA / DoRA 实现（v1）。

- [原始来源](https://github.com/huggingface/peft/blob/e13de7e469d37e3163d93f2356ec013c7a7e1f0a/LICENSE)：LICENSE。
- [原始来源](https://github.com/huggingface/peft/blob/e13de7e469d37e3163d93f2356ec013c7a7e1f0a/src/peft/tuners/lora/layer.py)：src/peft/tuners/lora/layer.py。
- [原始来源](https://github.com/huggingface/peft/blob/e13de7e469d37e3163d93f2356ec013c7a7e1f0a/src/peft/tuners/lora/dora.py)：src/peft/tuners/lora/dora.py。

条件：operation=LoRA or DoRA adapter training；framework=PyTorch with PEFT；backbone=supported model modules。

- layer.py 包含 adapter layer 与 merge 逻辑；dora.py 包含幅值/方向实现。

限制：示例 target_modules 占位必须按模型替换；quantized merge 和 dropout 路径需单独核查。；未安装/训练目标模型，不能声明质量或速度已验证。

最小检查：核对冻结参数、target_modules、训练/推理输出与 merge 前后数值。；保存 adapter 配置、基座版本与加载测试；量化迁移需新质量检查。

<a id="ds.dsu-connectivity"></a>

### ds.dsu-connectivity

DSU：增量连通与不可删除边界（v1）。

- [原始来源](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)：LICENSE。
- [原始来源](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/dsu.hpp)：atcoder/dsu.hpp。

条件：operation=incremental undirected connectivity；updates=insert-only；concurrency=single writer。

- parent_or_size 负值存 root 大小；leader 压缩路径，merge 合并较小树。

限制：均摊不等于每操作常数；rollback 不能直接套有压缩实现。；动态图删除需不同结构/离线算法。

最小检查：用 BFS 小图连通性作独立 oracle。；核对重复合并、自环和 size；需要删除时换方案。

<a id="ds.faiss-exact-vector"></a>

### ds.faiss-exact-vector

Faiss IndexFlat：精确向量搜索强基线（v1）。

- [原始来源](https://github.com/facebookresearch/faiss/blob/83ae8b0908312c1e40734a806a3cc435b64f9496/LICENSE)：LICENSE。
- [原始来源](https://github.com/facebookresearch/faiss/blob/83ae8b0908312c1e40734a806a3cc435b64f9496/faiss/IndexFlat.h)：faiss/IndexFlat.h。

条件：operation=dense vector nearest-neighbor search；metric=L2 or inner product；quality=exact。

- IndexFlat 存完整向量；L2 与 IP 是不同 metric，L2 返回平方距离。

限制：IP 不是自动 cosine；cosine 需要规范化。；CPU/GPU API、传输与目标 build 要核对；没有无条件高性能保证。

最小检查：核对 float32/layout、metric、归一化与 k>n 返回行为。；小样本直接计算距离，ANN 的 recall 对此基线比较。

<a id="ds.fenwick-point-range"></a>

### ds.fenwick-point-range

Fenwick tree：点增量与区间和（v1）。

- [原始来源](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)：LICENSE。
- [原始来源](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/fenwicktree.hpp)：atcoder/fenwicktree.hpp。

条件：operation=point add and range sum；range=zero-based half-open；concurrency=single writer。

- add 沿 p += p&-p 上升，prefix sum 沿 r -= r&-r；sum(l,r) 是前缀差。
- 整数实现内部使用 unsigned；支持类型和溢出语义应核对。

限制：不支持直接区间赋值/min；非可减聚合不能用前缀差。；教学库不提供并发安全/持久化或生产性能承诺。

最小检查：核对类型范围、l=r、边界和负增量。；用独立朴素数组对照少量操作，再按目标规模测开销。

<a id="ds.hnsw-recall-budget"></a>

### ds.hnsw-recall-budget

HNSW：ef、召回与内存预算（v1）。

- [原始来源](https://github.com/nmslib/hnswlib/blob/ca426729609b3221563047ceb269cc1213e0d376/LICENSE)：LICENSE。
- [原始来源](https://github.com/nmslib/hnswlib/blob/ca426729609b3221563047ceb269cc1213e0d376/hnswlib/hnswalg.h)：hnswlib/hnswalg.h。
- [原始来源](https://github.com/nmslib/hnswlib/blob/ca426729609b3221563047ceb269cc1213e0d376/README.md)：README.md。

条件：operation=approximate vector nearest-neighbor search；metric=l2 ip or cosine；quality=approximate。

- README 分开定义构建 M/ef_construction 与查询 ef；源码为多层图搜索。
- 并发 insert/query 组合限制与索引保存后的 ef 恢复行为要按固定版本核对。

限制：无所有数据分布上的 O(log n) 最坏搜索保证；分布变化可影响召回。；不支持把 ANN 结果作为 exact correctness oracle。

最小检查：用精确检索测 Recall@k 与 p95 延迟；包含目标分布和内存。；至少一个较高 ef 对照，确认召回而不是仅速度。

<a id="ds.maxflow-matching"></a>

### ds.maxflow-matching

最大流：容量网络与二分图匹配（v1）。

- [原始来源](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)：LICENSE。
- [原始来源](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/maxflow.hpp)：atcoder/maxflow.hpp。

条件：graph=directed capacity network；capacity=nonnegative integer；source_sink=distinct。

- add_edge 保存正反边；flow 用 level graph 和阻塞流更新 residual capacity。
- flow 是增量修改残量状态；再次调用的结果不是自动从零重算。

限制：加权最小成本问题需要 min-cost flow；不能把最大 cardinality 当最大 weight。；容量溢出、状态复用和不当图建模会改变语义。

最小检查：小二分图枚举匹配或检查 min-cut 容量作独立 oracle。；核对重复 flow 调用与 cap 类型上界。

<a id="ds.segment-monoid"></a>

### ds.segment-monoid

Segment tree：结合聚合与边界搜索（v1）。

- [原始来源](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/LICENSE)：LICENSE。
- [原始来源](https://github.com/atcoder/ac-library/blob/864245a00b00dd008d1abfdc239618fdb7d139da/atcoder/segtree.hpp)：atcoder/segtree.hpp。

条件：algebra=associative op with identity；range=zero-based half-open；operation=point set and range aggregate。

- prod 用左右两个累积器保持顺序，适用于非交换 monoid。
- max_right/min_left 需符合文档的单调 predicate 且 f(e())=true。

限制：无结合律的运算不可直接使用；区间更新需另选 lazy_segtree。；整数溢出、浮点结合律误差和 predicate 非单调可破坏结果。

最小检查：检查独立 algebra 例子、空区间与非交换顺序。；边界搜索先核对 predicate 单调性。
