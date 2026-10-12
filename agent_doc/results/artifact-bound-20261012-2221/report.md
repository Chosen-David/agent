# 文本比较的序列化大小下界剪枝

2026-10-12，基线 f8c92dc15bd948f0b50f748991cac782a913af0a。入口 `scripts/artifact_context.py` → `compare_artifacts`。原实现遇到重复多行删除仍会运行 `SequenceMatcher(autojunk=False)`，虽然很短的 splice 已不可能被 edits 表示击败。

本轮在现有生产函数原地加入保守下界：用相同 ref/base_sha256 构造假设单空 edit 的序列化长度。真实 edits 至少一条，非负整数至少一位、字符串至少两个引号，更多 edit 只增大长度。若当前 target <= 下界，任何合法 edits 都无法严格胜出，可以省去 matcher。假设 patch 不输出、不用于恢复。其余情况保留原唯一单行守卫和 matcher；自定义 token counter 保留全部候选。这里严格对应原有 JSON **字符长度** 指标，不称 UTF8 字节或token最优。

独立新上下文计划审核先于补丁；固定验收先于测量。生产1229案例×3模式=3687完整入口检查，packet与冻结基线完全一致且恢复成功。独立复跑同组3687检查；另写独立候选/恢复oracle，Unicode、CRLF、引号/转义169对×8flags×2metrics=2704检查，全过，并专门覆盖下界相等与counter偏好edits。独立oracle仍复用Python标准SequenceMatcher/JSON，不宣称独立diff算法。源码、配置、输入、环境和原始样本绑定见manifest及独立报告。

合成目标输入是2048条`x\n`删除两条重复行。warmup后7对交替顺序，计时包含文件读取、SHA、候选构造及选择序列化。生产中位数407.541182ms→0.627848ms；独立复测386.892123ms→0.592301ms（降低99.8469%）。不隐藏样本。该下界不适用时增加少量序列化开销，不证明所有输入更快。

42项artifact回归通过；全库1175项：1167通过、8跳过；reader另3通过。两次定向及初次全库的旧fixture失败保留，详见failure-history.md及失败日志。修改fixture不是放宽输出契约：短输入现在能剪枝，分别用长插入和custom counter继续核验必须匹配的回退路径。

检索已实际执行，189目录、partial=true、若干record缺失；手动读取相关旧报告。旧收益不移作本轮数据。历史十篇全文批次保留，本轮新增全文精读0；近期HDSO只作公平比较启发。官方Python说明matcher最坏二次复杂度：[difflib文档](https://docs.python.org/3/library/difflib.html)。本轮改进来自本库候选大小契约的严格剪枝，不将外部论文机制或数据冒称已复现。

独立验收usable-with-scope，详见independent-review.md。无模型质量、token、账单、GPU或完整Agent请求收益主张；没有安装模型后端、监督器或ManagedEngine宿主验收适配器。源码/测试与证据通过后普通发布main；发布SHA与远端回读以交付简报为准。
