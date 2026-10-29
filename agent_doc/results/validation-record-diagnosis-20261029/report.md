# 验收显示记录：流构造失败遗留最终文件并阻断相同请求恢复

SYSTEM-99 / Plan54 限域诊断检查点，未修生产。源码基线91da769569cc63c107d848bbb5738cc54c00095f。方案先独立批准，主控一次、独立一次均在各30秒/共享截止内执行冻结3方法；每次exit1，2失败断言跨1注入方法、2对照通过、0error/skip。独立结论usable-with-scope仅接受诊断证据，不把失败测试说成回归通过。

真实 `write_validation_context` 在最终 `validation-<SHA>.json` 上先O_EXCL创建，随后才构造写入流。注入os.fdopen抛OSError时，finally关闭FD却保留空文件；撤销注入后的相同请求进入已有文件字节比较，抛出 `ResultValidationError: existing context record changed; preserve and repair`。原始失败在producer.stderr/independent.stderr，观测在两个stdout。一个机制破坏两个恢复性质，不是两个独立bug。

只用固定shape有效的invalid状态RESULT、proof=None及TemporaryDirectory项目，未调用可信verifier/backend或真实用户结果。正常roundtrip/幂等及篡改记录拒绝且字节保留均通过。空文件不会通过记录SHA/恢复校验，本次没有证明坏记录获得验收或下游结果被错误授信；确定的是本异常点的可恢复性缺口。

## 固定输入与证据

plan-v1.md及plan-review.md保留事前验收/资源/范围；inputs.json固定实际环境、源hash、命令和预算，prior-search.json保留335目录partial=true/25errors及三候选，未以部分查询推断绝无旧先例。三个候选是advice/语料集成，与本边界不匹配，拒绝复用其经验结论。

executed-source.txt逐字节保存实际runner（SHA008ce3b9…a3c7d050f），不是新测试发现入口。实际执行位置为 `.agent-runs/validation-record-diagnosis-2059/diagnose.py`，其ROOT依该目录层级绑定项目；不要在当前results目录把txt直接改名运行。复制为证据不改变真实执行路径/hash，也不授权重跑已耗尽诊断。后续复现/修复验证须新的限域协议，保留本次失败与来源。

独立原始流从审核者完整返回逐字保存，并与其报告的两个SHA一致；independent-review.md为明确标记的结构化结论摘录，不冒充可信运行时回执。ResultStore历史登记维持unknown/null/context{}，不因手工审核自动授信。

## 后续修复边界

下一步需版本化方案：在完整写入并fsync私有同目录暂存文件后，采用不覆盖发布；相同完整记录仍幂等，已有不同字节/非普通路径仍拒绝且不破坏原件，不自动删除“坏的已有记录”。可以参考本库ResultStore._save已有tempfile+link模式，但本次不批准复制/重构或调用它代替不同schema的writer。

修复验收还须覆盖stream构造、写入/flush/fsync、发布错误、相同/不同竞争目标、FD/本方暂存清理及真实CLI显示/恢复，独立代码/数据复核和所声明平台原生CI。父目录恶意替换、断电持久化或不支持硬链接的平台需明确范围，不因本局部方案宣称完整安装/全并发原子性。当前仅注入构造异常，未测这些后续条件。

本次无生产修改、性能/真实故障发生率或模型质量结论，40篇同批阅读不增计。唯一TASK稳定Plan/guide原样，MemDerive及全部旧耗尽/暂停门禁不重置。真实宿主、完整输入、任务质量、全角色费用和并发恢复等仍未决；本诊断不是整轮完成，后续修复尚待实施。
