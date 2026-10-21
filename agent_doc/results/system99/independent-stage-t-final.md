# SYSTEM-99 阶段 T v2 独立最终验收

结论：**usable-with-scope**。首轮 `independent-stage-t.md` 的 `blocked/revise` 原样保留；该轮发现的
“单一文件尾部被误标成较早内容、实际留下旧 Stage N”的阻断已由 `task-navigation/v2` 消除。
本结论只接受本地文档导航的选择、预算和中性文件边界语义，不接受真实 token、模型质量、费用、
完整历史审计或 SYSTEM-99 整轮完成主张。

## 独立代码与语义核对

- `_progress_edges` 在总字符预算内返回 `start`、`end`、`truncated`；字段名、实现和 scope 都只描述
  文档位置，不推断时间。真实 SYSTEM-99 输出的 `start` 是 Version28 Stage T，`end` 是旧记录末尾，
  同一结果明确带 `no newer/older guarantee`，且完整 JSON 不再含 `earlier`。
- 新的置顶/尾部追加回归分别用 `NEW-PREPENDED/OLD-AT-END` 与
  `OLD-AT-START/NEW-APPENDED`，两种都只断言文件首尾，不把任一边当当前状态。
- 默认先从 canonical index 选未勾选条目，再打开所选详情。已勾选坏身份默认不读，显式全量才
  fail-closed；`unchecked` 在代码、scope和文档中均未冒充受管 `active`。
- 输出显式携带 `selection`、总数、选中数和省略的已勾选数。文档说明默认不验证省略详情中的
  更正/异议/依赖，缺结构化摘要/状态须打开详情；全量审计走 `--include-checked` 或 snapshot/delta。
- `nav` 使用与 `max_chars` 检查一致的紧凑 JSON。旧 CLI `--progress-tail-chars` 只作参数别名，
  输出仍是 v2 中性 `progress_edges`；别名与新参数在相同输入上逐字节一致。

## 独立实测

在候选工作树直接运行普通和 `python -O` 专项，各15项通过：

```text
python -m unittest tests.test_task_navigation -v       -> 15 OK
python -O -m unittest tests.test_task_navigation -v    -> 15 OK
```

真实317项仓库默认 CLI：

```text
returncode=0, schema=task-navigation/v2
selection=unchecked, total=317, selected=34, omitted_checked=283
compact JSON=11555 chars / 15975 bytes (excluding newline)
sha256=0de9cda448381144dbf97d6e89fa4e62cc46f612f84b1a88d323c7d6d2fbcc34
```

显式全量在默认12000预算下返回2及明确 budget error；使用
`--include-checked --max-chars 200000 --progress-chars 2` 返回317/317、省略0，83154字符，SHA256
`04f43db77a5ee27df2346ef87d74fa2c0221839fc4858006a42c31fe9bc18867`。把最后参数改成兼容别名
`--progress-tail-chars 2` 输出逐字节相同。

`scripts/sync_plugin_references.py --check`、runtime 与 model-with-knowledge 脚本逐字节比较、
`git -c core.whitespace=cr-at-eol diff --check` 均通过；canonical 工作流的17份生成引用由同步门禁覆盖。
主控全库原日志 SHA256
`9ab137d26d116d0e0f760d7a22f216888d8445404f98968315baa654c745d6de`，记录1500项、1492通过/
8跳过、94.245秒；Reader日志 SHA256
`fa1ba7212c1e776d29db76d354d4a1f77a62b9c57e818ec9db12c07723a23b91`，记录3项通过、1.567秒。
本审核读取并核对两份原日志，未独立重跑全库或 Reader；独立重跑范围是普通/`-O`专项、真实CLI、
显式全量/预算、兼容别名、同步/镜像和diff检查。

## 接受边界

默认视图只读取34份未勾选详情，被省略的283份已勾选详情仍可能含历史更正、异议或依赖；计数可见
不等于全量语义验证。首尾片段不是“最新进度”，尤其当前317份详情的结构化摘要/状态覆盖仍很低，
消费者必须按文档打开目标详情。11555是 JSON 字符数，不是模型 token、缓存命中、费用或任务质量
提升。无真实模型、tmux、SSH、跨主机、Windows/NFS或多轮质量验证；阶段 T 可作为有界检查点发布，
SYSTEM-99及用户定义的整轮继续 open。
