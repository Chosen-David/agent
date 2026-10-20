# SYSTEM-99 阶段I：上下文回答初探，未通过完整验收

基线`48db42643844bbb0b9f7ab5935676fdfb75d661f`，Plan10独审后派发。
仅用现有compose_entries切换共享协议去重，源码和三题相同；没改生产指令、
runtime、schema或目录。先查旧结果252项、partial/81错误，无当前条件证据。

[固定材料、派发原件与rubric](inputs-i.json)、[回答JSON值](responses-i.json)、
[构包脚本](build_pilot_i.py)、[独审及撤回历史](independent-stage-i.md)。
回答从真实final消息转存并重新缩进，不是provider字节原件；不是自报pass。
原生两会话为`/root/pilot_i_arm1`、`/root/pilot_i_arm2`，fork_turns=none，
各仅一次会话/回答，未补答或另起会话替换失败。

| 观察 | 全文组arm1 | 去重组arm2 |
| --- | --- | --- |
| 固定包字节数 | 173627 | 153381 |
| 固定rubric逐题结果 | 3/3 | 2/3 |
| 读取声明核对 | 10连续块hash相符 | 9连续块hash相符 |
| 异常 | 首次合并输出截断，同会话补读有重复暴露 | 自报无可见截断 |

去重组R2未明确说“选择器不验证语义相关性”；所写“不证明科学适用性”
不等于该限制，按预先rubric判fail。不能据此认定去重导致遗漏：全文组
重复暴露、问题有提示、样本仅一对三题，完整公平质量比较inconclusive。
读取range/hash是可核对自报，不证明provider完整摄入或无包外读取。
精确模型/usage/cache/费用、所有工具轨迹均unknown，不报质量或效率收益。

独审仅接受固定材料、逐题事实评分和异常记录。主控另跑原prompt回归14项
通过；无生产改动，未重跑全库。Python3.12.14，本地宿主原生会话；模型条件
只能声明请求相同默认设置，不能认证实际provider版本/采样相同。
复现包须在上述基线运行`PYTHONPATH=. python agent_doc/results/system99/build_pilot_i.py`，
按raw bytes保留CRLF；模型回答不可保证重现。各源/包/问题hash在inputs-i。

[新增两篇正文](research-g.md)及[记忆实验约束](research-h.md)使同批累计16篇。
后续重点为完整可观察加载、跨会话更正/异议/依赖和真实最终任务质量；
本次负结果不支持删规则、裁必需依据或推广目录迁移，整批仍未完成。
