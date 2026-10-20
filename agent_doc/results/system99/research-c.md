# SYSTEM-99 补充正文阅读 C：恢复与 fencing

2026-10-20 UTC；同一 SYSTEM-99，新增正文阅读1篇，不计新一轮。输入基线 `9ab9becde217b74c50464155ab675dee9f422a60`；只写本文件，未改旧报告、源码或TASK，未调用模型/GPU。

## 查重与固定来源

实际对 `agent_doc/results/ docs/ .agent-runs/` 执行 `rg -n -i 'chubby|burrows|conf/osdi/Burrows06|osdi06.*burrows'`，阅读前无命中；SYSTEM99已有 research-a/b 也包含在检查范围，不复用旧阅读计数。相关既有fencing材料只是本库契约，不算这篇已读。

Mike Burrows，[The Chubby Lock Service for Loosely-Coupled Distributed Systems](https://www.usenix.org/conference/osdi-06/chubby-lock-service-loosely-coupled-distributed-systems)，OSDI 2006，pp.335–350；稳定键 `conf/osdi/Burrows06`（无arXiv版本）。会议出版日期2006-11；[会议原始HTML](https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows_html/)署日期2006-09-06。实读版本是[作者主页链接的原PDF](https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf)，16页，SHA-256 `0747c84a49d32744a2744e2f2951b05fb7a0829ce44afb0b700833eb2bb3ecdd`。

取源失败保留：`https://research.google.com/archive/chubby-osdi06.pdf` 在网页工具返回500/重定向目标不可取；改从作者主页的Download取得上述官方存储PDF，没有用第三方摘要代替正文。

## 实读与证据

按pdf技能读取原PDF，分段覆盖正文§1–6（物理1–15页）：§2.1–2.12设计/API/缓存/会话/恢复/备份，§3扩展，§4.1–4.6运行观测、失败设计与经验，§5比较及§6总结。重点核§2.3–2.4、§2.7–2.9、§4.4；另实际看物理8页图2和11页运行统计。无附录；图1未视觉核验，参考文献所引原文、实现与原始运行日志未核，不能声称源码复现或全页视觉审读。

§2.4由接收方检查携带锁代次的sequencer，拒绝迟到旧请求；lock-delay只是较弱缓解。§2.8区分暂时不确定与永久失效句柄，§2.9恢复先换epoch、清缓存并等待确认，再放行。§4.4报告省略部分只读session登记会留下旧读窗口的负例。§4.1是10分钟工作负载快照和累计700 cell-days的61次停机观察，排除了整数据中心维护停机；没有组件消融/随机对照，也不证明本库性能或正确性。

## 对阶段D/E的取舍

- **D / adapt**：可发现的名称/内容校验信息不等于当前可执行权限。本库 `ResultStore.register_history` 已明确 `contract=None`、`unknown`；登记只补发现路径，继续拒绝把旧pass、内容哈希或新登记时间升级为独立验收。此信任边界来自本库契约，论文不提供“历史结果已可信”的证明。
- **E / adapt**：保留“旧身份失效→持久拒绝→明确恢复条件”的验收结构，检查审核恢复、重复wake和重启不会自动解除 `requires_reconciliation`；显式 `Engine.reconcile` 仍须当前审核、授权、依赖和证据，取消仍拒绝。建议以旧完成证据/计数不丢、handler不重放作负控；本角色未运行这些实现测试。
- **reject**：Chubby中可自行恢复的暂时jeopardy不等同已撤销审核，不能据此自动恢复done；论文也不证明外部副作用恰好一次或防恶意同权限写入。不采用其分布式锁服务、五副本或时间参数来重构当前单机SQLite/可信宿主边界。

已对照本库 `workflows/result_reuse_workflow.md`、`workflows/dual_main_workflow.md`、`agent_runtime/result_store.py::register_history` 与 `agent_runtime/core.py::_check_done/reconcile`。以上只支持阶段D/E现有边界的设计理由与测试取舍；作者运行数据不是本库收益，最终修复/独立验收仍归主控。
