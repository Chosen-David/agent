# 同一案例的显式重跑

2026-10-08，KERNEL-FEEDBACK-01。父任务明确要求对修复后的当前解析器重复原案例；这是已见输入的回归核对，不是第二个未见案例，也不是独立 GPU 验证。

结论：新脚本在相同输入上退出 0，实际解析 JSON 与原产物完全相同，字段差异为空。**任务分析与下一步建议无需修订**；需要更新的只有脚本版本与本轮执行证据。原前向目录中 9 个顶层文件的执行前后哈希完全一致，未改原产物。被绑定的源码和输入在运行期间保持稳定。

| 绑定项 | SHA256 |
| --- | --- |
| 原解析器 | `3320d6b3e3c0cccba65fe14b2a33ec098c696bd69299ffcaac641650d3cadf38` |
| 当前实际执行解析器 | `c7c4fdc5655e2c2a8cdb81cb557579b0c445f599950ccc48e4d7e723dceb4bc9` |
| 同一合成输入 | `5c5bef39ca452c7ea6380cad6c57167fb175cb18bd74a47fbe4419467dfa0ef0` |
| 本轮命令 argv 的紧凑 JSON | `b3c6973dc86fb49234a387e9fc1efbbf6b34eceeb28cb58a36b3bcef967ad308` |
| 本轮原始 stdout | `de92718c859eee694fb5ee51c1077a935c28506efeadd1799b850183a68dd662` |

实际命令是 `tool-trace.json` 中的绝对 Python 路径加 `-B`、当前 Skill 的 `scripts/compiler_feedback.py` 绝对路径及原 `forward-input.log` 绝对路径，cwd 为项目根。`-B` 只禁止 Python 字节码写入。解析程序退出码不能当作编译器退出码。

本轮仍观察到：case_forward 为 sm_90、128 registers/thread、32768 bytes static shared、64 bytes stack frame、32 bytes spill stores 和 16 bytes spill loads。helper 的 stack/spill 为显式 0，架构、寄存器和 static shared 为 null。parse_status 仍为 partial，compile_success 仍为 null，performance_verdict 仍为 not_measured。没有把静态 spill 字节解释成动态流量，也没有推算 occupancy 或收益。

原报告的配置适用性判断保持：CUDA 12.4、-rdc=true、动态 shared memory 不满足直接启用 shared-memory spilling 的条件；tcgen05 不适用于给定 H100/sm_90 目标。依据仍是原报告已核对的官方文档与未变化的反馈参考，未把新脚本版本当成 GPU 能力变化，也未重新引用厂商性能示例。

下一步仍是收集并绑定真实源码、完整构建命令/工具链、单次日志与可信退出码，补齐工作负载、线程块和动态 smem 量，检查 spill 对应代码是否位于热点。后续 timeline/profiler、独立正确性和配对计时都需要未来 GPU 授权与实际输入；本轮没有执行。

证据：`compiler-feedback.stdout` 为原始工具 stdout，`compiler-feedback.json` 为其解析保存；`tool-trace.json` 保存实际命令、退出码、stdout/stderr 与命令/输出哈希；`input-lock.json` 对比旧/新依赖版本并记录原文件哈希；`comparison.json` 保存完整相等比较、原件保留检查和运行期间版本稳定性。`capture.py` 是本次重跑捕获程序。

没有发现本案例新增的可用性问题。本次仅说明既有案例在当前版本中保持相同行为，不能证明其他修复缺陷已关闭、解析器无 bug 或 Agent 能力提高。没有读取测试文件或根任务评分预期，没有修改生产、TASK、guide、原始前向产物或 Git 状态。验证状态继续为 pending independent review，交由主 AI 的独立 owner 验收；主 AI 串行维护唯一 TASK。
