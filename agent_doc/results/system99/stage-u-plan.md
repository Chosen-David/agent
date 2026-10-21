# SYSTEM-99 阶段 U 方案：可信输出阶梯与可复用文档工具链

Status: U1-plan-and-candidate-accepted; U2-planned-not-implemented
Baseline: `26d6b20791a40d39e01b928502e6bfc50a55e009`

## 新指令与取舍

用户要求把“受控文字→图表→交互网页→讲解视频”的输出阶梯用于升级 Agent，设计相应 harness，
并让仓库具备一次安装、后续复用的 PDF 阅读与 Markdown、PPT、LaTeX 文档能力。

- **adopt**：先冻结受众、核心主张和验收要求，再选择真正降低理解成本的最低输出层；
  `controlled_text` 永远保留为可独立理解的基线。
- **adapt**：ASD-STE100 只作受控语言设计启发。未实际运行适用词典、规则检查器和人工复核，
  不宣称 STE100 合规；中文和科研术语不被英语词典机械替换。
- **adapt**：Manim、HTML/GSAP、TTS、FFmpeg 和商业语音服务只是可选生成适配器。
  harness 不执行它们，不以动画、音色或页面美观替代事实、数学和代码正确性。
- **adopt**：文档能力采用固定依赖 profile、显式一次安装、真实 capability smoke 和可复核 receipt；
  普通 setup、回答或输出验证不得隐式联网、安装或修改全局 Python。
- **reject**：不 vendor TeX/Pandoc/FFmpeg/浏览器/商业 TTS，不提交二进制缓存或凭据；
  缺能力时诚实降级并保留恢复路径，不能把 `which`/import 成功冒充实际可用。

## 既有结果查询

在当前结果库执行了两个有界查询，不把结果称为穷尽检索：

1. `explanation output ladder controlled language diagram web video harness`：扫描 253，
   `partial=true`，10 个候选，13 个错误。
2. `visual explanation figure rendering semantic harness`：扫描 253，
   `partial=false`，10 个候选，13 个错误。

候选仅提供旧 token/figure/handoff 的接口参考；没有可直接复用的四层可信请求合同或文档能力凭据。
既有 `visual_explanation_workflow.md`、`validate_handoff.py` 和 synthetic figure suite 会被扩展和链接，
不另造竞争解释路线、TASK 或共享聊天池。

## U1：输出阶梯合同与 harness

### 信任链和状态

唯一链路为：

`explain/assistant → trusted request → producer artifacts → structural validator → independent observer → delivery`

普通文字问答不强制创建 manifest；只有受管的多媒体交付使用本合同。可信消费者独立生成
`output-ladder-request/v1`，固定 request ID、受众、语言、冻结主张、请求层级、是否允许降级、
是否要求连续层级、逐层 required checks，以及可选的文档 capability receipt 哈希。producer 不能
改变或补写这些字段；manifest 必须绑定 request 原字节 SHA-256。

结构验证只返回 `invalid`、`pending`、`ready-for-independent-review`。最后一项仅表示请求、产物、
声明和证据在本地结构上齐备，绝不等于已被接受；producer 自报 reviewer 名称、角色不等或 pass
均不能形成独立认证。实际 delivery 仍需可信宿主保存的独立观察回执，且不由本 harness 签发。

### 合法层级组合

`controlled_text` 必须存在；中间层默认可跳过。因此合法组合包括 text、text+diagram、text+web、
text+video，也可包含多个高层。只有 request 的 `require_contiguous=true` 才要求从 text 到目标层连续。
若请求禁止降级而目标未交付，结果 invalid；允许降级但目标缺失时结果 pending，并保留 requested、
delivered、capability gap、limitations 和 recovery。不能用 producer 字段授权跳过 request 的 required checks。

各层最小角色：

- text：`primary_text`；
- diagram：`editable_source`、`rendered_preview`、`caption`、`alt_text`；
- web：`web_entry`、`static_fallback`、`interaction_spec`、`accessibility_report`；
- video：`video`、`storyboard`、`transcript`、`captions`、`audio_provenance`。

每个已声明层必须精确引用 request 中的同一冻结 claim ID 集，并提供 request 要求的检查证据。
程序只证明 ID 和字节绑定，不能证明表达等价、正确、好看、可理解、可交互、可播放或许可合规。
未引用产物默认拒绝，避免把无关文件塞进 manifest。

### 闭合 schema 与确定状态表

`output-ladder-manifest/v1` 仅允许：`schema_version`、`request_id`、`request_sha256`、
`producer`、`delivered_levels`、`claims_by_level`、`artifacts`、`checks`、`limitations`、
`recovery`。其中：

- artifact 仅允许 `id`、`level`、`role`、`path`、`declared_sha256`；一个 artifact ID 只能出现一次，
  一个路径只能绑定一个 artifact，不能用同一文件填多个角色。
- check 仅允许 `check_id`、`level`、`request_check_id`、`status`、`evidence_artifact_ids`、
  可选 `producer_observer`；status 只能是 `pass|fail|not_run`。观察者只是来源声明，不参与信任升级。
- `claims_by_level` 的 key 必须精确等于 delivered levels，每个值必须精确等于 request claim ID 集；
  不能多报“容易满足”的新 claim，也不能漏报困难 claim。
- capability receipt 不在 producer manifest。trusted request 可选持有 `capability_receipt_sha256`；
  U1 只验证该固定字符串被原样绑定，不读取或信任 receipt 内容。

状态 oracle 固定为：

| 状态 | 条件 |
|---|---|
| `invalid` | schema/类型/上限、request 绑定、claim exact-set、角色、路径安全、普通文件、hash 或禁止降级合同违规；required check 条目缺失也属合同违规。 |
| `pending` | 合同合法且允许暂缺/降级，但未达到目标、已有 required check 为 `fail/not_run`、能力缺失，或必要证据 artifact 尚未交付。 |
| `ready-for-independent-review` | 达到 request target，所有 required checks 均 `pass` 且证据 artifact 字节绑定齐备；仍未获得独立接受。 |

禁止降级而目标层缺失是 invalid；允许降级且目标层缺失是 pending。声明了目标层却缺其必需角色是
invalid；尚未声明允许暂缺的目标层是 pending。这样 CLI 退出码有唯一 oracle。

### 严格格式和文件边界

request/manifest 使用闭合字段集合并经 `agent_runtime.external_json` 严格、有界读取：未知/重复字段、
非有限数、错类型、额外 claim、重复 ID 一律拒绝。初始上限固定为：JSON 1 MiB、路径 1024 字符、
一般字符串 4096 字符、ID 128 字符、claims 256、artifacts 128、每层 checks 32、单产物 256 MiB。
返回值包含 request/manifest 实际哈希及每个产物实际 SHA-256，不只回显 producer 声明。

产物路径必须是规范化相对词法路径，拒绝绝对路径、`..`、NUL、父目录和终点 symlink。
读取使用 `O_NONBLOCK|O_NOFOLLOW`，同一 FD `fstat` 普通文件和大小，流式 hash；读取前后
inode/device/size/mtime_ns/ctime_ns 必须稳定。读完后重新以同样安全规则打开当前路径并核对
`(device,inode)`，打开后路径替换必须 invalid；该复查仍不保证恶意父目录竞态或路径 ABA。
消费方在使用前仍须重新验证返回的实际摘要。本边界不声称跨文件事务或提供 OS 沙箱。

CLI 采用稳定退出码：0=`ready-for-independent-review`，2=`pending`，3=`invalid`，1=内部错误；
普通和 `python -O` 行为一致。

### 接入

新增一个 output-ladder workflow，并作为既有 visual explanation workflow 的跨媒体扩展；
六个消费者 `explain-research-concepts`、`research-figures`、`research-diagrams`、
`research-data-visualization`、`paper-reading-companion`、`research-assistant` 保持同一合同镜像，
通过现有 sync-generated 机制同步。若同步闭包要求，把新源加入既有 `RAW_COPY_SOURCES`，不手改生成件。
测试从每个包的 `SKILL.md` 实际遍历到新合同，而不只查文件名或关键字。

## U2：一次安装、可复用的 documents profile

U2 与 U1 独立评审和验收，避免文档安装失败污染输出合同。

1. `documents-linux-cp312-v1` 首版只支持 CPython 3.12、Linux x86_64；其它平台返回 unsupported，
   后续须增加独立 lock。下表只是 U2 实现前的候选版本与摘要检查点；实施时必须重新下载并核对
   完整 wheel 文件名、tag、来源、许可证元数据和 SHA-256，未复核前不得作为安装授权：

   | 包 | 版本 | SHA-256 | 许可证元数据 |
   |---|---:|---|---|
   | PyMuPDF | 1.26.6 | `7777d0b7124c2ebc94849536b6a1fb85d158df3b9d873935e63036559391534c` | AGPL-3.0 或 Artifex commercial 双许可 |
   | markdown-it-py | 4.0.0 | `87327c59b172c5011896038353a81343b6754500a08cd7a4973bb48c6d578147` | MIT |
   | python-pptx | 1.0.2 | `160838e0b8565a8b1f67947675886e9fea18aa5e795db7ae531606d68e785cba` | MIT |
   | Jinja2 | 3.1.6 | `85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67` | BSD |
   | mdurl | 0.1.2 | `84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8` | MIT |
   | lxml | 6.1.3 | `909f4e927bb051f7740d6367285fc60cdcfdaf0258c2dba4ff5ba7eadadc250c` | BSD-3-Clause |
   | MarkupSafe | 3.0.4 | `8e124f974786f831d6043728e38296969d3579db8896fe004682f5758e613581` | BSD-3-Clause |
   | Pillow | 13.0.0 | `42d63be3af4f9b951b199b0a9d23365d37ab14687e6d77b74940432c8515c4ca` | MIT-CMU |
   | typing-extensions | 4.16.0 | `481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8` | PSF-2.0 |
   | XlsxWriter | 3.2.9 | `9a5db42bc5dff014806c58a20b9eae7322a134abb6fce3c92c181bfb275ec5b3` | BSD-2-Clause |

   PyMuPDF 是为了复用现有 paper-reader 的真实打开/文本/渲染路径而采用；安装命令必须先显示其
   AGPL/commercial 选择边界并要求显式 `--pymupdf-license agpl-3.0|commercial`，本仓不替用户作
   商业合规判断。
   Markdown 用 markdown-it-py，PPTX 用 python-pptx，LaTeX 源用 Jinja2 严格模板。
2. 提供显式 one-time install 命令，只允许创建或复用带本工具 marker 的受管根。venv 直接在最终
   规范路径创建，并以 `.incomplete` 隔离；不得先在 staging 创建再移动（venv 脚本 shebang 会绑定
   旧绝对路径）。按 profile/lock hash 用 `pip --require-hashes --only-binary=:all:` 安装，全部 smoke
   成功后才原子发布 receipt 与 `current` 指针。失败清理前必须核对 marker、真实目录且无 symlink，
   不原地修改旧环境。禁止普通 `setup.py`、harness、回答路径调用，禁止静默写全局/用户 site-packages。
3. 首版平台明确为 CPython 3.12、Linux x86_64、glibc≥2.28；锁文件逐项记录完整 wheel 文件名、
   compatibility tag、来源 URL、SHA-256 和许可证元数据，安装前用当前解释器的兼容 tag 核验。
   PyMuPDF 许可参数不是模糊接受，而是显式 `--pymupdf-license agpl-3.0|commercial`；选择写入 receipt，
   本仓不替用户判断商业合规。receipt 绑定 profile/lock SHA-256、Python 版本、OS、架构、glibc、
   venv 规范路径、许可选择和实际包版本。
   相同 lock 的重复 install 在验证 receipt/smoke 后直接复用，禁止再次调用 pip/网络；离线第二次
   install 与 probe 均须通过。
4. v1 的承诺是生成确定的 `.tex` 源，不是自带 TeX 发行版；用 Jinja2 strict undefined 生成含转义输入的
   最小源码并做固定结构检查。若宿主已有受支持 engine，可额外编译 smoke；固定 argv、`shell=False`、
   有界超时、隔离临时目录并禁用会自动拉包的 engine 网络。缺 engine 只使 `latex_compile` unavailable，
   不影响 `latex_source` ready。仓库不下载或 vendor 数 GB TeX；若未来要求自带编译器，须另提带 checksum/
   license/cache-only 的 opt-in 方案。
5. 提供稳定的 documents adapter/CLI，而不只证明包已安装：`probe`、`pdf-read`、`markdown-render`、
   `pptx-create`、`latex-source`；smoke 必须调用同一公开入口。各命令固定输入/输出 schema、字节/页数/
   渲染像素/超时上限和失败状态。PDF 解析器不是OS沙箱；不接受不受信内容的无界处理。LaTeX 使用
   专用转义器而非HTML autoescape；可选编译只接受显式可信 engine，禁 shell escape/自动下载并限时。
   PyMuPDF smoke 创建/打开/提取/渲染 PDF，Markdown 实际转换，PPTX 创建后重开；import/`which`
   不计通过。失败不发布 receipt/current，也不损坏旧环境。
6. U1 只能绑定可信消费者指定的 capability receipt 哈希；harness 不安装、不执行生成器，
   producer 也不能靠自写 receipt 提升信任状态。

## 固定验收

- trusted request 任何字节变化都使旧 manifest 失效；producer 自报 reviewer 永不变成 accepted。
- 覆盖 text 与三种可跳层组合、显式连续组合、允许/禁止降级、目标虚报、主张增删/遗漏、
  required check 缺失、未知字段、重复 ID、精确上限与上限+1、稳定退出码。
- 文件夹、父/终点 symlink、FIFO、socket/设备（平台允许时）、缺失、绝对/`..`、增长、截断、
  打开后路径替换必须拒绝；恶意父目录竞态和路径 ABA 明确不保证。
- U1 的 FD-relative `O_NOFOLLOW` 边界首版只支持具备该 POSIX 能力的宿主；缺能力的平台明确返回
  unsupported/invalid，不把它表述为 producer 内容错误，也不宣称 Windows 已覆盖。
- 六角色 Skill 镜像、链接和 package closure 均通过现有同步测试。
- documents 安装/真实 smoke/receipt、相同环境幂等和离线第二次 probe；失败不得破坏旧环境。
- 保存修前失败或明确的新增能力基线；实现后做定向、`-O`、全库、Reader、同步和独立结果复核。

不修改 `agent_doc/guide/`，不新增付费依赖或凭据，不声称真实读者理解率、模型质量、token、费用、
媒体生成质量或生产部署提升。阶段 U 仍只是 SYSTEM-99 检查点，不是整轮完成。

## 独立方案审查返修

首次独立审查结论为 `REVISE`。除上述 U2 修订外，U1 必须使用 FD-relative、逐路径组件
`O_NOFOLLOW` 打开 artifact root 与内部父目录，覆盖 root 祖先 symlink；check ID 全局唯一，检查证据
只能引用同层 artifact。output manifest 是单次交付合同，不替代 `artifact_index/v1` 的运行/项目树
统一清单。返修代码与反例完成后重新独立审查，不能把首次退回写成通过。

二次独立复核确认 U1 的祖先 symlink、check ID 和同层证据阻断均已关闭；再次统一许可参数并明确
POSIX-only 安全打开边界后，最终结论为 `ACCEPT (scope-limited)`。该接受仅覆盖 U1 合同和 U2
可实施方案，不把 U2 计划升级为已安装能力。
