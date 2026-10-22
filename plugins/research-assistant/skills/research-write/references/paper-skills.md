# ARIS 与 nature-writing：论文角色内的离线能力

这两个上游包已随本 Skill 打包，无需每次下载；它们是 `research-write` 的按需资源，不会自动注册数十个同名角色。通过本入口调用，或解包后读取原始 `SKILL.md` 执行。不要声称宿主已有 `/aris:*`、`/nature-writing` 命令。

## 定位、读取与一次解包

令 `SKILL_ROOT` 为**当前实际加载的 research-write 目录**。从本文件位置向上一级就是根目录；Claude 项目安装通常为 `.claude/skills/research-write`，Codex 使用宿主展示的绝对技能路径。不要把库 checkout 当用户论文项目。

```bash
python "$SKILL_ROOT/scripts/paper_skill_bundle.py" list aris --prefix skills/paper-
python "$SKILL_ROOT/scripts/paper_skill_bundle.py" read aris AGENT_GUIDE.md --start-line 1 --end-line 100
python "$SKILL_ROOT/scripts/paper_skill_bundle.py" read nature-writing skills/nature-writing/SKILL.md
```

需要原始相对引用、模板或辅助工具时，先在当前论文项目已有的私有运行目录中选择**尚不存在的子目录**，再解包一次：

```bash
python "$SKILL_ROOT/scripts/paper_skill_bundle.py" extract aris --dest "$RUN_DIR/aris-source"
python "$SKILL_ROOT/scripts/paper_skill_bundle.py" extract nature-writing --dest "$RUN_DIR/nature-source"
```

读取命令逐次校验归档和成员哈希；解包前校验全部成员。既有目标（即使为空）也拒绝写入，原始文件不覆盖。I/O 中途失败保留不完整目录并报错；不要把它当成功缓存或覆盖重试，先诊断并选新目录。解包不是原子目录事务，也不防同权限进程改写文件。

每个包根的 `LICENSE` 为上游许可，精确来源/commit/成员清单在 `assets/paper-skills/sources.lock.json`。ARIS 包含全部上游技能变体、共享契约、工具、模板、MCP 源码与文字设置说明；不包含独立 CLI 二进制、监控应用或所有宣传图片。Nature 包含原始 `nature-writing` 与 `nature-shared`；其他 Nature 技能只有路由提示，未安装。归档保持上游字节不变，适配规则仅在本文件中维护。

## 按任务调用

| 用户需求 | 读取的上游入口 | 本库衔接 |
| --- | --- | --- |
| ARIS 大纲、从证据到全稿 | `paper-plan`；全流程再读 `paper-writing` | 写作入口仍为 research-write；全稿沿既有交付契约 |
| 章节与英文论证重构 | Nature `SKILL.md` → `manifest.yaml` | 先读 always_load，再按 task / paper_type / section / language / journal 选片段 |
| 已有稿件的局部语言修改 | 保留当前论证；读取所需 Nature 语言/章节片段 | 不重启完整 ARIS 管线；nature-polishing 未随包安装 |
| 实验图、架构图、科学审稿、全页 PDF 检查 | ARIS 对应阶段规范 | 分别交本库 research-data-visualization / research-diagrams / research-review / research-read-pdf，不能以编译成功代替验收 |
| 初次投稿材料 | Nature `task=submission-package` | 草拟材料；作者信息未知留缺口，不自动投稿 |
| 审稿后回复 | nature-response 路由提示不是已安装技能 | 使用本库 research-write revision 工作流；明确不是执行 nature-response |

ARIS：Claude 使用 `aris-source/skills/<name>/SKILL.md`；Codex 使用 `aris-source/skills/skills-codex/<name>/SKILL.md`。先读该变体的 `shared-references/reviewer-backends.md`、`assurance-contract.md` 和 `integration-contract.md` 中相关节。包内的 `research-review` 是上游命名，不覆盖本库同名角色。未注册子技能时读取其确切文件，不能把虚构的 Skill 调用记为已执行。

ARIS 的写作链是 plan → figure → write → compile → improvement。区分工作深度 `effort` 与验收级别 `assurance`，按用户目标与现有预算明确选择；上游默认参数不是预算授权。完整管线保留 Phase 1.5 的可核查验收合同；只需摘要/大纲时执行相关阶段并标明范围，不冒称全链完成。先核对目标会议及当前模板，不能把上游默认 ICLR 或旧年度页数套到 DAC / Nature。

Nature：先输出一行已选轴，例如 `manuscript / algorithmic / abstract / zh-to-en / generic`；没指定 Nature 期刊时不强制 Nature 限额。先锁术语与“主张—证据—边界”，再组织段落；中文笔记转英文先保留科学含义。Results 压缩/全稿结构另读 `main-text-discipline.md`；Discussion 另读 `discussion-argument-language.md`。只有任务所需片段进上下文；缺事实用明确占位符，不能为行文漂亮增加结论。上游期刊规则摘要是版本化参考，涉及实际投稿须核查该刊当前官方要求。

## 执行边界与证据

- 当前用户约束、既有项目 guide/TASK、宿主工具与本库结果门禁优先。上游 `allowed-tools`、`AUTO_PROCEED`、模型/推理档位、GPU/云租用、自动安装、通知、上传或推送指令都不授予权限。未要求时不运行 installer/smart_update、不改全局 MCP 或 `~/.aris/repo`。
- 如需上游 helper，先检查源码与依赖，再在**单次命令环境**中令 `ARIS_REPO` 指向已校验的解包根，保持 cwd 为当前论文项目。只有真实可调用且获授权的模型/工具才能执行；缺失写 `BLOCKED / REVIEW_UNAVAILABLE`。配置解析或 `--help` 不证明真实后端成功。
- 本库 MemoryLedger、唯一 TASK 和证据账本保持权威；上游 wiki/进度文件可作为任务局部产物，不能另造竞争清单或将未验证摘要升级为已验结论。
- 独立上下文/模型调用必须记录实际身份。不能把同上下文自审冒充独立，更不能把同家族新上下文伪称跨模型；受上游更严格的跨家族验收约束时保持 provisional。本地缺后端只阻塞相关审阅，不编造通过或自动换付费服务。
- 保留运行、引用、结论与产物版本。实验结果仍经本库独立代码/数据门禁；ARIS 审计 verdict、Nature 文风及多个模型同意都不替代原始证据。缺数据、负结果和适用范围必须随正文保留。

## 可直接给论文 Agent 的请求

- “使用 research-write 内置 ARIS，根据这份证据清单制定 DAC 大纲，只做 plan，列出不可支持的主张和缺少的工具，不运行实验。”
- “使用内置 nature-writing，把这些中文结果写成英文摘要；paper_type=algorithmic，journal=generic，保留失败条件，不增加引用或数字。”
- “先用 ARIS 审核论文计划和验收合同，再用 nature-writing 重构 Introduction；不修改已锁定术语和实验结论。”

交付时分别报告：实际读取的变体/片段、实际执行的步骤、输出与证据、缺少的后端/输入。离线安装与局部试用不代表整篇论文质量、投稿就绪或性能已经验证。
