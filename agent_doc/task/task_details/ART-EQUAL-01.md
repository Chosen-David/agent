# [ART-EQUAL-01] 相同文本比较的无损 CPU 快路径

Task-ID: ART-EQUAL-01
Date: 2026-10-12 Asia/Shanghai

## Plan

授权：持续优化 Agent，验收后直接推 main；当前仅普通本地 helper 优化，未启动受管服务器任务或模型实验。父执行者维护唯一索引与源码；独立上下文 artifact_equal_review 先审计划再复验源码/数据。未声称部署可信 ReviewSession、后台监督器或模型验收。

基线 bd65a2348e32d8a70af9e003cbc309064363dd9e。先查 result registry 与知识库；既有 token-fifty-05 是不同 token 选择任务，只复用接口契约，不挪用收益。向量检索知识命中不适用于字符 diff；采用实际源码等值不变量与 CPython difflib 文档。

目标：两个 SHA-bound 文本相同且 multi_edit 开启时不运行必然返回 None 的 SequenceMatcher。输出、候选集合、字符预算、token_counter 调用字节、完整 base、恢复和 stale 拒绝保持。仅原地修改既有文件，不保存第二份生产实现。

固定验收：至少20组完整payload/counter序列/restore等价；已有artifact回归通过；2048重复行输入7对完整入口 CPU 中位耗时减少至少50%；改变输入仍执行diff。计时包括双方读取/hash、codec选择和序列化，交替顺序，记录全部样本。CPU预算60秒，模型调用0。研究借鉴2608.11888已全文阅读记录的减少额外流程方向，算法为经典等值早退，不声称新算法或重新精读该文。已有10+论文阅读记录保留，不用本轮单篇凑数。

DAG：prior-search/read/plan-review → implement+paired CPU producer → independent code/data verifier → report/publication。全部原始结果只支持合成相同文本的 CPU 入口；模型质量、token、账单和完整任务收益未知。结果目录 agent_doc/results/artifact-equality-20261012。

## Progress

- 已原地加入 before!=after 守卫，保持双方SHA验证。
- 36项artifact测试通过；72组基线输出/counter调用/restore逐位一致。
- 7对公开入口测量：中位473.834342ms → 1.400838ms，降低99.704%；所有原始样本见measurement.json。
- 独立结果验收通过：480组组合等价和独立7对CPU复测，见independent_review.md。全库两项既有生成同步失败已用现有工具修复，23knowledge+1sync定向复验通过，reader3通过；原始失败日志保留。未将CPU局部收益计作模型token优化轮数。
- 提交前ff整合并发edab6b4（in-place规范与相同知识副本同步），去掉重复metadata修改；影响路径字节未变，36项artifact和sync检查复验通过。
- 远端发布/回读待完成，未触碰其他研究目录；后台监督/可信ReviewSession未启动。
