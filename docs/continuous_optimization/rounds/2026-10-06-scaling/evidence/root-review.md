# 独立根执行者复核

2026-10-06。实际读源码diff及完整新测试，确认stream循环只在EOF停止、context关闭、midstream异常拒绝；Kahn只计已知不同前驱，未知依赖诊断仍由原循环给出，不能把未知节点当合法图扩展。固定消费者任务清单、状态、证据、路径与重复依赖门禁不变。

实际执行：

```
python -m unittest discover -s tests -v
python -m unittest discover -s apps/paper-reader/tests -v
git diff --check
git show cb3e133ded7f2c878b3eddb10a0e7876fe6cac2b:scripts/validate_handoff.py > /tmp/scaling-baseline-validator.py
python docs/continuous_optimization/rounds/2026-10-06-scaling/evidence/compare_decisions.py --baseline /tmp/scaling-baseline-validator.py --candidate scripts/validate_handoff.py --out /tmp/scaling-root-decisions.json
```

结果：360总计/352通过/8跳过，reader3通过，diff check无错误，差分count366/identical366。原始测试日志保存一次；根复跑差分JSON与既有raw decisions相同信息，不重复提交大文件。比较为排序后诊断列表（保留重复计数），不是仅比较success标签。Kahn替换只添加最后的cycle诊断，不引入具体cycle路径承诺。

基线/候选benchmark脚本/参数和rawruns已读，三重复、tracemalloc非RSS、图内存未测、顺序执行与负载未控制等边界保留；不将337倍局部链检查外推Agent整体性能。

关键论文证据复核：原ExpeL PDF p10实际view Table3及局限，网页原文方法/消融与同数值交叉核对；MemoryBank PDF p9 Table2实际view，并读§2原文，检索与回答分离。其余关键方法/成本/失败条件通过固定原文页面复核；精读上下文的完整笔记保留实际读/未读范围。没有独立复现论文模型。

候选冻结本地4ee5f7f2b1e189514c876b2290e368aff0899c7a。本文件只证明上述程序和阅读复核，全部角色模型任务及最终图/PDF由另外的真实执行证据验收，不用此文件替代。

## 根执行者实际产物复核

- PDF reader原4个物理页渲染全部实际view：p3错误普适RoPE断言、p4固定V/平移logit反例确有原文；未见虚构的乱码/重叠缺陷。
- 混合figure实际view最终figure.png：六节点五边、V绕过softmax；六行两scope30/10,60/45,60/30,100/100,120/60,180/225准确，单位ms/单replicate/未核验来源边界清楚。
- data-visualization实际view最终PDF渲染timing_results_pdf_render.png，两panel同0–250ms轴、全部值、medium tie和large regression正确；diagrams architecture.png六节点五边、无反馈/多余边，proposed/unimplemented标签明确。视觉可读性检查不证明美观提升，不是公平blinded before/after比较。
- code-organization首次grade实际读：rollback缺失fail；完整读freshretry的REORGANIZATION_PROPOSAL.md，包含备份preimage、正/反向精确路径、pre/posthash并发守卫、活动路径保护。验收只是获授权的文档提案，目标移动/回滚未执行、未验收。不以一句“有回滚”或通用Git reset通过。
- writer旧评分文字与新fixture矛盾（medium regression vs真实medium tie），根批准保留原manifest/产物为ungradable并另prepare修正评分事实、新上下文重执行。没有追溯修改为pass，不将控制器材料修复当模型恢复收益。
- 完整读corrected writer中文结果/英文摘要，small42/30降低28.57%、medium80/80持平、large120/150延迟上升25%及合成/统计边界准确。根独立sha256sum确认writer的analysis.json与coordinator真实输出均为 `28e87980607bc7a6194bfa03848e83ae98a76f6fe2fc921a1f0e27d05197e327`；聚合CSV实际cmp退出0。这是实际数据交接，不是将预制答案交给写作模型。
- Main一般任务发现冻结rubric错误举例B→user6，但条目也显式允许equivalent correct settlement。根实际读task与answer：付54/36/0，总90均分30；独立Python净额oracle运行C→user24/C→B6后net均30，两个收款者需至少两交易。按预先允许的正确分支通过，原错误例仍记录，未改manifest或追溯放宽条件。这与writer没有可满足正确分支的错误事实不同；CO-020将覆盖数值评分材料一致性。
- 根实际运行 `model-eval/restore.py --out /tmp/scaling-root-replay-20261006`，4run完整性无错误；base16/16、correctedwriter1/1、baseline1/1，历史writer0/1仍ungradable。结果存root-replay.json；这是记录重放，不是模型重跑。读取最终matrix/rawreports并对config/role_registry动态14ID与manifest.role集合实际断言覆盖。
- 旧新code-reading manifest该case输入/任务/entry完全一致，恢复后的两rubric该case criteria实际相等。整个rubric文件哈希不同是因为baseline catalog只有一个case，未将此误说成整文件相等。两版真实工具退出0；精确model/seed未知，模型AB不确定。
- 全部证据/文档形成后最终回归再次实际执行360tests/352pass/8skip（27.358秒），reader原3通过；保存最终日志一次，不把重放或重复检查增加到独立样本分母。
