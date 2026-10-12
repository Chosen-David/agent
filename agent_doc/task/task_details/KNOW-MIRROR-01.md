# [KNOW-MIRROR-01] 恢复可安装知识副本的一致性

Task-ID: KNOW-MIRROR-01
Date: 2026-10-12

## Plan

用户持续优化Agent授权下，仅用既有生成器同步两份知识metadata，源文件不变。baseline 5de55fb8。验收为完整知识树字节一致、独立安装CLI可用、23 knowledge + 1 sync及全库回归；独立验证之后才发布。无模型、token、性能收益主张。此前AEVAL阅读强调首次失败必须保留，因此原始失败日志不覆盖。

## Progress

- 基线1174测试有2个生成副本漂移失败；现有生成器只更新coverage.json、learning_state.json。23+1定向测试通过，独立验证和全库复测进行中。

- 全库1174项：1166通过、8跳过、零失败。独立238文件与7CLI通过。仅安装一致性。报告：agent_doc/results/knowledge-mirror-repair-20261012-1856/report.md。
