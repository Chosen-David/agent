# README 首页升级

Date: 2026-10-08
Task-ID: README-01
Baseline: c60f576eab9545ceaf123b29306e81a604477115

## 交付与目的

重构总 README 的阅读顺序：定位 → 快速接入 → 能力地图 → 架构/验收 → 目标项目文档 → 伴读 → 开发验证。历史研究和治理细节通过既有文档入口继续访问，原始记录不移动。新增 docs/assets/readme/hero.svg 与 architecture.svg：固定背景、青绿主路径、淡紫返修回路、可编辑 SVG，无远程资源或脚本。

首页由 26,418 bytes 精简为 13,233 bytes；这是文件大小观测，不是用户阅读效率或模型性能试验。15 个角色全部映射到注册表，两个插件包及 Claude marketplace 接入保留。明确 Project A 的 agent_doc 属于 Project A；修正旧科研技能列表遗漏、旧知识条目硬编码数与离线/在线伴读能力混读问题。未添加虚构评分、星数、CI 徽章或性能承诺。

## 验证与修复

- 相对路径、内部锚点与全角色枚举检查通过，详见 checks.json；Pandoc GFM 解析成功。
- project_docs validate、sync_plugin_references --check、git diff --check 均返回 0。
- 作图角色真实生成并查看 SVG 的 850/420px 渲染；主控独立查看同尺寸架构图及850px横幅。独立审阅者另看 1200/390px，报告 review_by_gpt.md。
- 首轮图形修复水平渐变连接线与箭头终点间隙；独立审阅发现 cd Project A 后相对 --check 路径错误，已改绝对路径并复核最终哈希。
- 仅文档和图源改变，没有更新运行时、技能正文、用户指南或 SGLang，因此未重复全仓程序/GPU测试或真实模型性能 A/B。

完整 GitHub 线上页面未做浏览器截图验证：本机 Playwright 包存在，但无 Chromium 执行文件，保留失败并未下载额外浏览器。SVG 已真实渲染，不把 HTML 转换称为网页视觉验收。手机尺寸辅助小字需放大，正文和 alt 保留图意；未声称取得客观“高分”。

## 来源与复用边界

能力、数量和命令以本次基线 config/role_registry.json、两个 marketplace 清单、setup.py、scripts/setup_codex.py、相关工作流及阅读器文档核对。Claude 命令另核查 https://code.claude.com/docs/en/discover-plugins ，访问 2026-10-08；没有实际安装到用户的 Claude/Codex 环境。

新任务先执行 result_store search 'README architecture onboarding' --limit 3，返回三个不适用的知识语料候选与 partial/10 个缺失 record；未复用它们的验收。本文无需科学知识迁移，未调用知识库并未声称加载。原持续优化批次、未发布历史 stash、论文计数与收敛状态保持；本次是明确授权的展示升级。

发布采用远端 main 基线复核、内容树一致校验、expected_sha 与 force=false 更新及远端回读。具体发布提交由本报告所在 Git 历史和宿主回执定位，未发布前不把候选当线上结果。
