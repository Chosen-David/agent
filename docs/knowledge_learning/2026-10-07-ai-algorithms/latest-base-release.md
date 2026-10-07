# AI算法两卡：最新主线发布验收

## 范围与冻结

本次以 `2e854cac85a6f69e3a15926173896fae74d8b7f6` 为主线基线，仅补入两条已审查的推测采样/解码知识及其证据、知识入口提示和插件派生文件。基线75条的150个元数据/正文文件逐字保留，新增四文件与 `final-candidate-freeze.json` 一致；总计77条，知识快照 `ac4174699799dde5a41ed05cae23b3469389ee6c4683731f04c6bb5ebb69b930`。数学游标、既有工程后续队列、RL/概率论/神经科学历史与每小时维护优先级均保留。本次没有runtime、SGLang、网页作图或旧取消批次改动。

`report.md`、`release-20261007.md`、旧evaluation与历史归档保留各自当时的39→41条语料和程序测试结果；这些是历史证据，不是本次77条语料的读回结果。来源、有限代数检查与新卡正文未因主线扩容改写。

## 最新验证与未通过项

- 全仓 unittest 548项：547通过，1项真实tmux集成opt-in跳过。Reader 3/3通过。日志 `latest-base-checks/tests-first.log`、`reader.log`。Matplotlib首次缓存目录警告保留；公开日志只规范化宿主路径，转换哈希见 `public-log-transformations.json`。
- 七套当前主线旧目录58个查询、files与SQLite两后端：逐查询比较召回、上下文、倒数排名和负例，共116对，新增两卡没有任何新退化；原有失败保留。完整结果见 `latest-base-checks/legacy-catalogs/comparison.json`，不可把“不新增退化”写成旧查询全部通过。
- 冻结12道开发题、两后端的原始默认上下文21/24，显式AI算法领域筛选23/24；原先较小语料分别22/24、24/24。该扩容差异如实保留，未更改问题、标准答案、卡片、运行时或原始8条/20,000字符预算。见 `latest-base-checks/default.json` 与 `domain.json`。这些不是未见测试或模型评测。
- 12组独立有理数/短序列检查全部通过；另一实现的225单步分布对、240确定性候选序列、9个停止序列联合坐标、1620成本网格均通过。有限枚举补充已审核推导，不是一般形式化证明；见 `math.json`、`independent-math.json`。
- 源/审查文件、四卡冻结、历史归档与插件闭包另做字节验证；所有来源仅原始摘要与定位，不打包第三方论文/代码或私有源。

## A12的有界补读与发布决定

SQLite领域检索的A12（生成停止/剩余预算）返回两条RL卡与残差正确性卡；成本卡被列为相关项，但完整依赖包超过当前上下文预算。扩大到5候选的诊断仍未解决，未将其作为成功结果。

沿实际已检索到的残差卡调用 `related`，返回明确的成本卡标题和引用；再用 `show` 读取该成本卡及其必需的残差卡，逐字对照并核验完整knowledge_refs。一次related、两次show得到11,538字符完整证据包，未超过20,000字符预算。命令、实际返回与核验见 `latest-base-checks/a12-related.json`、`a12-cost-show.json`、`a12-residual-show.json`、`a12-bounded-followup.json`。

本次接受该既有工作流的有界补读作为可用性依据；这不是自动路由、不修改原始21/24与23/24分数，也不声称默认检索已解决。新卡的数学前提与来源冻结、旧75→77目录无新增退化、完整补读和程序回归共同满足本次有限知识发布门槛。没有GPU运行、真实模型A/B、账单收益、无条件加速或目标宿主安装结论。

## 发布记录

最终发布采用最新主线parent/base tree、expected_sha和force=false，发布后独立读取远端SHA与完整树。本文及本地验收不单独证明已发布；最终实际commit/树读回记录另行追加。若main移动，先整合并重新运行受影响检查，不覆盖他人提交。

## 最终并发整合与测试夹具修复

发布前先整合 `7ad02cf49e1e3c4f4fa4874160d3c9e71f1278b8` 的神经科学候选，再整合 `907890831929a5d200d3fb64c6299449391a1ee8` 的收尾记录，保留全部既有76对卡片（75 published、1 candidate）及其来源、报告、历史和当前游标。最终语料共78条，其中77 published、1原有candidate；快照 `35d6a2001b51a55b5b73dee77a817e51ac04391114ca57f7abf9b93d1b41a85b`。并发文件不属于本次新增科学知识。

新增candidate暴露旧索引测试夹具将所有元数据数目当作已发布索引数目的问题。未修复的当前主线907基线10项索引测试出现4失败（75与76不等）；AI整合树全仓548项出现同4失败（77与78不等），原日志分别保留在 `concurrent-base-checks/baseline-index-before-fix.log` 和 `tests-before-fixture-fix.log`。只修复测试夹具：语料/ingest断言用total_count，索引断言用published_count，并加强为核对完整索引ID集合且排除candidate。运行时、知识卡、查询与gold未改；修复后索引10/10通过。全仓最终复跑结果见本节后的最终验收记录。

最终并发语料七套58查询双后端116对无新增退化；固定12题双后端仍为默认21/24、领域23/24，见 `concurrent-base-checks/`。原A12补读的两个卡片和引用不变，在最终语料重新核验完整依赖；原小语料指标保留，不混用快照。

本次仅发布文本/代码证据，未上传可选的1.3MB历史归档。完整归档与原始文件仍保留在既有检查点，历史归档SHA256与313成员清单保留。原报告的唯一活动归档下载链接被明确的“未上传”说明替代；原始与发布副本哈希、变化范围见 `packaging-transformations.json`。原artifact-manifest记录的是历史完整包，不冒充当前减量发布清单。四卡、source-lock/source-review、冻结题/gold、已有首次失败与结果的字节/数值均保留。没有将归档未上传声称为源检查完成之外的新证明。

最终验收：907整合及测试夹具修复后的全仓548项为547通过/1项真实tmux opt-in跳过，Reader3/3；插件派生检查通过。日志 `concurrent-base-checks/tests-final.log`、`reader-final.log`、`index-after-fix.log`，独立907身份/范围检查18/18，旧条目与并发文件保持。最终A12引用与完整正文在新快照重新核验，见 `concurrent-base-checks/a12-bounded-followup.json`。仍未进行GPU/模型A/B或目标宿主安装。

## 最后一次并发主线读回

CAS前再次读回主线 `e5db0479ed4f814e85a81670bb1fffc34ee9544f`，合入fd9012c/e5的两栖类candidate及收尾记录，全部77对既有卡片和最新状态保留。最终79条=77 published+2原有candidate，快照 `c3a35809513ae49e4a3858f9489f95d682852ebd64574f03e5a181bb122fbaca`；科学卡与runtime未变。全仓再跑548项547通过/1跳过，Reader3/3；旧58查询双后端116对无新增退化，固定题逐行结果与上次一致，默认21/24、领域23/24。A12完整引用再次校验。简洁逐题指标、原始最新日志/结果哈希见 `final-base-checks/validation.json`，未重复发布大型结果副本。原907报告及其数据继续作为历史基线。
