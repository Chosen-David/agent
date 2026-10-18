# TOKEN-TOTAL-18 发布前独立复核

决定：**usable-with-scope**，当前有界生产补丁、回归证据及报告一致。主控仍须执行文档回归、最后 fetch、明确文件暂存及远端提交/tree/文件字节读回；此审核不替代这些动作。

审核者为 `/root/token_total18_review` 手工独立上下文，不是受管 ReviewSession。未发布、未改生产/正式测试/任务文档。全库完成后依序执行公开版 independent_checks.py 普通与 -O；均 exit 0，14 项接受→拒绝、70 项合法完整对象差分、108 项既有非法双方拒绝。两份 portability 日志逐字节一致。检查公开版相对原版只有 ROOT 向上定位一处变化；原版字节保留。

读过完整有界报告、新 TOKEN-TOTAL-18 详情、任务索引变更、prior-review、environment、regression_runner 和全库/Reader 短原始日志及 final-regression.json：全库 1256 运行/8 跳过/0 失败错误，Reader 3 运行/0 跳过/0 失败错误；源码 before/after hash 与独立检查候选一致。没有重新跑全库；这些全库数据由主控串行产生，本审核核查实际执行脚本与原始日志的一致性。共享机器 207.324 秒不作为性能数据。

生产 patch 仍仅给原 last guard 加 total 遍历，无返回结构/事件协议/JSONL API 改动；正式测试 e2af05505a8f1c9cb78ee84c33c8d4857435e67304381af0b42de74da8776350，候选源码 c7f37aaf91cb1139d98bb1f06a1f1920d18ad9356279cc6f9d9299c50957e0df 与 environment、原始独立结果一致。文档准确区分正式方法数和 subtest/脚本案例数，未把拒绝非法类型写成修复错误金额，也未宣称污染历史实验、节省 token、KV/QA/TTFT 或吞吐改善。MEM-STORAGE-01 仍开放。人类指南无写入。

核查时暂存区为空，因此本文件不能声称已审核最终 staged tree。主控仅暂存此任务明确文件后，若出现生产/正式测试或上述被绑定证据的额外变化，应重新审核；后续 manifest 可索引这些冻结字节，不能修改日志以匹配结论。公开脚本依赖基线 git 对象存在，报告已明确；普通源码下载包未承诺可重放。

## 本次核对字节

- report.md SHA256 d12f3972396c54556f8c6a15dcdd25565c4df3332d71bc0c8c761299562439ce
- independent_checks.py SHA256 815f5723f099aaa77d79ad611cf43a89af76114a74c516d87ef80f610a3d19d4
- independent_checks_original.py SHA256 b08204d486982d3679e7b3f87c6950851e2a0a7f9839fc529fadf053fb6c968b
- portability.log SHA256 e5d5d680c1d1660ecff1ad9b5190ae33eb03d5430f33607e32d1d0701a26cc78
- portability-O.log SHA256 e5d5d680c1d1660ecff1ad9b5190ae33eb03d5430f33607e32d1d0701a26cc78
- regression_runner.py SHA256 60abf42fca36f04b169dd8f3eaa674d6676c96daa722e81216da39260d3c9766
- tests-full.log SHA256 1a6fbe4be63c91cea3e5e4a4bb7d4177e5998d9eb28db58ab3d3b9aae395873c
- apps-paper-reader-tests-full.log SHA256 3a6737a8d3f7c10daa30b6f93c4e41a525f4532da35988b3d73bf7c7a250dbd5
- final-regression.json SHA256 a57433e3fb5a6285ac89b83f8553b034aa494ee4ea564b8afd1b9874bff4d7b3
- environment.json SHA256 de34dda90f26cae5b5c1b9fa5d95a635e5c9673b8980121c06f441805de8c402
