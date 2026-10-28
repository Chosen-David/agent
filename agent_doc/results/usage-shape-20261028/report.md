# USAGE-SHAPE-01：用量事件容器的受控拒绝

SYSTEM-99 Version54；基线3f3f9f6810574541718936352a4ee23ece73d737。只原地修复三个离线解析器的容器错误处理，不改用量口径，也不保留旧生产实现。

原逻辑在event/params/turn/item/usage等处直接访问对象或遍历items，错形JSON会泄漏AttributeError/TypeError；空字典items及被后续有效快照遮盖的坏外层tokenUsage亦曾被接受。共享私有对象/条目列表校验现于消费前拒绝；缺失必需计数不转零，合法零值、完整输出、身份/终态/no-tool/缓存与推理子集、fresh和current历史口径保留。只逐个校验较早快照的外层usage容器，last/total及计数仍按最终快照校验，不声称所有中间快照均深层有效。

| 固定四模块/四新方法 | 实际结果 |
| --- | --- |
| 修前 | 34方法；130失败子场景跨两新方法：112 AttributeError、6 TypeError受控类型不符，12错形接受；两新合法完整输出对照通过 |
| 修后 | 34通过，0error/skip；引用同步通过 |
| 独立 | 同测试/源码34通过，0error/skip；引用同步通过；实际源码/原始输出/哈希已复核 |

130是子场景数，不是独立根因数量或真实失败率；运行秒数仅过程记账，不是性能结果。初版合法输入不变断言比较了未被解析的对象，独审v1退回；运行基线前修正，v1原件/意见保留，v2最后审核通过。无token_probe、后端/模型、旧全库/PID/C20/role等耗尽门禁重跑。短探针现有受控错误出口只静态核对，未实际调用。

完整失败流以gzip无损保存：解压235247字节，SHA256为382fbe1526fdab7ad8be39206b9891b33c5f30edb19bf839775b12373267e2d3。archive-map逐项对应原路径与精确归档；空stdout/sync流是真实空文件，未删失败或尾部空白。capture.py.txt和v1测试.txt仅审计原件，不是可重开额度的运行入口。

本地证据接受usable-with-scope；独立审核不冒充native ReviewSession/provider认证，历史登记unknown、contract/proof为空。五组原生CI新增4方法及普通main发布/回读另核，未完成前保持pending。无实际token/费用/模型任务质量或性能收益主张；24篇精读不增加，SYSTEM-99及真实宿主/完整输入/全角色成本与其余重大未决继续open。
