# SETUP-LEGACY-TEXT-01：旧任务指针读取边界

安装器已有canonical任务索引时，检查根旧TASK.md仍无界read_text；超限文件被接受，is_file后被换成FIFO会阻塞，换成链接也被接受。仅把这一表达式改为既有_installed_text，不重写共享helper；拒绝16MiB以上与受控类型替换，保留合法UTF8/通用换行、缺canonical必须迁移及双活跃清单拒绝。原指针和canonical任务字节均保留。

| 冻结阶段 | 方法数与实际结果 |
| --- | --- |
| 修前原源码 | 7方法；3判别方法共5失败断言，4控制通过，0error/skip |
| 修后 | 38方法全部通过，0error/skip |
| 独立同命令 | 38方法全部通过，0error/skip；仅执行一次 |

[方案](plan.json)与[完整方案审核](plan-review.json)先于实际执行；[冻结结果输入](result-inputs.json)和[完整结果审核](result-review.json)接受的仅是本机Linux3.12.14限定范围。源/测试/工作流/Plan63均与冻结候选逐字节一致；[原始失败/修后/独立输出映射](evidence-index.json)完整保留，非摘要替代。空stdout/once文件是实际原件，不是占数文档。新类只借用现有fixture三方法，没有继承旧测试或重复执行。

独立调用途中报告容量错误，但落盘once/meta和38项日志证明原命令已经完成。主控纠正最初“未执行”的判断，续接同一未完成审核，只读原产物并完成原反馈，未重跑、改scope、换模型或重置额度；[中断记录](capacity-interruption.json)保留。实际独立角色2个（方案/结果），结果角色经历容量中断及原请求续接；全角色token/费用unknown，不把宿主审核当额外模型实验或可信runtime回执。

原生新增7方法安排在旧卸载步骤之前；本源码检查点的CI结果仍待发布后逐job核对。已有Windows卸载CRLF测试失败未修、未借新scope重置其额度；不能称全CI通过。源码CI此新scope最多2提交，第二次只可处理本scope原生失败。baseline/fixed/independent各1次已用，原共享deadline和所有旧冻结保持。

只证明所列临时CLI/API夹具：FIFO/link替换在is_file内注入，不是任意并发/父路径/读取后修改安全保证；POSIX本地runner不等于可移植CIrunner，不证明所有后代或关机恢复。未测峰值RSS、吞吐、模型质量、真实会话加载和全费用，命令耗时仅资源记账，7方法与38方法不作速度对比。未新增论文精读计数（历史58不变），本库SYSTEM99仍未完成，全部系统级未决保留。
