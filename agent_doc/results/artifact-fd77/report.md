# ARTIFACT-FD-77：目录拒绝路径 fd 泄漏修复

日期：2026-10-20。基线：`91114412e26d85ae06be5421e42e11bf84fee9c6`。

问题位置：`agent_runtime/result_validation.py::_bytes`，原第65行。Linux上打开目录得到合法fd，随后fdopen抛出IsADirectoryError，尚未进入with，描述符没有释放。反复处理非法artifact可能耗尽进程fd。历史artifact-read76独立诊断已发现此缺陷，本轮单独修复，未改写历史结果。

修复：第65–88行使用try/finally保留原始fd所有权，fdopen(closefd=False)借用；成功、构造失败和读取失败都关闭fd。路径限制、16MiB限制、小文件探测/增长回退及摘要逻辑未改变。依据为[Python3.12官方open文档](https://docs.python.org/3.12/library/functions.html#open)的closefd所有权契约，2026-10-20核查。

修前运行新增回归4项：真实目录与构造失败2项失败，stat失败与正常读取2项通过；完整原始短日志`before.txt`。修后专项45项通过，见`after.txt`。独立22组对照中，旧版泄漏13个fd（12次目录及1次构造失败）、候选0；候选21次成功open各关闭一次，open失败没有误关。独立审查与原始配对记录见`independent.md`、`raw.json`。全库1318项（8跳过）、Reader3通过；完整回归摘要及私有大日志哈希见`tests.txt`。

环境：CPython3.12.14、Clang22.1.3、Linux6.18.55 x86_64/glibc2.39；纯CPU文件I/O测试，不涉及GPU、模型、框架或编译kernel。测试输入在临时目录构造；独立脚本保存输入/源码哈希。指标是每次错误后泄漏fd个数，不以测试总耗时作为性能数据；未测吞吐、wall时间、RSS、token或模型质量。

实际复用检查：result_store查询`directory descriptor leak`扫描199项、partial=true、63项缺失record.json；唯一词法命中token-fifty-03-r2-20261012与本问题无关，拒绝迁移其结论。直接采用artifact-read76/independent.md的缺陷定位，重新测量当前代码。知识查询`file descriptor ownership closefd`命中speculative-decoding-cost-bound、speculative-sampling-residual-exactness、car-lora-transfer，均无关、不采用。现有十篇论文阅读保留在read-boundary56/research_a.md、research_b.md，本轮不声称新读十篇。

边界：独立工具审查不等于已部署ManagedEngine或监督服务。只支持本机已测资源释放与字节/异常语义，不证明任意并发文件变更的原子快照，也不代表整个仓库无bug。后续继续定位其他实际缺陷，不为提交而扩大改动。
