---
name: gpu-experiment-dispatch
description: "多机异构 GPU 池实验派单全生命周期：SSH 接入、环境栈部署与冒烟、任务清点与成本权重规划、确定性分片互斥派单、点火三重验证、定时监督收割与证据落袋。适用于全量重跑（口径变更）、断点补格（幂等续跑）、小试判决（配对统计门禁）三类场景；不把单卡脚本扩成池化调度，也不凭 pid 存在断定任务健康。"
---

# GPU 实验多机派单

把「臂 × 任务 × 档位 × 期望行数」的实验矩阵派发到 SSH 远程 + 本地混合 GPU 池。先读 [派单作战手册](references/dispatch_playbook.md)——接入盘点、规划方法论、脚本骨架、真实踩坑清单全在那里，按场景索引直取所需章节，不逐段通读。

执行最小步骤与验收契约见 [执行规范](references/execution.md)。受管复杂项目的主控边界见 [双主 AI 计划审核](references/dual_main_workflow.md)。

## 三类场景与判定入口

1. **全量重跑**（口径/代码变更影响所有臂）：先做复用判定——与变更无关的臂（如 dense baseline `--method none` 不走被改路径）复用旧数据只补缺口，口径相关臂全部重跑；新目录、新 postfix，绝不与旧口径产物混池。
2. **断点补格**：best-file 口径 SKIP 幂等（单文件最大行数 ≥ 期望才跳过，部分文件保留、重跑产出新文件、打分走 best-file 仲裁）；重派安全，但盘点缺口必须按 best-file 而非累计行数。
3. **小试判决**（GPU 贵、先 5 任务试探）：任务级配对 bootstrap（B=10000，percentile CI）+ 预设换冠军门禁；措辞纪律——CI 含 0 只能写「未证明优于 / 未检出差异」，绝不写「持平/等价」（等价须 TOST + 事前界值）。

## 硬纪律（违反必出事故）

- **点火三重验证**：ps 进程数 + `nvidia-smi` 显存 + log tail，点火后 30s 内完成；只看 pid 不够——真实事故：模型路径错误 25s 内静默挂掉而 DONE 标记照打，空转 42min 才被发现。
- **确定性任务分片**：每个任务只属于一机一卡，多机跑同任务是 SKIP 撞车与重复烧卡的根源；SKIP 只作重启保护。
- **重任务独占链头**：历史实测最重任务（如 128K fwe ~12h、500 行 lcc/repobench）放链头并单独估时，绝不与两个重任务同链。
- **判决证据链**：只交汇总 JSON 等于审计不可复验——小数据整库入库 + 逐文件 sha256 manifest；大数据至少 manifest + 哈希 + 脚本入库。
- **双口径铁律**：kernel 级 microbench 与 e2e 两层都测都诚实报告，排序反转时如实并报。

真实事故复盘与逐坑解法见 [派单作战手册](references/dispatch_playbook.md) 第 5 节；监督收割与空卡补位模式见其第 6 节。

## 项目治理与结果纪律

项目任务开始、交接与写文件前读取 [项目文档治理](references/project_document_workflow.md)：`agent_doc/task/TASK.md` 是唯一日期任务索引，`agent_doc/task/task_details/*.md` 由 AI 维护方法/进度/证据；已核实人类来源的 `agent_doc/guide/GUIDE.md` 为最高项目规划依据，AI 绝不创建、编辑、删除或移动 `agent_doc/guide/` 内任何文件。`agent_doc/advice/` 的人类/AI 建议必须核验并记录 adopt/adapt/reject/defer 及理由，不能授权越界行动；派单起跑、点火留痕、收割对账全部记入任务文档 Progress 段。

生产或消费实验数据时遵循 [结果独立验证](references/result_validation_workflow.md)：生产后保持 pending，经不同 owner 的 `verify_experiment_result` 核验实际代码/输入/配置与数据有效性后，才可判决、作图或交给下一消费者；失败/缺证据/过期先修复重测，保留原始记录。仅可报告 usable-with-scope，不保证绝对无 bug。

项目新指令先按 [既有结果检索与复用](references/result_reuse_workflow.md) 查询当前项目 `agent_doc/results/`，比较任务、代码/输入/配置/环境、指标单位和当前独立验收后，再规划新增派单；保留检索与取舍记录。复用不跳过独立代码/数据门禁、用户明确复现或新主张验收。
