# 代码 Agent 编译反馈升级 by GPT

日期：2026-10-08。Task: KERNEL-FEEDBACK-01。基线 main `9d0d05bfca88faf5c8fc57420bad4d5abf3b01a4`。

## 本次改动与证据

增加标准库只读 `compiler_feedback.py`，按函数/架构提取 PTXAS 寄存器、静态 shared memory、stack/spill 指标，保留原日志哈希和行号，缺项/冲突不填零。CLI 不执行编译、不写文件，不把解析通过或静态指标当编译/正确性/速度通过。

新增按需参考 `workflows/kernel_optimization_feedback.md` 并接入代码 Agent 与主控独立包。采用“定位关键路径→绑定源码/输入/编译配置→形成可证伪假设→少量实验→独立验收”的反馈流程。trick 按 CUDA/ISA/资源条件选择，复用现有 `gpu_adapter.py`、`measurement_review.py`，不叠加另一套 scheduler 或统计工具。外部来源、日期、采用/拒用原因在该参考中；未宣称某工具普遍最强。

发布检查还复现 main 的三个已完成 CONT 详情不符合现有 Plan/Task-ID/Date 格式。只修复结构元数据，独立逐字核对原内容保留，旧任务状态及历史派发不重激活。没有修改 SGLang、人类 guide、通用/旅行/科研角色职责或 marketplace 入口。

## 验证与失败保留

| 证据类别 | 实际结果与范围 |
| --- | --- |
| 程序测试 | 最终全仓 813 项：805 通过、8 环境相关跳过；Reader 3/3；新增解析器 11 项包含在全仓中；包同步与项目文档校验通过。原日志 `final/` |
| 独立检查 | 首次发现 2 项语义缺陷：异常数值被截断解析、陌生函数标题造成归属泄漏；原失败保留。修复后 9 个独立原案例、10 个补充解析检查及 3 个元数据保留检查通过；见 `review/` |
| 真实角色任务 | 独立模型从实际代码 Skill 入口读取合成诊断并调用脚本。拒绝 CUDA 12.4/-rdc=true/动态 smem 下直接开 shared-memory spilling，拒绝把 H100 当作支持 tcgen05；保留未知 helper 字段。输入不是实际 GPU 编译结果 |
| 跨角色交接 | 代码使用者返回实际工具 JSON/引用→独立审核→主 AI 核对。修复后明确重跑同一已见案例，JSON 一致；不称新增未见测试。见 `forward/` 与 `forward/revalidation/` |
| 公平 A/B | 未执行固定模型条件的旧新版质量/成本 A/B，结论 inconclusive；程序缺陷前后复验不冒充模型能力改善 |
| 外部集成 | 本地 CLI 和独立包路径核对；没有 CUDA/GPU/远端模型或持久 supervisor 部署；更新 GitHub 不等于所有宿主已安装 |

源码最终 parser SHA256：`c7c4fdc5655e2c2a8cdb81cb557579b0c445f599950ccc48e4d7e723dceb4bc9`。完整候选与输入绑定在 `final/candidate-inputs.json`、独立审查绑定及前向执行 lock；报告/进度收尾元数据不改变已测生产源码。

首次项目结果搜索返回 incomplete、无可复用命中：十个旧目录缺 record.json，原错误未隐藏。实际知识查询/正文读取了 `infra.flashattention4-blackwell` v1，拒绝把其 B200 attention 结果作为本次性能依据；完整 refs、语料 hash 与采用/拒用原因保留在 baseline/knowledge/forward 证据中。本次本地结果登记和实时独立验收分开，不从旧 pass 自动授权复用。独立 host 事件及精确审查哈希经主控核实后，现有 inspect_result 一次性门禁返回 usable-with-scope，证据 `host-acceptance.json`；未安装持久 verifier。登记时 pending 的原记录保持不变，后续复用仍须实时独立核验。

## 发布与接续

本报告是用户明确要求的有界代码 Agent 升级记录；不计原持续优化大批次完成、不重置其论文/实验进度、不累加收敛轮次。本次博客调研新增全文论文计数 0。原 HOST 未提交证据完整保存在 baseline.json 所列 stash，未混入本次改动。

发布使用最终内容树和预期 main SHA 的普通非强制更新，并回读 SHA/tree。CLI 缺少 GitHub 写凭据，采用已连接 GitHub 接口；具体远端交付以 publication.json 的实际读回为准。尚无该读回时不能称发布完成。

下一接续点：在用户实际 GPU 项目取得源码/配置、真实编译日志、独立正确性和隔离计时后，检验反馈能否改善具体 kernel；保留基线与负结果。没有这些条件时只交付可审阅设计，不报告极致性能或预测加速倍数。
