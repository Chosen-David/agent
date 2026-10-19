# PROMPT-READ-67

Task-ID: PROMPT-READ-67
Date: 2026-10-20

## Plan

限制提示词加载器拒绝超限文件前的读取量，保留原1,000,000字节阈值、
解码/hash/换行及完整装配语义。基线0cb8cc1d。先复现失败，再有界读取，
定向边界、全回归与独立对照；主控仅发布验收版本。只修改prompt读取和测试文档。

## Progress

修前新增3项测试1失败；修后普通/-O各17项prompt测试、Reader3通过。
独立12读取/6compose对照通过。16MiB超限文件分配由约16.78MB降至1.01MB，
只支持Python追踪峰值，不宣称延迟、RSS、LLM质量收益。
详见 [报告](../../results/prompt-read67/report.md)。全库1307项（8跳过）其余通过；
实现与验证完成，发布另行回读远端SHA和文件树。
