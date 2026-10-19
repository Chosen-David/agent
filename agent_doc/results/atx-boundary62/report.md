# ATX-BOUNDARY-62：原始标题边界

基线 `b69b4150e41492183433b1061add742aaa44510b`。`agent_runtime/knowledge_index.py:47–57` 原正则不要求尾部井号之前有空格，导致 `# C#` 的标题变成 `C`；Unicode空白会被误识别/吞掉，空ATX标题遗漏。CLI的tree/section及索引search/build均调用sections，因此这不是只存在于测试辅助函数的问题。现有115条语料本次分段差分为0，不能声称既有线上回答已经受损。

局部修复采用 CommonMark 0.31.2 §4.2 的标记边界：开头与闭合井号仅允许对应ASCII空格/tab，允许空标题，保留原始inline字符。不解析inline HTML、实体或转义，不扩展HTML/container/setext支持；原splitlines行划分、fence逻辑和body字节不变。同步standalone镜像；引擎v5→v6，使旧SQLite缓存必须重建。源知识及历史实验不改。

规范来源：https://spec.commonmark.org/0.31.2/#atx-headings （版本2024-01-28，核验2026-10-19）。已有十篇论文精读记录在 read-boundary56/research_a.md、research_b.md；本次仅复核其研究记录作背景，不计十篇新阅读，也不把规范修复包装成论文算法创新。

## 修前与修后证据

固定测试在生产修改前已写并经独立计划审查。修前 `python -m unittest discover -s tests -p test_knowledge_atx.py -v`：2 tests，40 failures（39个单行失配+1层次失配），完整临时日志 `/tmp/atx62-before.log`；该日志不保证跨机器可用，稳定重放由probe固定git基线完成。

修后同命令及 `python -O` 均2 tests OK。probe.py 在普通与-O分别加载真实固定旧源码与当前生产源码：72个单行完整节点字典，baseline 33/72、candidate 72/72；115条语料完整分段逐项相等。另一显式三节点测试覆盖空标题parent、fence和原文拼接。输入/源码/脚本hash、系统版本、全部逐例期望与实际输出保留 raw.json/raw-O.json；不覆盖重跑，应使用新的 --output 路径。

真实v5完整module对一条合法合成语料建库；新搜索拒绝 `stale index engine; run index to update`；相同store/snapshot公开build_index重建1条、chunks结构得到修正，第二次unchanged=1且engine_changed=false，公开search/navigation通过。不是仅替换cache版本字符串的测试。

集成：test_knowledge_index*.py 16项通过，Reader3项通过。全库和独立结果验收状态在本文件末尾追加。两份生产源码SHA256均 `9ae7016563e11bc2ac74fd9ea7863cb704d5744b023229ceedd8fca46346558b`；git diff --check通过。

仅Python3.12.14、Linux x86_64、标准库sqlite CPU逻辑验证；没有模型/GPU调用、无速度/显存/任务质量测量。正确性比例只适用于冻结合成矩阵，不是自然分布成功率。缓存首次重建有必要开销，未测速。旧fence/section性能数据不改，未来性能比较须标新引擎并分开重建与查询成本。

## 宿主与发布边界

独立计划审核保存初始revise和修订approve；真实独立上下文将验收代码和数据。没有managed tmux/ReviewSession适配器，未伪称部署受管守护进程。guide只读、旧任务/结果/无关归档临时文件保留；发布仅暂存本任务准确文件，fetch并发核对后原子main更新、远端回读单独闭环。

## v2修订：首版不发布

上文raw.json/raw-O.json和9ae70165源码hash均是首版历史。独立验收期间主控发现去尾正则长空白重复扫描风险，审查者的小规模长度诊断支持此风险；首版不发布。完整首版源码/测试以candidate-v1.py/tests-v1.py保留并精确匹配hash。v2改用固定宽度lookbehind，目标和oracle不变，追加长串控制，不放宽验收；细节见revision-v2.md。

最终候选数据为raw-v2.json/raw-v2-O.json，生产/镜像SHA256 `ab45ef3d0a9005741951a1e8c114366533338c861373cbdd78ac1efd41558a8c`；仍33/72→72/72、115语料不变和真实v5缓存迁移通过。普通/-O专项各3 tests OK，Reader3通过；首版全库1303/8skip通过只算旧验证，v2已重新运行等待结果。诊断时间不算正式性能对照，不发布提速百分比。

v2最终全库：1304 tests，8 skipped，OK；Reader3和普通/-O专项3通过。短原始摘要见validation.txt；独立实际重跑与六项验收另见result_review.md。全量本地unittest日志不提交，不把其运行耗时当性能收益。

独立验收最终为v2 usable-with-scope：普通/-O各37212边界、115完整语料节点/原文拼接、真实v5迁移与独立专项回归通过。详见result_review.md（包括v1拒绝史）。四份约1.9MB独立完整raw只在本地，不入git；对应summary保存完整文件hash及逐条状态、原始代码与可重放脚本提交，不宣称摘要能恢复全部原文或已远端持久化所有raw。ResultStore历史索引只为发现，status保持unknown，不替代真实独立验收。
