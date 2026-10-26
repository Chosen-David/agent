# CONTEXT-WIRE-01 v2：实际CLI输出边界

SYSTEM-99同批；基线80c4a368。仅五个已存在CLI：source/advice/grid/artifact/dispatch_context。
静态嫌疑：输出未固定UTF-8；内部对象/任务文本预算未包含最终JSON格式、父配置和平台换行。
先增加真实子进程回归并在原生产源码执行固定基线；确认失败后原地复用context_serialization。
成功stdout为完整UTF-8数据包；实际输出字符（含原生换行）恰好预算成功、少1字符拒绝，stdout为空、stderr JSON、exit2。
源码/引用/坐标/建议原文、取消/异议与依赖/派发method及父设置、旧数据错误协议保持；不执行派发。
source/artifact/dispatch已有数据错误exit1+stdout JSON保留，新增显示预算错误独立exit2；advice/grid错误统一exit2/stderr。
运行时API原payload预算/语义不改；CLI按原输入/解析硬上限构建，再按最终显示预算拒绝，不截断。
artifact的16MiB既有预算范围须保留：共享render_cli_context加显式、受16MiB上限限制的可选max_chars_limit；默认仍1MiB，其他消费者不放宽。
artifact有token_counter时按用户预算扣除原生换行筛选codec，避免先选不适配显示预算的表示；无模型名推断。
仅写五CLI、共享serializer、相应回归、SYSTEM-99稳定Plan版本/Progress和本结果目录。不改guide/权限/模型/账本/目录架构。
预算：本分支仅本地CPU临时文件，主控最多3次目标回归调用（每次<=120秒），独审最多1次相同冻结回归调用（<=120秒）。
命令：python -B -m unittest discover -s tests -p test_context_cli_wire.py -v（基线）；修后用同一文件及相关context/dispatch/source/grid/advice/artifact模块组成固定suite（见run_checks.py）。
先独立方案审核，基线/修后日志保留，独立代码/原始输出复核后方可发布。新测试判据来自stdout实际UTF-8解码与完整JSON/来源，而非重复内部长度公式。
这不是PID/ALIAS/role/Codex旧逻辑要求的替代阶段，不恢复/重试旧候选、不清账/延长其已耗尽预算；不跑旧fullsuite门禁。
不宣称性能、模型任务质量、原生Windows或整批完成；新CI仅继承已有安装范围，完整套件缺口显式保留。
文献关系：同批10篇仍保留；本次补读SWE-agent2405.15793v3 A.2实现边界（原先未精读），不另计一篇。其ACI动机只启发核对真实渲染与环境反馈，不是本库收益证据。

返修：保留plan-review.md全部意见和proposed-fixture-v1.py原件；新fixture加入五类独立原文/恢复/完整params oracle、拒绝路径只读、受控token_counter换行选择/全不适配、Popen fail-if-called及helper显式/默认上限。有限mock不证明未知宿主全部API零调用，需最终静态检查无RPC路径。
仅扩展生产范围agent_runtime/artifact_context.py两处comparison-budget失败为共享ContextBudgetError（仍ValueError子类，错误文字/预算语义不变），不靠异常字符串分类；其余API不改。主控suite外层subprocess.run(timeout=120)，超时保留失败且不自动重试。新方案冻结后方执行基线。
