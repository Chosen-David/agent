# PAPER-SKILLS-01：论文 Agent 的 ARIS / nature-writing 接入

Task-ID: PAPER-SKILLS-01
Date: 2026-10-22

## Plan

Version: 2

用户明确要求安装 ARIS、nature-writing，并让既有论文 Agent 学会调用。保持 research-write 为写作入口，不改人类 guide、不新增竞争任务索引、默认不注册全部上游技能的元数据。原始技能与辅助工具以离线资源打包，按需读取/解包；不自动执行上游脚本、安装模型、改 MCP、启动服务、提交论文或外发材料。

固定来源：ARIS `wanshuiyin/Auto-claude-code-research-in-sleep@23745b69a14880b5716d1773e5d20f5f1e6ab1d6`（MIT）；nature-writing `Yuan1z0825/nature-skills@c6ae86c742705fd968b13c79db1a8518a84089d4`（Apache-2.0），随包保留 LICENSE 与路径清单/哈希。ARIS 包含技能/共享契约、工具与模板及必要文字说明；Nature 包含 nature-writing 与 nature-shared。未安装其他 Nature 技能及 ARIS 独立 CLI/监控服务；涉及外部工具的阶段须报告能力缺口。

实际接入目标：本仓库论文角色的 standalone Skill；以及当前已经存在的用户 Skills 工作区 `/root/.codex/skills/remote-skills/research-write/`。后者现有三个文件未跟踪，保留其正文和接口，仅补充按需入口、新离线资源和脚本，精确暂存本次文件。其他未跟踪角色文件不动。Skills 工作区独立提交/push 后才宣称持久安装，宿主新会话发现另行说明，不能假称热重载。

宿主路由：Claude 使用 ARIS `skills/<name>/SKILL.md`，Codex 使用 `skills/skills-codex/<name>/SKILL.md`；其同名 research-review 等只在包内引用，不覆盖本库角色或注册独立 slash 命令。Nature manifest 的 always_load、axes.values、references.on_demand 路径须逐项验证闭包；ARIS 主/子阶段与 helper 路径核对，缺依赖标 blocked，不能替换为自审或默认成功。

验收：原始来源与许可/成员哈希；离线 list/read/extract 和安全拒绝；现有 setup 链接/复制安装后的资源闭包、卸载；独立上下文对限定证据写摘要与仅规划 ARIS 任务；独立代码/输出复核；普通 main 推送并回读。这里只验证安装、局部试用与拒用边界，不主张整篇论文质量、真实 GPU/MCP 执行或速度提升，不将此安装当 SYSTEM-99 全批完成。

## Progress

- 初始基线 `5c23b3c6dc9f9b11b73730d8043bd1bd81fdd22d`；干净独立 worktree。现有结果库查询 `ARIS nature-writing` 仅返回无关 corpus 候选，max100 部分检索且若干历史文件缺失，没有可复用的相同安装/质量验收。当前任务不做性能基准。
- 方案独立复核进行中；本条不宣称安装或验收已经完成。

- 独立方案 v1 要求补齐来源/实际部署/宿主变体，已在 Version2 修订并获 approve；是当前原生独立上下文的人工审阅证据，不伪称受信任 runtime 回执。
- 来源读取：ARIS AGENT_GUIDE、paper-writing 关键阶段、paper-plan 及共享 reviewer/assurance/integration；Nature SKILL/manifest、核心、algorithmic/abstract/zh-to-en/generic 片段。未宣称学习全部 ARIS 技能或完成十篇论文新批次。
- 实现随 research-write 打包 ARIS584 / Nature99 个原始成员，包含原始许可；嵌入资源不新增角色元数据。新增离线 list/read/extract；保留覆盖拒绝及未完成解包错误。当前 runtime research-write 已添加同资源与按需入口，原 workflow/openai.yaml 字节保留；持久 push 和发布回读尚待完成。
- 普通回归53项通过（bundle/setup/model-routing/figure-contract），专项优化模式8项通过；install-profiles/role-process/figure/bundle组合35项通过；Reader3项通过、reference sync和diff检查通过。组合有重叠，不相加成独立用例数。
- 首次新增安装测试两项因旧installer卸载保留空白分隔而失败；核对现有契约后测试改为精确核验用户正文及受管块移除，未修改installer，未将此记为生产bug。新任务详情标题先不符合Plan/Progress schema，已修正；全量文档默认显示上限拒绝后显式提高max-chars，validate退出0，不以截断当通过。
- 原生新上下文试用：nature-use写100词英文摘要，输入明确为虚构练习，不计研究实测；aris-use只做DAC大纲，保留局部慢3.31倍、质量/e2e未测与REVIEW_UNAVAILABLE。结果与实际读取片段保存在私有run目录。宿主无完整子调用工具轨迹导出，不能仅凭输出自报独立证明全部禁止动作未发生，更不主张普遍写作质量提升。

- 持久安装：首次gzip候选推送HTTP422拒绝，远端未改变；原因未知。改为更紧凑xz后，683个来源成员完全不变，独立复验8项、普通53项和优化8项重跑通过；不由此推断具体服务端限制。个人Skills仓库普通推送成功至 `6085dc8`；当前宿主已列出并实际读到新 `research-write` package `6ad9c5c0ea1081918ed5a4edd733b4c8`，元数据含ARIS/nature-writing。原有三个文件的原文重建哈希与未改workflow/metadata核验保留；未修改其他未跟踪角色。
- 独立结果复核ACCEPT（限定安装与两条试用），原gzip审核和xz复验均保留。公开短日志、输入/实现哈希与复核见 `agent_doc/results/paper-skills-20261022/`。Linux/Python3.12验证；不主张原生Windows、完整论文质量或外部后端已部署。SYSTEM-99所有既有未决项保持开放。
- Agent仓库发布候选仅本任务文件；main推送/远端整树和关键内容回读由主控最后完成，并在对话与私有检查点记录实际SHA，不以预写文档冒充成功。

- Skills服务端规范化目录为 `skill-6ad9c5c0ea1081918ed5a4edd733b4c8`，materialized远端SHA `9f74a1e843ed935a9a461baeaadfc51e861a7444`；从该远端逐字节回读入口、原workflow、调用指南、脚本、来源/许可与两归档共8项，与推送源完全相同。服务端生成UI图标不记为本次原始资源。
