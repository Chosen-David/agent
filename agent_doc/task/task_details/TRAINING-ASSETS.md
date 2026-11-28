# Training assets and verified recovery

## Plan

Keep the existing ResultStore evidence gate and scheduler. Bind worktrees to a shared physical root, track scientific identity separately from trajectory and run, reserve capacity at dispatch, and use references and explicit creation-time policy for retirement.

## Progress

Two-rank CPU Torch 2.9 DCP integration successfully restored the longest committed generation and fell back to an earlier generation after deliberate corruption of disposable test data. The project-specific production adapter uses its native FSDP2 checkpoint format. Existing human-owned material and historical generations remain protected. Scientific validation and end-to-end production receipts are tracked by the producing project.

## Verification

Run the ordinary result store, storage, recovery and training claim tests. For real distributed verification, run the two scripts under agent_doc/agent/test/training-artifact-policy in a disposable directory using the intended Torch environment.

2026-11-28 · V5 复核交接。五步训练进程已结束，但宿主验证器未接入；生产者零差、两个等待会话和 exit 75 均不构成科学验收。新增可选 research_handoff 与受管 timer hook；绑定双模型、证据及原 cycle，业务授权与科学判定分离。训练机真实 Codex 两模型 nonce 调用及一正一反独立复核已观察；生产验收状态以原项目 experiment receipt 为准。

真实接管恢复经验：区分模型 readiness nonce、独立科学回执和生产进程实际进度。知识检索关键词：exit 75、未绑定消费者、十分钟人工窗口、stale receipt、独立科学复核。观察到已到期的只读复核模型调用仍可能超过原宿主 100 秒预算；先核对旧调用退出、宿主是否已落盘回执及下游认领，再决定同一任务上有界重试。保留原截止时间和事件，不重开人工窗口。可缩小重复证据段和每域答复长度，保留原始证据引用与哈希。
