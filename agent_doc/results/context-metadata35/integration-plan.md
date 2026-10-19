# CONTEXT-METADATA-35 integration phase v1

本阶段依赖review.md最终六项usable-with-scope验收，不仅依赖producer accepted字段。基线仍24c892a721d0d511c0b38704ad5093fabfce5433；用户同接口实现优化/验证后main直推授权不变。原测量计划/脚本及全部原始数据冻结；保存原脚本与task精确副本及哈希后，才更新复现入口与Progress，记录历史路径映射。人工guide、历史数据和其他仓库不改。

目标：把已测候选三方法迁入生产，完全保持公共get、最终bundle深拷贝、导航顺序、预算、custom-get回退与错误门。新增私有_metadata，context/related各一处调用替换；原get不重构，避免改变旧克隆/验证顺序。源码与standalone mirror字节同步。非JSON注入、任意并发外部records修改不作等价保证；不得称全域语义证明。

复现脚本新增固定BASE git加载与--production选择。默认仍测同候选，--production实测真实生产类对固定旧基线；计时/16场景/2warmup+11pair/10%目标及其他时间内存门槛完全不变，不看数据调阈值。保留原脚本在results/frozen-benchmark.py以对应旧测量。仅新增1次实际生产路径120s配对测量，0调参重试；独立审核者检查其全部原始数据/源码身份/边界，无额外性能复跑要求，因为上一阶段已有独立复跑。若生产路径门槛或正确性失败，不发布，不凭候选好结果覆盖失败。

新增结构回归：元数据导航无需序列化全文、拒绝超条目预算的seed无全文物化、最后输出get仍隔离、custom-get包装器仍被调用；先保存修前失败再实施。运行新专项、知识相关回归、全库unittest tests（timeout300s）、paper-reader（timeout60s）、镜像同步检查。全库受平台/依赖限制的原有skip如实报告，不新增skip躲避错误。主控单写实现/镜像/测试/复现脚本/TASK/CODEMAP/简报；同一独立审查者审核计划及最终代码/实际数据/回归，不能自己改生产。

DAG：最终候选验收 → 本阶段独立计划审核 → red测试 → 三方法集成及镜像/脚本 → 新测量+全回归 → 独立集成验收 → fresh fetch main → 仅本任务小文件普通push或expectedSHA非force原子API更新 → fetch/关键内容/tree回读。大原始数据保留本地而不混入提交；公开短报告注明不能仅凭短报告复算全部样本。无原生ReviewSession/tmux适配仍如实保持受管执行/发布blocked，本轮仅用户授权的人工有界维护，不伪造认证回执。

资源：CPU串行，不与独立测量并行跑全库；本阶段不超过900s，包含120s测量/300s全库/60sReader，其余检查有界；本次计划审核作为总预算第2轮，不隐式续开循环。维护异常闭包、主分支并发保留、凭据不得写入报告；不可把局部CPU收益写成LLM质量/TTFT/token成本收益。有限修复完成不关闭持续任务。
