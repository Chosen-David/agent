# RESULT-FD-95 研究取舍（2026-10-20）

已有十篇定向/全文精读记录保留在 [A](../read-boundary56/research_a.md)、[B](../read-boundary56/research_b.md)，本轮重新阅读记录，不虚增为十篇新阅读。采用 AgentChaos 的触发核验和故障/正常对照原则；语义记忆压缩、训练和自主写回不满足本次资源所有权问题的前提，继续暂缓。

本轮新查 [When Agent Evaluation Becomes Unreliable](https://arxiv.org/html/2610.16067v1)，v1，2026-10-12；阅读§1、§3–6方法、数据与边界，未复现代码或视觉审读PDF。该文把评价器作为被测软件，分别检查状态不变量与已知答案；其变体级检测仍有遗漏，第二框架迁移也受可重建状态接口限制。这里采用“检查异常后实际状态，不只看返回值”的方法，不迁移其模型成绩或宣称新算法创新。

本库对应：捕获真实 open 的fd，调用结束后、测试清理前用fstat验证EBADF；不能仅因预期异常出现就判定无泄漏。正常登记和不可变记录对照同时检查，避免错误修复改变文件状态。独立验收使用另一套故障脚本。论文不是本补丁正确性的证明。

直接API依据：2026-10-20核查 [Python3.12 os.fdopen](https://docs.python.org/3.12/library/os.html#os.fdopen) 与 [open](https://docs.python.org/3.12/library/functions.html#open)。closefd=False让流借用现有fd，由创建者finally关闭；原有模块result_validation已使用该模式。本轮不新增依赖、不引入内存压缩或模型调用。

知识查询命中推测采样/成本/CAR-LoRA卡均不适用，不作知识采用。结果检索partial=true且存在未登记目录，不声称遍历全部历史；artifact-fd77仅作设计线索，其测量不复用到新代码。创新应用限于将故障后状态不变量落实到未覆盖的真实存储链路，收益仅按本机资源泄漏数验收，吞吐/模型质量未知。
