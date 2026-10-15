# MEM-STORAGE-REG

Task-ID: MEM-STORAGE-REG
Date: 2026-10-15

## Plan

MEM-STORAGE-01已发布实验的登记修正：保持旧8文件及manifest字节，用现有register_history建立只供发现的历史record，禁止伪造native/current验收。不改运行时、排序、模型或GPU配置。基线14cee3a，主AI独占任务/record/报告；独立上下文只核对登记、查询与拒用边界。

验收：固定两个具体查询能发现目标，宽泛查询负结果保留；contract=null、status unknown、当前独立验证前不授权reuse；artifact hash核对、明确复现/new_claim必rerun，既有ResultStore回归。旧12篇阅读作为已有依据，不计新阅读/算法/推理收益。

## Progress

- 真实搜索发现memory-storage目录缺record，目标无法解析；原子登记后两条具体查询首位，第三条宽泛查询仍不进前五。扫描200/partial=true；其余61项错误保持未知。
- 证据入口：[报告](../../results/memory-storage-20261015/registration-20261015/report.md)。模型KV与scope装配优化均未在本子项实现，持续任务保留。
- 已独立核对8项原始证据与Git基线相同，重复登记不可覆盖、隔离raw变更转stale/rerun、明确复现及新主张必重跑；现有21项ResultStore回归通过。发布前保留其他并发工作并核对最新main，只有此历史登记子项完成，不关闭整体持续任务。
