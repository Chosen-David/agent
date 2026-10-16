# MEM-CLI-09：损坏文档快照的CLI错误边界

基线 `9e2064bf534a4438aa6132d55920c8d1574f5aa2`。目标是记忆存储CLI失败协议，非推理性能。

## 问题与修复
`agent_runtime/project_memory.py:444–450` 的add/correct读取外部document_refs文件时，
JSONDecodeError及UnicodeDecodeError不在main既有MemoryError/OSError处理范围内，导致
未捕获异常/traceback。新`_load_document_refs`（404–410）只包围文件read_text和json.loads，
转换为MemoryError，由原出口输出stderr JSON和exit2；没有在main广泛捕获ValueError。
原有默认文件编码、空参数、构造器先初始化顺序和内部数据损坏信号均保留。

不吞掉内部账本JSON错误，不改数据库事务、记忆筛选、依赖失效、模型KV或接口字段。
首次add失败仍可能先初始化/升级schema；业务entries/deps/documents/events不因此新增。

## 验证与指标
冻结4种坏文件×add/correct共8子场景：修前8次未捕获解码错误；修后8/8返回exit2、
stderr可解析JSON、stdout为空、所有业务表和sqlite_sequence逐行不变。
此数值只衡量输入失败协议，不代表LLM可靠率、QA或端到端性能。
另测合法文档绑定add/correct、缺文件、首次初始化，以及内部异常不被重标。
独立复核真实CLI进程、旧库、实际损坏scope/document JSON等13组，原始记录见reviewer-raw.json。
最终完整回归以final-regression.json为准；optimized-tests.log为-O专项5项。

## 研究与适用边界
此前TallyMem定向阅读强调证据访问与执行边界；这里仅应用保持原始证据并显式区分
输入失败的工程原则，不宣称复现论文、原创算法、读完新十篇或新增性能提升。
前两次KV论文调查仍未建立真实模型服务消费者；不以本项修复替代该目标。

## 发布与历史影响
只会影响传入损坏快照的CLI错误表现；旧有效记忆/测量无需改写。调用方如依赖traceback
应改为按既有JSON错误协议处理。最终提交链接由真实远端读回确认；本报告不提前声称发布。
没有GPU、模型API、收费资源或未知训练作业调用。环境见environment.json。

手工独立plan/result审查是有界usable-with-scope，不冒充受管ReviewSession、
运行中tmux监督服务或密码学认证回执。父任务MEM-STORAGE-01保持打开。

## 保留的失败尝试
最终复核曾错误使用stdin执行完整unittest harness，multiprocessing spawn无法重新打开
`<stdin>`，随后序列化TestCase失败元组也报TypeError；该次无有效JSON，未用作通过证据。
改用带`__main__`守卫的磁盘runner，串行重跑；原失败文件/说明保留。
先前普通`python -m unittest`全库1229项（8跳过）通过，但仅最终冻结源码hash绑定的
final-regression.json支持最终发布。检索扫描160项为partial且有50条缺失记录；三个
候选为combined-corpus系列，与本CLI失败输入无匹配验收，未复用其数据。

最终冻结源码SHA256 `82ddddac68994fd53191d51a5177a91501752709023c7440161f8b7e70a950e9`；
全库1229项（8跳过）无失败/错误75.272s，Reader3项1.582s，-O专项5项通过。
