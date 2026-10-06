# 推理、可靠反馈与验收：三篇新增精读

阅读日期：2026-10-06。按固定版本阅读原文，非当前模型排行榜；与全局 `papers.json` 去重，三篇均为新增。机器可合并元数据见 `reasoning-papers.json`。以下文献结果没有在本仓库复现，采用状态由本轮总报告和测试证据确定。

## 1. Large Language Models Cannot Self-Correct Reasoning Yet

Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou；ICLR 2024；[2310.01798v2，2024-03-14](https://arxiv.org/html/2310.01798v2)。

**实际阅读**：正文 §§1–7、Tables 1–8；附录 A 部分提示/失败例；PDF 第 6 页 Figures 1–2 原图。不声称逐页审读 17 页全部附录。

**方法与证据**：§3 将有答案标签决定停止的 oracle 与没有外部反馈的 intrinsic correction 分开；初答→批评→改答最多两轮。GPT-3.5 用完整 GSM8K/CSQA 集，其余模型抽 200 题，HotpotQA 100 题。Table 3 的 GPT-4 GSM8K 从 95.5% 降至第二轮 89.0%；Fig.1 直接分解“对改错/错改对”。§4 同等响应次数比较辩论与 self-consistency；§5 将遗漏要求放回初始提示，暴露不公平基线。Tables 5–6 为反馈提示消融。

**局限与迁移**：结论限当时模型、所测任务/提示，不能推出 2026 年所有模型都不能纠错。可借鉴的是等预算、完整初始要求、真实停止规则及回归计数；不能把“多反思几轮”当作准确率提升证据。主要证据位置：§3.1–3.3、§4 Table 7、§5 Table 8、§7。

## 2. Let's Verify Step by Step

Hunter Lightman, Vineet Kosaraju, Yura Burda, Harri Edwards, Bowen Baker, Teddy Lee, Jan Leike, John Schulman, Ilya Sutskever, Karl Cobbe；[2305.20050v1，2023-05-31](https://arxiv.org/html/2305.20050v1)。

**实际阅读**：正文 §§1–8、Tables 1/3/4、附录 B–H；附录 I 失败例文字；PDF 第 5/7/8 页，特别是 Figures 3–4。未逐图审查 Appendix I 的全部长解答，未全文阅读被引论文。

**方法与证据**：固定 generator，训练 outcome/process reward model 后 best-of-N 排序；PRM 学每步正/负/中性标签，默认各步正确概率乘积，标注到首个错误为止。§3 的 78.2% 是 500 道保留 MATH 题、best-of-1860，ORM 72.4%，并非单次回答准确率。§4 用相同数据、小模型及大 PRM 合成标签隔离混杂；主动选“高分但错”的样本约有 2.6 倍数据效率。Appendix F 的 product/min 与 neutral 处理差异较小；乘积偏向较短解。§4.2 迭代重训 selector 无收益；§6.3 不能完全排除污染。

**局限与迁移**：属于训练/选择实验，云 API 外置工作流不能据此宣称训练了 PRM。借鉴“定位第一处可核验错误”，落实到需求、输入、统计、图表和结论的公开中间产物；不要求导出模型私密思维链。跨科研任务收益须另测。

## 3. CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing

Zhibin Gou, Zhihong Shao, Yeyun Gong, Yelong Shen, Yujiu Yang, Nan Duan, Weizhu Chen；ICLR 2024；[2305.11738v4，2024-02-21](https://arxiv.org/html/2305.11738v4)。

**实际阅读**：正文 §§1–5、Algorithm 1、Tables 1–3；Appendix A–B、D.1–D.4；PDF 第 6 页 Table 1/Figure 3。未逐项读完 78 页中的全部示例和提示附录。

**方法与证据**：生成→外部工具核查→依据反馈修订，有上限与停止条件；搜索用于 QA，解释器用于数学程序。§4.1 每个 QA 数据集抽 500 题、最多三次修订；Table 1 的 ChatGPT HotpotQA F1：42.8→52.9，无工具为 46.1。§4.2 数学最多四次修订；Table 2 也有负例：text-davinci-003/SVAMP 84.0→80.7。D.2.2 中 1,319 道 GSM8K，原本正确题有 41 道改错。CRITIC* 和 rejection sampling 对照含 oracle，不可冒充部署结果。

**局限与迁移**：执行成功不证明理解用户正确；搜索可失误，反馈依赖任务/提示，迭代增加延迟。把实际工具返回与模型批评分开保存，给修订绑定被核查的版本，重新独立验收；不能把 API 返回存在、自评“正确”或答案连续不变直接当验收。证据位置：Algorithm 1、§4.1–4.4、Appendix A、D.1–D.2。

## 对当前仓库的具体映射（工程设计，非论文原结论）

已读 `prompts/decision_review.md`、`scripts/semantic_acceptance.py`、`scripts/agent_eval_pipeline.py` 的记录/评分/报告路径、`agent_runtime/core.py` 的完成重验与依赖失效路径。仓库已有独立验收和最后一次尝试指标，应该扩展这些入口，避免另造一个只检查“报告里写了成功”的裁判。

| 当前入口 | 已有能力 | 本轮应补的机制 | 最小验收 |
| --- | --- | --- | --- |
| `decision_review.md` 与角色交接 | 区分观察/推导/假设；不以多数模型同意代替证据 | 核查 requirement revision、用户原话/解释、单位、数据版本；纠正解释后不得沿用旧结论 | 注入单位和目标两种错误，改正意图后旧报告不能继续作为当前证据 |
| `core.Engine._check_done` | 重验产物并沿 DAG 传播失效 | 把跨运行的意图/假设版本作为可失效依赖；语义失效不必伪装成文件损坏 | 同字节旧数据仍可保留，但失效解释的派生报告不能验收；无关链保持有效 |
| `semantic_acceptance.validate_acceptance` | 受信控制器提供独立、绑定哈希的验收 | reviewer 核查内容是否回答当前任务，证据与报告是否一致；评分文件存在不等于真实审阅 | 工具返回“成功”但答非所问的样例仍拒绝 |
| `agent_eval_pipeline.report` | 已按最后 attempt 的 `passed` 汇总，并保留 `first_pass` | 展示 `correct_to_wrong`、`wrong_to_correct`、未完成/未评分及总成本；禁止把 any-attempt pass 当最终指标 | 初次通过后末次失败：最终不通过，回归计数为 1，分母不减少 |
| 监督续跑与探索协议 | baseline-first、预算和独立分支、固定验收 | 反思仅创建待验证假设；当前目标仍以最新 TASK 为准；公平对比要保存负结果 | 基线未验收不得转入 B；B 失败保留 A；新用户纠正优先于旧探索 |

**有界评测建议**：在现有通用评测入口设置同一冻结用例与 rubric，比较完整初始提示 A、无外部证据的反思 B、带可信工具证据/版本检查 C。三者同模型/数据/调用与 token 上限，工具和失败重试都计费；记录 final pass、正确答案被改坏的比例、错误前提拦截率及耗时。不要给被测 agent 隐藏答案，也不要用答案标签替它决定停止。合成案例只证明门禁和统计正确；声称科研质量或当前模型准确率提升前，还需真实宿主执行、独立评分和未公开保留集。

**优先级**：先补前提纠正及传播失效，再把相关回归加入通用评测。按用户要求仍先完成 TASK 基线，反思产生的更好 idea 记录为 hypothesis，不自动升格为 memory fact 或有效结论。当前三篇支持工程方向，不提供本库升级后的收益数字。
