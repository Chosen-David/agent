# Two-Level Attention：性能脚本与提交复盘

## 触发与范围

写 GPU benchmark、改 kernel 接口、跨机器跑实验或扩展 batch 时检索本卡。
2026-11-17 核读下列三个固定提交的相关 diff；这是历史样本复盘，不是全部历史审计，
也不是对当前 main 仍有这些缺陷的判断。错误归因于代码/流程，不据提交署名判断作者能力。
本次没有运行目标 GPU、模型或复核远端原始性能日志；下述运行结果明确标为原提交报告。

## 1. 直接 benchmark 漏传 kernel 参数

来源：[4bc6aa98730e060489f742bfe1875d687237e422](https://github.com/Chosen-David/two-level-attention/commit/4bc6aa98730e060489f742bfe1875d687237e422)，2026-11-07。
三个文件为 benchmark/efficiency/benchmark_nfa_topk_{merge,partial,tile}.py。
修复均为给 _nfa_filtered_topk_partial_kernel 调用补 TOKEN_BITS=16。

**已核实**：三个旧调用没有该关键字、三个新调用补齐。
**原记录说明**：静态复核发现缺少既有参数；修复后空卡监控下三个脚本返回0，各10个seed及Graph对拍通过。
本次未重新执行这些 CUDA 测试，不能把返回0转述成本机复现。

不优雅之处是多个直接调用点复制私有 ABI，容易与生产入口脱节。复用小型统一 launcher 或
签名契约可减少漂移，但不能为了“统一”把不同 tile/warp 实验强行合并。
改接口时同时枚举生产、benchmark、测试调用者；语法检查不验证 JIT 调用参数。
最小验收为真实脚本小输入启动、输出与独立 oracle 对拍，再计时。
删除必要参数的负控应被契约检查明确拒绝；若只是 GPU 编译崩溃，记录启动失败，不能算正确性变异检出。
本例的16只属于固定版本和编码约束，不是所有容量/实现可照抄的常量。

## 2. 监控脚本硬编码另一台机器的 GPU UUID

来源：[7842c6fb590308976aa05902b3fb5b5f668ec5bd](https://github.com/Chosen-David/two-level-attention/commit/7842c6fb590308976aa05902b3fb5b5f668ec5bd)，2026-10-30，
exp/bench/request_gpu_monitor.py，GPU0Monitor.__init__。

旧实现固定单一 GPU UUID；新实现读取 CUDA_VISIBLE_DEVICES 首项（未设置时用0），
调用 nvidia-smi 查询 UUID，对空设备、空结果或多行结果拒绝。修复体现了“先核设备身份，再测量”的优点。
不可把逻辑 cuda:0 当固定物理 GPU0；基准实际设备和占用监控设备必须一致。
不优雅之处是把部署机器状态写进代码；应从真实运行设备取得身份并写入回执。

**适用边界**：该 diff 不证明所有 CUDA_DEVICE_ORDER、MIG、容器映射都正确。
在这些环境中还需核对 CUDA 实际设备 UUID 与监控 UUID，未知时停止性能结论；
不能声称此修复已解决全部设备映射问题。拒绝通过关闭占用检查来让脚本“跑过”。

## 3. batch 输出人口与 TPOT 分母要分开

来源：[84a16f1210133803a3bf4d69be2a2ef7bfff70cf](https://github.com/Chosen-David/two-level-attention/commit/84a16f1210133803a3bf4d69be2a2ef7bfff70cf)，2026-11-14，
benchmark/official_baselines/longbench_official.py 的 _generated_rows/timed_pair；
tests/test_official_longbench.py 的 batch-major/参差行用例。

旧 timed_pair 按扁平列表长度验收 B1；新实现核验每行固定长度、两次 batch 布局/行数一致，
分别记录 batch_size、每请求 token 数和总 token 数。这是扩展契约，不应倒推旧 B1 实现本身有错。
保留的好做法：不支持的 backend/batch 明确拒绝，不暗中降级成别的实现。

可计算例：B=2，每请求33 token，T(1)=0.1秒，T(33)=3.3秒。
差值3.2秒含32个 batched decode step，TPOT=100毫秒/step；输出总量66，
差分 decode token 数64，其吞吐为20 token/秒。用66或64作 TPOT 分母会混淆指标。
该数值是原测试的合成时间例，不是 GPU 实测；两点差分还要求初始化、缓存和计时边界可比。
不能无条件用两次独立请求相减解释逐步延迟，不能把固定长度忽略EOS的性能协议当自然停止质量评估。

## 值得保留的实验行为

4bc6aa98 的 ITERATIONS.md 保留 eager 26.047992→27.610776毫秒和 Graph
9.787616→9.841296毫秒等原报告负结果，并指出 eager 两条 candidate 腿方向不一致，
追加独立 ABBA 复跑而不覆盖原数据。这比只挑最好的一次或把算子提速写成生产 TPOT 收益可靠。
上述数字只是原记录的归属引用，本卡不认证其性能或显著性。

可复用顺序：固定提交/输入哈希、环境与设备身份 → 正确性和边界形状 → 独立预热与明确计时范围
→ 配对/交错多次运行 → 留存每腿及异常 → 同时报告质量、计时口径和限制。
GPU 异步工作必须在所选计时边界完成；事件计时与含调度/拷贝的主机墙钟要分列。
Graph capture、编译、缓存构建是否计入必须说明；正确性 trace 的同步/拷贝不能混入宣称的无插桩性能。
这些是本次从案例归纳的检查建议，不宣称每一项都是该库已经发生过的错误。

## 后续 AI 的任务映射

沿现有 pstack 验证生成/维护/correct 串行流程，把适用断言写进 agent_doc/<项目>/test，
复用项目已有 benchmark 入口，不另造一套计时系统。最低负控包括：漏参数、错误设备身份、
缺失请求行、参差输出、错误分母、非正差值、声明Graph却fallback。
用目标断言拒绝错误；导入失败/超时/崩溃另记基础设施失败。先正常样本通过再做负控。
结果复用仍核代码、输入、环境、完整性及独立验证；结构PASS不能证明数值正确。

本卡通过知识库 schema/检索入口核验后可按需加载，不复制到所有启动提示。
未验证：目标GPU复现、全部历史提交、所有设备映射、长期避免重犯的效果。
