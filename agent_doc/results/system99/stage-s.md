# SYSTEM-99 阶段S：supervisor锁文件阻塞修复

基线：`5b9bae0b0db6889fec6a96bee9ef4d0733e2c784`。稳定问题ID：
`SYSTEM99-S-LOCK-001`。本项属于同一未结束的SYSTEM-99批次，沿用同批17篇正文记录。

## 证据与范围

已读阶段R及当前未决清单；R修复外部JSON，不覆盖锁文件本身。实际执行历史查询
`python scripts/result_store.py --root <project> search 'supervisor lock FIFO artifact bounded'
--limit 3 --max-scan 200`：scanned=200、partial=true，候选为math-packet-entry、combined-corpus-delta-v2、
corpus-fd9012-delta；范围分别为数学FIFO定理/语料，而非当前锁入口，不能复用为本次验收。
保留检索缺口，不以未命中证明没有历史。当前guide为空，只读；其他检出论文交付校验的dirty内容
保持未动。

`agent_runtime/task_supervisor.py` 的start和worker原以
`guard_write_path(...).open('a')` 打开launch.lock/worker.lock。路径guard不检查普通文件类型，
FIFO写打开会等待读端，因此恢复/启动在数据库与backend之前永久等待。真实临时目录、有效
prepare计划和真实start/worker入口固定反例：仅tmux可用性及禁止副作用的Store/tmux调用用桩；
两个入口均超时，父进程回收了自己的子进程。

```text
python -m unittest discover -s tests -p test_supervisor_lock_files.py -v
修前：Ran 1 test in 4.017s — FAILED (failures=2)
launch FIFO lock blocked instead of rejecting input
worker FIFO lock blocked instead of rejecting input
```

先前怀疑contamination的a+b锁也有同一缺陷；实测它对FIFO立即报not seekable，因此排除，
未制造该处修复。[独立方案审核](stage-s-plan-review.md)认可缩小范围。

## 修复与固定验收

`task_supervisor.py:46-59` 私有_lock_file保留写入guard，以
O_CREAT|O_RDWR|O_NOFOLLOW|O_NONBLOCK打开，在同FD上fstat拒绝非普通文件，finally关闭FD。
start/worker仅改用该opener；launch的LOCK_EX等待、worker的LOCK_NB重复返回0保持，
不截断/unlink/replace合法锁，保留稳定inode。打开非普通文件的OSError/ValueError继续被CLI
结构化捕获。没有改变任务/schema/授权或下游数据验收。

固定候选文件SHA256：

- `agent_runtime/task_supervisor.py`：
  `e700affc6d4ef6e49d499128527f7e9f4a8d290ad0187363cbf2fdd984f06f4e`
- `tests/test_supervisor_lock_files.py`：
  `4b4f9a30f50ac57c2b3827693e7554c4b30d22ca98b0abc905f1e687fcbc792c`

新增5方法含8个坏锁入口子例：FIFO、目录、symlink、guard后替换为FIFO；验证零Store/backend/tmux
调用及状态目录没有额外输出。另验合法inode/原字节不变、body异常/fstat异常关闭FD、真实子进程
退出释放锁、重复worker返回0且不建库。测试的TMUX环境标记是CPU夹具，未启动真实tmux。

```text
python -m unittest discover -s tests -p test_supervisor_lock_files.py -v
Ran 5 tests in 0.685s — OK
python -O -m unittest discover -s tests -p test_supervisor_lock_files.py -v
Ran 5 tests in 0.786s — OK
python -m unittest discover -s tests -p test_managed_supervisor.py -q
Ran 10 tests in 16.252s — OK (skipped=1)
python -m unittest discover -s tests -p test_external_json_boundaries.py -q
Ran 24 tests in 8.262s — OK
python -m unittest discover -s apps/paper-reader/tests -q
Ran 3 tests in 1.121s — OK
python scripts/sync_plugin_references.py --check
python -m compileall -q agent_runtime/task_supervisor.py tests/test_supervisor_lock_files.py
git diff --check
# 三项退出0
```

全库实际执行：`python -m unittest discover -s tests -v`，1484项、109.659秒，
1476通过/8跳过。私有原始日志`.agent-runs/system99-stage-s/full.log`的SHA256为
`e8f24501df84fb8b3f271d2c8af250fb2da5a5c4b7e62d6b1333f6b77f4d0cff`。
独立审核者分别在普通/-O模式重跑39项（各38通过/1真实tmux跳过），另验跨进程LOCK_EX
等待、/dev/null实际FD拒绝且关闭、正常退出FD关闭。完整结论见
[独立验收](independent-stage-s.md)；全库日志由其核算，不冒称独立重跑全库。

环境：Linux 6.18.55 x86_64、glibc2.39、CPython3.12.14。本项只恢复有界拒绝与锁生命周期；
修前永久等待不换算为加速比。未测真实tmux/SSH、模型质量/usage/费用、Windows、恶意父目录/
普通inode替换或跨主机文件系统。当前后端缺口、历史12个复杂目录与完整真实任务验收继续open，
该阶段不能算整轮完成。
