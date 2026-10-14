# 知识索引代码块边界修正

审查与生产基线：`2393d96ea17b9e8db4999ab8ea74c1ad23ae9dc8`。本轮是可维护的局部正确性修复，不称新Agent算法或模型/端到端性能提升。研究阅读继续；SkillDelta原始论文入口不可用未计精读，历史52项登记不充当本轮十篇精读。

## 问题与改动

`agent_runtime/knowledge_index.py:sections`原本只匹配fence前缀和长度。代码块内部的“``` info”被当作关闭符，导致后续代码标题进入索引、真实关闭符反而开启新块并隐藏正常标题；含backtick的非法backtick opener也被接受。Unicode空白尾部同样错误关闭。

依据[CommonMark0.31.2 §4.5](https://spec.commonmark.org/0.31.2/#fenced-code-blocks)（2024-01-28）：关闭符后只能有ASCII空格/tab，backtick起始info不能包含backtick。修正只约束已有fence分支，保持树/切片和调用接口。独立Skill脚本同步同字节；ENGINE_VERSION从v4到v5，使旧SQLite缓存拒绝查询并通过已有事务路径重建。首次重建有一次性索引成本，无提速主张。

## 预定指标与原始证据

固定16案例包含两类fence、info边界、长短/异字符关闭、NBSP、CRLF、EOF、未关闭、缩进与普通标题树。完整字典（node/title/level/parent/start/end/text）对照冻结oracle：baseline **11/16**，candidate普通和`-O`均 **16/16**；五类失配全部修正。原输入、输出和输入SHA256在`probe.py`及`raw-*.json`，原完整源码`baseline.py`保留。baseline只提取sections函数，未假称旧版本完整服务实测。

115条现有知识记录的完整sections输出均与baseline相等；这说明当前语料没有此次边界变化，不能证明任意Markdown正确。新增三个回归验证代码内info行、非法opening、ASCII/Unicode尾部和公共旧engine拒绝/重建。定向14项普通/-O通过；独立检查与完整测试结果见同目录记录。

全库`unittest discover -s tests -v`：1182项运行，1174通过、8跳过（61.860秒）；Reader 3项通过（1.569秒）。这两个耗时是回归执行时间，不是产品性能对比。

独立验收为usable-with-scope：额外20个holdout普通/-O均20/20，115/115语料完整输出与原版一致；独立加载完整历史`baseline.py`构建真实v4缓存，live查询拒绝后未改源重建，缓存移除CacheHiddenUnique标题并恢复CacheVisibleUnique，下一次构建no-op。该缓存验证使用完整历史模块，与主生产者sections-only探针分开。

独立首轮19/20源于审阅者oracle错误：连续额外backtick实际上组成合法更长关闭符，不能作为非法tail。纠正预期后复跑20/20，首轮失败原始输出保持不变；不是修复实现来迎合oracle。独立完整raw含重复公开语料，保留本地；交付compact证据保留所有边界输入/完整输出/缓存数据，逐条语料完整输出hash、比较结果以及原始文件hash，配套独立脚本可复现。没有将该首轮算作实现通过。

先查历史结果：230条扫描、partial=true、84errors，三项命中均非本parser/边界；未作为可复用实验。`prior-search.json`保存真实返回。无失败结果被删改，无模型/API/GPU测量；未测试检索质量模型指标或生产部署。

## 范围与取舍

不是完整Markdown解析器；HTML/container/嵌套blockquote/list解析仍不在本轮范围。现有语料内容、指南、旧实验均未修改。手动宿主独立核查不等于部署ReviewSession或后台监督器。发布前检查main并发变化；仅显式交付清单进入普通main提交，远端回读另行记录。
