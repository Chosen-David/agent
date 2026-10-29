# CHECKPOINT-FD：已确认诊断，修复方案待审核恢复

SYSTEM-99 / 当前稳定Plan56 / 基线main d243266e9b9707ea6aac666e21a3ba8edb8e3a34。此记录不是已实施修复、性能或整轮完成。

## 实际发现

通用task_manifest.atomic_json在mkstemp取得原始FD之后，以默认closefd=True构造fdopen；注入构造入口OSError时尚未进入with，finally仅删除临时名。主控与独立执行各一次、均3方法、同一故障方法下既存/不存在两场景各1个FD关闭断言失败（合计2断言，不是2根因）；正常Unicode及NaN序列化失败两个控制通过，0error/skip。原始FD由清理前os.fstat直接观察为open，随后runner只关闭本方资源。临时名已删除，旧目标状态/字节未变，撤销注入后的同路径重试完整成功。因而本次是确定性构造故障路径的描述符所有权缺口，不是最终文件损坏或重试阻断。

实际argv、起止/解释器/平台、完整stdout/stderr与哈希分别见producer-*和independent-*；两次子进程exit1，均正常回收，失败原件不改判。执行源码为executed-source.txt的原字节；ROOT与原私有运行路径深度绑定，不能把公开txt就地执行或以它替代原执行身份。源码SHA027fb51e791230eb9379211f44bb3623e9594192b073649c22bd77062b038092；目标源码SHA69c4fe53bf09b101bdffda7e5a3d9a8b3a71ba40ddc25174402c2b7260979425。

## 修复进度与阻断

候选只把流改成closefd=False借用，并由创建者innerfinally关闭原FD后再guard/replace，保留原JSON/UTF8/物理换行/fsync/覆盖式原子更新和临时名清理。没有实施到生产，也没有运行修后测试。既有ResultStore的RESULT-FD-95仅提供模式，旧结果不作为本函数证据；validation_context最终记录修复也不是本函数验收。正式检索340项/25errors的限制保留，不说历史全覆盖。

[修复方案独审](repair-plan-review.md)为revise：v1持久测试EXPECTED固定LF，与保留的Windows文本模式CRLF输出不一致。生产修复本身未发现阻断，但整份方案不批准。主控已按建议保存平台换行oracle的v2提案（repair-tests-v2-proposed.txt、repair-proposal-v2.json），所有完整字节/JSON/FD/临时名/旧目标/去故障重试断言保留，无Windows skip；v2尚未审核/执行，不冒充已修或原生通过。repair-source-workflow.patch仅是未实施提案，基线/候选哈希均见方案；没有更改生产、测试发现范围、workflow或稳定Plan57。唯一TASK只追加本进度。

诊断plan1/producer1/independent1全部耗尽，修复plan1/1已用且revise；baseline重执行上限0，fixed/independent各0次。依照workflows/dual_main_workflow.md有界返修规则，不能换ID/换reviewer/静默增加额度来执行候选。后续须明确对齐新的审核/资源边界，并由有权限的可信宿主处理，保留旧失败、反馈、消耗和候选；本记录不提供自动恢复权限。其它独立已授权工作可继续，SYSTEM-99并非因此整批终止或完成。

## 可用范围

Linux6.18.55 x86_64/glibc2.39、CPython3.12.14，仅本机真实临时文件+指定构造入口注入，注入异常身份保持。未测真实发生率/线上FD耗尽、自然标准库异常覆盖、Windows/macOS、close/unlink失败、敌意父目录或FD替换/复用、目录断电、全事务、模型质量、实际输入或全角色费用。无延迟/吞吐或普遍性能提升结论，测试计时不作性能比较。

手工独立AI方案/结果审核不是可信ReviewSession回执、部署或运行时验收认证。历史登记unknown/contractNone只提供发现；不能自动复用为已验证新实验。42篇同批正文计数不变，本次无新增论文计数；真实宿主/完整输入/最终任务质量/总费用/并发恢复等原未决全部保留。此前d243的五组CI成功，只覆盖其原提交；不证明当前未实施候选。
