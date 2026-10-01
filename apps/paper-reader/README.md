# 本地 Web 论文伴读器

左侧阅读 PDF 原页，右侧记录问题并调用在线模型讲解。PDF、页码和笔记保存在自己的电脑；模型推理由本机 Codex 客户端连接的服务执行。它不是纯离线模型，也不自动接管某一段 ChatGPT 网页对话。

## 启动

要求 Python 3.10+；需要网页内 AI 讲解时，另安装官方 Codex CLI 并登录。建议 Windows 用户在 WSL 中运行服务与 Codex，确保它们处于同一个环境。

从本仓库根目录：

```bash
python -m venv .venv
# Linux / macOS / WSL
source .venv/bin/activate
python -m pip install -r apps/paper-reader/requirements.txt
# 若需要在线讲解，先按官方文档安装 Codex，然后：
codex login
python apps/paper-reader/app.py
```

打开 **http://127.0.0.1:8765**。每次使用时保持该进程运行；可以收藏这个本地地址。再次启动会恢复论文和阅读位置。端口被占用时加 `--port 8766`。它不是部署在 ChatGPT 工作区的长期公网服务，别把工作区的 localhost 链接当作你电脑上的地址。

导入这次的 QuantMLA 示例及已核实的入门导读：

```bash
python apps/paper-reader/app.py --arxiv 2609.36760v2 --notes apps/paper-reader/examples/quantmla-notes.json
```

下载受限时，在浏览器下载 PDF 后使用 `--pdf /path/to/paper.pdf`，或启动后拖入页面。示例笔记绑定具体 PDF SHA-256；不同版本/不同字节的文件不会静默混用笔记。原论文来源：[QuantMLA v2](https://arxiv.org/abs/2609.36760v2)，作者 Zunhai Su 等，2026-09-30，论文公开许可为 CC BY 4.0。仓库不包含论文 PDF，示例是原创导读而非全文翻译。

## 怎样获取模型讲解

1. 本机 `codex login`，在官方登录页面选择自己的 ChatGPT 账号；不用把密码、Cookie 或令牌粘贴到阅读器。
2. 确认 `codex login status`。如 CLI 安装在自定义目录，可用 `PAPER_READER_CODEX` 环境变量指定其可执行文件路径。服务只检测是否存在 CLI，实际模型访问以成功回答为准。
3. 选择页码，输入问题。文字模式允许选中原文；公式和图必须结合原页。
4. 点击“请 AI 讲解”。服务通过 Codex 的非交互接口，将当前页图片、前后相邻页文字、用户问题、最近 4 条问答及仓库知识讲解规范交给模型。
5. 完成后保存答案到提问时的论文和页码。可以继续追问，或跳页后再问。联网选项控制 Codex 的 web search 配置；允许联网不表示每次真的执行了搜索，答案须提供可核实来源。

这使用本机 Codex 已配置的模型和登录方式，不保证与当前 ChatGPT 网页选中的模型完全一致，不会自动获得网页聊天历史或账户记忆。可用 `PAPER_READER_MODEL` 环境变量指定账号可用模型；没有指定则使用本机配置。ChatGPT 登录与 API key 登录的额度/计费方式不同，按实际登录方式适用。不会在失败时自动切换到另一付费服务。

没有 CLI 或尚未登录时，PDF、笔记、阅读位置仍可用；也可以“复制到 GPT”。缺失连接不会返回模拟 AI 答案。当前环境已测阅读与服务接口，**未完成真实账号的模型往返测试**。

## 当前功能与范围

- 拖入 PDF、arXiv 导入、按需加载原页、文字选取、缩放、页码导航。
- 本地 SQLite 保存论文清单、进度、按页问答和笔记；按论文导出 JSON。
- 讲解上下文最多当前及相邻 3 页，文字最多 65,000 字符；不把局部材料冒充全文。问到其他页时应跳到该页。
- 回答当前按纯文本呈现，可点击 HTTP/HTTPS 来源；LaTeX 和 Mermaid 代码尚未自动排版/渲染。复杂图解可继续在 ChatGPT 中生成，不能称为已实现网页绘图服务。
- 模型请求最多 240 秒；仅收到完成事件且有最终答案时保存。当前不做逐 token 流式显示，界面显示处理状态。
- 本地导入上限 32 MiB / 1,000 页。PDF 原页保真显示，提取文字仍可能存在顺序或公式识别误差。

## 数据与运行边界

默认目录为 `apps/paper-reader/data/`，已被 git 忽略。`--data` 可换位置。备份时保留此目录的 SQLite 与 PDF。导出的笔记 JSON 适合归档；本版未实现通用 JSON 回灌接口。

服务只监听 127.0.0.1，检查 Host/Origin，写请求使用进程级令牌；不提供监听公网的选项。CLI 调用使用参数数组、只读 sandbox 和独立临时目录，不绕过客户端安全控制。它是个人本地工具，不是多用户生产服务。

点击模型讲解会将附近页面、当前页图片及问答上下文发送给本机 Codex 连接的模型服务；联网搜索可能另外发送查询词。登录凭据由官方客户端管理，阅读器不读取 auth.json，也不接收 API key。

## 验证

```bash
python -m unittest discover -s apps/paper-reader/tests -v
```

覆盖上传/页图/原文、进度与笔记持久化、越界页码、请求来源与令牌、下载域名限制、模型完成与失败分支。模型返回使用明确的测试替身，不代表在线模型已通过测试。页面 JavaScript 通过语法检查；云浏览器禁止访问本地地址，因此完整浏览器交互与视觉验收仍需在运行机器完成。

## 官方接口依据

核查日期：2026-10-01。后续客户端升级需重新核查参数及 JSON 事件格式。

- [Codex 登录与账号方式](https://learn.chatgpt.com/docs/auth)
- [Codex exec、图像输入和 JSON 输出](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- [应用使用 ChatGPT plan 的官方接入说明](https://developers.openai.com/siwc/token-sharing-open-source)：未来可升级为应用内官方 OAuth；本版使用本机已登录的官方 CLI，没有自行实现 OAuth。
