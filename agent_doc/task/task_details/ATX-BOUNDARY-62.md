# ATX-BOUNDARY-62：知识标题边界

Task-ID: ATX-BOUNDARY-62
Date: 2026-10-20

## Plan

修复 sections 的 top-level ATX 原始标题边界，保留原文字节、fence、层次与检索接口；缓存引擎升级，旧库拒绝并公开重建。固定方法、验收、限制与人工维护 DAG 见 ../../results/atx-boundary62/plan.md。基线 b69b4150e41492183433b1061add742aaa44510b。主控独占生产代码、镜像、测试和任务文档，真实独立上下文审核计划与代码/结果后才可 main 发布。guide 全目录只读。局部解析正确性指标，不宣称模型质量、速度或完整Markdown兼容。

## Progress

- 已完成只读源码/旧结果查询和 CommonMark 0.31.2 §4.2 核对。深链已有迭代实现，不重复实验；固定 ATX 案例尚未运行。计划待独立审核；当前没有受管 tmux/ReviewSession 宿主，继续已授权的有界人工维护。
- 独立计划先revise（缺canonical登记）后approve；原反馈保留。修前2 tests/40失败，修后普通和-O各2通过。固定单行矩阵33/72→72/72，115语料分段不变，真实v5缓存拒绝/重建/no-op通过；16索引测试及Reader3通过。独立结果验收与全库回归尚在进行，未发布。
- v1有限语义通过但发现长空白正则重复扫描风险，独立诊断支持，拒绝发布；原源码/测试/数据保留。v2固定宽度lookbehind，不改原oracle，添加长串控制。revision-v2.md已获独立范围审核approve。
- v2独立验收usable-with-scope：普通/-O各37212扫描参考对照、115完整节点/原文重拼接、真实旧cache迁移通过；独立专项3/index16/Reader3通过；主控全库1304（8跳过）日志经独立检查。result_review.md绑定精确hash和限制。全量独立raw本地保留不入git，摘要/hash/重放脚本提交；不是完整raw远端存储。
- 本次收尾更新索引为修复与验证完成；冻结计划与初始文档hash保留，收尾索引不冒充原审核字节。主控负责最终fetch/显式暂存/原子main发布与远端回读，持续优化及模型质量/性能验证仍未完成。
