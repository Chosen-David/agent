# TOK-007：明确技能目录排除的短对照

实际源码/输入/配置和六域 plan 在付费前冻结。相同短 packet 和 schema，唯一预期改变是新线程的明确 skills.config 排除；共同 no-external profile 与所有项目/权限规则保留。源码原始清单、派发哈希、归档和 manifest 均可核对，不复用旧账单。

| 用量 | 默认目录 | 明确排除 |
|---|---:|---:|
| input | 19,253 | 18,326 |
| output | 80 | 80 |
| input+output | 19,333 | 18,406 |
| cached input / reasoning output | 0 / 0 | 0 / 0 |

本对支出37,739，减少927。两次 exact oracle 一致。`independent-allowed-diff.json` 记录实际11条完整目录行删除和其余消息/可见外部工具目录一致；必需角色实际保留。`acceptance.json` 和不可变登记 record 接受 usable-with-scope，仅这一个短合成任务。5个独立边界/真实CLI测试在 `independent-skill-scope.log`。

`producer.py` / `skills_fixture.py` / `host_verify.py` 是本轮实际执行代码，`code_snapshot/` 保留测量前字节。原生完整私密日志留在宿主 `.agent-runs/token-optimizer-20261009/`；公共 RPC 仅将 account/rateLimits/updated 内容换为原行 SHA，独立宿主已核对，所有 token/输出事件未变。完整控制文本由本机原始 rollout 验证，公共记录给哈希和明确差异；外部克隆不能凭哈希自行复验私密宿主环境。

原生发现23项与模型目录36项不同，不以发现证明全量。门槛只控制派发和验收，没有服务输出硬上限。没有重试、模型工具调用或旧数据 rebill；开发/研究/本会话/静态审查账单和现金成本未知。未证明长文、多轮、其他模型或全部通信成本降低。当前需宿主显式接入；后台小时阶段尚未开始。

main 发布需另附 publication.json。只有普通发布、远端ref/tree读回、本地全树一致和安装同步通过后，TOK-007才计为一次成功；本结果登记和记录补充不单独计数。
