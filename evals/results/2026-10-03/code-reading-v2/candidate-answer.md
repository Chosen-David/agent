# CODE-READ B：合成机制静态阅读

## 范围与证据等级

只读取本 packet 的 skill、三个必要引用、taskset.json 和 inputs 四个文件；未执行输入代码、联网、安装、启动子 agent 或读取其他 packet / oracle / 仓库文档。以下路径均相对于 `/tmp/code-reading-v2-eval/b/inputs/`。`source_fact` 表示源码表达式，`static_inference` 表示注明条件的静态推断，`unknown` 表示证据不足。没有 `executed` 的目标行为结论。

当前源码 commit、工作区差异和分支未知：授权范围不含仓库元数据，未读取 Git。`notes.json:11–12` 中 indexed_commit=`1111111111111111111111111111111111111111`、requested_commit=`2222222222222222222222222222222222222222` 只是提供材料的声明，不能把后者冒充已核实 checkout SHA。所有行号引用对应本次实际读取的文件。

## 1. dispatch

- **source_fact / static_inference**：在注册表未被外部修改的条件下，`run(index, 'fast', ...)` 从 `REGISTRY` 取得 `Index.one`（`engine.py` 模块级注册表:52；`run`:55–59），调用形式是 `selector(index, q, cache)`。随后 `Index.one`:29–32 可能更新 gate 并调用 `choose`；`choose`:10–11 返回带路径标签的元组。其返回值赋给 `positions`，再传入 `exact_attention`（`run`:59–60）。没有通向 `flash` 的已解析边。`run` 的 `mode` 是必填参数，并无 `mode='fast'` 的签名默认值。
- 未知 mode：注册表查找得到 `None` 时，采用 `extension`（`run`:56–59）。若保持默认 `extension=None`，调用不可调用对象会失败，最终 attention 不可达。若传入可调用 extension，则必须能接收 `(index,q,cache)`；其具体行为、返回值及是否间接调用 `flash` 均 unknown。直接把现有 `flash` 作为 extension 也不匹配：`flash(q,cache)` 仅接收两个参数（`engine.py:14–15`），而 selector 调用传三个。
- `notes.json:3` 的叙述及 `notes.json:16` 的 run→flash 边不能证明调用。该边标注为置信度 0.25 的同名启发式，且图索引与请求 commit 不同（:11–12）。这既不是已解析调用，也不是运行观察。未解决项包括外部注册表变更、实际 extension、调用参数、目标版本和真实运行轨迹；未提供对应证据。

## 2. state

| 路径 | 生产 / 重置 | 消费与条件 | 证据 |
| --- | --- | --- | --- |
| 初始化 | `skip_far=False`，`stat=None` | 保存传入 profile | `engine.py`, `Index.__init__:19–22` |
| prefill(score) | dynamic 真时重置 `skip_far=False`；无论 dynamic 与否都设置 `stat=score` | 不做阈值比较，也不调用 choose | `Index.prefill:24–27` |
| one(q,cache) | 仅 dynamic 真且 stat 非 None 时写入 `stat < threshold` | choose 消费更新后或原有的 skip_far | `Index.one:29–32` |
| many(q,cache) | 无生产、无重置、无比较 | choose 直接消费现存 skip_far | `Index.many:34–35` |
| choose | 不修改 Index 状态 | truthy gate 返回 near_only，否则 near_and_far，均同时带 q/cache | `choose:10–11` |

**static_inference**：同一实例且 dynamic 一直为真时，`prefill → many` 会用重置后的 False，即 near_and_far；不会根据新 stat 重算 gate。即使之前 one 把 gate 置为 True，随后这个 prefill 也会清除它。`one → many` 中若没有 intervening prefill / 状态变更，many 则继承 one 最后写入的 gate。dynamic 假时 prefill 不清 gate，one 也不刷新，因此若之前在 dynamic 真时得到了 True，再关开关，则该状态可继续被消费。stat 为 None 时 one 同样沿用旧 gate。

阈值比较是严格 `<`，默认阈值 0.05（`config.py`, `Profile.__init__:10`）；等于阈值不会置 True。上述比较假定 stat 的类型支持比较及后续布尔使用；其类型、来源、更新时机与多元素 tensor 比较语义未提供。`prefill` 保存调用者提供的 score，并未调用 `Index.score`。因此不能声称每次 decode 都重算 gate，也不能声称 near_only 已实际跳过某 kernel：这里仅返回标签元组。

## 3. tensor

以下 shape 是声明的接口及在通常算子语义下的条件推导，不是运行 tensor 观察。`ops` 在 engine 中未定义、未导入，接口自身还注明不可用（`engine.py`, `Index.representation:38–43`）。

1. 输入接口为 q `[B,H,D]`、k `[T,Hkv,D]`，且 `H=Hkv*G`（`representation:38`）。basis 缺省时，`Profile.tail_dims(D)` 返回 `[D//2-2,D//2-1,D-2,D-1]`（`config.py:12–15`）；`representation:40–42` 以最后轴索引双方。对支持这种索引且维度有效的 tensor，输出约为 q′ `[B,H,4]`、k′ `[T,Hkv,4]`，保持 head 轴。D=8 时选择 `[2,3,6,7]`。这不是任意小 D 都有四个互异合法坐标的保证；代码无尺寸校验，负索引、重叠和越界取决于 D 与 tensor API。
2. 可选 basis 声明为 `[Hkv,D,r]`，传给 `ops.project_grouped(q,basis)` 和 `ops.project_keys(k,basis)`（`representation:38,43`）。按该接口意图，投影输出应为 `[B,H,r]`、`[T,Hkv,r]`，query heads 使用所属 KV head 的基；实际分组映射、轴布局、dtype、stride、矩阵方向及算子实现不可用，不能断言实际返回此 shape。
3. `experiments.py`, `calibrate:12–18` 逐 KV head 读取 `far_keys[:,h]`，对 `[T,D]` 做 `svd(...,full_matrices=False)`，取第三返回值 `vt[:rank].T`，最后 stack。若 ops 遵循常规实数 reduced SVD 且 `0<rank<=min(T,D)`，每个基为 `[D,rank]`，堆叠为 `[Hkv,D,rank]`。rank 超出可用奇异向量数时切片不会保证请求的 rank；负 rank、空输入和复数转置等情况没有处理或语义保证。代码没有减均值、没有 query 输入；这是以 far keys 为数据的未中心化 SVD 子空间构造，不是“每个 query 学得的中心化 PCA”（冲突叙述 `notes.json:6`）。calibrate 与 representation 之间也没有实际调用/传参边，调用者须提供 basis；当前运行是否校准未知。
4. `Index.score:45–49` 意图把 q′ reshape 成 `[B,Hkv,G,r]`，沿 G 轴求和得到 `[B,Hkv,r]`，再以 `'bhr,thr->bht'` 与 k′ `[T,Hkv,r]` 收缩，得到 `[B,Hkv,T]` 分数。这里 h 是 KV-head 轴，GQA 聚合是求和而非均值，不是把所有 H 混成一个 head。tail 分支在此以 r=4 理解；reshape 字符串中的尺寸如何绑定、head 排列是否满足分组前提、ops 的实际行为都 unknown。源码没有缩放、归一化、softmax 或 mask，也未说明这是某种上下界。
5. 最终调用明确是 `exact_attention(q, original_k, original_v, positions)`（`run:60`），不把 q′/k′ 传过去。`exact_attention:6` 的注释给出原始、已选 K/V `[B,Hkv,K,D]` 和输出 `[B,H,D]` 的接口意图；其函数体 :7 实际只返回 `('full_dimension_attention', q, original_k, original_v, positions)`，既不 gather 也不执行 attention。`choose:11` 返回的也不是已验证的位置索引。因此只能确定 full-D 原始参数的传递意图，不能确定实际选中 K 个 token、实际 GQA 扩展或数值输出。`notes.json:8` 所称 final 使用 projected keys 没有这条源码路径支持。

## 4. models

- `FullRotary.__init__` 默认 dim=8，设置 `rotary_dim=dim`、`layout='rotate_half'`（`config.py:18–21`）。在这些字段确实驱动标准全维 rotate_half、D 为有效偶数且 q/k 已处于对应表示的前提下，旋转配对是 `(i,i+D/2)`，tail_dims 选出最后两对；D=8 为 `(2,6)`、`(3,7)`。第二半也是旋转配对成员，**不是未旋转的半维**。
- `PartialRotary.__init__` 默认 dim=8，设置 `rotary_dim=dim//2`、`layout='interleaved'`（`config.py:24–27`）。若标准 partial RoPE 仅旋转前 rotary_dim 个坐标，则后半可为未旋转坐标；但 interleaved 配对是相邻坐标而非跨半维。D=8 时 `[2,3,6,7]` 是一个旋转区域内的相邻对及两个未旋转坐标，不能解释成与 FullRotary 相同的两个 rotate_half 跨半配对。
- `Profile.tail_dims:13–15` 明确假定 rotate_half，且没有接收或检查 model。`representation` 也不接收 model；两个模型类在所给 engine 中没有实例化或调用边。故“两个类都有未旋转后半，并共享相同 paired-tail 解释”（`notes.json:7`）不可成立。相同数值下标不等于相同旋转含义。
- 限制：这两个类仅存储元数据，没有真正的 RoPE 算子；实际旋转范围、q/k 在 RoPE 前还是后、频率排序、head_dim 与 model dim 的对应关系、TP 分片与布局转换均未知。奇数/小 D、不同 layout、局部旋转维数或位置编码流程变化都需另查，不能无条件泛化上述条件解释。

## 5. configuration

| 项 | 构造默认及覆盖 | 实验覆盖 | 所给代码消费情况 |
| --- | --- | --- | --- |
| near | `int(READ_NEAR)`，缺省字符串 `'8'` | `make_trial` 强制设 16 | 未见 engine 读取 near |
| budget | 4 | 未改，仍由 Profile 给定 | 未见消费 |
| forced | 1 | 未改，仍由 Profile 给定 | 未见消费 |
| dynamic | 仅 READ_DYNAMIC 精确等于 `'1'` 才真，缺省 `'0'` 即假 | `make_trial` 强制设 True | prefill 重置、one 条件判断 |
| threshold | 0.05 | 未改 | one 的严格 `<` 比较 |

证据：`config.py`, `Profile.__init__:5–10`；`experiments.py`, `make_trial:5–9`；`engine.py`, `Index.prefill:25–27`、`Index.one:30–32`。READ_NEAR 不能转 int 时会在 Profile 构造处失败；没有回退处理。make_trial 先构造 Profile，再覆盖，所以构造失败不会被其后 near=16 避开。

near、budget、forced 是三个独立字段，分别表示的范围、额度和强制值不能互相等同；在这个 fixture 中，没有实现证明 near 真的是强制滑窗、budget 实际配额或 forced 实际强制入选数。因此 `notes.json:5` 的混同尤其没有消费者证据。`choose` 仅依据 skip_far 给标签，没有读取这些数值（`engine.py:10–11`）。

`notes.json:4` 的默认 dynamic 真与 runtime 缺省假冲突；“每个 decode 刷新”也与 many 不刷新冲突。实验工具的 True/16 与 `notes.json:18` 的旧摘要 dynamic=true、near=16 相容，但不能据相同值证明调用了 make_trial；它们也可来自环境/外部修改。实验文件 :1 声明不由 runtime 调用，engine 中也未见导入或调用。

旧摘要记录 mode=fast、passed=true、commit=111…；缺少命令、环境、输入、原始输出和 passed 的验收含义，且不绑定请求的 222… 版本。保留它作为旧报告，不能据此声称本次执行成功或当前 dynamic=true/near=16。当前实际 profile、环境、mode、extension、输入、basis、运行版本及输出均 unknown；本任务未运行目标。

## 6. coverage

| 已读取入口 / 边 | 最终消费者覆盖 | 状态 |
| --- | --- | --- |
| run → REGISTRY['fast'] → Index.one → choose → positions → exact_attention | 读取完整函数体；gate 可更新，返回元组沿 run 传递 | syntactic_call + resolved_target（注册表未修改条件）；未观察运行 |
| run → REGISTRY['batched'] → Index.many → choose → positions → exact_attention | 同样闭合至元组输出；gate 不刷新 | syntactic_call + resolved_target（同上） |
| run → 未知 mode → extension | 调用点明确，目标和返回行为未知；None / 不匹配签名可失败 | unresolved_target；最终消费者仅在调用成功后可达 |
| Index.prefill → stat / skip_far → one / many → choose | 已读写入、条件重置、条件更新和两个读取消费者 | inspected；prefill 外部调用者和 score 来源未提供 |
| representation 无 basis → tail_dims → q/k 选维 | 函数返回已读；没有内部调用者或连接 score 的调用边 | 接口 inspected，实际输入/API unknown |
| calibrate → SVD/stack → basis；representation 有 basis → project ops | 已读产生及预期消费接口，二者连接依赖外部调用者 | ops unresolved，调用链未闭合 |
| score → reshape → sum → einsum → 返回 score | 读到返回表达式；无 score→prefill 或 score→choose 的源码边 | ops unresolved，后续消费者未提供 |
| run → exact_attention(q,original_k,original_v,positions) | 已读最终返回元组 | 不等于实现真实 gather/attention |
| FullRotary / PartialRotary、make_trial、flash | 已读定义，但在提供源码中未见调用表达式 | 限定范围的未见引用；不能断言系统无调用 |

空图查询不是无调用或无依赖证明。`notes.json:14–15` 查询的是 Index.one callers 且返回空；然而 `engine.py:52,56,59` 已能通过函数对象注册解析出 fast 条件下的调用边。快照索引版本不匹配（`notes.json:11–12`），PDG 层 absent（:13）；空 caller 结果更不能推出无控制/数据依赖。源码已有 `dynamic/stat` 控制 gate 更新、gate→choose、selector 返回→positions→exact_attention 的控制/数据流。

要支持严格限定范围的否定命题，至少需要：确认目标源码与 indexed commit 相同；确认完整索引范围、查询过滤/截断、分析层和工具版本；验证对注册表、函数对象、extension、反射/外部入口的处理能力，并补充全授权范围的定义/引用与读写搜索。依赖否定还需真实存在且足够覆盖的控制/数据依赖分析，涵盖状态别名及跨函数流。有限运行 trace 最多证明该次输入未观察到调用，不能证明所有路径不存在调用。此任务范围不允许扩大搜索或重建索引，因此这些均为剩余缺口。

## 实际动作、验收与限制

读/搜索 tool call 共尝试 4 次，其中前三次成功，第 4 次未启动进程（每次一个 exec_command；将第 2 次中的读取及文件枚举合并计为一次 tool call）：

1. `cat`：`b/skill/SKILL.md` 与 `b/taskset.json`。
2. `cat`：skill 的 `references/workflow.md`、`references/execution.md`、`references/coverage.md`；`rg --files b/inputs` 枚举输入。
3. `nl -ba`：`engine.py`、`config.py`、`experiments.py`、`notes.json`，读取全体输入并取得行号。
4. 尝试 `rg -n`：计划仅在上述四个输入文件中复核分发、gate、ops、最终消费者、配置、模型字段和图版本等关键词。工具返回 `Failed to create unified exec process: exec-server transport disconnected`，未成功执行，也没有产生新的搜索证据。三次 wait 仅等待该调用结果，不是额外读取。本文依据第 3 次成功的完整带行号读取完成自查；未声称完成独立二次源码复读。

只将此交付写到 `b/answer.md`。未运行辅助 source_evidence 脚本或任何输入代码；没有 GPU/e2e/性能测试。6 个任务均给出静态结论或明确未知项。源码机制没有被执行验证，此交付仅是 synthetic 阅读结果，不是现实系统实测，也不自评得分。未另读 AGENTS.md、仓库元数据或外部文档，因为任务把读取权限限定为本 packet skill 必要引用、taskset 与 inputs。技能对版本固定的建议在该授权边界内无法完成，已显式标为未知。
