# [MATH-63] 消息容量、条件错误下界与压缩预算

Task-ID: MATH-63
Date: 2026-10-09

## Plan

目标/授权：基础学科持续建设与直接main；信息论补齐DPI已有条目的有限消息容量/分类错误下界，筛选最新FOCUS2609.37590v1，不制造压缩生产修改。指南为空，PROJECT_ROOT=WORKFLOW_ROOT本库，SGLang/guide禁止写。

对象：有限标签Y∈{1,..,M}；解码器仅见消息T和已声明侧信息Z，输出标签。M>=2时H(Y|T,Z)≤h2(Pe)+Pe log2(M-1)；弱界Pe≥max(0,(H(Y|Z)-I(Y;T|Z)-1)/log2M)。每个z消息至多C种则I(Y;T|Z)≤log2C，分类成功率≤E_Z sum_{C最大标签}P(Y|Z)，均匀无侧信息≤min(1,C/M)。M1单独处理；固定Bbit消息C≤2^B，固定n token词表V至多V^n，仅有限编码上界、不等于模型token性能；变长长度/工具/时序侧信道不能漏算。

顺序：独立新上下文planreview→produce实验→distinctfreshverify_experiment_result→publish，三个节点合同一致，见结果目录plan/contract/validation_plan。预算1800秒、最多2次计划返修、每个fixture公开小枚举，无GPU/付费模型。宿主真实独立调用，但无部署的ReviewSession/tmux/监控，未知token成本如实记unknown。

验收：8公开样例uniform4/8、偏斜分布、已知侧信息2类、变长长度侧信道、二元边界、M1；独立重算并核验一般证明。3无定理名称结构query各file/SQLiteTop3新ID命中，完整目标+DPI2条≤12000字符。34知识回归通过；所有原始card字节和保留测试hash不变，保留测试内容不读。跨域迁移固定标签分片路由，少消息不能认证零遗漏；后续条件/反例明确，手工前提拒用不是LLM实测。

新条目/镜像/coverage/state/本任务/证据为写范围，无runtime生产修改；先查旧结果与KB，仅取已有DPI为前置，旧数据不复用为新结论。近期论文选择性原文方法/理论/失败/成本读；作者经验结果不当本库收益。数学归纳/熵证明非Lean；数值entropy只核对有限样例。

完成：当前独立结果与范围接受后记录覆盖/限制/下一步，维持GPU和其他域cursor，重新同步处理并发、非force直接main，核对远端SHA/tree。

### 冻结验收补充

八个逐项 ID 与期望值见 `agent_doc/results/math-fano-message-20261009/fixtures.json`；F4 与 F5 分别检验旁信息存在时两消息/一消息的不同界。三条精确公开查询、两后端与上下文预算见同目录 `retrieval_protocol.json`。随机解码器的随机性必须给定观察与 Y 独立，相关随机性计入 Z。

## Progress

- 同步最新main aa93e85，读取指南、角色注册表、已有DPI与覆盖状态，未发现同题运行锁。先前结果查询与来源筛选保存本轮目录。


- 计划第二轮独立审查approve；结果由另一个fresh verifier做源文/数学/8公开案例/6命中/9670字符两条目前置/34回归核验，主AI观察真实完成后提供钉定receipt的可信provider，按原生ResultStore登记usable-with-scope。首次requires格式错误与失败回归日志保留，修正后34测试通过。
- 严格保留所有旧知识/候选和holdout字节、原GPU及其他领域游标，未读holdout内容；未做模型/GPU/e2e/实际token测量或生产升级。
- 全局project metadata检查仍被现有COMM20-01身份/日期不一致阻塞；不替本轮知识证据背书为全库通过。下一步是实测任务ID与旁信息协议，比较完整调用成本下的覆盖/错误。
- 发布：验证后重新fetch，直接main并核对远端；具体提交与读取结果见publication.json。
