# ARTIFACT-READ-76 — 小文件分配与增长回退

Date: 2026-10-20。基线 a55a3d14d8ebf0f840c4bdd9477562fdc369fe44。
用户授权局部实现、测试、直接 main 发布；不触及 TwoLevel/SGLang。GUIDE.md 为空且只读。

## 冻结计划 v1

沿续 artifact-read74 未合入候选。旧方案 size+1 后拼接余段，增长1字节→16MiB
时峰值约33.6MB，不能复用为非退化证据。旧目录仍可读，不移动或改写。
当前结果查询 `artifact read allocation bounded dispatch` 扫描199、partial=true，
返回 convex-projection/support、discrete-lyapunov 三项词法候选，无本任务适用证据。
因此新候选必须重测。已完成的 read-boundary56 十篇正文阅读作为历史研究输入，
不计本轮新增十篇；本任务为无损资源实现，不采用论文语义压缩/自动遗忘。

方案：仅 fstat 大小小于64KiB时先 read(size+1)；未填满即返回完整数据。
若已填满，删除首段、seek(0)、read(LIMIT+1)；大文件仍直接走旧有界读取。
同一已检查的普通文件句柄，保留原路径/哈希/类型/预算拒绝与异常优先级。
不承诺原子快照或并发写入时字节级跨调用等价。增长回退会重复读取至多64KiB，
明确不宣称维持累计LIMIT+1读取量，只保证最大请求/最终长度界限。
不采用拼接/无界读取/改动哈希或截断上下文。稳定文件O(n)，返回空间O(n)。

链：同步/历史读取 → 独立计划审核 → 修前失败 → 候选 → 配对测量/回归 →
独立代码数据审核 → fetch/重放复验/普通推送/远端读回。
仅本地CPU，最多2个审核上下文，无GPU/外部模型/付费资源；tmux不可用，
不声称部署持久监督器或托管引擎回执；工具调用记录为实际独立审核身份。

固定主指标：完整prepare_dispatch小fixture的tracemalloc峰值下降>90%，输出完全相同。
必要非退化：稳定和确定性fstat后增长/缩小用例的字节/错误相同；增长到16MiB及
16MiB+1峰值不超过基线1.01倍；大文件读取请求不新增。无wall/RSS/model质量主张。
同机同输入哈希，交替baseline/candidate各5次，fixture构造在追踪区外。
尺寸0/5/4096/65535/65536/1MiB/16MiB；增长0/1/65535/8MiB到16MiB或越界，
缩小、路径/符号链接/FIFO/旧迁移digest/stalehash继续覆盖，全部结果保留。
测试先于源码改动运行小文件峰值回归，候选跑针对测试、全库与Reader，串行测试。
独立审核检查六项：implementation、reference_boundary、data_integrity、
numerical_sanity、measurement_validity、reproducibility；不足保留pending，不发布。

输出唯一主控写：源码、tests/test_result_read_allocation.py、TASK详情/索引、
CODEMAP及本目录除review*.md/independent*以外文件。审核者仅写各自审核记录。
至多一个候选；失败保留检查点，不为提交放松门槛。
