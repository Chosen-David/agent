# TOK-002：任务需要哪些能力，再暴露哪些目录

研究入口：[Toollery，2026-09 预印本](https://arxiv.org/html/2609.22218v1)。已读方法3.3–3.4、BFCL表2/附录C、缓存实验B.2和限制6/D；未把该预印本称为已录用顶会论文。其方法先筛候选再给模型权威specification，实验显示大目录上的优势更明显；失败案例仍会漏互补能力。缓存实验还显示可见token大幅降低时，自然回放的账单成本优势并未确证，且预热调用不能当免费。因此本库分别记录总input+output、缓存与测试支出，不宣称同比例现金节省。

本轮只采用更窄的边界：宿主已经明确核实外部工具需求完整且为空时，使用零外部目录；需求不全或需要任何外部工具时保留默认。不训练新检索器、不按热门工具自动删能力，也不推断科研联网任务无需工具。外部工具需求契约不授予任何权限，不能覆盖GUIDE或宿主规则。

[Codex官方MCP配置](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) 提供服务器开关/allow list，并指出可选服务器初始目录受启动宽限影响。实际本机0.160.1零推理预检验证thread/start的配置覆盖：默认285连接器+4 Node工具，设置`features.apps=false`、`mcp_servers.node_repl.enabled=false`后目录为0；模型/high/只读sandbox和项目指令来源一致。推理前仍须检查未知自定义服务器是否暴露工具；有则拒绝此profile。

`scripts/codex_tool_scope.py` 从宿主显式选定、当前项目内的JSON契约输出配置；实际宿主将`config_overrides`传给新线程的`thread/start.config`。没有修改用户`config.toml`或让所有现有会话自动切换。对照使用完全相同的短问题和JSON schema，候选只改变声明的能力目录。只有总token下降、质量oracle及独立输入/权限/源码核验通过并发布main，才计本轮成功。

进一步定位上一轮失败A/B：不同的非任务developer消息是Skills目录，不能把此前“工具说明不同”的概括当作MCP连接变化的因果证明。它仍为无效对照，1680不计收益。上一轮受控成功比较所有实际非任务文本均相同，其98-token结论范围保持不变。
