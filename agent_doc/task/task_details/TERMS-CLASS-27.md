# TERMS-CLASS-27: 查询词类裁剪

Task-ID: TERMS-CLASS-27
Date: 2026-10-19

## Plan

授权：用户持续优化 Agent、验证后直推 main；EXECUTE。基线 a5a13c2aea4165d0d3aebcd6c99ca0135a6efdbb。独立检出，无他人改动；人类 guide 不修改。

目标：保持 NFKC/casefold、ASCII 整词、CJK 单字/双字规则及完整检索 JSON，按查询是否含 ASCII/CJK 词跳过不可能贡献交集的词类。默认 `_terms` 行为不变，无缓存，不改变索引构建。两个检索入口及插件镜像同步。

先验：result_store 检索 tokenization 扫描232目录无命中，登记缺失导致 incomplete；不能认定历史不存在。读取 audit-26 的 TERMS-MAP-26 负结果（0.9716/0.9682 未达0.90，拒绝）；不重复 map 候选。已有12论文矩阵只作为历史研究；本候选是精确集合交集的工程化裁剪，不归因于论文。

DAG：独立计划审查 → 实现/差分 → 全调用配对计时 → 独立结果审查 → 达标则全库及 Reader 回归、记录、fetch/原子发布/回读；不达标则保存负结果、恢复生产代码。

验收：冻结真实 knowledge 语料；lexical/indexed × matrix/量纲/attention/zzqxnonexistent/attention量纲 × limit5/20 共20例；每例2对预热、11对AB/BA计时，perf_counter_ns 完整热库调用，建库/加载在外。全JSON精确相等；几何均值比≤0.90，每例≤max(基线×1.10,基线+0.2ms)。独立复测同门槛。随机Unicode及兼容字符边界验证投影交集；默认完整分词不变。内存同输入分开测，候选峰值≤max(基线×1.5,基线+256KiB)。不声明LLM质量、网络、端到端任务收益。

统计：每例取11次候选中位数/11次基线中位数，20例等权几何平均。历史证据实际位于 /workspace/scratch/5d3e4236a5b4/agent-audit-26/agent_doc/results/terms-map26-20261019/；不复用为本候选测速数据。

资源：本地CPU，串行测量；无宿主独占保证。实际 ReviewSession/tmux host adapter 缺失，不伪造回执；采用独立上下文人工审查推进授权有界工作。主控唯一文档写者，审查者只回传结论。

## Progress

- 新建干净 worktree；协作锁已取得。生产代码尚未修改。
- 独立计划审核修订统计口径/历史路径/TASK登记后approve；非native回执。
- 词类裁剪及镜像完成。主测/独立几何比0.707817/0.722415；20例及6内存门槛均通过。独立208完整输出差分、4000投影通过，usable-with-scope。全库1277（8跳过）、Reader3通过。
- 证据：../../results/terms-class27/。发布及远端回读由主控闭环；模型质量、冷库及真实任务收益未验证。
