# 独立代码与数据审查

结论：`usable-with-scope`，本机合成 CPU 公开 `core.validate` 入口的冻结性能门通过；仅支持下列三种形状的观察，不证明实际任务分布、LLM 质量、token/费用或 Store/tick 端到端收益。宿主独立审查者 `/root/dag_membership_verify_0659` 实际阅读源码和运行复核；本文件不是 ManagedEngine/ResultValidationHandler 的可信部署回执。完整库回归由主 AI 后续完成，本审查不抢先标全库通过。

## 实现、参考与数据绑定

- git 基线：`6886c3ff3f4c5238d733d9da9ac349933f3020de`。
- baseline core.py SHA256：`198753673877360b828ba89bccc68bba1da70996a0f26fd8d2b5f7049ed94298`。
- candidate core.py SHA256：`d137bd76e938283611e47acad4eec5bf8b706f9f3e3dcf9d0b264ba5df4196d8`。
- plan.md：`310a15c32f7862f113fe94984a6df6bc8b63733a862ada59cb844a7616257394`。
- plan-v2.md：`3252539eed8fcf28e035ed53a684c59c6d16e2664e3205f3c7de1111943e5ed0`。
- plan-review-v2.md：`6a0698bea39b1422641f1af3074c4c189563633efa4e35b2bada54fc4c358d4f`。
- check.py：`694b962cad01769a734e1cc43c5b11b5202dc0f40f27f9776ebdb339a54c673e`。
- producer.json：`4a4b5ada6929992e35f1ddc7221aa881074eade71ca772f66a263a45c7ff67ac`。
- independent.json：`cc8006125ef304704a22ae35ee850610ff28a8f92786ae3ce3e52b637ace6177`。

真实调用 `Store.create` 在 core.py:154–155 调用 `validate(plan)`，候选能通过现有入口到达。计时仅调用 validator，含字段检查、循环检测及最终 JSON 编码；没有计 Store 数据库、保护计划注册或调度。原实现通过 git show 加载并编译，不用自造“更慢参考”代替真实基线。

代码保留原 invalid-ID 短路后唯一性集合构建、重复 ID 错误及后续字段/依赖/循环/JSON 检查顺序。仅所有 IDs 和当前依赖均为 exact builtin str 时使用集合成员；任何 ID 子类或当前依赖子类仍走原 list 成员。正常 str 无自定义 equality/hash，此分支语义等价；此论证不外推所有 Python 自定义对象或资源异常。

## 实际检查与冻结判决

执行 `python agent_doc/results/dag-membership-20261013-0659/check.py > agent_doc/results/dag-membership-20261013-0659/independent.json`，完整 541 次差分检查通过，输入未变。512 个三节点有向图、非法字段/依赖及子类等输出与基线一致；result digest 与 producer 同为 `985a911af570f94a6b3fc50bbc04a980977f8e8b5062cbb1a3e008f92aa549ac`。

另以 `python -O` 加载 check.py 至 `raw={}` 之前的代码运行正确性部分（不跑第二轮性能），541 次同摘要通过。独立构造 10 个补充案例通过：ID 或依赖分别为 hash 抛 RuntimeError、无 hash、相等恒 false、相等抛 RuntimeError 的 str 子类，以及非法 ID 短路先于后续坏 hash、未知无 hash 依赖先于缺失 risk。baseline/candidate 的异常类型和文本全部一致。输出依次为：hash denied 两次；unhashable type: 'Unhashable' 两次；unknown dependency 两次；eq denied 两次；unique nonempty task IDs required；unknown dependency。

| 冻结形状 | baseline 中位 ms | candidate 中位 ms | 观察降低 | 判决 |
| --- | ---: | ---: | ---: | --- |
| 1 节点，每样本 1000 次 | 0.007723092 | 0.007154915 | 7.36% | 小形状不超过 10% 退化：pass |
| 512 节点，依赖前最多 32 节点 | 48.805554 | 14.466526 | 70.36% | 至少降低 10%：pass |
| 1000 节点，依赖此前全部节点 | 1706.175503 | 126.066791 | 92.61% | 至少降低 10%：pass |

两次 warmup、七个交错顺序配对，原始全部配对保留 independent.json；只用第一独立普通轮判决，未重复计时挑结果。三形状输入 hash 分别 `543a9745c36e9b41ba52674da2f2fc95410b683437a3a079366e8fba50397c47`、`e61844995c4615659b5a4e2ed8eb5928865b2fe8262c26df3f2fc467d905de4b`、`76bb244e6f5910040c90d5b31e1f5d7f715f19211f53792eb5b2e43f10a49588`，与 producer 相同。所有计时有限且为正，单位 ms，重算中位与降低比例一致。

## 测量与结论限制

设备读回：Linux 6.18.44 x86_64，AMD EPYC 9V74 型号、9 个在线虚拟 CPU；型号的 80-Core 字样不代表本任务获授 80 物理核。

环境 Python 3.12.14 / Clang 22.1.3、Linux x86_64 虚拟机；没有 CPU 绑定、独占资源或锁频保证。主 AI 等本轮完成后才运行 tests；审查者自己的 `-O` 差分短进程约 0.27 秒与第一计时进程曾短暂并行，不能宣称零干扰。未因此重跑或删除第一观测。大形状 producer 与独立数据方向和数量级一致；小形状 producer 退化约 4.50%、独立降低约 7.36%，均在冻结门内，说明微秒级差值受噪声影响，不能主张小形状稳定提速。

优化仅把 exact-str 依赖成员检查从 O(E·V) 降为期望 O(E)；现有循环检测和 JSON 等仍在，不能称整个 validator 为线性复杂度。稠密 1000 节点输入接近任务数上限、约 499500 条依赖，是压力形状；实际运行频次未验证。无 GPU、模型或外部服务实测。旧 v1 已被计划审查要求修改；本次依 v2 保留子类兼容，不把 v1 revise 记录删除。

完整回归、最新远端并发核对与发布 readback 仍由主 AI 在此验收之后负责；若 core.py 或性能输入/协议改动，此记录不能自动套用。
