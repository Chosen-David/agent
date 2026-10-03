# 持续优化记录

从 `state.json` 读取最近已验证轮次、覆盖范围和下一步；`papers.json` 按论文 ID 去重，
`candidates.json` 保留采纳、待测与限制。历史评测见 `evals/results/2026-10-03/`。
当前目录是审计台账，不安装调度器、不授予权限，也不构成分布式锁。

用户明确要求每轮优化前先 pull、验证后直接 push main，不建 PR 或额外升级分支。
干净工作树先执行 `git pull --ff-only origin main`（或等效 fetch + fast-forward）；有未提交检查点时先保留并核对，不能覆盖。
每轮先刷新 main 并核对宿主正在执行的任务。相同基线/候选已有执行者时继续其检查点或跳过重复触发；
不要让两个执行者同时修改相同工作目录。发布使用非强制快进；若 main 前进，保留并发变更并重验受影响范围。

轮次内保存：基线、论文和源码定位、预定验收、实际运行、负结果、限制、后续候选。
文件里的 validated 不等于已发布：用该轮文件的引入提交及它在最新 origin/main 的可达性确认发布。
同一提交无法包含自己的 SHA，发布 SHA 由 Git 历史解析，不填猜测值。

连续无有效改进计数只统计完成调研和有效验证的轮次；网络失败、缺测和资源阻塞不计。
至少连续四轮无值得采用的改进，且完成全部角色/交接覆盖、没有权限范围内可推进的重要候选时，
才形成收敛提案；台账本身不自动关闭任何任务。

## 独立保留测试复现

R1 的 `evidence/holdout.py` 是当时锁定的测试源，运行会在脚本目录生成合成输入。
复制到临时目录运行，勿在历史 evidence 目录覆盖原始报告。`--lock` 仅首次生成该目录的路径相关 manifest；
随后旧新版都使用同一份 manifest，不能在两个版本之间改验收。

```sh
replay_dir=$(mktemp -d)
cp docs/continuous_optimization/rounds/2026-10-03-r1/evidence/holdout.py "$replay_dir/holdout.py"
git show a5328e407ba1f12a6b887d2206d2eb1258b6cee1:scripts/validate_handoff.py > "$replay_dir/baseline.py"
python "$replay_dir/holdout.py" "$replay_dir/baseline.py" baseline --lock
python "$replay_dir/holdout.py" scripts/validate_handoff.py candidate
```

报告是诊断工具的合成案例结果，不是 Agent 生产成功率；这些输入公开后不再是后续轮次的未见保留集。
