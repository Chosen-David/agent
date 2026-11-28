# Training assets and verified recovery

## Plan

Keep the existing ResultStore evidence gate and scheduler. Bind worktrees to a shared physical root, track scientific identity separately from trajectory and run, reserve capacity at dispatch, and use references and explicit creation-time policy for retirement.

## Progress

Two-rank CPU Torch 2.9 DCP integration successfully restored the longest committed generation and fell back to an earlier generation after deliberate corruption of disposable test data. The project-specific production adapter uses its native FSDP2 checkpoint format. Existing human-owned material and historical generations remain protected. Scientific validation and end-to-end production receipts are tracked by the producing project.

## Verification

Run the ordinary result store, storage, recovery and training claim tests. For real distributed verification, run the two scripts under agent_doc/agent/test/training-artifact-policy in a disposable directory using the intended Torch environment.

2026-11-28 · V5 复核交接。五步训练进程已结束，但宿主验证器未接入；生产者零差、两个等待会话和 exit 75 均不构成科学验收。新增可选 research_handoff 与受管 timer hook；绑定双模型、证据及原 cycle，业务授权与科学判定分离。训练机真实 Codex 两模型 nonce 调用及一正一反独立复核已观察；生产验收状态以原项目 experiment receipt 为准。
