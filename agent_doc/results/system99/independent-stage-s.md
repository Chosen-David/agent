# SYSTEM-99 阶段S独立实现与数据验收

结论：`APPROVE (zero blocker)` / `usable-with-scope`，限定为本机 POSIX
supervisor 的 `launch.lock` / `worker.lock` 特殊文件拒绝与原锁语义保留。
实际审核者为宿主独立子上下文 `/root/system99_lock_plan`；我只读源码、运行临时CPU
夹具并撰写本记录，没有修改生产代码、测试、任务或人类 guide。该独立调用没有接入
仓库 `ReviewSession` 认证，不宣称已经部署受管双主或真实 tmux。

基线：`5b9bae0b0db6889fec6a96bee9ef4d0733e2c784`。验收源码 SHA-256：

- `agent_runtime/task_supervisor.py`：
  `e700affc6d4ef6e49d499128527f7e9f4a8d290ad0187363cbf2fdd984f06f4e`
- `tests/test_supervisor_lock_files.py`：
  `4b4f9a30f50ac57c2b3827693e7554c4b30d22ca98b0abc905f1e687fcbc792c`

## 六域核验

| 域 | 结论与实际依据 |
| --- | --- |
| implementation | pass：私有 `_lock_file` 仅由 start/worker 两点消费；原路径和 guide 写入 guard 在先，`O_CREAT|O_RDWR|O_NOFOLLOW|O_NONBLOCK` 打开后同FD `fstat`，普通文件才进入临界区。finally覆盖fstat、flock与body异常并close；无截断、unlink或replace。launch保留阻塞LOCK_EX，worker保留LOCK_NB及重复返回0。 |
| reference_boundary | pass：独立加载基线原始模块源码，在真实临时FIFO上调用旧start/worker，两者各0.7秒后仍阻塞；测试父进程终止并回收，状态目录仅剩对应锁。候选真实入口8个特殊锁子例通过，包含guard后替换FIFO。 |
| data_integrity | pass：核对两个固定源码SHA；新测试为5方法、8个坏锁入口子例，Store/tmux为触达即失败的桩，未见后端前置副作用。全库原日志独立逐行核算1484项，其中1476 ok、8 skipped，无FAIL/ERROR/FAILED标记；没有把跳过记为通过。 |
| numerical_sanity | not_applicable：这是锁与资源生命周期正确性检查，没有数值算法、误差、模型质量或费用测量。测试计数和状态按实际日志核算。 |
| measurement_validity | not_applicable：0.7秒/2秒仅为检测永久等待的测试超时预算，不是性能采样，不能换算提速。没有吞吐、token、显存或费用主张。 |
| reproducibility | pass：独立运行普通/-O共39项相邻测试，均38通过/1真实tmux跳过；额外跨进程阻塞锁、非普通FD和关闭负控通过。Reader、同步、编译与diff检查亦独立执行。主控全库仅独立核算日志，没有冒称独立重跑。 |

## 独立执行

```text
python -m unittest -v tests.test_supervisor_lock_files \
  tests.test_managed_supervisor tests.test_external_json_boundaries
Ran 39 tests in 26.749s -- OK (skipped=1)

python -O -m unittest -v tests.test_supervisor_lock_files \
  tests.test_managed_supervisor tests.test_external_json_boundaries
Ran 39 tests in 28.162s -- OK (skipped=1)

python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.575s -- OK

python scripts/sync_plugin_references.py --check
python -m compileall -q agent_runtime/task_supervisor.py tests/test_supervisor_lock_files.py
git diff --check
# 三项均退出0，无输出
```

另外直接执行的独立负控：

- 保持父进程LOCK_EX，子进程打开同一普通锁后确实等待；父FD关闭后才获得锁，
  原inode及 `static-lock` 字节均保持。
- 注入实际打开的 `/dev/null` FD，候选经真实fstat拒绝非普通文件，且FD已关闭。
- 正常退出后旧FD再次fstat抛OSError；原测试另验证fstat异常、body异常及持有者终止释放。

基线独立复现使用 `git show BASE:agent_runtime/task_supervisor.py` 的真实源码模块，
没有根据候选逻辑拼装旧实现；真实start/worker的FIFO反例均在建库/tmux之前阻塞，子进程
已回收。没有用“未见输出”推断成功。

主控全库日志 `.agent-runs/system99-stage-s/full.log` 完成后独立读取核算：

```text
1484 test lines = 1476 ok + 8 skipped
Ran 1484 tests in 109.659s
OK (skipped=8)
raw SHA-256: e8f24501df84fb8b3f271d2c8af250fb2da5a5c4b7e62d6b1333f6b77f4d0cff
```

## 范围

环境为 Linux 6.18.55 x86_64/glibc2.39、CPython3.12.14；当前无tmux二进制。
相邻worker测试使用显式模拟的TMUX标记和真实子进程/SQLite，不代表tmux会话或SSH
断线存活。未验证Windows、NFS/跨主机锁、恶意父目录或普通锁inode被并发替换，
以及真实模型、多轮任务质量、usage/费用。正常合法锁仍可等待另一个合法持有者；
本阶段只保证特殊文件不会在打开时永久等待，不提供任意临界区时限。

本阶段满足已声明有界正确性验收，没有性能或模型质量提升结论；SYSTEM-99保持未完成。
