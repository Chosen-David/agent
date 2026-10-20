# READ-BOUNDARY-56：知识读取实际字节边界

Task-ID: READ-BOUNDARY-56
Date: 2026-10-19

## Plan

冻结版本 v1；基线 ffd9abfeb2264a21e46322e4bedf310947229b2b。用户授权局部实现、测试、研究及普通推送 main。仅修改 Agent；guide 只读且 GUIDE.md 当前为空。

目标：消除 KnowledgeStore 与 ingest 在 stat 检查后无界读取的窗口，保持合法内容、换行、hash、诊断及独立插件兼容。非目标：敌对目录替换防护、原子文件快照、模型质量或端到端速度提升。

完整 DAG：A 同步/锁/指南/旧结果检索 → B 独立计划复核 → C 冻结确定性回归并执行修前失败 → D canonical 有界读取及镜像同步 → E 针对性与全量回归 → F 独立代码和实测结果审核 → G fetch 最新 main、必要重放/复验、普通发布和远端回读。A → R1/R2 两个独立论文阅读节点 → F；R1/R2 各负责五篇正文，失败来源不计数。主控唯一维护 TASK 索引。其他任务不因本修复被标完成。

方案：在 knowledge.py 增加共享 helper，二进制 read(max_bytes+1)，先按实际返回字节数拒绝超限，再严格 UTF-8 decode，依次替换 CRLF 和 CR 为 LF；原先路径、stat 快速拒绝保留。ingest 的 package 与 standalone import 均引用 helper。指标为 Python 请求及返回缓冲的上限；默认 buffered 文件的物理 read-ahead 不作承诺。

验收协议 v1（实现前冻结）：四入口（store metadata/body、ingest metadata/body）在 stat 已通过、实际 open 前增长 +1/+4096 的确定性 hook；超限以原 byte budget 消息拒绝。元数据用合法 JSON 后置空白扩展，正文用换行字节扩展；不依赖线程概率。正常文件包括空、短、精确上限 ASCII/多字节、CRLF/CR/Unicode 分隔符；非法 UTF-8 保持异常，超限非法 UTF-8 优先 budget 错误。记录每次 Python read(size) 和返回长度，必须 <= limit+1；不宣称物理 I/O 上限。拒绝 ingest 前后 corpus 字节快照及目录不变，未进入 staging；正常 ingest 的正文/provenance hash 保持 universal newline 语义。插件逐字节同步并在复制后 python -I 下实际 ingest。合法 corpus snapshot、content、hash 保持一致；既有知识/index 回归及全量 tests、paper-reader tests、生成检查均执行。

主指标：八个四入口×两增量场景的拒绝结果及 read 请求/返回缓冲；分别报告原代码可能被后续校验拒绝的情况，不能把任何迟拒绝算无界读取已解决。针对性测试修前失败必须来自实际基线；无计时收益预设，不把 CPU 微型测试外推 LLM 请求表现。

历史检索：results/read-boundary56/prior-search.json 为实际 result_store 查询，scanned=236、partial=true，存在缺失记录；五个 lexical candidates 均不覆盖该 IO 边界且 validation pending，不能复用为本轮证据。旧 scratch 证据不可用，重建复现。资源：仅当前本机 Python/CPU，最多三个独立只读/专属文件审阅上下文；单测进程一次一个，预计 30 分钟内。持有 flock；tmux 不可用，不声称常驻监督器或可信托管引擎验收。

交付范围：共享读取修复、插件镜像、回归、中文证据简报和至少十篇实际正文阅读记录；任何不足保留 pending。发布前独立审核基于真实 diff/log；不伪造托管 callback。

## Progress

- 已完成新 clone、干净基线核对、锁和指南检查。代码修改与实验尚未开始；等待独立计划 v1 审核。

- 冻结计划副本：[plan_v1.md](../../results/read-boundary56/plan_v1.md)，独立计划审核 approve；该副本保留原始 SHA，后续进展不重写它。勘误：历史五候选四项 pending、一项 stored usable-with-scope，全部均不适用于本轮 IO 边界；准确检索路径为 agent_doc/results/read-boundary56/prior-search.json。
- 修前五项回归出现八个增长场景失败及一个编码异常优先级错误；修后五项通过。同输入哈希对照八个超限接受变为全部明确拒绝；Python 请求从 -1 改为 1048577，旧返回单位为文本字符、新返回单位为字节，不能混作物理 IO 对比。
- 全量 1290 项通过（8 skipped），Reader 3 项通过；生成镜像检查和 CRLF-aware diff 检查通过。两组共十篇正文定向精读完成，另一个原文不可访问来源不计数。独立结果审核及发布回读尚待完成。
- 执行偏差：Reader 的短测试与全量测试尾段重叠，未遵守原计划单测试进程串行预算；未进行计时对比或性能宣称，测试结果仅用于正确性门槛。资源范围仍为本地 CPU，无外部训练。

- 独立结果审核六项 pass；复测16个旧新增长执行、六项导入编码边界、343种换行组合及115条语料相同。实现/验收完成，最终 main 发布和远端回读为本提交之后的发布动作；不把计划写成已推送。
