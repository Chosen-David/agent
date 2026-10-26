# SYSTEM-99 独立阅读/静态源码复核（2026-10-26）
结论：approve，usable-with-scope；仅认可本冻结检查点，无阻塞发现，不是执行DAG批准或经验结果验收。
基线：1b348c33ce95dc9310b475ccdb7c1da542ebdff3；审核者仅写本文件，未执行测试、论文示例、安装或模型实验。
已读AGENTS、project_document_workflow、dual_main_workflow及SYSTEM-99的Plan/Progress；guide全目录只读。
HTML正文实际重读：MAST §§1–6/A/B/D–K；Agentless §§1–8及全部正文表/图注；SWE-agent §§1–7/B.1/B.4/B.5/B.9/E.1–E.3。
图像只核文字/图注；不声称PDF逐页或图内像素验收，未读附录不扩充范围。
MAST：150初始轨迹、14模式/3类、1642扩展、F1 .80/κ .77及非穷尽/标注误差限制吻合。
H/Table5的GPT-4拓扑85.50对84.75、p=.4及32题25.0→34.4/40.6核对；百分点、模型差异与H.3概括冲突保留。
J成功轨迹可含失败，K约$1.8仅标注成本；B.3缺Manus完整轨迹，不能据§3.4含混叙述纳入七框架。
Agentless：固定4o、4×10补丁/40复现测试、96/300与$0.70、定位58.33/53.67及77→81→96均匹配。
213旧库复现仅94通过gold修复核验，回归筛选/复现失败回退不构成本库放宽oracle理由。
Lite-S的249题名称经原始MathML核对为单个S；文本抽取的SS是mi/annotation重复，已撤回初步名称异议。
SWE-agent：2294题12.47%、Lite54/300=18%、$4上限、Table3消融及6次均值17.94/pass@6 32.67吻合。
仅37开发题调参、15人工校准/87%一致、248未解与54/300不一致及成功实例成本分母均正确保留。
静态核读communication契约/导航/consume_handoff/ACK/impact、validate完整函数、claim_graph/check_handoff_basis、ReportingHandler.run/verify及source_context完整实现/CLI。
源码确为consumer-owned路由、同次读SHA绑定、不可变basis/request和独立ACK；声明依赖/前提检查不能认证隐藏依赖或事实正确。
source_context保留非定义原文/完整类/声明效果/本地静态闭包，动态歧义回退与预算拒绝；外部模块/回调、实际token和任务质量未被证明。
inputs全部baseline_refs与基线git对象逐项匹配，生产/CLI当前字节同基线；3个HTML哈希匹配。
7旧正文记录的路径/哈希/ID及方法/消融/局限/实际阅读范围齐全；与3新ID去重共10，只认可记录完整性。
遗失55与独审重读不计；旧pass不认证新任务，达到阅读记录数不等于SYSTEM-99完成。
原搜索285/25缺record及第二查询partial均如实保存；独立只读复查为286/26，新增本候选未登记目录，五个词法候选ID不变，不授信。
相对基线只有SYSTEM-99在Progress插入；Plan/TASK/guide/生产未改，无旧预算重置或测试/收益/整批完成主张。
主控与独审实际推理用量/费用unknown，不能记零；后续register_history应contract:null、validation unknown，不登记为经验验证。
reading.md SHA256：e83f44fc922c3725e278575e1193c1a5bc420f31f1949f45f80ccc5dc19190d9
inputs.json SHA256：38a9e9c4d225137840b583a4c9e9c2b7d28bee911c6737b9877a6ec7f8e0dea9
SYSTEM-99.md SHA256：c2c27266e45a74d54cae1dbcad4ce6dd3dfa32d5c97fbcca2dbaa02d3d2f96ac
验收后以上字节变更须重核；PID/ALIAS/role/Codex旧受阻分支、真实宿主/完整输入/全部actor usage/任务质量仍open。
