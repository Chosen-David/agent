# 按精确 Python 符号读取源码

回答一个已定位函数的问题时，可先读取它的完整声明与静态本地依赖，减少重复发送整文件。完整 checkout 提供只读入口：

```powershell
python WORKFLOW_ROOT/scripts/source_context.py --root ABSOLUTE_PROJECT_ROOT --request agent_doc/task/source-request.json
python WORKFLOW_ROOT/scripts/source_context.py --root ABSOLUTE_PROJECT_ROOT --request agent_doc/task/source-request.json --full
```

请求为 `{"schema_version":"source-context/v1","source":{"path":"module.py","sha256":"实际文件摘要"},"symbols":["target"]}`。符号由消费者明确选择，仅支持顶层 Python 函数/类；不从问题猜测目标、不执行源文件、不写目标项目。当前根目录、原始 SHA 与精确行范围随输出保留。`--full` 可重新读取同一绑定版本的完整文件；文件过期、符号缺失或完整输出超预算则拒绝，不截断。

保留所有非定义字节、注释、导入、全局语句及其引用，沿静态 Name 扩展本地声明依赖。整类、装饰器、注解、类型参数及无法证明无定义时效果的默认值声明保守保留。仅当完整 JSON 更短才使用 focused，且列出全部省略符号。识别出的动态命名空间访问、反射与星号导入回退全文；歧义或不支持的语法也保留全文。行号按 Python 的 LF/CRLF/CR 物理换行映射，Unicode 字符串分隔符不另算一行。输出是带出处的阅读切片，不能当可运行的改写程序。

focused 不证明跨模块/回调/插件或整体程序依赖已闭合，也不证明不存在其他动态分发。沿真实调用点继续查边，遇未解析路径、问题扩展或需要模块整体判断时显式读取全文及外部依赖。源码展示不会削弱项目指南、取消、权限或独立结果验收。

独立验收的 [本次短测](../../agent_doc/results/token-009-symbols-20261010/README.md) 使用本库实际 `codex_tool_scope.py`：整文件 versus `check_scoped_catalog` 的完整源声明，三种固定调用与真实 Python 函数 oracle。同模型/high/配置/权限/工具/问题/输出约束，其他原生可见指令逐字一致。输入19,018→18,662，输出68→67（包含推理23→22），总19,086→18,729，少357，约1.87%；两次共37,815 tokens，缓存0，未扣除缓存或复用旧账单。七项边界测试与独立门禁通过，仅 usable-with-scope。未测跨文件修复、长文、整个协作链或现金收益；服务最终内部提示词拼装不可见。

调研筛选于2026-10-10：[Agentless v2](https://arxiv.org/abs/2407.01489v2) 展示分阶段定位/修复/验证路线；[2026代码表示预印本](https://arxiv.org/abs/2607.11046v1) 的摘要报告不同代码表示的定位效果与表示体积取舍。它们只支持研究这个入口，不是本库的性能证据，表示体积也不是实际模型账单；本轮未声称完整阅读或复现实验。源码边界采用实际运行 Python3.12 与 [官方 AST 文档](https://docs.python.org/3.12/library/ast.html)。已有知识卡和语料检索结果未满足本次来源/代码/用量条件，未拿其结论代替新验证。
