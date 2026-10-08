# Freedman 科学复用、引用与打包独立验收

Reviewer: `/root/knowledge_result`
Stable task: `EK-20261008-0915`；本轮 `knowledge-freedman-20261008T1215Z`。

结论：**science reuse usable-with-scope；当前正式卡的refs/依赖边界/package可用。** 整体发布仍须本轮独立检索验收和最终最新HEAD整合门槛；本报告不代替 retrieval_unseen 或 final reviewer 的职责。

## 冻结范围与旧证据复用

先读本轮 plan、run_checks.py、compare.py、当前TASK详情和旧归档卡，再核对实际代码、数据与哈希。09:15目录全程只读；本代理只写新目录 integration_verify.py、integration_results.json、integration_review.md。旧数学枚举没有重跑或冒称新实验，新一轮未见检索由另一真实宿主代理负责。原始两次检索失败、工具接线错误、并发退化和最终禁止发布的历史没有改写。

本轮卡正文SHA-256为 `014a071af03dc39f71ff874cff3e126d5193463660dc0c59f37f2a59637bda1e`，与旧归档已科学验收正文逐字节相同。逐层比较新旧JSON，差异只有 `status` 与 `verification.checks`。定理、适用前提、单侧上界、确定方差预算、根反演、超鞅证明、停止联合事件、三拒用反例、单位、来源、别名和关系均未修改。

旧五轮实际执行源码的哈希、候选历史五版本十文件的实际哈希均重新核对通过；相同正文已有独立证明审读和条件依赖/违例/停止/单位/生产数据复算证据。因此支持复用既有 `usable-with-scope` 科学结论，而不是凭生产者pass标记批准。其有限CPU/非形式化证明边界原样保留。固定来源的09:15独立web核查继续适用；本轮未谎称新增来源阅读或取得原PDF字节哈希。

旧发布失败不因科学复用变为成功。原有10组测试如复用只属于已见回归；本轮仅实际重放两个旧中英文检索表达，其四个backend/query组合均命中新卡top3及完整context，且applicability仍为unchecked。

## 正式引用与依赖

实际从当前 KnowledgeStore 读取published卡并执行check_refs。新引用为：

`math.freedman-variance-budget` v1，`1fa401c6307800e52301c08f3a4528f5c0587d30c0a712c1d74512b807e65e8b`。

自身引用有效；改哈希、改版本和旧09:15正式引用均被拒绝。虽然数学不变，status/checks元数据会改变内容身份，旧引用不能直接搬来当当前ref。`requires=[]`产生只有自身的强依赖闭包；三条related指向betting、alpha-spending和vector variance知识，是导航，未被当作证明依赖。卡片自身的标量推导足以支撑这一边界。

## 打包与实际命令

已核对canonical与插件的卡JSON、完整正文逐字节相同；当前knowledge_index.py也与插件脚本逐字节相同。新证据路径全部存在后才完成链接门槛；初次检查因本审核文件尚未写出而处于pending，保留在integration_results.json历史，不伪称首次即完整。

独立读取实际run_checks.py与candidate-commands.json，并计算日志实际SHA与回执比对。validate、sync、sync-check、index、diff-check退出0；全测试852项，OK（1项真实tmux opt-in跳过），Reader3项OK。original、round2及context8补充、morphology的5个检索命令仍退出1，不把继承缺口重标为通过。context3与历史context8设置分别记录。

当前验收只证明卡片科学复用、正式refs/导航边界、镜像一致、既有表达重放及命令证据完整。引擎修复质量、168个历史/current逐query非退化、新未见查询及并发最新HEAD完整范围由其独立负责人汇合；没有模型性能、GPU或整体语义检索收益声明。

## 复现与恢复

当前命令：`PYTHONDONTWRITEBYTECODE=1 python agent_doc/results/knowledge-freedman-20261008T1215Z/integration_verify.py --phase candidate`。工具只读取正文、旧证据、当前知识/索引和真实命令日志，将结果写到本轮integration_results.json，并保留自身执行源码和输入哈希。若主控随后产生final阶段，可用 `--phase final` 绑定最终日志；实际文件/refs或latestHEAD改变后，应只重验受影响部分，不沿用旧快照宣称新全局通过。

旧neuro阻塞、原PDF字节不可得、非形式化科学证据、继承检索失败和真实tmux跳过仍须随最终报告披露。
