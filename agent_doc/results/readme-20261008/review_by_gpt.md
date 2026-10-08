# README-01 独立审阅

日期：2026-10-08。结论：**通过（usable-with-scope：本次首页文档与 SVG 展示范围）**。没有未关闭的阻塞发现；不代表模型效果、性能或宿主集成得到提升。

## 版本与范围

基线：`c60f576eab9545ceaf123b29306e81a604477115`。审阅 README 全文、两张 SVG，以及相对基线的文档变更。冻结输入如下；修改这些字节后需复核受影响结论。

| 文件 | SHA-256 |
| --- | --- |
| `README.md` | `163645cf9e573d10ae2f14639ea912855bf69516874573279ed53c12dc86e55e` |
| `docs/assets/readme/hero.svg` | `d0561affe9d878a6bb585aedfbaa11fa3eee2650c0468aa029440310aea39d55` |
| `docs/assets/readme/architecture.svg` | `6cce2151bd4c4f7742b959e3c8b5f27565903d77cc733dee9d0b25d481e763af` |

README 从 26,418 bytes 调整为 13,233 bytes。已查看当前 diff/status：修改为 README、CODEMAP、任务索引及新增任务详情/SVG；本审阅另增当前报告。未观察到程序、配置、技能、工作流契约或 SGLang 改动；人类 guide 未改动。

## 核验结果

- **定位和入口**：首屏保持通用主 AI 身份；通用、科研、旅行、代码阅读、知识、Claude 本地安装、Codex、Claude marketplace 和独立工作流入口均保留。旧首页的历史升级与冗长治理正文被导航替代，未发现关键用户入口丢失。
- **角色与包**：独立读取 `config/role_registry.json`、各角色 SKILL description、两份 marketplace。15 个角色全部出现在 README；Claude marketplace 为科研 14 + 旅行 1、共 2 包。角色职责未扩张为未经验证的实际模型执行。
- **安装命令**：对照 `setup.py`、`scripts/setup_codex.py`、SETUP 与 Codex 接入说明，核对目标路径、15 角色来源、已有指引/修改保护和 committed 技能源。初审发现进入 Project A 后 `--check` 相对路径歧义，主控已改为 agent 脚本绝对路径，并已复查。没有执行安装或改写用户级配置。
- **外部语法**：独立在线读取 [Claude Code 官方插件文档](https://code.claude.com/docs/en/discover-plugins)，核对 `/plugin marketplace add owner/repo`、`/plugin install plugin@marketplace` 及界面选范围/确认启用的说明（2026-10-08）。未执行实际插件安装。
- **项目归属**：对照项目文档工作流，Project A/B 的 `agent_doc` 各归目标项目；人类指南只读、初始化仅空指南目录、单一 TASK 索引、建议不是授权、缺失不回退本库历史的说明一致。
- **运行边界**：对照监督、通信、文档工作流及 `agent_runtime/core.py`，README 正确区分规范、可选本地运行时与真实宿主能力；没有把安装、tmux、inbox 或角色名当作已部署服务/真实模型调用。SSH 断开与断电重启的区别保留。
- **伴读能力**：对照 `apps/paper-reader/README.md` 和伴读工作流，正确拆分本地阅读器的可选 Codex CLI 连接与自包含离线 HTML；未暗示自动继承网页会话、离线模型后端或全文已读。
- **链接与锚点**：脚本提取共 60 项 Markdown 链接/HTML 图源：52 项相对目标、6 项页内锚点、2 项外链。52 项相对目标全部存在，6 项中文锚点全部匹配实际标题。两条外链仅 Claude 官方文档已在线检查；GitHub Issues URL 未做在线可达性验收。`git diff --check` 无错误。
- **事实表达**：未发现虚构评分、徽章、性能收益或部署主张；开发检查明确不能替代真实角色任务、同条件性能测量或宿主集成。

## 独立视觉检查

使用运行时 Sharp，直接从冻结的 SVG 源分别渲染 1200 px 与 390 px 宽 PNG，再通过图像查看工具逐张查看（4 张）。临时预览位于 `/tmp/readme-review-{hero,architecture}-{1200,390}.png`；它们是可重建的本地检查中间件，不是发布资源。

桌面尺寸没有文字遮挡、裁切或线条穿字。架构主链为主 AI → 按需角色 → 工具/产物 → 独立验收；紫色返修箭头从验收返回主 AI，方向与正文一致。宿主条带列出模型、工具、凭据、权限；底部明确区分 WORKFLOW_ROOT 与 PROJECT_ROOT。Hero 是装饰示意，不包含性能数据。

390 px 预览保持布局和主层级；细字较小，详细阅读需要放大，正文提供对应中文解释与可点击导航。未把小屏预览等同于全部细字可不放大阅读。

## 未验范围

未验证 GitHub 线上 README 页面、GitHub 客户端的最终排版/锚点实现或真实移动浏览器交互；本次覆盖本地相对目标/标题核对及 SVG 真实渲染。未重跑全程序/GPU 回归、未做模型 A/B、未部署或启动监督器、未执行真实客户端安装。本次文档验收不能扩张为这些范围通过。
