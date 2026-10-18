# TOKEN-TOTAL-18 独立结果复核

决定：usable-with-scope（此有界输入类型修复）；全库/Reader 与发布前复核仍由主控完成。

手工独立上下文 `/root/token_total18_review`，未构造受管 ReviewSession 或协议回执。生产源码和正式测试仅只读；独立脚本从 git show 91d7545 读取基线为独立模块，不恢复或修改工作树。主控等待此复核结束后再运行全库，未与 producer 并发。

实际运行：independent_checks.py 在普通及 -O 下均通过，每种模式 14 项修前被接受/修后拒绝（5 个等值浮点、9 个等值 bool）；70 项合法完整返回差分（35 个计数组合分别单 snapshot 与早期非法 total、最终合法的多 snapshot）；108 项既有非法输入修前修后均 ValueError（两桶每字段空值/字符串/集合/负数/非整数/非有限值/缺失及已有事件、累计历史、算术门禁）。这些数量是脚本案例，不是正式 unittest 方法数，也不是统计样本或模型任务成功率。

独立检查包括大整数 2**54、全零、零输出/全缓存/全 reasoning 边界；所有合法结果逐字段与手写期望对象和基线比较。早期 snapshot 仍只由最终 snapshot 决定，未借机扩大协议。NaN/Infinity 是 Python json 解析器的额外鲁棒性输入，并非声称 provider 发出合法 JSON 非有限数。

补丁符合 v1 计划：2 行 generator guard 同时校验 last/total 的 exact int 与非负，之后仍执行相等及原算术检查。既有 last 校验顺序保留；total 非法时错误文本可由 cumulative history 转为 noninteger，这是本次明确输入校验行为。未引入依赖或更改返回结构。

读过 producer 原始日志：baseline 14 个 unittest 方法运行、14 个 subtest 失败；修后 targeted 与 targeted-O 各 14 方法通过。此处不把子断言数混成方法数。正式日志非本审核者重新生成；独立复现另由上述脚本执行。

不存在已核实错误金额/历史数据污染证据；返回计数始终取合法 last。收益仅是非法 total 被严格拒绝，不能据此报告 token 节省、模型 KV/QA/TTFT 改进。开销未测。

## 冻结绑定

- baseline source SHA256 a2174b54938aa9a5048183bd36f0b54ca1efc9713dcce444365e5001d8069043
- candidate source SHA256 c7f37aaf91cb1139d98bb1f06a1f1920d18ad9356279cc6f9d9299c50957e0df
- independent_checks.py SHA256 b08204d486982d3679e7b3f87c6950851e2a0a7f9839fc529fadf053fb6c968b
- independent.log SHA256 e5d5d680c1d1660ecff1ad9b5190ae33eb03d5430f33607e32d1d0701a26cc78
- independent-O.log SHA256 e5d5d680c1d1660ecff1ad9b5190ae33eb03d5430f33607e32d1d0701a26cc78
- baseline.log SHA256 7e5523aac71c1505824c8a5c8677a8a19c3cd33f79e8580733491a8358c575f7
- targeted.log SHA256 aa4f0b895cc89c050ee5b1db8da4cc7b321a3754e641e53ddb45ba84602abd18
- targeted-O.log SHA256 0d3ffc8a0b5cf5382278925e5a1aefc9b7e3a696fbaa2d4cec4bf398e033eb25
