# 本轮研究与采用边界

2026-10-20。本轮新增核查一篇，不把旧十篇再算为新阅读：旧阅读位置为[研究A](../read-boundary56/research_a.md)、[研究B](../read-boundary56/research_b.md)，覆盖AgentChaos、ACON、AgentFold、AgentFly、Reflexion、MemGPT、Mem0、MemoryBank、A-Mem、MEM1；各篇精读范围与未覆盖附录以原记录为准。

## 新原始来源

[When Agent Evaluation Becomes Unreliable](https://arxiv.org/html/2610.16067v1)，Junjie Chen，v1日期2026-10-12。此次核查方法§3.2、结果§4.1–4.3与限制§6、结论；未运行作者代码，未完成PDF逐页视觉检查。论文将评测器本身作为被测软件，用状态不变性、重复调用及已知正负控制检测错误；结果明确区分缺陷类别覆盖与变体漏检，跨框架迁移要求可重建参考状态。**adapt**异常路径不变量与故障触发检查，**defer**移植作者评分器：本库没有该工具环境。论文得分不作为本库收益。

工程映射是主AI推导：本库显示回执负责保存校验观察；异常必须停止交付且释放自身资源。`write_validation_context` 的构造异常没有原始fd释放，不能从正常roundtrip通过推断此分支安全。测试核对实际open返回的fd及实际注入异常身份；保存失败文件，不把清理操作当作自动修复原始数据。

直接语言契约：[Python3.12 open/closefd](https://docs.python.org/3.12/library/functions.html#open)。closefd=False使包装流关闭不关闭底层fd，调用者仍须关闭。因此使用finally作为唯一原始fd释放点；保留写入、flush、fsync顺序。os.close自身失败或外部关闭/复用同一fd不属于本轮保证。

知识检索实际调用 `python -m agent_runtime.knowledge --root knowledge search 'file descriptor ownership closefd' --limit 3`，snapshot `767a8fd84623613078f4e645afa2eb671e00bf1c71186c669830d809df218d18`；返回推测解码、推测采样、CAR-LoRA词法命中，均不满足本地文件资源所有权问题，拒作依据，knowledge_refs=[]。不新增语义算法或依赖。
