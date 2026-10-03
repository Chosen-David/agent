# 主 AI 反思协议：配置与验证

日期：2026-10-03 UTC。基线：`86b7c5c3d064463c0ec4c4110a5754535f9d90df`。

## 实现与实际加载边界

- 根目录 `AGENTS.md` 引用反思协议，为遵循该入口的仓库执行器提供默认指导。其他聊天宿主仍需读取主调度 Prompt，不能声称克隆仓库就改变所有会话。
- 通用主调度、科研主调度及科研插件实际入口引用的包内调度均内嵌同一协议；单独复制 Prompt 仍保留门禁。只同步新增决策片段，不覆盖插件既有职责/路由差异。
- 单独调用旅行或其他专业 Skill 不保证经过主调度门禁；本次只覆盖通用/科研主 AI 入口，未改冻结中的旅行入口，也不把它描述为所有已安装插件的全局策略。
- 三条分支是行为协议：原方案可行就执行；重大替代先出提案等对齐；未知先验证/询问。没有新增自动审批服务，也不保证所有模型必定遵守。
- 旅行文件本次保持原样；[旅行接口评估](decisions/travel_workflow_sync.md) 是待对齐提案，不是已实现集成。

## 深度推理的真实控制面

仅在仓库 `.codex/config.toml` 顶层增加 `model_reasoning_effort = "high"`。选择 high 作为深度推理请求，避免假定每个模型支持 xhigh/max；即使 high 也需核对所选模型和客户端。没有强制模型名称，没有修改用户全局配置、权限、插件账户状态或 ChatGPT/Claude UI。

官方依据（2026-10-03 查阅）：

- [Codex configuration reference](https://developers.openai.com/codex/config-reference/)：`model_reasoning_effort` 的可用档位由模型/客户端决定。
- [Codex config basics](https://developers.openai.com/codex/config-basic/)：项目配置作用于对应项目，需满足可信条件；更高优先级配置可覆盖默认值。

运行前核对客户端版本、所选模型支持的档位、项目配置是否加载及有效设置；只在宿主有可验证回显时声称实际档位已生效。不支持时明确降级为审慎分析，不能编造参数。这里未调用付费模型验证效果，未修改或认可项目可信设置。

## 测试命令与范围

```bash
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
```

新增测试只检验：三入口片段一致且先于路由；决策、证据和授权边界条款保留；TOML 值/插件开关/无额外权限字段；新增文档链接；默认入口引用。TOML 解析测试需要 Python 3.11+，旧版本明确跳过该项。规范情境表用于审阅，不冒充模型实测。

既有阅读器测试是独立回归，不是旅行或反思行为的验证。远端提交和 CI 状态需在发布后另行核验；未配置 CI 不等于 CI 通过。

## 本次本地结果

在 Python 3.12.14 环境执行以上两条命令：根测试 7 项通过（5 项新增静态契约检查、2 项既有 PDF 生成器行为检查）；阅读器应用 3 项通过。`git diff --check` 通过。未执行真实模型推理、ChatGPT/Claude UI 切换、旅行端到端流程或 JourneyPilot 服务部署。已核对旅行工作流、技能、模板与原基线无改动。
