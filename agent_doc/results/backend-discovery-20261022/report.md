# SYSTEM-99 / BACKEND-DISCOVERY-01（范围验收通过）

基线 `7abb604500859fe000efd9e711f5f427ecacf391`。`scripts/discover_backends.py:48–62`
在没有可用Python模块时仍生成全部import→distribution映射；映射无消费者，
CLI的11个后端都重复执行。只在存在可用模块时扫描；显式distribution版本仍查询，
不缓存跨调用结果、不安装/启动后端、不提升availability/authorization。

原始样本见samples.json；warmup单独保留不纳入五组统计。全部完整JSON逐组相等，
直接公开CLI结果亦等。13项普通及-O专项通过；旧源码新测试2项失败。
profile单独执行：11次packages_distributions累计5.60秒；不拿profile作正常wall对照。
环境：Linux x86_64/glibc2.39、CPython3.12.14。当前可选Python后端均未检出；
有已安装Python后端时仍走原映射路径，本结果不覆盖其加速，也不证明模型任务质量或整Agent收益。
首次计时调用与两次极短专项测试重叠，原数据全保留，需独立无并发测量确认。

复现（从仓库根目录，在新的自有目录运行，不改历史结果）：

```bash
mkdir -p .agent-runs
cp -R agent_doc/results/backend-discovery-20261022 .agent-runs/backend-discovery-reproduce
python .agent-runs/backend-discovery-reproduce/measure.py
```

同一wrapper冻结两版源码，以实际scripts入口的__file__执行，保持导入与默认registry一致，
计时包含解释器启动、源码读取/编译与stdout捕获；默认registry哈希见environment.json。
重现环境的软件包状态可能改变，脚本会拒绝任意一组JSON差异，不沿用本机收益。
未测冷文件缓存、其他机器/平台、真实后端、模型质量/费用；SYSTEM-99整体仍open。

独立验收：13普通、13个-O测试及5个额外边界探针通过，另做独立warmup+五组交错配对，
中位数2.20269→0.063398秒，逐组减少96.8703%–97.5477%，输出完整相等。
此复测不与主控短测试并发，满足事先固定的每组>=5%、中位>=10%门槛；
统计只适用本机该CLI工作负载。证据见independent/与validation.json；登记仍不替代未来消费时复验。

这是同一SYSTEM-99批次的局部检查点，未修复/验收tmux真实宿主、live模型或完整任务质量缺口。
