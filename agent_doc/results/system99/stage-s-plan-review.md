# SYSTEM-99 阶段S独立方案审核

实际审核者：宿主子上下文 `/root/system99_lock_plan`。基线
`5b9bae0b0db6889fec6a96bee9ef4d0733e2c784`，主控先保存修前入口级反例，未改生产源码后
请求审核；审核者只读源码及临时CPU探针。此记录是原生独立审核，不是已接入ReviewSession
认证或真实tmux部署。

结论：APPROVE，限定supervisor的launch.lock/worker.lock普通文件检查和资源释放。

七域：intent/guide/assumptions/prior_results/acceptance/risk/resources均pass。
修复直接对应SYSTEM-99真实入口/恢复目标；guide为空且不写；POSIX原已依赖fcntl；阶段R
没有覆盖锁自身；保留真实FIFO失败、零后端副作用和普通锁契约；稳定inode必须保留；临时目录
与有限子进程足够，不需真实模型、付费资源或其他作业。

审核者独立观察Path.open('a')对FIFO在0.6秒预算内超时；a+b立即抛not seekable，因此明确
排除contamination，不把未经证实的怀疑扩成修复。完整条件：写入guard在先，同FD fstat在
flock之前；finally覆盖fstat/lock/body失败；launch保留LOCK_EX，worker保留LOCK_NB及重复
返回0；不截断/unlink/replace；真实入口覆盖FIFO/目录/symlink/guard后替换，Store/backend/
tmux零调用。父目录与恶意普通inode替换、跨主机语义留作未验证边界。

该意见只批准修复设计与CPU验收；实现结果仍须独立复核，SYSTEM-99继续未完成。
