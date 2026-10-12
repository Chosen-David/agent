# 相同文本比较：去掉无输出差分计算

基线 bd65a2348e32d8a70af9e003cbc309064363dd9e，2026-10-12。

实际入口为 scripts/artifact_context.py → compare_artifacts。相等字符串不会产生任何edit，但原实现仍以autojunk=False在重复行上运行SequenceMatcher，再丢弃空edit集合。候选只在已读取并校验双方SHA后跳过相等文本的multi-edit计算，未用缓存提示替代文件读取，未改变token选择或完整输出。

7对交替完整入口测量（Python3.12.14/Linux x86_64，2048行同字节状态文本）：473.834342ms → 1.400838ms中位数，降低99.704%。72组payload、counter wire序列及restore等价，包括空、Unicode/CRLF、2048/2049行、65536/65537字符、相同/变化文本和flags。36项artifact测试通过。复现：`python agent_doc/results/artifact-equality-20261012/measure.py`；原始数据和源码hash见measurement.json。脚本从固定git基线加载旧实现，不保留另一份生产实现。

机制依据：[CPython difflib官方文档](https://docs.python.org/3/library/difflib.html)说明SequenceMatcher最坏二次复杂度；相等输入opcode只有equal，_edits返回None。近期[Agent Skills Can Be Harmful](https://arxiv.org/abs/2608.11888v1)（2026-08-12，先前已全文阅读）启发按实际额外步骤定位成本，本次将这一思路适配为消除已知零输出计算。不是该论文算法复现或新全文计数。先前精读ledger不重计。

对照候选：开启autojunk可能改变非相等文本的diff表示；移除multi-edit会损失已有codec；本次等值守卫保留接口和所有非相等路径。无需新增依赖或Skill。字符等值检查线性，替代相等重复行的二次匹配；实测收益仅此局部CPU工作负载，不声称provider token、账单、模型质量或整个Agent请求加速。独立验收见independent_review.md：480组组合等价检查，另一种相同重复行文本、reuse_identical=False，7对中位458.304713ms → 1.078548ms，降低99.7647%。未测试GPU，任务不使用GPU。

全库回归原始输出regression.log：1153项，2失败、8跳过，其他通过；两失败均为最新main原有知识metadata与plugin生成副本不一致。源码/生成副本在本轮改动前均与origin/main逐字节相同。用既有sync_plugin_references工具仅同步coverage.json、learning_state.json；sync-retest.log中23项knowledge+1项sync均通过，reader.log中3项通过。未重跑整套1153项，不称全量绿；修复验证只覆盖原失败依赖。同步修复不另计性能收益。

提交前整合并发main edab6b496e4f26be4e70ed3d3eeacd8288e44a29，其已包含相同metadata同步及用户要求的in-place规范；本轮去掉重复同步diff、保留该提交与最新TASK条目。artifact源码和影响路径未变，重新执行36项artifact+同步检查通过（integrated-tests.log）。本次发布仅原地helper补丁、回归测试、独立证据和任务状态，不新增生产实现副本。

先查结果：prior-search.json lexical hits含token-fifty-05等，协议/目标不同，不复用其验收或计数；搜索错误/partial原样保留。knowledge-search.json的向量等命中不适用，未据相关度引入数学保证。未触碰两个已有未提交研究目录和人类guide。
