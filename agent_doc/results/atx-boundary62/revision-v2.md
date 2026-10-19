# ATX-BOUNDARY-62 candidate v2

原 plan.md 的任务、目标、方法范围、72固定单行oracle、DAG和验收不变，无阈值放宽。首版通过有限语义测试但主控发现去尾正则的长空白重复扫描风险；独立审查者通过独立小规模诊断确认相容于二次增长。因此拒绝发布首版，保留 candidate-v1.py（SHA256 9ae7016563e11bc2ac74fd9ea7863cb704d5744b023229ceedd8fca46346558b）、tests-v1.py（253ad42cb0cf8a22155d508e09935fe5e472641ce8e3b8f2e148a20273cb112d）、raw.json/raw-O.json及独立v1记录。

v2只把左侧可变长空白匹配改成固定宽度lookbehind，从ASCII空白后的#串起匹配，不再从空白run每个位置重试；不改变预期语义。生产源码/镜像SHA256 ab45ef3d0a9005741951a1e8c114366533338c861373cbdd78ac1efd41558a8c。新增10k空白/hash/末尾tab控制，当前测试SHA256 25c518f7b44bcc55c027a25f072a5f7b4a751e1df68428097ead10b0425501f3，原72case与层次oracle未改。

新结果 raw-v2.json/raw-v2-O.json，仍33/72→72/72、115语料分段不变，真实旧缓存迁移通过；原数据从不覆盖。完整回归重新运行、独立验收只接受v2对应结果。独立长度增长计时仅用来识别首版风险，没有预热/正式性能协议，不作为生产提速证据；本轮仍只有解析正确性主张。
