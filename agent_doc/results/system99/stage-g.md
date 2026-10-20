# SYSTEM-99 阶段G：更正到消费者的CPU恢复验收

基线main `d033c9f045b0211441abca2eb63b9c6b4e61cd4f`。按Version7独立方案审核
增加`tests/test_correction_chain.py`，SHA256
`70e2f4aac8bf28a9c0a3f422ae344a8ee406a132364b82dc7752588f62431ae6`。
生产runtime原实现通过该组合探针，本阶段增加回归与证据，没有新增生产修复。
没有改schema、目录组织或人类guide；仍由唯一SYSTEM-99维护任务。

## 已实际接通的有限链路

现有CPUHost测试认证→受保护Plan/Store→Mailbox发布→两个消费者prepare_context
与ACK→MemoryLedger更正→新可信tick复核完全done链→新身份与审核后的恢复。
实际SQLite/文件及公开runtime入口运行，合成观测是margin0.5。

- 初始最低要求0.4，writer/reviewer实际消费完整记忆前置依赖并分别判断通过。
- 将intention更正为0.8，使decision-v1失效。重新打开Engine/Store/Mailbox后，
  impact准确列writer/review及certificate/paper；三个相关旧节点blocked并需
  reconciliation，无关原始观测支线仍done，链不可最终报告。
- 原始观测、旧报告字节和原ACK保持；旧证据reconcile被拒绝，后续tick不重放。
- 显式取消旧run，新增decision-v2、run/event与新回执，再派发4节点后done。
  同一0.5观测在0.8要求下变为不通过；旧run仍cancelled，旧历史未覆写。

两份4节点计划各自实际派发，受管handler共8次；准备fixture还有额外本地写入，
不能把8次解释为全测试过程全部动作。共有2次CPU测试审核，无模型调用。
Handler.verify只核task身份；语义比较在消费者代码执行，不称独立科学结果gate。
本测试对显式memory_refs和可信测试adapter成立，不自动发现未声明依赖。

## 对照、独审与日志

事先查询`memory correction consumed handoff terminal recovery`，limit5/max_scan5000：
scanned252/partial=true/81缺record等错误，返回combined-corpus及comm-ack/batch；
旧语料/局部计账不支持本次跨模块恢复，故新增验证而非复用旧pass。
最初探针将kind写成intent（正确接口是intention），产生MemoryError；已修正测试
构造并保留私有first.log，不作为生产bug或修前失败。原实现组合通过是正面结果。

```text
python -m unittest tests.test_correction_chain -v
Ran 1 test in 1.565s; OK
python -O -m unittest tests.test_correction_chain -v
Ran 1 test in 1.980s; OK
```

只发现1个组合测试；fixture以模块别名引入，避免unittest额外发现整个BasisTests。
普通日志SHA256 `efa1b9523e76c380631f5c87074857d3c3a5a0ee86c8791f2029d6aac9695f14`；
优化模式日志 `1cd04984d0f25f8a0a5349df6764c76a18fbab5d5aa6c12d6580c631983b103e`。
独立角色另实跑普通/-O，并以临时内存替换终态检查、impact为空使新测试实际失败；
其审核和最终接受记录见[independent-stage-g.md](independent-stage-g.md)。全库
1392项中1384执行通过、8项跳过，103.161s；完整日志SHA256
`bb38da10e10196872ae510670c0396417c6fed78d9c5f037816251b3dcb509ad`。
Reader应用3项通过、同步检查退出0。独审核算完整日志并另跑组合测试，
接受usable-with-scope；未独立重跑全库，不将跳过项计为通过。

Python3.12.14/Linux6.18.55/x86_64/glibc2.39，标准库与既有临时corpus；无新增
依赖、付费服务、GPU或后台任务。实现Skill用于固定入口与恢复判据，未以耗时
作benchmark。没有模型质量、总token、速度或费用提升主张。

## 剩余验收

[MemTxn正文新阅读](research-e.md)支持分开观察写入、更正和恢复；其词序门禁/
时间覆盖与整库回滚不直接移植。同一未结束批次累计13篇，论文成绩不记本库收益。
本环境tmux/claude/codex均不在PATH；当前未接入能实际submit/poll/cancel、认证
独立模型和返回真实usage的可信host adapter。工具子agent可审查代码，不因此
自动成为repository runtime的部署后端。Claude全新会话加载、真实消费者质量、
跨会话上下文装配/总成本及SSH/tmux恢复仍待可调用后端；不能据CPU链通过认定
这些未知项无重大问题。历史登记覆盖、advice任务包的实际成本/质量比较也保持open。
