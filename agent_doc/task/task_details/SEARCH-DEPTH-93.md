# SEARCH-DEPTH-93

Date: 2026-10-20

## Plan

用户授权 Chosen-David/agent 可靠性优化、验证后直推main；主AI独占写入源码/测试/TASK，保留DISPLAY91未提交检查点，不改其他仓库和人类guide。基线d065a055cf29b10ed37717db197995283c1665d4。目标是隔离单条存储JSON的解码深度错误，使其不阻断正常候选检索；不改变读取预算、信任或复用验收。

v1广泛捕获每条处理中的RecursionError被独立reviewer否决；v2只在json.loads处转换成私有RecursionError子类，search只捕获此子类。直接show和其他_json调用仍属于RecursionError且保留消息/原始cause，但具体异常类改变；其他自定义异常及调用者context异常原样传播。不是通用资源耗尽防护。

[冻结验收协议](../../results/search93/validation-plan.json)：真实临时文件、10000层数组/对象、正常邻居/无命中/全坏/CLI、输入不变和异常边界。普通/-O专项、全库及Reader，独立代码/结果复核后发布。指标为确定性错误隔离通过数，不主张速度、模型质量或线上成功率。独立计划审查→修前失败→修复→独立verify_experiment_result→报告/发布，全部消费者绑定本范围与协议；无ManagedEngine adapter，不声称安装监督服务。

历史结果查询scanned199/partial，词法命中不适用本缺陷；知识库概率卡同样不适用。历史十篇正文阅读在read-boundary56/research_a.md与research_b.md，不冒充本轮十篇新读。Python3.12官方JSON文档核对解释器嵌套限制，实际触发以本机测试为准。

## Progress

初始2000层未触发本机C解码器限制，原测试假设失败保留在私有before.log，不作为缺陷证据。冻结10000层后，未改生产代码的7项回归出现2项API错误、2个CLI子用例失败（同一测试方法）；4项兼容控制通过。原始before-v2.log保留，修复和验收尚未完成。

v2已修复，专项普通/-O各94项通过，全库1338项（1330通过、8跳过），Reader3通过。独立普通/-O基线对照及异常来源边界验证已执行，最终报告/发布回读待主控确认。报告与原始独立证据在agent_doc/results/search93/；没有速度或模型收益声明。此前DISPLAY91继续未提交保留，不并入本次发布。

独立最终报告independent-review.md已确认usable-with-scope，固定源码3da82814e44acdc8ff8aa26e4b5d103825713d515c688e0ca06e63518cb02c1b和测试acb325d482318e579f2a369920dd9c6f942e7cd09781e416cfd08cf0f15a0e6b。主控复查无阻塞，当前验收通过；下一步仅本轮文件提交、再次fetch、main非强制发布及回读。更广的资源耗尽/模型质量/性能不在完成范围内。
