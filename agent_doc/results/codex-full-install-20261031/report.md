# 完整 Codex 目录安装及已安装知识工具：离线验收

源码固定 `f88df350429f97fc1868ebd7f1304eaac5a3ed05`，范围 CODEX-FULL-INSTALL-E2E-01。此前只用少量 Skill 的边界测试不能覆盖完整 registry；本次使用真实已提交目录，导出安装16角色/537文件，文件逐项与独立 Git blob 参考一致。源代码、测试、工作流与真实用户 home 均未修改。

唯一生产序列在 Linux 空 cwd 下执行隔离 Python `-I -B`：install、check-before、五个安装后 knowledge 工具操作、check-after、local-edit-block，共9阶段。五工具为文件检索、show、引用闭包检查、SQLite 索引构建、索引检索；其导入来自安装目录，未用源码 cwd/PYTHONPATH 回退。两检索返回同 corpus snapshot，show 的两项依赖闭包有效，115语料中110 published 条目被索引。8阶段退出0，刻意编辑已安装 SKILL.md 后检查预期退出1并保留编辑/manifest/global preference。最终夹具有536原文件与1个精确增加31bytes的文件，不能称为最终 pristine configured tree。文件数、字节数和执行耗时不代表 token 或性能收益。

[完整原始输入](result-inputs.json)、[完整独审反馈](result-review.json)与[逐字节公共副本映射](evidence-index.json)保留原版本和全部 stdout/stderr，包括空日志。[parent观察](parent-observation.json)单列外层退出0的宿主观察及后加 DB hash；它们不在原56项独审冻结输入中。完整 SQLite、537安装文件与全 corpus 未另复制到公开包，当前夹具私有保留；原独审仅证明其实际静态检查范围，远端包不能独立回放私有 DB。

方案v1因错误 CLI schema/工具计数和仅文字 deadline 被 revise，未执行；v2只修两项并保留原期限后 approve。两方案/runner/完整反馈均在 frozen，映射提供路径。独立结果审核 usable-with-scope，无阻断项：56引用全匹配，另独立重建Git清单、检查当前文件hash与只读SQLite。它验证静态可追溯性，不含第二次执行，独立重复性/解释器完整构建与环境等价仍unknown。producer应用层deadline守卫与超时清理不是硬实时/硬磁盘配额。

原期限05:47:37.545398Z；plan2/max2、producer1/max1、result-review1/max1、independent-execution0/max0均已按原合同使用。旧 Windows/FD/后端/StageI 等失败与耗尽门禁不重开。手工独审不是trusted runtime认证，历史登记unknown。

此结果补齐一次完整目录导出→安装→已安装CLI链的离线证据，不证明真实 Codex 根指令加载/Skill发现/模型遵守、终局任务质量/检索质量/数学真值、速度/token/全角色账单、并发恢复/完整事务或跨平台正确。f88文档CI仅三POSIX成功/两Windows失败摘要，未重新推断失败原因或宣称全绿。SYSTEM99实际宿主、完整输入、最终质量、全费用和并发恢复仍未决，本检查点不算完成一轮。

下一篇 [MUSE 阅读检查点](next-reading-checkpoint.json)只有2610.38332v1前6500/63045字符，未完整方法/实验/附录/独审，0新增精读。已完成上下文物理成本论文见[独立包](../physical-context-reading-20261031/report.md)，不将论文policy或作者收益归因本次安装验收。
