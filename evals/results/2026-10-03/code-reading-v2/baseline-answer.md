# CODE-READ A：合成机制静态阅读

## 范围与证据等级

仅阅读本 packet 的 `skill/SKILL.md`、其两个必要 references、`taskset.json` 及 `inputs` 的四个文件。下文路径均相对 `/tmp/code-reading-v2-eval/a/inputs/`。`source_fact` 指源码直接事实，`static_inference` 指带前提的静态推断，`unknown` 指材料无法闭合；没有目标代码的 `executed` 结论。

当前输入文件的实际 commit、分支和工作区差异未知：授权范围不包含 Git 元数据或其它仓库文档，未读取它们。`notes.json:11–12` 仅声明索引 commit 为 `1111111111111111111111111111111111111111`、请求 commit 为 `2222222222222222222222222222222222222222`，不能据此把当前输入绑定到任一 commit。所有定位都是本次读取的文件行号；这是一组合成任务，不是真实系统实测。

## 1. dispatch

- **source_fact**：`engine.py:52` 的模块级 `REGISTRY` 将 `fast` 映射到 `Index.one`，`batched` 映射到 `Index.many`。`run` (`engine.py:55–60`) 先查表，只有查到 `None` 才采用 `extension`，随后在第 59 行以 `(index, q, cache)` 调用 selector。这里的 `run` 没有 `mode='fast'` 默认参数；题目所说的是显式传入该值。
- **static_inference**：假设注册表未被外部改写、index 是相容实例，`run(..., mode='fast', ...) → Index.one → choose → exact_attention`。`one` 的状态条件见下一题。已注册 fast 不消费提供的 extension。选择结果在第 59 行赋给 `positions`，第 60 行交给 `exact_attention`。
- 未知 mode 时，`extension` 必须能接受三个实参，并成功返回结果；其实现及输出契约 **unknown**。默认 `extension=None` 时，第 59 行调用 `None` 将失败，不能到达最终 attention。显式直接传 `flash` 也不构成有效适配：`flash(q, cache)` 仅接受两个参数 (`engine.py:14–15`)，而分发传三个，按此定义会发生参数数量错误。自定义 wrapper 是否调用 flash 未知。
- `notes.json:3` 的叙述与可见 fast 注册相冲突。`notes.json:16` 的 run→flash 是置信度 0.25 的同名启发式边，且索引与请求版本不一致 (`:11–12`)；它不能证明真实调用。可见 `run` 函数体无 flash 调用，flash 仅返回合成 tuple；外部注册表突变、extension wrapper、真实后端及当前运行 mode 均未验证。

## 2. state

| 入口 / 条件 | 状态生产或重置 | 消费证据 |
|---|---|---|
| `Index.__init__` | `skip_far=False`，`stat=None` | `engine.py:19–22` |
| `prefill(score)` 且 dynamic 真 | 先将 `skip_far=False`，再无条件保存 `stat=score` | `engine.py:24–27` |
| `prefill(score)` 且 dynamic 假 | 保留旧 `skip_far`，仍保存 `stat` | 同上 |
| `one(q,cache)` 且 dynamic 真且 stat 非 None | 重算 `skip_far = stat < threshold` | `engine.py:29–32` |
| `one` 其它条件 | 保留已有门状态 | 同上 |
| `many(q,cache)` | 不读取 stat、不重算、不重置门 | `engine.py:34–35` |

`one` 和 `many` 都把现有门交给 `choose`。`choose` (`engine.py:10–11`) 根据门返回 `'near_only'` 或 `'near_and_far'` 标签与 q/cache 的 tuple；这里没有真正执行远池过滤、候选选择或计算量跳过的实现。

**static_inference**（stat 与 threshold 可比较且所得值可用于条件判断）：dynamic 开启时，`prefill → many` 将消费重置后的 False，得到 near_and_far 标签；它不会根据新 stat 重算。若之前 `one` 已把门设为 True，则随后的 `many` 会复用 True，直到其它入口改变状态。若其间发生 dynamic 为真的 prefill，旧 True 会被清除，many 改用 False。若 prefill 时 dynamic 为假，旧门仍可保留；同样 one 在 dynamic 假或 stat 为 None 时也不会清除旧 True。全新实例在未发生更新时保持 False。多次 many 不刷新任何状态。比较是严格 `<`，等于 threshold 不跳过；stat 的具体类型、非标量比较语义和错误处理未验证。

因此 `notes.json:4` 的“每条 decode 都刷新”不成立，默认启用也不成立（见配置题）。这里未展示从 `Index.score` 到 `prefill(score)` 的调用，不能声称 stat 一定来自该打分函数。

## 3. tensor

**source_fact**：`Index.representation` (`engine.py:37–43`) 声明输入接口 q `[B,H,D]`、k `[T,Hkv,D]`、`H=Hkv*G`、basis `[Hkv,D,r]`；注释明确说明 ops API 不可用。没有 dtype、设备或数值精度契约。

1. 无 basis：以 q 的末维 D 调用 `Profile.tail_dims`，同时切 q/k 的最后一维 (`engine.py:40–42`; `config.py:12–15`)。在 D 为足够大的偶数、q/k 末维匹配、数组支持这种高级索引的前提下，四个索引为 `[D/2-2,D/2-1,D-2,D-1]`，预期 q′ `[B,H,4]`、k′ `[T,Hkv,4]`。这只是接口形状推断；类型和索引算子未提供，不能报告实测张量。
2. 有 basis：第 43 行调用 `ops.project_grouped(q,basis)` 与 `ops.project_keys(k,basis)`。按名称、basis 注释及下游契约，预期每个 KV head 的基用于其 G 个 query heads，得到 q′ `[B,H,r]`、k′ `[T,Hkv,r]`；具体分组映射、乘法方向、输出布局及算子校验 **unknown**，不能仅靠名称证明实现。
3. `Index.score` (`engine.py:45–49`) 要求将 q′ 保留 KV-head 维度地重排为 `[B,Hkv,G,r]`，沿 axis=2 求和得 `[B,Hkv,r]`，再用 `bhr,thr->bht` 与 `[T,Hkv,r]` 的 k′ 得 `[B,Hkv,T]`。无 basis 路径中 r 在这段接口表示选取宽度 4。若 ops 遵循普通 reshape/sum/einsum 语义，分数为 `sum_g sum_j q′[b,h,g,j]*k′[t,h,j]`，不是跨 Hkv 求和，也不是对 G 求均值。这里没写缩放、softmax 或归一化。该条件表达式不是运行结果；ops 没有在 engine 中定义/导入，正常直接执行相关分支会遇到未定义符号，除非外部注入。
4. 可选校准 `experiments.py::calibrate:12–18` 对每个 head 的 `far_keys[:,h]`（预期 `[T,D]`）进行 reduced SVD，取 `vt[:rank].T`，最后 stack。若 ops 为常规 SVD 且 `0<rank<=min(T,D)`，各基预期 `[D,rank]`，stack 后 `[Hkv,D,rank]`。rank 超限时常规切片会得到较小有效宽度；空输入、非正 rank、stack 轴及退化情况没有显式验证。没有中心化、没有 query 输入、没有按 query 拟合，所以 `notes.json:6` 的“中心化 PCA、每个 query 学习”不受支持。这是从远端 key 数据提取的可选 SVD 子空间接口；没有可见代码把 calibrate 输出自动送入 representation。
5. 最终 `run` 在 `engine.py:60` 调用 `exact_attention(q, original_k, original_v, positions)`，使用收到的原 q 和原始 k/v，并非 q′/k′。`exact_attention:5–7` 注释意图是 q `[B,H,D]`、选中原始 k/v `[B,Hkv,K,D]` 到输出 `[B,H,D]`；函数实际仅返回五元素标签 tuple。run 内没有 gather，choose 也没有返回数值索引，而是标签 tuple。因此是否已选中 K、positions 的真实格式、最终 GQA 广播、mask、缩放、softmax 和数值输出全未知，不能把注释的张量结果当作已实现。`notes.json:8` 的“最终用投影 keys”与可见传参冲突。

## 4. models

`Profile.tail_dims` (`config.py:12–15`) 只使用 dim，注释假设 rotate_half 布局，不检查任何 model。D=8 时返回 `[2,3,6,7]`。

- `FullRotary.__init__` (`config.py:18–21`) 声明 `rotary_dim=dim`、layout 为 rotate_half。**static_inference**：如果实际旋转遵守常规 rotate_half、D 是适当偶数且全部 D 坐标被旋转，前后半区按偏移 D/2 配对，所选两半尾部构成配对尾维。例如 D=8 的配对是 (2,6)、(3,7)。第二半是旋转配对的另一半，不能称为“不旋转的后半”。
- `PartialRotary.__init__` (`config.py:24–27`) 声明 `rotary_dim=dim//2`、layout 为 interleaved。若实际实现按通常约定旋转前 rotary_dim 个坐标，其余坐标不旋转，则 D=8 后半 `[4,5,6,7]` 不旋转；但旋转区是相邻配对，所选 `[2,3]` 是旋转区的一对，`[6,7]` 是未旋转区，不能解释为和 FullRotary 相同的跨半区配对尾部。代码没有实现旋转或给出旋转坐标位置，故“不旋转的后半”在这里仍须上述实际实现前提，不能从字段断言全部布局语义。

两个 model 实例都没有被 Profile 或 Index 接收并用于校验，故“返回同样索引”不等于“对两种布局都有同样机制”。basis 非 None 时完全绕过 tail_dims (`engine.py:40–43`)。奇数 D、D 小于 4、真实布局/rotary_dim 不同以及 q/k 维度不匹配也不在配对结论的保证范围；小 D 可产生负索引或重叠，源码没有防护。`notes.json:7` 把两个不同条件合并为通用叙述，不成立。

## 5. configuration

| 字段 | 构造默认及覆盖 | 可见消费 / 当前执行值 |
|---|---|---|
| near | `Profile.__init__`，`config.py:6`：环境 READ_NEAR 经 int，未设为 8；`make_trial` 在 `experiments.py:8` 覆盖为 16 | 输入中无 near 的选择消费；当前环境和运行值 unknown |
| budget | `config.py:7`：4；make_trial 未覆盖 | 无可见消费；不能推断配额如何实现 |
| forced | `config.py:8`：1；make_trial 未覆盖 | 无可见消费；不能推断保留哪些位置 |
| dynamic | `config.py:9`：仅 READ_DYNAMIC 恰为字符串 `'1'` 时真，默认假；`make_trial:7` 强制 True | `Index.prefill:25`、`Index.one:30` 消费；many 不消费开关而读取旧门；当前值 unknown |
| threshold | `config.py:10`：0.05；make_trial 未覆盖 | `Index.one:31` 作严格小于比较；当前实例有无外部修改 unknown |

**source_fact**：`make_trial:5–9` 先构造 Profile，再写 dynamic/near，返回该对象；runtime engine 中没有调用 make_trial。覆盖发生在构造之后，故 READ_NEAR 若不能转 int，会先在构造阶段失败，不能认为实验赋值消除了该错误。

near、budget、forced 是三个独立字段，不能把 near 范围等同于预算份额或强制保留数；实际范围、预算执行及强制集合的机制均未展示。`notes.json:5` 的叙述既混淆字段，也缺失消费实现证据。`notes.json:4` 的默认 dynamic=true 与构造默认冲突，只有环境/实验/其它显式修改才能改变默认。

`notes.json:18` 旧汇总记载 fast、dynamic=true、near=16、passed=true，版本为 `111…111`。这些值与 make_trial 的赋值相容，但不能证明旧运行使用了 make_trial，也不能把 passed 当成已验证测试。该汇总没有完整命令、环境、输入、输出或 current commit 绑定；它与 requested `222…222` 不同。因此只能报告“旧摘要如此声明”，不能据此推断当前执行开启 dynamic、near=16 或通过。当前是否有执行本身也未知。

## 6. coverage

可见调用和数据边的覆盖如下（“闭合”仅指此合成源码中的直接调用）：

| 边 | 调用点 / 条件 | 覆盖状态 |
|---|---|---|
| 外部调用者 → Profile / Index / prefill / run | 输入未提供调用入口 | unresolved：实例、配置注入与时序未知 |
| run → Index.one | `engine.py:52,56–59`，mode=fast 且注册表未变 | 静态可解析 |
| run → Index.many | 同上，mode=batched 且注册表未变 | 静态可解析 |
| run → extension | `engine.py:57–59`，未注册 mode | unresolved：外部 callable；None 或签名不兼容会失败 |
| prefill → stat，one → skip_far | `engine.py:24–31`，条件见状态题 | 状态写入可见；score 的来源未知 |
| one / many → choose | `engine.py:32,35` | 直接调用；门控制返回标签 |
| choose 返回值 → run.positions → exact_attention | `engine.py:10–11,59–60` | 数据边闭合到 tuple 消费者，不等于真实索引/attention |
| representation → tail_dims 或 ops 投影 | `engine.py:40–43` | tail_dims 闭合；ops 实现 unresolved；representation 的调用者未见 |
| score → reshape → sum → einsum | `engine.py:47–49` | 表达式可见，ops unresolved；representation→score 无直接调用证据 |
| calibrate → svd / stack → 返回 basis | `experiments.py:12–18` | 接口可见，ops 与 basis 消费者 unresolved |
| run → exact_attention → 最终返回 | `engine.py:60,5–7` | 闭合到合成 tuple；没有真实后端运行 |

还缺少 cache 构建、选择算法、索引逻辑/物理域、去重/排序、候选 gather、原始 KV 与位置对应、mask/padding、真实 attention 和算子实现。未提供测试源或可验证运行记录。不能补画 `score→prefill`、`calibrate→representation→score→choose` 等未展示的调用边。

空图查询不证明没有 callers，更不能证明没有控制/数据依赖：`notes.json:14–15` 只是一次 Index.one caller 查询的空结果，版本错配 (`:11–12`)，PDG 层明确 absent (`:13`)；而本地注册表加 selector 调用已给出条件可达路径。控制依赖可以直接见 run 的 fallback 分支、one 的动态条件、choose 的条件标签；数据依赖包括 stat→skip_far→choose→positions→exact_attention。图没有索引到不等于源码没有。

要支持某个有限范围内的否定结论，最少应取得与目标一致的源码 commit/工作区快照，证明索引覆盖全部相关文件与语言且构建成功，核实查询符号和范围、注册表/间接调用/插件/生成代码/FFI 的解析策略及漏报边界；若否定控制或数据依赖，还须存在并验证对应 PDG 层及分析覆盖。对外部 extension 和动态突变必须封闭环境或明确排除。特定输入的运行 trace 可补充某条路径是否发生，但有限 trace 不能证明所有可能路径不存在。以上均为建议证据，本次未收集、未执行。

## 实际动作、执行情况与限制

应用 `code-reading` skill，并在交付前自行复读关键条件；没有启动独立审阅者或子 agent，没有自评打分。

实际共 **4 次读/搜索 tool calls**（每次一个 exec_command；写答案另计，不是读/搜索）：

1. `cat` 本 packet 的 `skill/SKILL.md` 与 `taskset.json`。
2. `cat` 两个必要引用 `skill/references/workflow.md`、`skill/references/execution.md`；`rg --files` 仅列本 packet 的 inputs。
3. `nl -ba` 读取 `inputs/engine.py`、`config.py`、`experiments.py`、`notes.json` 全文，取得行号。
4. `sed -n` 复读 engine 18–60、config 4–27、experiments 5–18、notes 10–19，核对状态条件、注册、配置、校准及图版本。

上述只读命令均成功返回。仅写本 `answer.md`；未修改 inputs 或仓库，未运行或导入输入代码，未安装软件、联网、读取其他 packet/oracle/评测答案/仓库文档，也未运行可选源码证据脚本。实际执行仅限读取与答案写入，不包含目标测试、GPU、e2e、性能实验或真实系统测量。源码版本绑定、不可用 ops、外部分发与缺失实际消费实现是剩余验证边界，不以静态推断填补运行证据。
