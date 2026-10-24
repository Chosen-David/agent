# SUPERVISOR-TERMINAL-01

Task-ID: SUPERVISOR-TERMINAL-01
Date: 2026-10-24

## Plan

同未完成 SYSTEM-99。基线 `de0940e2`：真实 worker 子进程/SQLite 完成产物及报告后，实际 start 仅凭旧 final-report 文件即可返回 completed；产物改变、合法报告改变、明确取消均未重新验收。tmux 外部传输在此验收中模拟，不代表真实会话/SSH。

复用 worker 已有 ManagedEngine 完成证据复核及汇总，再使用当前可信验证器重建 report；仅新鲜 done/all_reportable 可返回 completed。取消优先，失败/活动状态保留旧报告并返回 blocked，不启动任务、不重试、不重置预算。终态判断须在新会话启动和旧文件清理之前执行，覆盖有/无现有会话。保留当前 monitor 读回字段；不承诺任意并发路径/跨存储原子性或实际模型任务质量。

固定验收：真实 worker/SQLite 的正常完成控制、产物和合法报告变化、取消与 crash-block 优先级、活动态标记；校验前后取消；科学结果可信验证器正常/缺失/拒绝。检查无新会话/派发、证据和尝试次数保留、拒绝时旧报告原字节保留。双版本相关回归、独立源码/结果及隔离负控后普通发布 main、回读。

## Progress

- 先查结果 `supervisor completed final report recovery`，扫描200、partial=true且有缺记录；前三候选为语料采用，与此次终态恢复不同，不复用通过标签。原始检索保留在私有 supervisor-terminal-prior-1357.json。
- 修前 probe 的 unchanged/artifact/report/cancelled 均返回 completed；report 的第二次基线使用合法 data 结构以隔离旧哈希问题。新增初版回归保留修前失败。原日志、probe、方案与独审见私有 supervisor-terminal-*1357*。
- 独立方案要求提前覆盖无会话路径、取消后的状态重读和验证器失败关闭，已纳入同一有限方案。修后 probe 对改变的产物/报告返回 blocked/failed，对取消返回 cancelled；正常控制仍 completed。
- 初版扩展夹具遇 Store.path 为字符串及 state_dir 误用项目根的保护拒绝；修正为 Path 和独立 resume 目录，未放宽生产守卫。旧错误日志保留，不当作产品回归。3.9旧解释器路径失效的 exit127 保留，恢复隔离 Python3.9.25 后，两版本相关各79项通过（各1项真实tmux opt-in skip），-O专项各7项通过，任务入口4项通过；独立结果复核另核。
- 这是恢复正确性检查点，不计新轮、性能、实际tmux/SSH或模型质量完成；原真实宿主/输入曝光/全部actor用量/任务质量及跨库边界继续open。本次无新增论文阅读，不重复计入同批既有26篇记录。

- 额外引用检查报告4处既有生成镜像漂移；核对 checker、工作流、普通镜像以及符号链接名称/实际共享目标均与 `de0940e2` 原字节一致，未自动同步或混入本提交。证据 supervisor-terminal-reference-*1357*；不宣称全库检查通过。终态回执只复核任务证据并携带 monitor 读回，不等于已停止全部监控/资源；该宿主清理验收继续属于 SYSTEM-99 未决。

- 独立结果接受 usable-with-scope：实际3.9.25/3.12.14各69项定向及-O专项各7项通过，任务入口4项通过；隔离恢复旧生产实现后两版本均17子场景失败/无错误。复核未重跑主控全部79项；只接受已测试的恢复证据/取消/验证器/会话分支，不外推真实tmux、模型或资源清理。报告与冻结哈希见 supervisor-terminal-review-1357.md/.log，普通发布回读另核。
