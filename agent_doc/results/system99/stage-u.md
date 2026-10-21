# SYSTEM-99 阶段 U：可信输出阶梯 U1

问题 ID：`SYSTEM99-U-OUTPUT-001`

输入基线：`26d6b20791a40d39e01b928502e6bfc50a55e009`

范围：U1 结构合同、CLI、六个既有 Skill 消费者接入；U2 文档工具 profile 未实施。

## 基线与问题

基线没有输出阶梯 request/manifest 合同或对应 CLI；既有 visual explanation 只覆盖图形交接，不能把
同一冻结主张可靠地贯穿受控文字、图、网页和视频，也没有确定的降级状态。因而“形式更丰富”可能在
缺主张、缺证据或 producer 自报 reviewer 时仍被当成完成。此项是新增能力基线，不作速度或质量提升
百分比主张。

同一结果库的两次有界词法查询各扫描 253 个目录、返回 10 个候选与 13 个缺登记错误；第一项
`partial=true`，第二项 `partial=false`。候选可提供旧 handoff/figure/token 接口参考，但没有可直接
复用的四层可信合同。完整方案、候选文档依赖和 U2 边界见 [阶段 U 方案](stage-u-plan.md)。

## 实现

- `agent_runtime/output_ladder.py:17-347`：闭合、有界 request/manifest；每层精确 claim 集和必需
  artifact role；required check、同层证据与全局 check ID；`invalid/pending/ready-for-independent-review`
  三态。ready 仍要求独立观察，producer 自报身份不能升级信任。
- `agent_runtime/output_ladder.py:139-216`：逐组件 FD-relative `O_NOFOLLOW` 打开 artifact root、父目录
  和文件；同一 FD 做类型、大小、摘要和读取前后身份检查，再安全重开核对 inode。当前仅验收支持这些
  POSIX 能力的宿主；不是 OS 沙箱、跨文件事务或 Windows 保证。
- `scripts/output_ladder.py`：稳定退出码 0/2/3/1；内部异常不输出 traceback 或 producer 内容。
- `workflows/output_ladder_workflow.md:1-76`：选择最低有效层、许可/工具/独立观察边界及降级闭环；链接
  既有 visual explanation，并由现有同步器生成六个角色包内副本，没有另建任务列表或共享聊天池。

## 返修与独立复核

首次只读独审为 `REVISE`：root 祖先 symlink 未覆盖、check ID 可重复、跨层证据可冒用，U2 还存在
venv 移动后 shebang 失效、平台 lock/许可不完整且只有安装 smoke 没有可复用 API。U1 三个反例均已
加入 `tests/test_output_ladder.py:147-209` 并由接受变为 `invalid`；U2 方案改为最终路径 venv、完整
wheel/tag/source/hash、显式许可和公开 documents adapter，但未写实现。

二次独审确认三个 U1 阻断关闭；最后发现 PyMuPDF 两种许可参数表述冲突。统一为
`--pymupdf-license agpl-3.0|commercial` 并明确 POSIX 边界后，最终结论为
`ACCEPT (scope-limited)`，独立重跑 U1/visual/sync 22/22、`python -O` U1 14/14 通过。该结论不接受
U2 为已实现能力。

## 实际验证

环境：Linux x86_64，Python 3.12；CPU/临时文件测试，无 GPU、模型、商业 API 或媒体生成器。

- 定向合同、既有 visual、同步、外部 JSON 与 artifact index：普通 55/55，`python -O` 55/55。
- TASK/项目文档/链接/导航相关回归：145/145。
- Paper Reader：3/3。
- reference sync `--check`、`compileall`、CRLF-aware `diff --check`：通过。
- 全库两次均运行 1548 项，1539 通过、8 跳过、1 失败。唯一失败是未改文件
  `tests/test_managed_supervisor.py:117` 在本执行环境偶发读不到当前 `/proc/<pid>/stat`；该单项普通/
  `-O` 连续重跑呈通过与失败交替。原失败保留，不把全库写成绿色，也不在本阶段顺手修改无关 supervisor。

## 未完成边界

U2 的一次安装 PDF/Markdown/PPTX/LaTeX profile、真实公开 adapter smoke、离线复用 receipt 和许可锁仍
未实施，因此不能声称 Agent 已经自带这些文档库。U1 也没有测真实读者理解率、模型任务质量、token、
费用、媒体生成质量或生产部署。阶段 U 是同一 SYSTEM-99 的可恢复检查点；整批继续 open。
