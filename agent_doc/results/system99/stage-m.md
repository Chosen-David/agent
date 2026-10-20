# SYSTEM-99 阶段M：第二批历史结果可发现登记

基线 `49bd76036097966a30014898576598c99a5e946a`；稳定方案Version17与
[登记边界](catalog-wave2-plan.md)先经独立审查返修，再获approve-with-scope。
第一次方案会给43条summary追加相同治理词，独审指出会污染词法排名；最终实现只写
`run_id: 原报告首个H1`，信任状态留在结构字段。

## 实际登记

在81个缺record顶层目录中，按冻结规则一次性预检并登记43个叶目录：共618个Git已跟踪
普通原文件、6108516字节，最大207364字节，无符号链接。目录名清单SHA256为
`d81fad885eadd022fa3e7243db383eaab98f0af4f91e56cf86273b28f8b3dbc5`；排序
`path<TAB>sha256`清单SHA256为
`a11c31a0d039645ff711e13b61a75576693b85285a2f2ab2ae9db4a9c6b9c3d4`。
全部原件与基线blob逐字节一致，登记前后不改原文件。

每目录只通过现有 `ResultStore.register_history` 新增 `record.json`；43条record合计
131571字节，排序 `path<TAB>sha256<TAB>bytes` 清单SHA256为
`d9be568026027ce91a119a9a3d77738758234d055d9c424ae45050b8c6cc38cb`。
全部为 `historical-external-reference`、空context、`measured_at=null`、
`contract=null`、validation `unknown/proof=null`。旧报告中的通过、失败、blocked、候选
和性能文字只是被哈希绑定的历史材料，没有升级为当前验收。

## 发现与不授信验收

- 正式查询 `historical result discovery validation unknown` 保持扫描252目录与
  `partial=true`，缺record错误由81降为38；剩余18个嵌套报告、15个无标准报告、5个
  超64文件目录仍显式报错，没有用空壳record隐藏。
- 43个run_id逐一正式search，均能找到自身；另以“序列化大小下界剪枝”“目录拒绝路径
  fd泄漏”“固定支持可行性”三个题名特征查询，目标均在limit20内。公共治理词没有批量写入
  summary。
- 43个 `show` 重验全部618 refs；43个 `decide_run(run_id,{})` 均为
  `verify_delta/unknown/proof=null/automatic_skip_authorized=false`，共享verifier spy总调用0。
  可发现不等于可复用。

## 实际测试与限制

本地Linux x86_64、CPython3.12.14、标准库文件/JSON路径，无模型、GPU或外部服务。

```text
catalog audit: records=43, refs=618, errors=38, scanned=252, partial=true, verifier_calls=0
ResultStore focused: 30 passed
reuse acceptance: 25 passed
full suite: 1396 tests, 1388 passed, 8 skipped
paper-reader: 3 passed
sync_plugin_references.py --check: exit 0
```

最初用模块名混合调用定向测试时，`tests.test_result_store` 因其历史绝对导入
`test_result_validation`在该加载方式下产生1个ImportError；同一源码随后按仓库标准
`unittest discover -s tests -p ...` 重跑30+25项全部通过。该命令错误不计生产回归通过，
也未通过改测试或PYTHONPATH掩盖。

本阶段没有runtime/schema/guide/旧报告变更，不测或声称模型质量、token、速度、内存、
费用或科学正确性收益。38个未登记目录、真实宿主/多轮质量和总成本仍open；这是SYSTEM-99
可恢复检查点，不是一轮完成。
