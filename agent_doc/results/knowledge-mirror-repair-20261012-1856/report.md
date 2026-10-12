# 独立Skill知识状态副本漂移修复

基线5de55fb800cfdbc0ad063a66bca1d24378ee676c，2026-10-12。仅用既有生成器更新model-with-knowledge/assets/knowledge/coverage.json和learning_state.json。缺失的MATH-94/95/96状态恢复为当前源文件原始字节；源知识、生成器、运行时未改。

基线1174项测试中2失败、8跳过；候选1166通过、8跳过、零失败。23knowledge+1sync定向检查通过。首次失败日志保留。独立verify_knowledge_mirror_1856确认238/238文件字节一致、7个隔离python -I CLI操作通过，新增历史仍为published_count=0、model_evaluation=false、unseen_tests=0。验收usable-with-scope，仅支持可安装知识副本一致性；无模型、科学、token、费用或性能收益主张。

研究复用：重读既有revision-handoff十篇机制笔记，不增加新精读计数；AEVAL v2（2026-07-21）首次失败与修复后结果分离作为证据整理原则。此为可靠性维护，不计论文算法创新/性能升级轮次。独立记录、原始回归与哈希附于同目录。

复现：python scripts/sync_plugin_references.py --check；python -m unittest discover -s tests。既有同步check可发现未来漂移，本次未新增防漂移机制。发布前fetch，发布后远端SHA和两份内容回读核对。
