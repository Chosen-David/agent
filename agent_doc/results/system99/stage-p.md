# SYSTEM-99 阶段P：JSON/状态型历史包登记

基线 `6e125d5df8a7cd48ab33a6af70830a2456c05ac7`；Version21方案经独立复审
`approve` 后实施。本阶段只恢复历史材料的可发现索引，不恢复旧结论信任。

## 实际登记

使用现有 `ResultStore.register_history` 为15个独立历史目录各新增一个 `record.json`。
登记前347个Git已跟踪普通原文件共3641161字节，排序 `path<TAB>sha256` 清单SHA256为
`ea734d8c1b47b8350e86b5c07508a89087682ffe1c5a91cc7f3a9bb4397daeee`；登记后排除
record重算仍完全相同。15个record共73400字节，排序记录清单SHA256为
`c43fb659e3c08f78ec8e9ea263ce3a05c72faf914d6e795c2b9e956fbb3a4eb0`。

每条record均以顶层目录名为run_id，精确summary见方案；失败、blocked、preflight/
registration rejected及有限scope词义均保留。全部为 `historical-external-reference`、空context、
`measured_at=null`、`contract=null`、validation `unknown/proof=null`，未把内部重复producer ID
或历史审核状态升级为当前结果身份/验收。

## 发现性与不授信验收

固定正式查询在同一252目录上由27个缺record错误降为12，`partial=true` 保持；写前/写后
响应SHA256分别为 `f6121fb371052ba351758411bb75c852571553f81fc7e2dddacace95fe320f8b`、
`f985ec317c8facc55c1d6b53e9793f11cc1b6d996a9a17a34be8867f7894a5bf`。
15个run-id查询均找到自身，15个show合计精确347 refs且当前hash匹配；15个decide均为
`verify_delta/unknown/proof=null/automatic_skip_authorized=false`，共享verifier调用0。
独立方案审查还在隔离临时根复现重复登记/坏hash拒绝，坏hash不产生部分record。

实际测试（Linux x86_64，CPython3.12.14，本地文件/JSON路径，无模型、GPU或外部服务）：

```text
ResultStore + reuse acceptance: 46 passed
full suite: 1406 tests, 1398 passed, 8 skipped
paper-reader: 3 passed
sync_plugin_references.py --check: exit 0
```

全库、Reader、同步日志SHA256依次为
`1d3e1c292cf895901cb6128664e35bcb884398bbb9b8dc7ad4350dfd9782d310`、
`7cc45cb39e168c6dd7df981f26c830168f123f7345f16a7b131c90c07de49e4d`、
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。首次定向命令未带
`PYTHONPATH=tests`，导致 `test_result_store` 导入夹具失败；补齐项目测试路径后46项通过。
另一次主控核对脚本误读不存在的 `stored_validation` 字段而报KeyError，改按实际
`validation_status` 重跑全部15项通过。两者均为验收脚本调用错误，不是生产测试失败，原失败
输出未改写成产品通过。

剩余12个缺登记目录仍可见，包括纯计划、活动目录、已登记子运行父容器、已由v2包装的失败包、
混合身份包和5个超过64文件的历史包。真实宿主、多轮任务质量、usage/费用与其它artifact快照
边界继续open；本阶段没有runtime/schema/guide改动，也没有模型质量、token、性能或成本收益。
