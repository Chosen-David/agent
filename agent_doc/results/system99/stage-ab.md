# SYSTEM-99 阶段A/B检查点（不是一轮完成）

2026-10-20，基线dcc10b10537a3b410a25f6ef3f2c842a3c1777b4；Python 3.12.14/Linux x86_64。本阶段只恢复实际文档准备链与Claude安装说明，不声称项目完善、模型收益或真实宿主部署。

## 已修复

- TASK原315项有16行缺解析器要求的链接前空格；五份详情缺身份/日期或Plan/Progress。真实`project_docs validate`及新增三个checkout入口回归均失败。现在仅插入空格、准确组织元数据/边界及SYSTEM-99登记；不放宽解析器，不删除/勾选原任务。316项快照和实际CLI草稿可生成。
- `setup.py:block`两行仍生成Project A/doc，与实际agent_doc初始化矛盾；旧install/check都configured，不能证明路径说明正确。新安装输出回归修前失败，现仅更正两行；普通doc CRLF字节和原有生命周期保护保留。
- 新测试直接消费本库TASK/详情和安装产物，补以往只有合成样例/模板契约通过而实际维护输入不可用的覆盖空洞。

## 实际验证与范围

私有原始日志位于`.agent-runs/system99/`；不提交大草稿/论文PDF/大日志。

```text
before.log: Ran 3 tests in 0.003s; FAILED (errors=3)
install-before.log: Ran 1 test in 0.015s; FAILED (failures=1)
task-after-extended.log: Ran 4 tests in 0.562s; OK
focused.log: Ran 43 tests in 0.792s; OK
reader.log: Ran 3 tests in 1.582s; OK
full-tests.log: Ran 1355 tests in 88.590s; OK (skipped=8)
```

固定Git archive基线重放snapshot/prepare/task_view仍在canonical路径检查拒绝；修后真实快照316项。TASK逆投影精确等于原字节+16空格，原782个CR均保留；五份详情移除指定插入后与基线逐字节相等，原段落/状态/证据不改。边界原始输出在`boundary-checks.log`。

真实`task_supervisor prepare`使用默认main-plan-review/v1，无legacy或scope降级，生成316个configure_host_action占位草稿；没有启动/批准/重跑历史工作。正式validate_contract拒绝未审核human guide；旧真实TASK SHA、未知/重复task ID和超预算视图均拒绝；316详情普通Progress追加不变更稳定Plan。较早v2草稿在Plan升级后被task_details新鲜性门禁拒绝，保留为正确负控，未篡改旧快照。

当前task_view选择SYSTEM-99所得text2072字符、明确省略315任务行，仍保留其它原文；这是导航输出，不读详情、不证明优先级/全局完成，字符不等于token。三项装配单测mock了历史查询；另行真实CLI包含全部实际查询，不用mock冒充全链成功。

`sync_plugin_references.py --check`及CRLF感知diff检查通过；全库1347项执行通过、8跳过，跳过不算通过。独立验收待完成。guide、原result/manifest/raw与旧review均未改；当前活跃Plan变新哈希，不追溯改旧证据，旧派发必须reconciliation/新run。

## 仍阻止整批完成

[独立链审查](independent-chain-audit.md)确认：安装说明之外，历史维护结果的共享登记覆盖不足（全扫描81错误，不等于81项均损坏）；portable完全done后tick不重验当前证据（managed另有复核，不能混淆）；多生产者查询漂移尚属待验证假设。

真实CLI草稿6857986字节，其中316份查询JSON共5111736字节、error列表完全相同。只是序列化/重复量测量，未证明全部进入模型、token或请求提速；不能直接删门禁。后续需验证审核者实际加载链和与因果产物相关的失效规则。

本批正文阅读由[前段两篇](../concise98/research.md)+[新四篇A](research-a.md)+[新四篇B](research-b.md)补齐10篇，版本/章节/实验/消融/局限与采用/拒绝均明确；未读附录图表另列，论文成绩不当成本库实测。

本会话可实际调用独立AI上下文，已经用于阅读/审查；这不等于仓库ManagedEngine的模型submit/poll、认证与tmux适配器已接通。代表性模型任务质量/总成本、Claude新会话加载、tmux断链与跨机器恢复仍未验；未验不能当通过。SYSTEM-99继续同一批次，不以本阶段提交计完成轮次。

## 最新main整合（独立补验通过）

发布前fetch发现8587b781新增记忆目录功能与MEM-INDEX-96。本批已在其上rebase；TASK冲突人工保留双方条目，新MEM行只补同类空格，总17处。逆投影精确等于8587b原字节加17空格，782个CR不变；快照317项。其余并发源码/结果/测试原样保留，未采用其不同Python环境的旧全库数字代替本机回归。Version3和新run重测，以下不把初始316项草稿冒充最新317项结果。

最新本机全库：`Ran 1366 tests in 102.461s; OK (skipped=8)`，即1358执行通过；Reader3项1.585s通过。真实新run CLI317项草稿生成；初始独立验收在[independent-stage-ab](independent-stage-ab.md)，最新版本补验在同文件追加。均只接受阶段检查点，不接受整批完成。

恢复后已读取317项集成独立回执：独立专项116项、Reader3项和镜像同步通过；当前草稿仍明确拒绝缺human guide审核。范围限本地CPU与阶段A/B，不代表真实宿主验收。暂停记录保留为历史；最新用户指令已恢复同一SYSTEM-99，发布前再次fetch核对远端8587b781未变。
