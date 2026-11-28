# Training assets and verified recovery

## Plan

Keep the existing ResultStore evidence gate and scheduler. Bind worktrees to a shared physical root, track scientific identity separately from trajectory and run, reserve capacity at dispatch, and use references and explicit creation-time policy for retirement.

## Progress

Two-rank CPU Torch 2.9 DCP integration successfully restored the longest committed generation and fell back to an earlier generation after deliberate corruption of disposable test data. The project-specific production adapter uses its native FSDP2 checkpoint format. Existing human-owned material and historical generations remain protected. Scientific validation and end-to-end production receipts are tracked by the producing project.

## Verification

Run the ordinary result store, storage, recovery and training claim tests. For real distributed verification, run the two scripts under agent_doc/agent/test/training-artifact-policy in a disposable directory using the intended Torch environment.
