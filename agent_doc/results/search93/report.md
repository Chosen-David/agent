# SEARCH-DEPTH-93：单条深层JSON不再中断整次结果检索

日期2026-10-20；基线`d065a055cf29b10ed37717db197995283c1665d4`。状态：已获[独立范围内验收](independent-review.md)，提交/远端回读由主控另核。

## 问题、方法和兼容边界

真实入口`scripts/result_store.py` → `ResultStore.search` → `show` → `_json`。原搜索逐记录捕获OSError/ValueError/KeyError/TypeError，但JSON解码深度超限抛RecursionError，导致整次API/CLI退出，其他正常候选无法返回。1MiB字节界限不能保证嵌套深度安全。未证明真实用户结果库已出现这类文件；可由损坏、外部编辑或异常输入触发。

修复位于`agent_runtime/result_store.py:36,91–94,377`：仅将`json.loads`抛出的RecursionError转换为私有`_ResultJSONDepthError(RecursionError)`并保留消息/cause；search把该类型纳入现有逐记录错误通道。不提高递归限制、不额外读取、不改变信任或预算。直接show及其他_json消费者仍抛RecursionError类别，但具体子类改变；依赖精确`type(exc) is RecursionError`的外部代码需注意。普通自定义show的RecursionError、RuntimeError、SystemExit和调用者context错误仍传播。

v1广泛catch方案被真实独立reviewer否决，避免吞掉自定义回调或其他逻辑的递归错误；v2窄来源方案获批准。契约为`validation-plan.json`。原始数据、审查过程保留私有`.agent-runs/search93/`，公开独立证据另附。主AI唯一写入代码/测试/TASK；未动DISPLAY91负结果、其他仓库或人类guide。无真实ManagedEngine适配器，不声称已部署该监督服务。

## 固定输入与环境

Linux6.18.55/x86_64/glibc2.39；CPython3.12.14，Clang22.1.3，`sys.getrecursionlimit()==1000`。标准库CPU测试，无模型/API/GPU；CUDA/驱动/kernel配置不适用。

10000层固定文件，均小于METADATA_LIMIT=1048576：

| 输入 | 字节 | SHA256 |
|---|---:|---|
| list | 20013 | c7392bc3b2b6f7966d6b194e660650e4ce021cb9cebc5e4a7ff63665c9eb419d |
| dict | 60013 | 3557ed177a36ae978c4ed4caf21170421196f5f59fbbf6a683755fe35aeeb8f3 |

初始2000层在该C解码器上被接受，修前初始日志只是测试假设不成立，不能算产品缺陷。校准后冻结10000层再执行正式修前/修后，不改验收目标。先前日志不删除。Python文档说明解释器自身约束适用，并不承诺该机器的具体触发深度。

## 已执行测试及原始短日志

```text
baseline: python -m unittest discover -s tests -p test_result_search_depth.py -v
Ran 7 tests in 0.306s
FAILED (failures=2, errors=2)
```

2个失败是同一CLI测试中的普通/-O两个子用例，2错误是API正常邻居/全坏两方法；因此是3个隔离测试方法失败，不将4个失败事件冒充4个方法。另4个兼容控制方法通过。修后直接show测试另增加原始cause/消息比较，不倒称其已在基线通过。

```text
candidate: python -m unittest discover -s tests -p 'test_result*.py' -v
Ran 94 tests in 4.518s
OK
candidate: python -O -m unittest discover -s tests -p 'test_result*.py' -v
Ran 94 tests in 4.566s
OK
```

测试总运行时间仅原始日志，不是优化计时。确定性隔离方法由0/3→3/3；新增7方法全通过，涵盖文件字节不变、坏记录不被检索、正常候选保留、无命中/全坏返回incomplete、异常边界和CLI JSON输出。原始before-v2.log SHA256 `a9c324c839fca09ced921b9f1faeabcd69670d6bd2d94bb242c3148d71e7fb24`。

```text
python -m unittest discover -s tests
Ran 1338 tests in 86.092s
OK (skipped=8)
python -m unittest discover -s apps/paper-reader/tests -v
Ran 3 tests in 1.586s
OK
```

8项跳过不算通过；实际全库1330项通过。独立reviewer已另外运行普通/-O冻结基线与候选对照：7组正常输出完整相等，list/dict真实文件错误、正常邻居、CLI、消息/cause、自定义show异常身份、show之后contamination原始RecursionError仍传播、调用者context及字节不变均检查。公开脚本与原始JSON位于本目录`independent_probe.py`、`independent-normal.json`和`independent-optimized.json`；最终独立报告和发布回读另核。

## 研究与范围

历史十篇精读留在`../read-boundary56/research_a.md`和`research_b.md`，不虚称本轮新读十篇或将论文指标记作本库收益。检索历史结果scanned199/partial=true，三条词法命中与知识库概率卡均不适用此边界，未复用其性能数据。直接依据：[Python3.12 JSON官方文档](https://docs.python.org/3.12/library/json.html#implementation-limitations)，2026-10-20核对；采用错误来源隔离，不引入新的解析框架。

无速度、峰值内存、token成本、模型质量或线上成功率主张。不吞MemoryError、任意运行时递归或进程退出；不解决所有深层输入、其他模块的JSON解析或OS级资源限制。历史正常结果数据不修改、不要求重算；受损记录需修复后重新搜索，不自动授予复用权限。
