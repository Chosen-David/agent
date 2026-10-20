# SYSTEM-99：历史结果最小登记方案

同一 SYSTEM-99 的后续方案，非新批次。只读核实于 HEAD `68e883e986c97ffbfc96602e96baafef46880e4d`；**未实际登记或授信**，未改旧文件、源码、TASK、guide。本文件不宣称 terminal 阶段或整个系统批次已完成。

## 代表性目录与冻结 refs

选择 `agent_doc/results/result-fd95/`。未来仅新增同目录 `record.json`，通过 `ResultStore.register_history` 登记历史引用，不使用 `register`，不补造旧 manifest/proof。当前目录存在但 record 不存在；写前须重新核对并发登记/大小写冲突。

下列十四个可读普通文件合计 **151,668 bytes**，均与原修复提交 `50c1ca1e74df1026ba05b4cfd53903605315b234` 一致（实际 git diff 无差异）。全部纳入精确 `{path, sha256}` refs，路径加统一前缀 `agent_doc/results/result-fd95/`；保留失败和初次 revise，不只索引最后 pass。14项低于64 refs上限，最大单文件33,536 bytes，低于256 MiB限制。

| 文件 | 实算 SHA-256 |
| --- | --- |
| after-opt.log | `5d2951f613ea09c453b85e4dc1f3489c8473e42a09c4fabb83c440b607c22088` |
| after.log | `eab9680fbd37dfa6b5fff2c0383d88cf581659e049cd7d507940c9f2e50db8e9` |
| before.log | `c43156217515e340a68ec7395cc254911d977450fe4791f0a686172d4b0be727` |
| independent-plan-v1.md | `a86ddd5982666a2ea12f20de0d32439288aac088a76179a6265eca97ebcb65c9` |
| independent-plan-v2.md | `e9806cbfbc3f224f066f1365aa81600be37dfc93f584c6f986e730195ab018d2` |
| independent-raw-normal.json | `66430f30e0b739ad0baeb071a05f1afbe9090a15649d8e8fe60ef2644d1bf95b` |
| independent-raw-opt.json | `8c6fdf2937e55d68dfda1e4501f915cf87dbbff36770b615c15df8f328d5e62d` |
| independent-regression.log | `42a9071123d75189e2b7f943e5ad36b1358be1536bfe625f08f3fb94546bd3e6` |
| independent-result.md | `3e0106160f993716d81f72647fa1b38083fb76c8283304970bc640907f5ebdb7` |
| independent_matrix.py | `627ce1e6571e8481a86cc22650206f14706719d32489d03c321e6d04074712fa` |
| plan.md | `0bfe1645759c3cb845b313e54c9703ef596a20b93d5790df96d8a93fd826ce07` |
| reader.log | `ea152184377bbf17aa0e9e4f8b64d18e21fb3933626fe01fd918410b6d0505c6` |
| report.md | `524b3c64b58eb54d7645fc1c99d9ec36471e3833452bc57e7dfa6709ce73fd53` |
| research.md | `a54daa1cc1cd766f87722240898a225593ab48b3190aac58e0e755dbc3e6ff12` |

缺件：旧报告引用的 `.agent-runs/result-fd95/full.log` 在当前检出不存在；原声明 hash `0d0262cfd63e31bc820ef7f12c8d7976d7ba6fac9707df9db518aca7e6c8ce4b` 只能保留为历史声明，不能纳入已读取 refs，不能补造日志或称完整全库日志已冻结。

已只读核对原修复提交的源码/test blob分别为 `6ef04bd8497e196dd728bc480afba11f192c29c43282b663aa410db3afdfefaf` / `564940de12e0e1cf3a5912c76cc427f5f9ce54cb10b4e18f5f8e6d0e4f851701`，与旧报告一致；不把当前可变源码当作当时完整执行树，不额外导出代码。

## 最小参数与不授信验收

参数：`run_id="result-fd95"`；summary含 `RESULT-FD-95 result-fd95`，说明“historical descriptor-ownership repair; original failure/regression logs, independent raw matrix and scoped review; discovery only; current validation unknown”；`artifacts` 为上表十四 refs；`context={}`；`measured_at=None`。注册时刻由程序当时生成，不回填为测量时刻。

旧文件可支持来源追溯，不足以补出：精确有时区的测量完成时刻、当前消费者条件、当时完整执行环境/依赖、可信宿主当前验收身份/proof、缺失私有日志、当前远端状态或吞吐/token/模型质量收益。故保持空 context，不拼造完整实验契约。

未来最小验收（本次未执行）：

1. 独立重算十四 refs并确认普通文件/路径、同名冲突；调用 register_history 后，十四旧文件字节不变，唯一目标新增 record。重复登记须拒绝，不覆盖；破坏性负控仅在自有临时 fixture。
2. show读回：十四 refs精确相同且record SHA可复核；`origin="historical-external-reference"`、`contract=None`、`context={}`、`measured_at=None`、`validation_at_registration={"status":"unknown","proof":None}`。旧Markdown的usable-with-scope不升级为当前回调。
3. 用正式 search分别查询 `RESULT-FD-95` 和 `result-fd95`（limit20/max_scan5000），返回同一run/record SHA，`stored_validation="unknown"`、`applicability="unchecked"`。只消除该目录缺record错误，不要求全库错误归零。
4. `decide_run("result-fd95", {})` 仍为 `verify_delta/unknown`、`proof=None`、`automatic_skip_authorized=False`，原因含缺独立validation contract；不能因为可发现、旧pass或传入pass回调获得reuse。已有测试明确无契约历史不调用verifier，本轮未运行会实际登记的测试。
5. 真正消费旧数值/结论时另由消费者固定本次条件、补必要证据并独立验收新版本；不编辑历史record制造已验证状态。缺完整私有日志的主张继续受限。

## 覆盖盘点的准确分母

实际只读查询 `RESULT-FD-95 result-fd95 历史登记`（limit20/max_scan5000）及顶层枚举一致：**252目录、170个可读取record、82缺record**；扫描未截断，82错误全是record不存在，不是既存record损坏。170可读也不等于170当前验收通过。统计为上述HEAD加主控在途变更时点，后续须重新读回。

| 结构维度（非验收判断） | 数量 | 含义 |
| --- | ---: | --- |
| 缺record，有直接report.md/report_by_gpt.md/report.json | 65 | 报告形态批次候选，可能失败或未完成，不是65个合格结果。 |
| 缺record，无上述标准报告名 | 17 | 2个仅计划/契约目录；system99为1个活跃多阶段目录；其余14含失败/执行/审读/恢复记录，未逐批重审。 |
| 缺record，无非缓存子目录 | 55 | 叶形，仍须判断实际批次及状态。 |
| 缺record，有非缓存子目录及本层直接材料 | 27 | 混合证据批次/父目录；子目录不自动算独立run。 |
| 仅空目录或README/.gitkeep的纯导航父目录 | 0 | 只说明本次顶层形态，不推广到全部嵌套目录。 |

65+17和55+27是两种划分，不相加；不递归将code_snapshot/input_snapshot/candidate/independent/failed_*或__pycache__计为新批次。82名称排序、换行连接并补末尾换行的SHA为 `caefb36114eaab934e032b273db74b3851a3b55fba8039b55b9495d032106e05`。

抽查保留例外：`comm-route-bind-integration-20261009`仅contract/validation_plan，所指manifest缺失；`result-time97`仅两个plan文件。它们不是可补造的已完成测量。`project-doc-scope-20261008/README.md`区分旧本层/release-check和最终integrated-check；`token-001-20261009/README.md`明确混杂对照无效、成功零、未创建接收manifest，后续是另一个run。因此不能把所有缺record当损坏或统一补成功登记。

4个未登记目录仅直接文件已超64项（knowledge-freedman两目录79/98、knowledge-normal-mixture74、memory-index96为113）；后续须选定冻结边界/有界清单，不能递归全塞一次调用。本方案只处理result-fd95，不扩大为全库补录，不追求用空壳record消除错误数。
