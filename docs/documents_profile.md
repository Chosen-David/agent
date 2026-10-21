# 可复用文档工具

完整 checkout 提供显式安装的 `documents-linux-cp312-v1`：PDF 文本/页面 PNG、
Markdown → HTML、PPTX 创建/重开、LaTeX 源码生成。普通 `setup.py`、Skill 加载和输出
harness 均不安装依赖。第一次安装后，后续调用复用同一个环境，无需每次下载。

首版要求 CPython 3.12、Linux x86_64、glibc≥2.28；其它平台需要独立 wheel 锁。
配置锁住10个直接/传递依赖的版本、wheel 文件名、tag、下载 URL、SHA-256、许可和依赖声明。
安装前验证平台、tag 和依赖闭包，用 `pip --require-hashes --only-binary=:all: --no-deps`
安装到独立 venv；不改全局 Python。完整 checkout 和宿主 pip/venv 是引导前提。

## 一次安装

PyMuPDF 提供 AGPL-3.0 与 Artifex commercial 两种许可。请按实际用途选择；参数记录选择，
不替代许可义务或商业授权。说明见 [PyMuPDF licensing](https://pymupdf.io/licensing)。

```bash
python -m agent_runtime.documents --root /absolute/dedicated/documents-env \
  install --pymupdf-license agpl-3.0
python -m agent_runtime.documents --root /absolute/dedicated/documents-env probe
```

商业许可用途使用 `--pymupdf-license commercial`。这不会购买或验证许可证。
已有离线 wheel 缓存可加 `--offline --wheelhouse /absolute/wheels`；全部文件必须匹配锁内
精确文件名和 SHA-256。首次联网安装仅访问锁内包 URL，不查询浮动版本。
同一锁/适配器/解释器/许可组合的重复 install 先重验 receipt 与真实 smoke，成功即 `reused`，
不创建 venv、不调用 pip。`--offline` 的首次安装必须显式提供 wheelhouse。
本地 wheelhouse 的全部路径和哈希先预检；缺文件、链接或损坏缓存不会创建版本目录，
修正缓存后可直接重试。预检后 pip 仍以锁内哈希核验实际读取的文件。

venv 位于最终路径，不能移动，否则 shebang 和 receipt 路径失效。`current.json` 是受限 JSON
指针；新环境带 `.incomplete`，真实 smoke 全过后才发布 receipt/current。失败保留诊断目录和
旧 current；未知 incomplete 不自动删除或重试。手动恢复时先核对目录身份，使用新的专用 root
或由维护者恢复失败目录，不能把 `.incomplete` 删除当作成功。receipt 证明当次观察，不证明环境
以后不被其它进程修改；每次操作前重验版本/真实 smoke。

## 公开入口

```bash
python -m agent_runtime.documents --root /absolute/dedicated/documents-env \
  pdf-read --input paper.pdf --pages 1 2 --output-dir /absolute/new/pdf-pages
python -m agent_runtime.documents --root /absolute/dedicated/documents-env \
  markdown-render --input notes.md --output-dir /absolute/new/html
python -m agent_runtime.documents --root /absolute/dedicated/documents-env \
  pptx-create --input slides.json --output-dir /absolute/new/slides
python -m agent_runtime.documents --root /absolute/dedicated/documents-env \
  latex-source --input text.txt --output-dir /absolute/new/latex
```

`slides.json` 是1–64项数组，每项精确为 `{"title":"标题","body":"正文"}`；每页两字段合计最多
16000 UTF-8字节。输出目录必须不存在，避免覆盖原产物。公开操作先写同父目录的私有暂存目录，
全部成功后用 Linux `renameat2(RENAME_NOREPLACE)` 原子发布；非法输入、超时或适配器失败不会留下
半成品目标，同一路径可修正输入后重试。并发创建的空或非空目标均不覆盖；平台/文件系统不支持
no-replace 原子发布时明确返回 `unavailable`，不降级到会覆盖目标的 rename。PDF上限16MiB、1000页，每次选1–16页；
渲染前检查页面尺寸，每页最长边2000像素、总像素不超过400万，提取文本总量不超过1MiB。
Markdown输入最多1MiB，禁用原始HTML；HTML输出不是浏览器沙箱，交互/无障碍/视觉质量需另验。
LaTeX输入最多64KiB，逐字符转义反斜线、花括号及特殊字符后填入固定严格模板。
首版 `latex_compile=unavailable`；没有自带 TeX 发行版或隐式下载引擎。

解析在自有子进程执行，60秒墙钟、50秒CPU、1GiB地址空间；stdout/stderr通过临时文件观察，超过8MiB
拒绝并回收子进程，单文件OS上限64MiB。原生PDF解析器不构成安全沙箱，不能据此接收任意敌意文件。
JSON输出统一使用 `documents-result/v1`；成功为 `status=ok`、退出0，能力不可用为
`unavailable`、退出2，非法输入为 `invalid`、退出3。安装的 `result.status` 为
`installed/reused`，probe的 `result.status` 为 `ready`。

四种真实 smoke 与公开操作共用 `documents_adapter.execute`：PDF创建后打开/提取/渲染、Markdown
转换、PPTX创建重开、LaTeX转义和固定结构。它们只证实工具链基本可用，不认证排版、事实、公式、
论文阅读覆盖或读者理解率。多媒体交付仍按 [输出阶梯合同](../workflows/output_ladder_workflow.md)
独立验收。现有 Paper Reader 使用同一 PyMuPDF 依赖，但本命令不自动启动其服务或模型。

维护者更新锁可显式运行 `python scripts/lock_documents_profile.py WHEELHOUSE`，核对每个 PyPI
发布条目的 filename/hash 和 wheel metadata，再审查变更；此命令不安装、不自动替换锁。

维护者可显式设置 `AGENT_DOCUMENTS_TEST_WHEELHOUSE=/absolute/wheels`，运行
`python -m unittest tests.test_documents.DocumentsOfflineInstallTests -v`：隔离目录中验证
缺包后重试、真实离线安装和删缓存后复用。该开发测试使用 AGPL 参数；默认测试不执行这次安装。
