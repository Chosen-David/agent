# 按任务明确排除技能目录条目

角色调度中，一个固定、范围完整的短子任务可由可信宿主显式排除无关技能的目录条目。必需角色及其依赖、用户明确指定的技能、项目规则和权限先核实；任务仍需发现新能力、需求不完整或配置无法解析时保留宿主默认。目录的 enabled 状态不是任务授权，也不证明角色已执行。

完整 checkout 的入口：

```powershell
python C:/Users/WI/Desktop/home_work/AI_LLM/agent/scripts/codex_skill_scope.py --root ABSOLUTE_PROJECT_ROOT --request host-skill-request.json
```

命令的位置属于 WORKFLOW_ROOT，`--root` 始终是当前 PROJECT_ROOT。request 位于当前项目，字段如下；示意路径须换成宿主实际发现的绝对路径：

```json
{
  "project_root": "ABSOLUTE_PROJECT_ROOT",
  "contract": {
    "schema_version": "codex-skill-scope/v1",
    "requirements_complete": true,
    "required_skill_paths": ["/actual/required/SKILL.md"],
    "excluded_skill_paths": ["/actual/unrelated/SKILL.md"]
  },
  "catalog": {
    "cwd": "ABSOLUTE_PROJECT_ROOT",
    "skills": [{"path": "/actual/required/SKILL.md", "enabled": true, "scope": "user"}, {"path": "/actual/unrelated/SKILL.md", "enabled": true, "scope": "user"}],
    "errors": []
  },
  "current_skills_config": []
}
```

宿主通过原生 `skills/list` 对当前 cwd 重新发现，独立解析所有生效配置层的现有 `skills.config` 数组，不把接口未返回的字段自动当空。请求不是由工人自行推测或改写的权限文件。本轮原生 config/read 的项目、用户、系统层都无技能覆盖，因此实际数组是空；有现有设置时原样保留，只有明确排除项可改为 false。不支持或歧义的现有条目拒绝缩窄。当前入口支持真实非符号链接的绝对 SKILL.md 文件路径；不会静默删除其他形式的设置。

输出 `config_overrides` 是给新线程 `thread/start.config` 的机器配置，宿主与其他已批准覆盖合并后直接传入；不要把整个配置或发现目录再作为模型消息发送。脚本不写全局配置、不重启宿主、不改运行中上下文或模型权重。只排除明确列出的 enabled user/repo 技能，system/admin、必需、未列出和未知技能保留。没有可排除项或 requirements_complete=false 时返回默认；无效、缺失、重复或已关闭的必需技能停止该 profile。当前功能仍需宿主显式调用，安装不意味着自动生效。

派发前绑定源码、技能文件、配置、request、profile、输入和输出 schema；任务/项目/证据/能力需求变化后重新判定，不能沿用上一任务的关闭列表。工具目录独立管理：技能排除不是工具权限或目录控制；本轮共同的 no-external profile 仅因短测试无需外部工具。实际调用需要的工具不能因省 token 被关掉。

官方 [Build skills](https://learn.chatgpt.com/docs/build-skills) 和 [App Server](https://learn.chatgpt.com/docs/app-server) 的实际阅读限路径启停、发现及调用段落。文档不提供本库节省数字。本机原生发现23项，而实际模型输入目录36项，故不能把发现列表当全部目录。`check_skill_catalog_delta` 仅接受实际 Available skills 区段内完整行删除；独立宿主另外把根别名解析到固定排除路径、确认必需角色实际可见，并逐字核对其余所有消息和可见外部工具目录。引用、行内子串、目录外条目及权限变化不会通过。

一次真实 Codex0.160.1/gpt-6.1-sol/high 同 server、两个新只读线程的相同短取消任务：总 input+output 从19,333到18,406，减少927（约4.8%）；input19,253到18,326，output均80，缓存和 reasoning均0。两次取消状态、输入版本、停止行动和三个完整 blocker 相同；实际只删除11个声明目录行，五个必需角色保留，其他实际文本/外部工具目录一致。独立宿主重放真实 CLI、原始账单、付费前清单与dispatch哈希、目录差异及5项边界测试，接受 usable-with-scope，见 [结果](../../agent_doc/results/token-007-skills-20261010/)。

这对短测支出37,739 tokens；开发、研究、本会话及静态审查用量未计入该数字。一次样本不证明长文/多轮质量、全部调度成本或现金节省；必须在自己的宿主和任务链上验证实际目录、总用量及任务质量。门槛是两次调用、零重试、每次90秒、首个总量<=25,000、整对<=50,000；它们不是服务端输出硬上限。
