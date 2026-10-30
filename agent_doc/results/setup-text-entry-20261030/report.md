# 安装目标文本：拒绝阻塞输入并保留换行语义

SETUP-TEXT-ENTRY-01，SYSTEM-99同批Plan60→61。`setup.py`复用既有`checked_target`和`regular_bytes`读取目标CLAUDE/受管文本；静态链接和非普通文件拒绝，UTF-8输入上限明确为16MiB。CRLF/CR仍按原`Path.read_text`规则归一化；安装比较与所有权指纹使用同次文本快照。检查入口收集错误为needs_setup，模型文件刷新保留完整预检再写。共享reader、清单schema、Skill/guide/唯一TASK及正常所有权策略不改；新六方法纳入现有五组CI，保留原macOS TMPDIR。

原版单次六方法中14拒绝断言失败：CLAUDE四CLI、受管安装、模型刷新共六次FIFO超时；两文本路径的check/doctor四次静态链接误接受；四次为新增16MiB上限合同，不能都称为旧bug。CRLF/CR生命周期控制通过，0error/skip。修后主控和独立各单次55方法（6+17+8+8+16）全通过，0failure/error/skip。原始日志、执行器、实际时间/环境/源码及前后哈希核对完整保留；两组方法数量不同，耗时只作资源记录，**没有速度、模型质量或费用提升结论**。

v1独审revise发现CI步骤意外转移TMPDIR、测试少算原卸载留下的换行；未执行即修为v2，原候选和完整反馈均保留，第二次方案approve后才单次baseline/fixed，独立另单次55。计划2/2、baseline/fixed/independent各1/1已消费，不重试旧门禁或抬预算。独立六域结果为usable-with-scope，手工审核不等于可信ReviewSession、真实部署或全项目无缺陷；历史登记unknown/contractNone。

新增上限会拒绝原先可读的超大文本。**卸载较后受管文件若无效UTF-8或超过上限，前面的受管文件可能已删除**；问题文件和所有权清单保留，须显式修复/恢复。此前无效编码已可导致这种部分失败；本次上限扩展此拒绝边界，不能声称全输入零修改或整个卸载回滚。敌意父目录替换、跨文件原子性、全部元数据、真实会话加载/多轮质量/全角色成本仍未验。普通换行/用户说明和旁文件字节保护仅在声明夹具内通过。

先查结果355scanned/partialtrue/25缺record错误；仅setup-json-entry元数据修复是相关前置，不复用为文本质量证据，其余词法命中与两条推测解码知识卡不适用。Python3.12官方io文档的通用换行规则提供语义依据（https://docs.python.org/3.12/library/io.html），非运行版本/性能证明。沿用同批既有文献的真实输入、配对质量与总成本区分，未部署新压缩策略。

CompactionBench的官方2026-10预印本已实际读至3/15页，固定PDF SHA与精确下一页/offset见reading-checkpoint.json；reading-partial.md记录实际方法开头和生产缓存统计限制，**不在代码独审范围、未完成全文/消融/独审、不新增篇数**。53篇不变。原aa4fa869五组CI通过；本次新源码CI及普通发布精确回读另核。SYSTEM99真实宿主/完整输入/最终质量/全费用/并发恢复等继续open；这是可恢复检查点，不计整轮完成。
