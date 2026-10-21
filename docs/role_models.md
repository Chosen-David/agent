# 角色模型与默认回退

`setup.py` 为 Claude Code 安装模型偏好及路由快照；`scripts/run_role.py` 在独立调用前选择模型。无可用候选时使用宿主默认模型。无需配置新厂商即可继续原来的使用方式。

## 初始分工

2026-10-21 核对官方型号后制定的工程初值，未做本项目跨模型质量/成本对比。配置唯一来源是 [role_model_policy.json](../config/role_model_policy.json)，可调整候选顺序；不自动追逐新型号。

| 角色 | 首选 | 依据与边界 |
| --- | --- | --- |
| planner-main、review-main、research-assistant | Opus 5.5 | 复杂规划与整合；独立审核仍须新上下文和宿主认证 |
| research-write、research-review | Opus 5.5 | 论证、写作及证据审查 |
| research-implement-optimize、gpu-experiment-dispatch | GLM-5.3 | 编码和终端任务；不自动提供GPU |
| research-explore、model-with-knowledge、explain-research-concepts | DeepSeek V4 Pro | 推导和数学建模；带图片的解释须追加vision要求 |
| code-organization | DeepSeek Flash | 常规整理、结构化提取 |
| research-read-pdf、paper-reading-companion、code-reading、travel-planner | Kimi K3 | 长文、图文阅读及资料整合；旅行实时信息仍需工具 |
| research-figures、research-diagrams、research-data-visualization | Sonnet 5.5 | 图源代码与视觉反馈；输出需实际渲染核验 |

PDF/伴读/三类作图角色要求 tools + vision，其他默认要求 tools。任务有更高要求时，派发可加 `--require vision`。宿主必须声明相应输入和工具链可用，不能仅凭厂商模型页判断部署能力。

## 安装时配置

普通安装保持所有角色继承默认模型：

```bash
python3 agent/setup.py --target /absolute/project
```

可复制 [型号目录模板](../examples/role_model_inventory.json)，初始全部 `available:false`，只有宿主验证后才设为true并确认能力。确认当前 Claude 接口确实支持某个模型后，提供不含密钥的目录：

```json
{
  "schema_version": 1,
  "models": [
    {
      "provider": "anthropic",
      "model": "claude-opus-5-5",
      "available": true,
      "capabilities": ["tools", "vision"],
      "transport": "native"
    }
  ]
}
```

```bash
python3 agent/setup.py --target /absolute/project --model-inventory /private/host-models.json
python3 agent/setup.py --target /absolute/project --check
python3 agent/scripts/run_role.py --project /absolute/project --role research-write --dry-run
```

`native` 表示该精确型号已能经**当前同一个宿主接口及身份**调用，包括已配置的多厂商网关。不要把直连 DeepSeek API 的可用模型标为 Anthropic 直连会话的 native。不同供应商/endpoint 的切换使用下文的 adapter。

安装器将输入快照存入 `installation.json`，生成 `model-policy.json`、`model-routing.json`。只有 eligible native 路由写入子 Agent 的 `model:`，其余写 `inherit`。已有安装不传目录时保留上次目录；更新可用性需显式重新传入。重置为默认可传 `{"schema_version":1,"models":[]}`。

`--check` / `--uninstall` 不联网、不调用模型，不从环境变量猜测权限。安装报告中的 `host_declared` 是操作者/宿主声明；`live_model_tested:false` 明确没有在线验收。手改受管文件会按原有机制报冲突，卸载保留手改内容。目录无效则拒绝更新，不静默覆盖现有安装。

## 运行时派发

```bash
# 直接走当前Claude环境；任务文本从stdin传入
python3 agent/scripts/run_role.py --project /absolute/project --role research-write < /private/task.txt

# 跨厂商：明确指定宿主维护的可执行适配器
python3 agent/scripts/run_role.py --project /absolute/project --role research-implement-optimize \
  --adapter /trusted/agent-model-adapter < /private/task.txt
```

无 adapter 时使用已安装的 native 目录；也可用 `--inventory /private/current-models.json` 覆盖这次调用的目录。带 adapter 时先从它读取当前目录；读取失败、未知权限、缺能力、型号未列出或没有适配器时回退 native 默认。`--dry-run` 始终离线，只显示安装/显式文件快照，不执行适配器。

运行器动态建立 `model: inherit` 的角色定义，保留角色/Skill正文，避免回退时又加载安装文件中固定的旧型号；native选中才加 `--model`。两个主控加载各自已有prompt。当前CLI的新默认会话不等于另一个交互会话临时 `/model` 的选择；若须继承那个精确型号，宿主应显式提供其可用目录或自行实现派发回调。

**派发后不自动重跑。** 列表查询通过也不能保证余额、实时可用性或任务成功。模型调用拒绝、任务报错及超时原样返回，由宿主先核对已产生的作用再恢复，不能把可能已写文件的任务换模型重新执行。默认模型的能力也未由路由器验证；能力不足仍须报告任务阻塞，不能降低验收标准。

## 可信适配器接口

适配器是由部署者显式选择的可执行程序，直接执行（无shell展开）；不得从任务文本、模型输出、策略或安装目录自动选取执行路径。每次请求JSON从stdin输入，工作目录固定为目标项目。支持两个操作：

1. `{"schema_version":1,"operation":"inventory","project_root":"/absolute/project"}`：仅查询，不能执行任务。stdout返回上面的目录结构，外部模型标 `transport:"adapter"`。不接收任务正文；必须确认身份、接口、工具能力和授权预算后才声明 available。失败输出不写入路由报告。默认10秒、最多读取1MiB目录。
2. `operation:"run"`：接收 `schema_version`、`project_root`、`role`、`definition`（角色prompt）、`prompt`（任务正文）和 `route`（provider/model/transport/requires等）。运行真实Agent循环，stdout输出任务结果，退出码表示调用结果。路由器只调用一次；默认600秒，可用`--timeout`设置。适配器须自行管理其派生进程、取消、成本、检查点、权限及审计，不把LLM文本调用当成完整工具执行。

适配器只负责被选中的外部路由；default/native由原Claude CLI执行。Python宿主可直接调用 `agent_runtime.model_routing.dispatch(..., native=..., adapter=...)` 接入已有harness，handler异常不被捕获为重试。

认证由适配器/既有宿主自行管理；配置与报告不存API key，不改全局Claude设置，不增加permissionMode或绕过权限。`definition`不是所有权限/任务验收的序列化副本：适配器必须加载目标项目规则并保留原工具控制及独立审核约束。本库提供并测试协议，**没有随安装提供各厂商在线Agent后端**。可用模型目录/适配器缺失时默认回退仍可使用。

原生Claude `agent-*`调用读取安装快照；不会自动运行跨厂商适配器。需要运行时重新查询或跨厂商时，主控须使用上述runner或dispatch API。安装块已导航该入口。Codex/marketplace纯Skill安装不改模型；由其宿主使用同一policy/API显式接入。此功能不安装监督器，也不构成双主审核的可信认证回执。

## 官方来源及验证范围

- [Claude型号表](https://platform.claude.com/docs/en/models/overview)：`claude-opus-5-5`、`claude-sonnet-5-5`与通用能力定位。
- [Claude子Agent模型语义](https://code.claude.com/docs/en/sub-agents)、[CLI](https://code.claude.com/docs/en/cli-reference)：`model: inherit`、`--agents`、`--agent`、`--model`。
- [DeepSeek型号与能力](https://api-docs.deepseek.com/quick_start/pricing/)：`deepseek-v4-pro`、`deepseek-flash`；Pro不支持视觉。
- [Kimi K3](https://platform.kimi.ai/docs/guide/kimi-k3-quickstart)：`kimi-k3`、视觉及长文；[Claude接入](https://platform.kimi.ai/docs/guide/claude-code-kimi)明确settings环境字段优先于shell环境，故不自行用进程环境冒充可靠跨厂商路由。
- [GLM-5.3](https://docs.z.ai/guides/llm/glm-5.3)：`glm-5.3`及编码/Agent定位。

离线测试覆盖路由、回退、能力门槛、安装生命周期和真实子进程协议；fake executable不代表真实厂商调用。线上质量、价格、账号权限和模型间优劣需部署后以相同任务另测。
