# SYSTEM-99 阶段O：TASK单次快照绑定

问题ID：`CHAIN-TASK-SNAPSHOT`。基线SHA：
`5379fb9e8541df478ccbdb3c682ed6eff4c6e486`。方案及独立方案审阅分别见
`stage-o-plan.md` 与 `independent-stage-o-plan.md`。

## 触发条件与根因

旧 `agent_runtime/task_manifest.py` 的 `validate_contract` 先用 `digest(path)` 读取一次TASK.md，
再用 `requirements(path)` 重新按路径读取。只要文件在两次读取间换版并在后续project-doc检查前
恢复，摘要和任务集合就来自不同版本。实际最小反例让绑定OLD摘要、仅覆盖NEW ID的计划通过：

```text
{'accepted_ids': ['NEW'], 'bound_sha_is_original':
'aabce6bf85cf17ef46901259006c130ed98382e856fbe438b3810f2a1fb51193',
'disk_after': '- [ ] [OLD] original requirement', 'swapped': True}
```

同类分离也存在于prepare的任务项/摘要/project-doc读取，以及publication freeze的候选树、所有权
ID与project-doc读取。影响主计划审阅、submit review、start、每次tick、进度派生和发布所有权
冻结，不只是显示层。

## 修复

- `agent_runtime/project_docs.py:104` 的普通文件读取增加可选字节上限：先检查文件类型/`st_size`，
  再读取 `limit+1` 检查读取期间增长；默认调用语义不变。同步更新生成的research-assistant引用。
- `agent_runtime/task_manifest.py:27-67` 新增1 MiB任务源边界；一次原字节读取同时计算SHA256、严格
  UTF-8解码并按原canonical规则解析任务。公开 `requirements` 复用该路径。
- `agent_runtime/task_manifest.py:143-207` 的prepare把同一快照与project-doc task_index交叉核对；
  validate从同一快照完成摘要和任务覆盖，并拒绝task_source/project-doc身份冲突。
- `agent_runtime/publication.py:178-210` 把发布候选树、任务所有权ID和project-doc task_index三者绑定
  到同一TASK摘要，任何中间换版均拒绝冻结。

当前TASK输入SHA256为
`58c0c234f3c7ed89bfd49d8670048c21e99193c0abc42b2365212d3e11b69bdd`。最终核心文件SHA256：

```text
project_docs.py  7a9f21624eed1eb5993c90332657a945d7d5f6086be687e575638d829a029d1f
task_manifest.py e1811431542caea96c7ed1e0faa6b6025d16cd8954f3f50264ba2f6277c40ec6
publication.py   435d3fca6e67d51717ae25d729b2ec59a755e710f4434501e063b924c5593db2
snapshot tests   76919d28bb2cb1686802c6279824152c877071fcf156bd50739ac889a9810997
```

## 实际验证

修前同条件反例为接受NEW；修后输出：

```text
{'status': 'rejected',
 'error': 'ValueError: each runtime task must map to known TASK.md IDs',
 'second_path_read': False,
 'disk_after': '- [ ] [OLD] original requirement'}
```

新增回归覆盖当前reader读取A后磁盘变B并由project-doc重检拒绝、读取A后A→B→A仍只返回A、
prepare/publication中间换版、source/doc冲突、中文CRLF原字节摘要、非法UTF-8、超1 MiB、恰好
1 MiB、目录、FIFO、文件及父目录符号链接。实际命令结果：

```text
相关调用链：174 tests, OK (1 skipped)
新增快照/publication/plugin-sync：40 tests, OK
python -O 定向：125 tests, OK
全库：1406 tests, 1398 passed, 8 skipped
Reader：2 tests, OK
sync_plugin_references.py --check：exit 0
git diff --check：exit 0
```

环境：Linux 6.18.55 x86_64、CPython 3.12.14，标准库文件/Git/SQLite临时夹具；未调用模型、
网络、GPU或付费服务。独立最终验收复跑39项新快照/publication测试，结论
`usable-with-scope`。

## 边界

该修复只保证每次TASK读取内部一致，并以现有重验连接task source、project-doc和发布候选身份；
不提供TASK、详情、guide、advice的跨文件事务快照，不抵御有写权限的恶意OS对手，也不证明校验
之后所有副作用的全局原子性。本阶段没有速度、token、费用或模型质量收益。27个未登记历史目录、
真实宿主/多轮质量、usage/费用和其它artifact读取边界仍待SYSTEM-99后续阶段处理。
