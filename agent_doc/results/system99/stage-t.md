# SYSTEM-99 阶段 T：摘要导航真实规模默认入口

问题 ID：`CHAIN-TASK-NAVIGATION`  
基线：`1cf7258f572a9fb3ab7b6e8e967eabde93cd20eb`（tree `aa26221246540c66fa57de025de27e996315dce8`）  
环境：Linux 6.18.55 x86_64，Python 3.12.14；无模型、GPU、tmux、SSH、付费后端调用。

## 触发与根因

并发 main 新增 `task_navigation` 后，用仓库自身317项 canonical TASK 实跑：

```text
python -m agent_runtime.project_docs --root . nav
returncode=2
{"error": "task navigation exceeds character budget; narrow the digest"}
```

34项未勾选、283项已勾选；原实现无选择接口，先读取317份详情再序列化。即使把每项
`progress_tail_chars` 降到1，全量紧凑JSON仍约80369字符，默认12000预算必然失败。既有测试只有
一个未勾选任务，未覆盖真实规模。既有结果检索扫描240条且`partial=true`，命中均与此入口条件
不匹配，未复用为修复证据。

## 修复

- 默认只选择 canonical 索引中未勾选的条目，且在打开详情前完成筛选；不把它称为受管 active 状态。
- 返回 `selection`、`total_tasks`、`selected_tasks`、`omitted_checked_tasks`，不静默冒充全量视图。
- `include_checked=True` / `--include-checked` 显式读取历史全量；预算不足仍拒绝。
- 首轮独审发现单一尾部把新记录置顶的 SYSTEM-99 旧 Stage N 误作当前进度，结论
  `blocked/revise`；原记录保留在 `independent-stage-t.md`。
- 返修为 `task-navigation/v2`：默认64字符总预算内返回中性文档首/尾片段，只标文件位置，
  不推断较早/较新；缺结构化摘要/状态时调用方必须打开详情确认。旧参数名仅作兼容别名。
- `nav` CLI 使用与预算校验相同的紧凑JSON，避免缩进输出绕过口径。
- 文档明确默认视图不验证被省略详情中的身份、格式、更正、异议或依赖；完整审计仍需显式全量
  或 snapshot/delta。

源码与镜像：`agent_runtime/project_docs.py`、
`plugins/research-assistant/skills/model-with-knowledge/scripts/project_docs.py`；测试：
`tests/test_task_navigation.py`；canonical工作流及17份生成引用按既有同步器更新。

## 实际验证

真实 checkout 默认入口：

```text
returncode=0
selection=unchecked total=317 selected=34 omitted_checked=283
schema=task-navigation/v2 compact_json_chars=11555 bytes_utf8=15975
sha256=0de9cda448381144dbf97d6e89fa4e62cc46f612f84b1a88d323c7d6d2fbcc34
```

显式全量使用 `--include-checked --max-chars 200000 --progress-chars 2` 返回317/317，省略0；
默认预算下的大型全量fixture仍明确失败。新增/相关专项普通与`-O`各15项通过，另含CLI、60项规模、
置顶/追加进度首尾、已勾选坏详情不读取、显式全量再拒绝、零未勾选、bool/int、身份和预算边界。
全库1500项（1492通过、8跳过，94.245秒）；Reader 3项通过（1.567秒）；
生成同步、compileall和`git -c core.whitespace=cr-at-eol diff --check`通过。

## 结论与边界

本阶段恢复了仓库当前规模的默认导航可用性，并使省略范围可观察；11555是实际JSON字符数，不是
provider token、费用或质量收益。默认视图故意不读283份已勾选详情，因此不能用于全量更正/异议/
依赖审计。详情的 Progress 既有尾部追加，也有像 SYSTEM-99 这样新记录置顶的历史写法；v2首尾
片段明确不保证哪边最新，仍须以索引/结构化摘要和打开目标详情核对，不能静默猜测。真实模型宿主、多轮任务质量、
usage/费用、tmux/SSH与跨主机恢复仍未验证；SYSTEM-99和
整轮继续未完成。同批17篇论文正文记录沿用，本阶段没有另起轮次或重复计数。v2返修经
`independent-stage-t-final.md`独立复测接受`usable-with-scope`；首轮阻断记录继续保留。
