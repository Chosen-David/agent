# 结果检索循环不变量候选

Agent main已fetch/ff到9c071f7c735eed861244951a150d456ffe27a4ef，现有未提交检查点保留；无生产改动。沿用已读取AGENTS/决策/结果复用/独立验收契约，guide不写。ResultStore先查result search exact context performance，scanned222/partialtrue；combined-corpus旧结果为知识检索质量/语料发布，不是当前完整ResultStore性能，拒绝复用。原返回保留prior-search.json。

来自现有入口的候选：ResultStore.search对每个已读取记录重复计算context是否字段完整、以及递归_unknown(context)。这些只依赖调用者context。候选仅在入口一次计算exact_eligible，循环内仍精确context==record.context；show/污染撤销/metadata/错误检查不删，不缓存记录/答案。前提是一次同步调用内输入context不被外部并发修改；原函数没有这种并发输入修改保证，也不能为subclass自定义副作用额外承诺。

先独立新上下文计划审读。通过后冻结原search源码，通过inspect提取并只替换这两个表达式构造隔离候选，尚不修改生产。实际项目完整search入口：大context combined-corpus-v4、math-inverse-update，中型comm-batch，以及None、空context、含unknown context作控制。固定query、limit3/max_scan250；每场景一次warmup+11对交替次序计时，比较整个返回JSON精确相等；记录完整错误及partial，不裁样本。先验门槛：大context中位延迟降低>=10%；None/小控制不超过10%退化（噪声不足标不确定）。只称当前CPU文件检索收益，不称模型token/任务质量/端到端收益。

独立结果审读/复跑后再决定生产小补丁。需覆盖known/unknown/incomplete/non-JSON/empty registry、污染撤销和现有result_store/contamination/全库回归；未执行不当通过。测试数据→独立核验→消费者，不声称这份手动计划部署了ReviewSession/ResultValidationHandler/tmux宿主。读过的近期恢复/证据论文已提醒匹配不授信，本轮不把经典循环不变量伪称论文新算法，不重计十篇精读；有界工程采用仍需要真正收益和非退化。
