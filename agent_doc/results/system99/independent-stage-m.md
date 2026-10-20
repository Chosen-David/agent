# SYSTEM-99 阶段M独立验收

结论：**usable-with-scope**。仅接受43个历史叶目录的可发现登记、原件绑定及
不授信语义；不接受旧结论复用、模型质量/性能主张或SYSTEM-99整批完成。

独立审查上下文只读核对基线/当前HEAD/origin-main
`49bd76036097966a30014898576598c99a5e946a`。实际结果候选对象：

- SYSTEM-99 Version17：
  `d0acf3ab39b890bae502b829fcca60a24ff9dae110245c8f33386e4008be58c5`；
- `catalog-wave2-plan.md`：
  `6f94c6ff09e09f7e348ae6dd79d6999ba49166da37cf5677b7059b7df12bd78c`；
- `stage-m.md`：
  `4c0ad9857d3cb5035c9f736e0d0775eef58bcadf26215f515d72a8708554d866`。

## 六域结果

| 域 | 判定 | 独立核验 |
| --- | --- | --- |
| implementation | pass | 43个新record均使用现有schema；无runtime/schema/guide/旧报告修改。 |
| reference_boundary | pass | 全部为historical-external-reference、空context/contract、unknown/null proof；43次decide均verify_delta，verifier调用0。 |
| data_integrity | pass | 43目录、618文件、6108516字节，最大207364；无符号链接/未跟踪原件，全部与基线blob一致。 |
| numerical_sanity | pass | 名称、原件、record清单SHA及18/15/5剩余分类独立复算一致；无浮点或性能指标。 |
| measurement_validity | pass-with-scope | 只验证发现、绑定和不授信语义；历史pass/fail/blocked/性能文字未升级为当前证据。 |
| reproducibility | pass-with-scope | 冻结规则、完整清单哈希、基线和聚合record哈希可复现。 |

独立复算的名称清单SHA256为
`d81fad885eadd022fa3e7243db383eaab98f0af4f91e56cf86273b28f8b3dbc5`；618项
`path<TAB>sha256`为
`a11c31a0d039645ff711e13b61a75576693b85285a2f2ab2ae9db4a9c6b9c3d4`；43个record
共131571字节，其 `path<TAB>sha256<TAB>bytes` 清单为
`d9be568026027ce91a119a9a3d77738758234d055d9c424ae45050b8c6cc38cb`。
43个summary严格为 `run_id: 首个H1`，统一治理后缀计数0。

正式查询独立观察为scanned252、partial=true、错误81→38；剩余严格分为嵌套报告18、
无直接标准报告15、超过64文件5。43个run-id查询各命中自身，计划指定的3个H1特征
查询均在limit20内。43次show覆盖精确618 refs且当前哈希成立。

## 独立执行与限制

独立运行ResultStore21、fd9、reuse25、depth7，共62/62通过。临时目录负控确认重复
run-id不能覆盖、坏artifact SHA拒绝且失败不留部分record。第一次负控脚本把预期错误
文案写成 `hash mismatch`，实际为 `stale artifact` 而失败；改正测试断言后通过，这是
审核脚本错误，不是产品失败。`git diff --check`通过。

独立审核未重跑全库、Reader或同步，只核对阶段报告与主控完成回执一致；因此1396
（1388执行通过/8跳过）、Reader3及sync exit0不是独立重复样本。工作树只含本阶段
SYSTEM-99、43 records和两份阶段文档，另有既存无关未跟踪压缩包保持未触碰。

38个目录、真实宿主、多轮任务质量、usage/费用、性能和其它artifact全局快照继续open。
