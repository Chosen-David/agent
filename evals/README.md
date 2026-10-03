# Agent 执行任务集

这不是关键词出现次数测试。当前目录有14个角色任务，覆盖注册表中的14个插件skills，输入为本仓库合成材料；评判代码、数据、报告、图片、HTML与状态记录。外部模型调用不由本仓库脚本伪造。

## 可审计的宿主驱动 Pipeline

新入口为 [scripts/agent_eval_pipeline.py](../scripts/agent_eval_pipeline.py)，接口与证据边界见 [运行说明](../docs/agent_eval_pipeline.md)。它冻结指定Git版本与评分合同，接收真实宿主启动/完成回执，收集产物哈希并导入独立评分；`report --require-complete` 才是完整性门禁。Python脚本不会伪装调用宿主Agent，也不自动发布。

新增的 [pipeline_smoke/tasks.json](pipeline_smoke/tasks.json) 包含主AI普通任务/路由、协调→写作真实文件交接与新的旅行修订输入；评分在相邻rubric中，不传给执行者。跨角色writer只有接收到真实producer文件后才能准备；缺依赖不能预填答案或记通过。当前更新仍须实际运行全部角色；合成smoke不是生产成功率估计。

## 原有手动准备方式

1. 安装运行任务所需的实际环境。代码/文本任务只需Python；图任务需要Matplotlib；PDF/HTML任务需要PyMuPDF，PDF读者也可使用Poppler。使用当前环境支持的真实图像查看工具。不要自动安装无关后端。
2. `python scripts/prepare_agent_eval.py --dev-eval --out /tmp/agent-eval-new-run`。目录必须全新，避免覆盖历史。可用 `--case research-write` 只准备受影响角色。
3. 为每个目录启动独立、空白上下文的执行器：读取 `skill/SKILL.md` 和 `task.txt`，只读取该目录的 `inputs/`，写入 `outputs/`。不要让执行者读取rubric、其他角色或旧产物；没有独立执行器则记录串行非隔离限制。
4. 评审者读取 [rubric.json](rubric.json)，打开真正输出，复算数值、运行代码检查、观察图像和页面；检查执行记录，不能仅信“我已完成”。记录模型/宿主可见信息和是否重复运行，未提供的token/成本不编造。
5. 保留失败和修订原因；变更技能后新目录、新上下文复跑。重要改动应加入不同输入的保留任务；统计提升需同条件旧版/新版重复A/B。

`fixtures/make_pdf.py` 可生成三页合成PDF；版本锁以实际PDF SHA-256为准。仓库自带固定fixture，通常直接使用它，无需每次重新生成。生成文件不表示已阅读。

## 历史运行（首次12角色版本）

执行环境：本次Codex Work会话的真实独立子任务执行器；子任务不继承主线程历史，每个仅获自己skill、请求、材料与输出路径。未显式指定模型覆盖，具体底层模型/seed/token/cost不从提示词推断。人工语义判定由主执行者复核，非盲审。真实图像查看由子任务执行，主执行者额外复核关键图。

全部任务均是有限范围的合成输入smoke test，不代表真实论文科学结论、实时商户真实性或外部后端集成测试。没有旧版同模型A/B，不报“提升X%”。

[逐项评分](results/2026-10-03/grading.json)与 [复核记录](results/2026-10-03/review.md)记录最终状态，原始产物在相邻角色目录。文件内 `/tmp/agent-forward-v1/` 等路径是执行时路径；它们是留档证据，不承诺换目录后所有当次生成脚本无修改可重跑。重跑请使用上面的任务准备步骤重新执行。

首次调度任务存在done依赖skipped的状态歧义。该缺口由产物复核发现，rubric补上完成依赖条件，技能增加“保留检查任务”，随后独立重跑；初次产物完整保留在research-assistant目录，复跑位于research-assistant-v2。不得把修复后的结果改写成首次全通过。

代码/结构测试独立运行：

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
python scripts/sync_plugin_references.py --check
```

代码测试包含真实文件/哈希/依赖失败案例、后端只探测不执行的检查、阅读器生成与本地HTTP边界。HTTP测试绑定127.0.0.1，需要宿主允许loopback；模型完成路径使用测试替身，不代表真实模型服务已连通。所有文档契约测试仍只是结构检查。

## 维护原则

新bug保存最小脱敏fixture和能区分对错的断言，先复现再改；负例包括缺证据、哈希变化、路径越界、依赖环、未运行检查却声明完成、导入副作用、PDF版本错配和不可信笔记。评分不只看文件存在/关键词；禁止把缺测记为通过。敏感输入、私人行程或真实未公开稿件不得放入公共评测集。

并发main新增作图拆分后，另测research-data-visualization、research-diagrams及更新后的research-figures混合图入口。旧纯数据作图产物保留为历史证据，新任务与rubric在新执行前固定。旅行共享契约更新后也独立复跑；不将旧版本成功直接归到新版本。所有输入和技能文件SHA-256见 execution_snapshots.json。

`results/2026-10-03/execution_inputs.tar.gz` 保存每次执行真正收到的task、输入和技能快照（含首次与复跑），与哈希清单配合审计；该归档对应当时的12任务版本；当前catalog已包含代码阅读和代码组织角色，共14项。

代码组织任务使用 `fixtures/organization/` 的合成目录：两组脚本/结果、历史 CODEMAP、活动输出和受保护孤儿笔记。只在任务 outputs 中生成文档与提案，输入目录不移动、不删除、不执行。

本轮 [cross-feature 实测与开发边界](../docs/crossfeature_validation/README.md) 包含真实角色、程序正反例、已发现漏检和可重放证据。仅在显式开发评测/CI运行；日常任务保留必要自检但不加载合成评测或gold。
