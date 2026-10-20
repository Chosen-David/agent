# SYSTEM-99 阶段N：单一顶层报告目录登记

基线 `4240287294ee7c90fc675902c7af5fc40a0a9cef`。Version18方案两次返修后经独立
`approve-with-scope`；首次候选中的 `comm20-20261009` 因内含另一个已登记run而排除，
避免父记录重复包装子run。

## 实际登记

按冻结规则为11个目录各新增一个 `register_history` 生成的 `record.json`，绑定358个Git已
跟踪普通原文件、3349153字节，最大105432字节，无符号链接或未跟踪文件。目录名清单
SHA256为 `4b9183b865b80a59978819cb20b7abc6733de18dcb1cd4619ed8b374bbbe7c11`；
排序 `path<TAB>sha256` 清单SHA256为
`cd94f4498658227686e55ce913690ea40dd8e5b6e10e3274782aa3203a2fc370`。
全部原件与基线blob一致，登记后逐引用重验hash。

11条record共69835字节，排序 `path<TAB>sha256<TAB>bytes` 清单SHA256为
`60a30b360f39a363d07968f26b98c8cb600bfacf9947577ec1d03b1b6d14b3ee`。summary只含
目录名与顶层报告首个H1；失败/无效题名原样保留。全部为
`historical-external-reference`、空context、`measured_at=null`、`contract=null`、
validation `unknown/proof=null`，没有把旧报告结论升级为当前验收。

## 发现、不授信与回归

- 正式查询 `historical result discovery validation unknown` 保持扫描252目录与
  `partial=true`，缺record错误38→27；`comm20-20261009`、活动证据目录 `system99` 和
  其余未分型目录仍显式报错。
- 11个run-id查询均找到自身；“近似耦合边际修正 未通过验收”“无效 独立启动 对照”与
  “DOC-SCOPE 验收入口”题名查询均在limit20内命中目标。
- 11个show覆盖精确358 refs；11个decide均为
  `verify_delta/unknown/proof=null/automatic_skip_authorized=false`，共享verifier调用0。
- 临时目录负控确认重复run不能覆盖，坏hash拒绝且不产生部分record。

实际命令结果（Linux x86_64、CPython3.12.14、标准库文件/JSON路径，无模型、GPU或外部
服务）：

```text
ResultStore focused: 21 passed
reuse acceptance: 25 passed
full suite: 1396 tests, 1388 passed, 8 skipped
paper-reader: 3 passed
sync_plugin_references.py --check: exit 0
```

本阶段没有runtime/schema/guide/旧报告变更，不测或声称模型质量、token、速度、内存、费用
或科学正确性收益。27个未登记目录、真实宿主/多轮质量、usage/费用和其它artifact全局快照
继续open；这是SYSTEM-99可恢复检查点，不是一轮完成。
