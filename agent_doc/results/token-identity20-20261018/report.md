# TOKEN-IDENTITY-20：计量身份校验

日期：2026-10-18。基线：22053c039fe0a71a6cfb28a5ecbbb7d2449bed18。

## 问题与修复

`agent_runtime/token_usage.py:4` 与 `agent_runtime/turn_usage.py:2` 直接用传入身份与事件字段比较。
当请求身份与事件身份同为 None、空串或非字符串时，匹配可成立，完整合法计数会被当作可归属的成功测量。
缺失字段经 `.get()` 也会与 None 匹配。现在两个入口先要求非空 str，再读取事件。
不修剪/归一化不透明 ID；不调整计数、最终快照、缓存或累计统计规则。

真实调用路径已核对：`agent_doc/results/token-002-scope-20261009/producer.py:178`
从原生 thread/turn 返回值调用短测解析器；`token-r6-close-20261014/audit_trace.py:23`
用归档事件身份重新审计。修复不改冻结历史脚本或日志，也无证据证明历史账单已污染。

## 验证与边界

初版修前测试4项，26个非法身份子场景断言失败；保留 before.log。
最终测试补充提前拒绝、合法不透明身份、输入不变与错误匹配控制。
普通与 -O 的三个专项模块各21项通过。独立结果另见 independent-review.md。
完整回归及 Reader 的原始摘要分别见 full.log、reader.log。
独立结果：最终5项修前27个失败、修后5项通过，另62个边界检查通过；
两份真实历史轨迹×两个解析器共4个完整返回值对照一致。

复现：`python -m unittest tests.test_usage_identity tests.test_prompt_context tests.test_turn_usage -v`；
优化模式增加 `-O`；完整回归 `python -m unittest discover -s tests`；
Reader `python -m unittest discover -s apps/paper-reader/tests -v`。
独立 runner 是实际执行原件：执行时 HEAD 为上述基线，输出目录为 `.agent-runs/usage-identity20/`。
发布后重跑需将 runner 的 `git show HEAD:` 显式改为上述基线 SHA，并先创建该私有输出目录；
不得用发布后的 HEAD 冒充修前基线。原始初版日志与最终版日志分别保留，不能混算失败数。

仅 CPU/Python 遥测输入契约检查，不证明所有畸形事件容器都转换为 ValueError，
不证明服务端真实性，不产生新模型调用或账单观测。新增检查耗时未测速，无性能收益主张。
当前运行是独立人工审查和执行证据，不是 native result-validation/ReviewSession 认证回执。

## 既有结果与研究取舍

实际检索 `memory serialization invalid input`（limit3/max-scan250），扫描228目录，partial=true；
命中 token-fifty-05、token-ten-3、token-ten-4 等历史短测，且部分旧目录缺 record。
这些数据不覆盖身份域，不能作新修复验收；TOKEN-TOTAL-18 只覆盖累计计数类型，故另做身份回归。
既有12篇方法细读矩阵保留在 `../memory-storage-20261015/research.md`，本轮未冒称新读10篇。

本轮访问作者项目页 [How Do Coding Agents Spend Your Money?](https://longjubai.github.io/agent_token_consumption/)
（2026年4月预印本，2026-10-18访问）：研究按任务轨迹分析输入/输出与缓存成本，强调实测波动和自估成本偏差。
应用决定：计量必须能归属到具体轮次，不能以预测或无法归属的数字支持收益。
这是评估原则的应用，身份校验是常规可靠性修复，不是论文算法创新。
论文 HTML 抓取失败，未计作本轮论文全文细读；作者页面数据不作为本库性能证据。

## 最终回归

全库重跑1269项，8跳过（1261通过）；Reader3项通过；文档validate通过。
首次读取工具输出曾显示 `fatal library error, lookup self`，当时未见汇总，因此进行了详细模式重跑。
发布复核发现首次最终落盘日志也已完整通过1269项/8跳过，耗时110.625秒；
保留原始字节full-incomplete.log（文件名沿用观察时命名，不表示最终未完成）。
两次最终日志均通过；瞬时工具观察与最终落盘内容的差异根因未确认，不归因于实现。
详细模式重跑耗时118.456秒。
full.log是明确标注的末尾摘要及完整原始日志hash/字节数，非完整原始日志。
