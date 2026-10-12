# ART-LOCAL-01 第二版独立验收

独立审查者 `/root/artifact_localized_verifier` 对冻结基线、候选源码、manifest 引用和真实公开入口进行了只读复核。结论：**PASS，usable-with-scope**。

候选源码 SHA-256 为 `fa5935472ad49c6a80ae88e6d2c19cd9675e89780323e6275cffa1b868ebb738`，冻结 manifest SHA-256 为 `e4c7a382df14070923e76a388d637be9beee5fd404184eae3dbafbb8a9605e16`；manifest 的 8 个引用文件全部存在且哈希匹配。

独立从 `71496c7b1f42b94616343683c7671b6a0e6e8a3b` 加载基线，使用 seed `190823` 检查 3,016 个案例、普通/计数两种模式共 6,032 次完整入口。候选与基线的最终 JSON packet 逐字节一致，独立 applicator 全部恢复目标 SHA。覆盖第一版失败索引、空输入、CRLF、Unicode、插入/删除/替换、重复行、2,048 行及 65,536 字符边界。

门禁调用也符合契约：满足唯一单行条件的 byte 模式不调用 matcher；同一输入加 token counter、两行变化、插入行可复用、删除行可复用时均保留 matcher。23 项 artifact 定向测试全部通过。

独立 7 对交替计时中位数为 `632.832658 ms → 1.809249 ms`，降低 `99.7141%`；冻结生产样本重算为 `612.883613 ms → 1.603235 ms`，降低 `99.7384%`，7 个样本均有限、非负并与 manifest 一致。

全库回归共 1,174 项，2 项失败、8 项跳过。两个失败分别是 knowledge bundle 和 plugin generated references 不同步；涉及路径相对冻结基线没有差异，不归因本候选。该事实不等于全库通过。

验收范围只支持 CPU byte-selection 下唯一局部单行插入、删除或替换；不支持 token-counter、模型质量、token/费用、GPU 或端到端加速结论。结构化复核观测见 `independent_summary.json`，冻结生产样本见 `measurement.json`。
